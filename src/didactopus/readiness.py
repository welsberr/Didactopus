from __future__ import annotations
from .learner_state import LearnerState

def concept_dimension_score(state: LearnerState, concept_id: str, dimension: str) -> tuple[float, float]:
    rec = state.get_record(concept_id, dimension)
    if rec is None:
        return 0.0, 0.0
    return rec.score, rec.confidence

def concept_ready(
    state: LearnerState,
    concept_id: str,
    prerequisite_ids: list[str],
    dimension: str = "mastery",
    min_score: float = 0.65,
    min_confidence: float = 0.45,
) -> bool:
    for prereq in prerequisite_ids:
        score, conf = concept_dimension_score(state, prereq, dimension)
        if score < min_score or conf < min_confidence:
            return False
    return True
