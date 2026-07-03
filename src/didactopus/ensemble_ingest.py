from __future__ import annotations

import hashlib
import json
import re
import socket
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .document_adapters import adapt_document, canonical_source_path, detect_adapter
from .topic_ingest import extract_key_terms, slugify


SUPPORTED_SUFFIXES = {
    ".632",
    ".md",
    ".markdown",
    ".txt",
    ".log",
    ".html",
    ".htm",
    ".pdf",
    ".docx",
    ".pptx",
}
CHECKPOINT_MODES = {"none", "file", "chunk"}


@dataclass
class EnsembleIngestResult:
    out_dir: Path
    manifest: dict[str, Any]
    artifacts: dict[str, str]


def _timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    text = "\n".join(json.dumps(row, sort_keys=True) for row in rows)
    if text:
        text += "\n"
    path.write_text(text, encoding="utf-8")


def _append_jsonl(path: Path, row: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")


def _is_under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _is_supported_path(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES


def discover_ensemble_sources(source_root: str | Path, out_dir: str | Path | None = None) -> list[Path]:
    root = Path(source_root)
    output = Path(out_dir).resolve() if out_dir is not None else None
    if root.is_file():
        return [root] if _is_supported_path(root) else []
    if not root.exists():
        raise FileNotFoundError(f"Source root does not exist: {source_root}")
    if not root.is_dir():
        raise ValueError(f"Source root is not a file or directory: {source_root}")
    paths = []
    for child in sorted(root.rglob("*")):
        if output is not None and _is_under(child, output):
            continue
        if _is_supported_path(child):
            paths.append(child)
    return paths


def _default_display_root(source_root: Path) -> Path:
    return source_root.parent if source_root.is_file() else source_root


def _source_id_for(display_path: str, digest: str) -> str:
    return f"src_{slugify(display_path)}_{digest[:12]}"


def _split_long_text(text: str, max_chars: int) -> list[str]:
    stripped = text.strip()
    if not stripped:
        return []
    if len(stripped) <= max_chars:
        return [stripped]
    paragraphs = [item.strip() for item in re.split(r"\n\s*\n", stripped) if item.strip()]
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    for paragraph in paragraphs or [stripped]:
        if len(paragraph) > max_chars:
            if current:
                chunks.append("\n\n".join(current).strip())
                current = []
                current_len = 0
            for idx in range(0, len(paragraph), max_chars):
                chunks.append(paragraph[idx : idx + max_chars].strip())
            continue
        projected = current_len + len(paragraph) + (2 if current else 0)
        if current and projected > max_chars:
            chunks.append("\n\n".join(current).strip())
            current = [paragraph]
            current_len = len(paragraph)
        else:
            current.append(paragraph)
            current_len = projected
    if current:
        chunks.append("\n\n".join(current).strip())
    return [chunk for chunk in chunks if chunk]


def _fragment_records(source_row: dict[str, Any], doc: Any, max_chunk_chars: int) -> list[dict[str, Any]]:
    fragments: list[dict[str, Any]] = []
    sequence = 1
    for section in doc.sections:
        section_text = section.body.strip()
        if not section_text:
            continue
        for chunk_index, chunk in enumerate(_split_long_text(section_text, max_chunk_chars), start=1):
            fragments.append(
                {
                    "fragment_id": f"frag_{source_row['source_id']}_{sequence:04d}",
                    "source_id": source_row["source_id"],
                    "source_path": source_row["path"],
                    "section": section.heading,
                    "chunk_index": chunk_index,
                    "text": chunk,
                    "metadata": {
                        "source_type": doc.source_type,
                        "max_chunk_chars": max_chunk_chars,
                    },
                    "current_status": "draft",
                }
            )
            sequence += 1
    if not fragments and doc.text.strip():
        for chunk_index, chunk in enumerate(_split_long_text(doc.text, max_chunk_chars), start=1):
            fragments.append(
                {
                    "fragment_id": f"frag_{source_row['source_id']}_{sequence:04d}",
                    "source_id": source_row["source_id"],
                    "source_path": source_row["path"],
                    "section": "Main",
                    "chunk_index": chunk_index,
                    "text": chunk,
                    "metadata": {
                        "source_type": doc.source_type,
                        "max_chunk_chars": max_chunk_chars,
                    },
                    "current_status": "draft",
                }
            )
            sequence += 1
    return fragments


def _observation_role(text: str) -> tuple[str, float, list[str]]:
    stripped = text.strip()
    lowered = stripped.lower()
    if stripped.endswith("?") or lowered.startswith(("question:", "q:")):
        return "question", 0.55, ["needs_answer_or_source_support"]
    if lowered.startswith(("exercise:", "objective:", "prompt:")):
        return "practice_prompt", 0.65, ["learning_signal"]
    if stripped.startswith(("- ", "* ", "+ ")):
        return "claim", 0.7, ["bullet_claim"]
    if re.search(r"\b(because|therefore|thus|shows|indicates|suggests|supports|rejects|causes|caused|proves)\b", lowered):
        return "claim", 0.65, ["argument_cue"]
    return "summary", 0.6, ["summary_candidate"]


def _observation_units(fragment_text: str) -> list[str]:
    units: list[str] = []
    for raw_line in fragment_text.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue
        if stripped.startswith(("- ", "* ", "+ ")):
            units.append(stripped)
            continue
        parts = [part.strip() for part in re.split(r"(?<=[.!?])\s+", stripped) if part.strip()]
        units.extend(parts or [stripped])
    return units


def _concept_ids_for(section: str, text: str) -> list[str]:
    concepts = [f"concept::{slugify(section)}"] if section else []
    concepts.extend(f"concept::{slugify(term)}" for term in extract_key_terms(text, max_terms=6))
    return sorted({concept for concept in concepts if concept != "concept::untitled"})


def _build_records_for_fragment(fragment: dict[str, Any], source_row: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    observations: list[dict[str, Any]] = []
    claims: list[dict[str, Any]] = []
    concepts: list[dict[str, Any]] = []
    review_items: list[dict[str, Any]] = []

    fragment_concept_ids = _concept_ids_for(fragment["section"], fragment["text"])
    for concept_id in fragment_concept_ids:
        concepts.append(
            {
                "concept_id": concept_id,
                "title": concept_id.replace("concept::", "").replace("-", " ").title(),
                "aliases": [],
                "description": f"Draft concept candidate from section '{fragment['section']}'.",
                "source_fragment_ids": [fragment["fragment_id"]],
                "source_ids": [source_row["source_id"]],
                "current_status": "draft",
            }
        )
        review_items.append(
            {
                "review_candidate_id": f"review_{concept_id.replace('concept::', 'concept_')}_{fragment['fragment_id']}",
                "candidate_type": "concept",
                "candidate_id": concept_id,
                "triage_lane": "concept_promotion",
                "priority": 60,
                "finding_codes": ["draft_concept_candidate"],
                "rationale": "Promote, merge, alias, or reject after ensemble ingestion completes.",
                "current_status": "draft",
            }
        )

    for index, unit in enumerate(_observation_units(fragment["text"]), start=1):
        role, confidence, finding_codes = _observation_role(unit)
        cleaned = re.sub(r"^[-*+]\s+", "", unit).strip()
        observation_id = f"obs_{fragment['fragment_id']}_{index:03d}"
        observation = {
            "observation_id": observation_id,
            "source_id": source_row["source_id"],
            "fragment_id": fragment["fragment_id"],
            "role": role,
            "text": cleaned,
            "section": fragment["section"],
            "confidence_hint": confidence,
            "finding_codes": finding_codes,
            "current_status": "draft",
        }
        observations.append(observation)
        if role not in {"claim", "summary"}:
            review_items.append(
                {
                    "review_candidate_id": f"review_{observation_id}",
                    "candidate_type": "observation",
                    "candidate_id": observation_id,
                    "triage_lane": "source_support",
                    "priority": 50,
                    "finding_codes": finding_codes,
                    "rationale": "Observation captured without blocking the ensemble ingestion pass.",
                    "current_status": "draft",
                }
            )
            continue
        claim_id = f"clm_{fragment['fragment_id']}_{index:03d}"
        claim = {
            "claim_id": claim_id,
            "claim_text": cleaned,
            "claim_kind": "statement" if role == "claim" else "summary",
            "source_observation_ids": [observation_id],
            "supporting_fragment_ids": [fragment["fragment_id"]],
            "concept_ids": fragment_concept_ids[:4],
            "confidence_hint": confidence,
            "review_confidence": 0.0,
            "provenance": {
                "origin_artifact_id": source_row["source_id"],
                "origin_path": source_row["path"],
                "origin_section": fragment["section"],
                "machine_id": socket.gethostname(),
                "support_kind": "direct_source",
                "grounding_status": "partially_grounded",
            },
            "current_status": "draft",
        }
        claims.append(claim)
        review_items.append(
            {
                "review_candidate_id": f"review_{claim_id}",
                "candidate_type": "claim",
                "candidate_id": claim_id,
                "triage_lane": "claim_review",
                "priority": 70 if role == "claim" else 55,
                "finding_codes": finding_codes + ["needs_review_before_promotion"],
                "rationale": "Draft claim captured during complete ensemble ingestion; review after the full source set is processed.",
                "current_status": "draft",
            }
        )
    return observations, claims, concepts, review_items


def _merge_concepts(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: OrderedDict[str, dict[str, Any]] = OrderedDict()
    for row in rows:
        existing = merged.setdefault(row["concept_id"], row)
        if existing is row:
            continue
        existing["source_fragment_ids"] = sorted(set(existing.get("source_fragment_ids", [])) | set(row.get("source_fragment_ids", [])))
        existing["source_ids"] = sorted(set(existing.get("source_ids", [])) | set(row.get("source_ids", [])))
    return list(merged.values())


def _checkpoint_payload(
    ingest_id: str,
    event: str,
    source_path: str,
    counts: dict[str, int],
    completed: bool = False,
    error: str = "",
) -> dict[str, Any]:
    payload = {
        "ingest_id": ingest_id,
        "event": event,
        "source_path": source_path,
        "counts": dict(counts),
        "completed": completed,
        "updated_at": _timestamp(),
    }
    if error:
        payload["error"] = error
    return payload


def run_ensemble_ingest(
    source_root: str | Path,
    out_dir: str | Path,
    ingest_id: str | None = None,
    display_root: str | Path | None = None,
    checkpoint_every: str = "chunk",
    max_chunk_chars: int = 3000,
) -> EnsembleIngestResult:
    if checkpoint_every not in CHECKPOINT_MODES:
        raise ValueError(f"Unsupported checkpoint mode: {checkpoint_every}")
    if max_chunk_chars < 200:
        raise ValueError("max_chunk_chars must be at least 200")

    source_path = Path(source_root)
    target = Path(out_dir)
    actual_ingest_id = ingest_id or f"ensemble-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    actual_display_root = Path(display_root) if display_root is not None else _default_display_root(source_path)
    discovered = discover_ensemble_sources(source_path, out_dir=target)
    target.mkdir(parents=True, exist_ok=True)

    started_at = _timestamp()
    checkpoint_path = target / "checkpoint.json"
    checkpoints_path = target / "checkpoints.jsonl"
    checkpoints_path.write_text("", encoding="utf-8")

    source_rows: list[dict[str, Any]] = []
    fragment_rows: list[dict[str, Any]] = []
    observation_rows: list[dict[str, Any]] = []
    claim_rows: list[dict[str, Any]] = []
    concept_rows: list[dict[str, Any]] = []
    review_items: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    counts = {
        "source_count": len(discovered),
        "processed_source_count": 0,
        "failed_source_count": 0,
        "fragment_count": 0,
        "observation_count": 0,
        "claim_count": 0,
        "concept_count": 0,
        "review_candidate_count": 0,
    }

    for path in discovered:
        display_path = canonical_source_path(path, actual_display_root)
        try:
            digest = _sha256(path)
        except OSError as exc:
            errors.append({"source_path": display_path, "error": str(exc)})
            counts["failed_source_count"] += 1
            payload = _checkpoint_payload(actual_ingest_id, "source_error", display_path, counts, error=str(exc))
            _write_json(checkpoint_path, payload)
            _append_jsonl(checkpoints_path, payload)
            continue

        source_row = {
            "source_id": _source_id_for(display_path, digest),
            "title": path.stem.replace("_", " ").replace("-", " ").title(),
            "source_type": detect_adapter(path),
            "path": display_path,
            "sha256": digest,
            "byte_count": path.stat().st_size,
            "metadata": {},
            "current_status": "draft",
        }
        source_rows.append(source_row)
        try:
            doc = adapt_document(path, display_root=actual_display_root)
        except Exception as exc:  # noqa: BLE001 - ingestion must continue and record source-level failures.
            errors.append({"source_path": display_path, "error": str(exc)})
            counts["failed_source_count"] += 1
            payload = _checkpoint_payload(actual_ingest_id, "source_error", display_path, counts, error=str(exc))
            _write_json(checkpoint_path, payload)
            _append_jsonl(checkpoints_path, payload)
            continue
        source_row["metadata"] = dict(doc.metadata or {})

        fragments = _fragment_records(source_row, doc, max_chunk_chars=max_chunk_chars)
        for fragment in fragments:
            fragment_rows.append(fragment)
            observations, claims, concepts, reviews = _build_records_for_fragment(fragment, source_row)
            observation_rows.extend(observations)
            claim_rows.extend(claims)
            concept_rows.extend(concepts)
            review_items.extend(reviews)
            counts["fragment_count"] = len(fragment_rows)
            counts["observation_count"] = len(observation_rows)
            counts["claim_count"] = len(claim_rows)
            counts["concept_count"] = len(_merge_concepts(concept_rows))
            counts["review_candidate_count"] = len(review_items)
            if checkpoint_every == "chunk":
                payload = _checkpoint_payload(actual_ingest_id, "chunk_processed", display_path, counts)
                _write_json(checkpoint_path, payload)
                _append_jsonl(checkpoints_path, payload)

        counts["processed_source_count"] += 1
        if checkpoint_every == "file":
            payload = _checkpoint_payload(actual_ingest_id, "source_processed", display_path, counts)
            _write_json(checkpoint_path, payload)
            _append_jsonl(checkpoints_path, payload)

    concept_rows = _merge_concepts(concept_rows)
    counts["concept_count"] = len(concept_rows)
    counts["review_candidate_count"] = len(review_items)
    completed_at = _timestamp()
    manifest = {
        "run_kind": "didactopus_ensemble_ingest",
        "ingest_id": actual_ingest_id,
        "source_root": str(source_path),
        "display_root": str(actual_display_root),
        "started_at": started_at,
        "completed_at": completed_at,
        "machine_id": socket.gethostname(),
        "non_interactive": True,
        "stop_policy": "never_block_on_extracted_claim_or_concept",
        "checkpoint_every": checkpoint_every,
        "max_chunk_chars": max_chunk_chars,
        "counts": counts,
        "errors": errors,
        "artifacts": {
            "sources": "sources.jsonl",
            "fragments": "fragments.jsonl",
            "observations": "observations.jsonl",
            "claims": "claims.jsonl",
            "concepts": "concepts.jsonl",
            "review_queue": "review_queue.json",
            "checkpoints": "checkpoints.jsonl",
        },
    }

    review_queue = {
        "queue_kind": "didactopus_ensemble_review_queue",
        "ingest_id": actual_ingest_id,
        "queue_length": len(review_items),
        "items": review_items,
        "policy": "Review after complete ensemble ingestion; do not require review during extraction.",
    }
    coverage = {
        "ingest_id": actual_ingest_id,
        "source_count": counts["source_count"],
        "processed_source_count": counts["processed_source_count"],
        "failed_source_count": counts["failed_source_count"],
        "unprocessed_source_count": counts["source_count"] - counts["processed_source_count"] - counts["failed_source_count"],
        "complete": True,
        "errors": errors,
    }
    summary = {
        "ingest_id": actual_ingest_id,
        "out_dir": str(target),
        "counts": counts,
        "complete": True,
        "error_count": len(errors),
        "review_queue": "review_queue.json",
    }

    _write_json(target / "manifest.json", manifest)
    _write_json(target / "coverage.json", coverage)
    _write_json(target / "review_queue.json", review_queue)
    _write_json(target / "summary.json", summary)
    _write_jsonl(target / "sources.jsonl", source_rows)
    _write_jsonl(target / "fragments.jsonl", fragment_rows)
    _write_jsonl(target / "observations.jsonl", observation_rows)
    _write_jsonl(target / "claims.jsonl", claim_rows)
    _write_jsonl(target / "concepts.jsonl", concept_rows)

    final_checkpoint = _checkpoint_payload(actual_ingest_id, "complete", "", counts, completed=True)
    _write_json(checkpoint_path, final_checkpoint)
    _append_jsonl(checkpoints_path, final_checkpoint)

    artifacts = {key: str(target / value) for key, value in manifest["artifacts"].items()}
    artifacts |= {
        "manifest": str(target / "manifest.json"),
        "coverage": str(target / "coverage.json"),
        "summary": str(target / "summary.json"),
        "checkpoint": str(checkpoint_path),
    }
    return EnsembleIngestResult(out_dir=target, manifest=manifest, artifacts=artifacts)
