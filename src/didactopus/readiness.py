from __future__ import annotations
import warnings

from .learner_state import LearnerState

def concept_dimension_score(state: LearnerState, concept_id: str, dimension: str) -> tuple[float, float]:
    rec = state.get_record(concept_id, dimension)
    if rec is None:
        return 0.0, 0.0
    return rec.score, rec.evidence_coverage

def concept_ready(
    state: LearnerState,
    concept_id: str,
    prerequisite_ids: list[str],
    dimension: str = "mastery",
    min_score: float = 0.65,
    min_evidence_coverage: float = 0.45,
    min_confidence: float | None = None,
) -> bool:
    if min_confidence is not None:
        warnings.warn(
            "concept_ready(min_confidence=...) is deprecated; use min_evidence_coverage.",
            DeprecationWarning,
            stacklevel=2,
        )
        min_evidence_coverage = min_confidence
    for prereq in prerequisite_ids:
        score, coverage = concept_dimension_score(state, prereq, dimension)
        if score < min_score or coverage < min_evidence_coverage:
            return False
    return True
