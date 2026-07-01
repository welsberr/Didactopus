from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
import re

import yaml

from .augmentation_bundle import load_augmentation_bundle


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def _load_alignment(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    rows = payload.get("alignments", []) or []
    return [item for item in rows if isinstance(item, dict)]


def _slugify(text: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return cleaned or "untitled"


def probe_augmentation_bundle(
    augmentation_bundle_dir: str | Path,
    groundrecall_query_bundle_path: str | Path,
) -> dict[str, Any]:
    bundle = load_augmentation_bundle(augmentation_bundle_dir)
    bundle_payload = _load_json(Path(groundrecall_query_bundle_path))
    concept = bundle_payload.get("concept", {}) or {}
    related = bundle_payload.get("related_concepts", []) or []

    target_titles = {str(concept.get("title", "")).strip()}
    related_titles = set()
    related_ids = set()
    for item in related:
        title = str(item.get("title", "") or item.get("label", "") or "").strip()
        if title:
            related_titles.add(title)
        concept_id = str(item.get("id", "") or "").strip()
        if concept_id:
            related_ids.add(concept_id.replace("concept::", "", 1))
    normalized_hub = {_slugify(title) for title in target_titles if title}
    normalized_related = {_slugify(title) for title in related_titles if title} | {_slugify(item) for item in related_ids if item}

    snippets_dir = Path(bundle["snippets_dir"])
    snippet_paths = sorted(
        str(path)
        for path in snippets_dir.glob("*.md")
        if path.name != "README.md"
    )
    alignments = _load_alignment(Path(bundle["concept_alignment"]))
    matched_hub = []
    matched_related = []
    unmatched = []
    for item in alignments:
        source_title = str(item.get("source_title", "")).strip()
        target_title = str(item.get("target_title", "")).strip()
        row = {"source_title": source_title, "target_title": target_title}
        normalized_target = _slugify(target_title)
        if normalized_target in normalized_hub:
            matched_hub.append(row)
        elif normalized_target in normalized_related:
            matched_related.append(row)
        else:
            unmatched.append(row)

    return {
        "bundle_title": bundle.get("title", ""),
        "bundle_dir": bundle.get("bundle_dir", ""),
        "groundrecall_query_bundle_path": str(Path(groundrecall_query_bundle_path).resolve()),
        "hub_concept_title": next(iter(target_titles), ""),
        "related_concept_titles": sorted(related_titles),
        "snippet_count": len(snippet_paths),
        "snippet_paths": snippet_paths,
        "alignment_count": len(alignments),
        "matched_hub_alignment_count": len(matched_hub),
        "matched_related_alignment_count": len(matched_related),
        "unmatched_alignment_count": len(unmatched),
        "matched_hub_alignments": matched_hub,
        "matched_related_alignments": matched_related,
        "unmatched_alignments": unmatched,
    }


def write_probe_report(
    augmentation_bundle_dir: str | Path,
    groundrecall_query_bundle_path: str | Path,
    out_path: str | Path,
) -> dict[str, Any]:
    payload = probe_augmentation_bundle(augmentation_bundle_dir, groundrecall_query_bundle_path)
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Probe an augmentation bundle against a GroundRecall hub bundle.")
    parser.add_argument("augmentation_bundle")
    parser.add_argument("groundrecall_query_bundle")
    parser.add_argument("--out")
    args = parser.parse_args()

    payload = probe_augmentation_bundle(args.augmentation_bundle, args.groundrecall_query_bundle)
    if args.out:
        Path(args.out).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
