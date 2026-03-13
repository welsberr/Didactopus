from __future__ import annotations

from pathlib import Path
import json
import yaml

from .review_schema import DraftPackData, ConceptReviewEntry


def load_draft_pack(pack_dir: str | Path) -> DraftPackData:
    pack_dir = Path(pack_dir)
    concepts_yaml = yaml.safe_load((pack_dir / "concepts.yaml").read_text(encoding="utf-8")) or {}
    concepts = []
    for item in concepts_yaml.get("concepts", []):
        concepts.append(
            ConceptReviewEntry(
                concept_id=item.get("id", ""),
                title=item.get("title", ""),
                description=item.get("description", ""),
                prerequisites=list(item.get("prerequisites", [])),
                mastery_signals=list(item.get("mastery_signals", [])),
            )
        )

    conflicts_path = pack_dir / "conflict_report.md"
    review_path = pack_dir / "review_report.md"
    attribution_path = pack_dir / "license_attribution.json"
    pack_path = pack_dir / "pack.yaml"

    conflicts = []
    if conflicts_path.exists():
        conflicts = [
            line[2:] for line in conflicts_path.read_text(encoding="utf-8").splitlines()
            if line.startswith("- ")
        ]

    review_flags = []
    if review_path.exists():
        review_flags = [
            line[2:] for line in review_path.read_text(encoding="utf-8").splitlines()
            if line.startswith("- ")
        ]

    attribution = {}
    if attribution_path.exists():
        attribution = json.loads(attribution_path.read_text(encoding="utf-8"))

    pack = {}
    if pack_path.exists():
        pack = yaml.safe_load(pack_path.read_text(encoding="utf-8")) or {}

    return DraftPackData(
        pack=pack,
        concepts=concepts,
        conflicts=conflicts,
        review_flags=review_flags,
        attribution=attribution,
    )
