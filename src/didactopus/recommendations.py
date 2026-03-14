from __future__ import annotations
from .learner_state import LearnerState
from .readiness import concept_ready

def recommend_next_concepts(
    state: LearnerState,
    concepts: list[dict],
    dimension: str = "mastery",
    min_score: float = 0.65,
    min_confidence: float = 0.45,
) -> list[dict]:
    recs = []
    for concept in concepts:
        cid = concept.get("id")
        prereqs = list(concept.get("prerequisites", []) or [])
        ready = concept_ready(
            state,
            cid,
            prereqs,
            dimension=dimension,
            min_score=min_score,
            min_confidence=min_confidence,
        )
        if ready:
            existing = state.get_record(cid, dimension)
            if existing is None or existing.score < min_score or existing.confidence < min_confidence:
                recs.append({
                    "concept_id": cid,
                    "title": concept.get("title", cid),
                    "reason": "prerequisites satisfied but mastery not yet secure",
                })
    return recs

def recommend_reinforcement_targets(
    state: LearnerState,
    dimension: str = "mastery",
    low_confidence_threshold: float = 0.35,
) -> list[dict]:
    out = []
    for rec in state.records:
        if rec.dimension == dimension and rec.confidence < low_confidence_threshold:
            out.append({
                "concept_id": rec.concept_id,
                "dimension": rec.dimension,
                "reason": "confidence low; reinforce with fresh evidence",
            })
    return out
