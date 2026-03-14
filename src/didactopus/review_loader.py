from __future__ import annotations
from pathlib import Path
import json, yaml
from .review_schema import DraftPackData, ConceptReviewEntry

def load_draft_pack(pack_dir: str | Path) -> DraftPackData:
    pack_dir = Path(pack_dir)
    data = yaml.safe_load((pack_dir / "concepts.yaml").read_text(encoding="utf-8")) or {}
    concepts = []
    for item in data.get("concepts", []):
        concepts.append(ConceptReviewEntry(
            concept_id=item.get("id",""),
            title=item.get("title",""),
            description=item.get("description",""),
            prerequisites=list(item.get("prerequisites", [])),
            mastery_signals=list(item.get("mastery_signals", [])),
            status=item.get("status","needs_review"),
            notes=list(item.get("notes", [])),
        ))
    pack = yaml.safe_load((pack_dir / "pack.yaml").read_text(encoding="utf-8")) if (pack_dir/"pack.yaml").exists() else {}
    attribution = json.loads((pack_dir / "license_attribution.json").read_text(encoding="utf-8")) if (pack_dir/"license_attribution.json").exists() else {}
    def bullets(path):
        return [line[2:] for line in path.read_text(encoding="utf-8").splitlines() if line.startswith("- ")] if path.exists() else []
    return DraftPackData(pack=pack or {}, concepts=concepts, conflicts=bullets(pack_dir/"conflict_report.md"), review_flags=bullets(pack_dir/"review_report.md"), attribution=attribution)
