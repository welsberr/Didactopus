from __future__ import annotations
from pathlib import Path
import json, yaml
from .review_schema import ReviewSession

def export_review_state_json(session: ReviewSession, path: str | Path) -> None:
    Path(path).write_text(session.model_dump_json(indent=2), encoding="utf-8")

def export_promoted_pack(session: ReviewSession, outdir: str | Path) -> None:
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    promoted_pack = dict(session.draft_pack.pack)
    promoted_pack["version"] = str(promoted_pack.get("version", "0.1.0-draft")).replace("-draft", "-reviewed")
    promoted_pack["curation"] = {"reviewer": session.reviewer, "ledger_entries": len(session.ledger)}

    concepts = []
    for concept in session.draft_pack.concepts:
        if concept.status == "rejected":
            continue
        concepts.append({
            "id": concept.concept_id,
            "title": concept.title,
            "description": concept.description,
            "prerequisites": concept.prerequisites,
            "mastery_signals": concept.mastery_signals,
            "status": concept.status,
            "notes": concept.notes,
            "mastery_profile": {},
        })

    (outdir / "pack.yaml").write_text(yaml.safe_dump(promoted_pack, sort_keys=False), encoding="utf-8")
    (outdir / "concepts.yaml").write_text(yaml.safe_dump({"concepts": concepts}, sort_keys=False), encoding="utf-8")
    (outdir / "review_ledger.json").write_text(json.dumps(session.model_dump(), indent=2), encoding="utf-8")
    (outdir / "license_attribution.json").write_text(json.dumps(session.draft_pack.attribution, indent=2), encoding="utf-8")
