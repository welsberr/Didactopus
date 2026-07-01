from __future__ import annotations

"""Legacy flat GroundRecall import module.

Compatibility path retained during the internal namespace migration.
Prefer imports and CLI usage under ``didactopus.groundrecall.ingest`` or
``didactopus.groundrecall.cli`` for new code.
"""

import argparse
import json
import socket
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .groundrecall_discovery import DiscoveredArtifact, discover_llmwiki_artifacts
from .groundrecall_lint import lint_import_directory
from .groundrecall_normalizer import (
    ImportContext,
    build_artifact_record,
    build_claim_record,
    build_concept_records,
    build_observation_record,
    build_relation_records,
    manifest_record,
)
from .groundrecall_review_bridge import export_review_bundle_from_import
from .groundrecall_review_queue import build_review_queue
from .groundrecall_segmenter import SegmentedPage, segment_markdown_artifact
from .groundrecall_source_adapters.base import detect_source_adapter
import didactopus.groundrecall_source_adapters  # noqa: F401


VALID_MODES = {"archive", "quick", "grounded"}


@dataclass
class ImportResult:
    manifest: dict[str, Any]
    artifacts: list[dict[str, Any]]
    observations: list[dict[str, Any]]
    claims: list[dict[str, Any]]
    concepts: list[dict[str, Any]]
    relations: list[dict[str, Any]]
    out_dir: Path


def _timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _default_import_id(source_root: Path) -> str:
    stem = source_root.name.lower().replace("_", "-")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{stem}-{stamp}"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    text = "\n".join(json.dumps(row, sort_keys=True) for row in rows)
    if text:
        text += "\n"
    path.write_text(text, encoding="utf-8")


def _dedupe_by_key(rows: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    unique: OrderedDict[str, dict[str, Any]] = OrderedDict()
    for row in rows:
        unique.setdefault(str(row[key]), row)
    return list(unique.values())


def run_groundrecall_import(
    source_root: str | Path,
    out_root: str | Path | None = None,
    mode: str = "quick",
    import_id: str | None = None,
    machine_id: str | None = None,
    agent_id: str = "didactopus.groundrecall_import",
) -> ImportResult:
    source_path = Path(source_root).resolve()
    if mode not in VALID_MODES:
        raise ValueError(f"Unsupported import mode: {mode}")
    adapter = detect_source_adapter(source_path)
    discovered = adapter.discover(source_path)
    artifacts = [
        DiscoveredArtifact(
            path=item.path,
            relative_path=item.relative_path,
            artifact_kind=item.artifact_kind,
            is_text=item.is_text,
        )
        for item in discovered
    ]
    actual_import_id = import_id or _default_import_id(source_path)
    output_root = Path(out_root) if out_root else source_path / "imports"
    output_dir = output_root / actual_import_id
    output_dir.mkdir(parents=True, exist_ok=True)

    context = ImportContext(
        import_id=actual_import_id,
        import_mode=mode,
        machine_id=machine_id or socket.gethostname(),
        agent_id=agent_id,
        source_root=str(source_path),
        imported_at=_timestamp(),
    )

    artifact_rows: list[dict[str, Any]] = []
    observation_rows: list[dict[str, Any]] = []
    claim_rows: list[dict[str, Any]] = []
    concept_rows: list[dict[str, Any]] = []
    relation_rows: list[dict[str, Any]] = []
    structured_rows = adapter.build_rows(context, discovered)
    if structured_rows is not None:
        artifact_rows.extend(structured_rows.artifact_rows)
        observation_rows.extend(structured_rows.observation_rows)
        claim_rows.extend(structured_rows.claim_rows)
        concept_rows.extend(structured_rows.concept_rows)
        relation_rows.extend(structured_rows.relation_rows)
    else:
        for artifact in artifacts:
            page: SegmentedPage | None = None
            if artifact.is_text and artifact.path.suffix.lower() in {".md", ".markdown", ".txt", ".log"}:
                page = segment_markdown_artifact(artifact)
            artifact_row = build_artifact_record(context, artifact, page)
            artifact_rows.append(artifact_row)
            if page is None:
                continue

            concept_rows.extend(build_concept_records(context, artifact_row, page.concepts))
            relation_rows.extend(build_relation_records(context, artifact_row, page.concepts, page.links))

            for index, observation in enumerate(page.observations, start=1):
                observation_row = build_observation_record(context, artifact_row, observation, index)
                observation_rows.append(observation_row)
                if mode == "archive":
                    continue
                if observation.role not in {"claim", "summary"}:
                    continue
                claim_rows.append(build_claim_record(context, observation_row, observation, page.concepts[:3], index))

    concept_rows = _dedupe_by_key(concept_rows, "concept_id")
    relation_rows = _dedupe_by_key(relation_rows, "relation_id")
    artifact_rows = _dedupe_by_key(artifact_rows, "artifact_id")
    observation_rows = _dedupe_by_key(observation_rows, "observation_id")
    claim_rows = _dedupe_by_key(claim_rows, "claim_id")

    manifest = manifest_record(context) | {
        "source_adapter": adapter.name,
        "import_intent": adapter.import_intent(),
        "artifact_count": len(artifact_rows),
        "observation_count": len(observation_rows),
        "claim_count": len(claim_rows),
        "concept_count": len(concept_rows),
        "relation_count": len(relation_rows),
    }

    _write_json(output_dir / "manifest.json", manifest)
    _write_jsonl(output_dir / "artifacts.jsonl", artifact_rows)
    _write_jsonl(output_dir / "observations.jsonl", observation_rows)
    _write_jsonl(output_dir / "claims.jsonl", claim_rows)
    _write_jsonl(output_dir / "concepts.jsonl", concept_rows)
    _write_jsonl(output_dir / "relations.jsonl", relation_rows)
    lint_payload = lint_import_directory(output_dir)
    _write_json(output_dir / "lint_findings.json", lint_payload)
    review_queue = build_review_queue(output_dir)
    _write_json(output_dir / "review_queue.json", review_queue)
    export_review_bundle_from_import(output_dir)

    return ImportResult(
        manifest=manifest,
        artifacts=artifact_rows,
        observations=observation_rows,
        claims=claim_rows,
        concepts=concept_rows,
        relations=relation_rows,
        out_dir=output_dir,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Import an llmwiki-style repository into GroundRecall import artifacts.")
    parser.add_argument("source_root")
    parser.add_argument("--out-root", default=None)
    parser.add_argument("--mode", choices=sorted(VALID_MODES), default="quick")
    parser.add_argument("--import-id", default=None)
    parser.add_argument("--machine-id", default=None)
    parser.add_argument("--agent-id", default="didactopus.groundrecall_import")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = run_groundrecall_import(
        source_root=args.source_root,
        out_root=args.out_root,
        mode=args.mode,
        import_id=args.import_id,
        machine_id=args.machine_id,
        agent_id=args.agent_id,
    )
    print(f"Wrote import artifacts to {result.out_dir}")
