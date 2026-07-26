from __future__ import annotations
import warnings

from .learner_state import LearnerState
from .readiness import concept_ready

def recommend_next_concepts(
    state: LearnerState,
    concepts: list[dict],
    dimension: str = "mastery",
    min_score: float = 0.65,
    min_evidence_coverage: float = 0.45,
    min_confidence: float | None = None,
) -> list[dict]:
    if min_confidence is not None:
        warnings.warn(
            "recommend_next_concepts(min_confidence=...) is deprecated; use min_evidence_coverage.",
            DeprecationWarning,
            stacklevel=2,
        )
        min_evidence_coverage = min_confidence
    recs = []
    for concept in concepts:
        cid = concept.get("id")
        prereqs = list(concept.get("prerequisites", []) or [])
        ready = concept_ready(state, cid, prereqs, dimension=dimension, min_score=min_score, min_evidence_coverage=min_evidence_coverage)
        if ready:
            existing = state.get_record(cid, dimension)
            if existing is None or existing.score < min_score or existing.evidence_coverage < min_evidence_coverage:
                recs.append({
                    "concept_id": cid,
                    "title": concept.get("title", cid),
                    "reason": "prerequisites satisfied but mastery not yet secure",
                })
    return recs

def recommend_reinforcement_targets(
    state: LearnerState,
    dimension: str = "mastery",
    low_evidence_coverage_threshold: float = 0.35,
    low_confidence_threshold: float | None = None,
) -> list[dict]:
    if low_confidence_threshold is not None:
        warnings.warn(
            "recommend_reinforcement_targets(low_confidence_threshold=...) is deprecated; use low_evidence_coverage_threshold.",
            DeprecationWarning,
            stacklevel=2,
        )
        low_evidence_coverage_threshold = low_confidence_threshold
    out = []
    for rec in state.records:
        if rec.dimension == dimension and rec.evidence_coverage < low_evidence_coverage_threshold:
            out.append({
                "concept_id": rec.concept_id,
                "dimension": rec.dimension,
                "reason": "evidence coverage low; reinforce with fresh evidence",
            })
    return out
