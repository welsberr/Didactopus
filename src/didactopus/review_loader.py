from __future__ import annotations
from pathlib import Path
import json, yaml
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
                source_role=item.get("source_role", ""),
                distinctions=list(item.get("distinctions", [])),
                definition_candidates=list(item.get("definition_candidates", [])),
                qualification_candidates=list(item.get("qualification_candidates", [])),
                constraint_candidates=list(item.get("constraint_candidates", [])),
                status=item.get("status", "needs_review"),
                notes=list(item.get("notes", [])),
            )
        )

    def bullets(path: Path) -> list[str]:
        if not path.exists():
            return []
        return [line[2:] for line in path.read_text(encoding="utf-8").splitlines() if line.startswith("- ")]

    pack = {}
    if (pack_dir / "pack.yaml").exists():
        pack = yaml.safe_load((pack_dir / "pack.yaml").read_text(encoding="utf-8")) or {}

    attribution = {}
    if (pack_dir / "license_attribution.json").exists():
        attribution = json.loads((pack_dir / "license_attribution.json").read_text(encoding="utf-8"))

    return DraftPackData(
        pack=pack,
        concepts=concepts,
        conflicts=bullets(pack_dir / "conflict_report.md"),
        review_flags=bullets(pack_dir / "review_report.md"),
        attribution=attribution,
    )
