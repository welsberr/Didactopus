from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .query import build_query_bundle_for_concept
from .store import GroundRecallStore


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    text = "\n".join(json.dumps(row, sort_keys=True) for row in rows)
    if text:
        text += "\n"
    path.write_text(text, encoding="utf-8")


def export_canonical_snapshot(
    store_dir: str | Path,
    out_dir: str | Path,
    snapshot_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, str]:
    store = GroundRecallStore(store_dir)
    target = Path(out_dir)
    target.mkdir(parents=True, exist_ok=True)

    actual_snapshot_id = snapshot_id or f"snapshot-export-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    snapshot = store.build_snapshot(
        snapshot_id=actual_snapshot_id,
        created_at=_now(),
        metadata={"export_kind": "canonical", **(metadata or {})},
    )
    store.save_snapshot(snapshot)

    snapshot_path = target / "groundrecall_snapshot.json"
    _write_json(snapshot_path, snapshot.model_dump())
    _write_jsonl(target / "claims.jsonl", [item.model_dump() for item in snapshot.claims])
    _write_jsonl(target / "concepts.jsonl", [item.model_dump() for item in snapshot.concepts])
    _write_jsonl(target / "relations.jsonl", [item.model_dump() for item in snapshot.relations])
    provenance_manifest = {
        "snapshot_id": snapshot.snapshot_id,
        "created_at": snapshot.created_at,
        "source_count": len(snapshot.sources),
        "artifact_count": len(snapshot.artifacts),
        "observation_count": len(snapshot.observations),
    }
    _write_json(target / "provenance_manifest.json", provenance_manifest)
    manifest = {
        "export_kind": "canonical",
        "snapshot_id": snapshot.snapshot_id,
        "files": [
            "groundrecall_snapshot.json",
            "claims.jsonl",
            "concepts.jsonl",
            "relations.jsonl",
            "provenance_manifest.json",
        ],
    }
    _write_json(target / "export_manifest.json", manifest)
    return {
        "snapshot_json": str(snapshot_path),
        "claims_jsonl": str(target / "claims.jsonl"),
        "concepts_jsonl": str(target / "concepts.jsonl"),
        "relations_jsonl": str(target / "relations.jsonl"),
        "provenance_manifest_json": str(target / "provenance_manifest.json"),
        "export_manifest_json": str(target / "export_manifest.json"),
    }


def export_query_bundle(
    store_dir: str | Path,
    concept_ref: str,
    out_path: str | Path,
) -> dict[str, Any]:
    payload = build_query_bundle_for_concept(store_dir, concept_ref)
    if payload is None:
        raise KeyError(f"Unknown concept reference: {concept_ref}")
    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    _write_json(path, payload)
    return payload


def export_canonical_bundle(
    store_dir: str | Path,
    out_dir: str | Path,
    concept_refs: list[str] | None = None,
    snapshot_id: str | None = None,
) -> dict[str, Any]:
    target = Path(out_dir)
    target.mkdir(parents=True, exist_ok=True)
    outputs = export_canonical_snapshot(store_dir, target, snapshot_id=snapshot_id)
    query_bundle_paths: list[str] = []
    for concept_ref in concept_refs or []:
        safe_name = concept_ref.lower().replace(" ", "-").replace("::", "-")
        bundle_path = target / f"query_bundle__{safe_name}.json"
        export_query_bundle(store_dir, concept_ref, bundle_path)
        query_bundle_paths.append(str(bundle_path))
    manifest = json.loads((target / "export_manifest.json").read_text(encoding="utf-8"))
    manifest["query_bundles"] = query_bundle_paths
    _write_json(target / "export_manifest.json", manifest)
    return {
        "canonical_outputs": outputs,
        "query_bundles": query_bundle_paths,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export canonical GroundRecall artifacts.")
    parser.add_argument("store_dir")
    parser.add_argument("out_dir")
    parser.add_argument("--snapshot-id", default=None)
    parser.add_argument("--concept", action="append", default=[])
    return parser


def main() -> None:
    args = build_parser().parse_args()
    payload = export_canonical_bundle(
        store_dir=args.store_dir,
        out_dir=args.out_dir,
        concept_refs=list(args.concept or []),
        snapshot_id=args.snapshot_id,
    )
    print(json.dumps(payload, indent=2))
