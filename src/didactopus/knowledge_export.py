from __future__ import annotations
import json
from pathlib import Path
from .repository import get_pack, load_learner_state

def build_knowledge_snapshot(learner_id: str, pack_id: str) -> dict:
    pack = get_pack(pack_id)
    state = load_learner_state(learner_id)
    concept_map = {c.id: c for c in (pack.concepts if pack else [])}
    observations = []
    for rec in state.records:
        concept = concept_map.get(rec.concept_id)
        observations.append({
            "concept_id": rec.concept_id,
            "title": concept.title if concept else rec.concept_id,
            "score": rec.score,
            "confidence": rec.confidence,
            "evidence_count": rec.evidence_count,
            "interpretation": (
                "candidate mastery"
                if rec.score >= 0.65 and rec.confidence >= 0.5
                else "still developing"
            ),
        })
    return {
        "learner_id": learner_id,
        "pack_id": pack_id,
        "export_kind": "knowledge_snapshot",
        "pack_title": pack.title if pack else "",
        "observations": observations,
        "pack_improvement_candidates": [
            "Look for concepts with repeated low-confidence evidence.",
            "Check whether hidden prerequisites are missing.",
            "Inspect surprising learner success for better examples or shortcuts."
        ],
        "curriculum_product_candidates": [
            "study_guide",
            "lesson_outline",
            "exercise_set",
            "mentor_notes"
        ],
        "skill_export_candidates": [
            "agent skill manifest",
            "evaluation checklist",
            "failure-mode notes",
            "canonical examples"
        ],
    }

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("learner_id")
    parser.add_argument("pack_id")
    parser.add_argument("out_json")
    args = parser.parse_args()
    payload = build_knowledge_snapshot(args.learner_id, args.pack_id)
    Path(args.out_json).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {args.out_json}")
