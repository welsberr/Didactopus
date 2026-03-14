from __future__ import annotations
from .learner_state import LearnerState
from .orchestration_models import StopCriteria, RunState

def assess_claim_readiness(
    learner_state: LearnerState,
    run_state: RunState,
    criteria: StopCriteria,
    dimension: str = "mastery",
) -> dict:
    relevant = [r for r in learner_state.records if r.dimension == dimension]
    mastered = [r for r in relevant if r.score >= criteria.min_average_score and r.confidence >= criteria.min_average_confidence]
    avg_score = sum(r.score for r in relevant) / len(relevant) if relevant else 0.0
    avg_conf = sum(r.confidence for r in relevant) / len(relevant) if relevant else 0.0
    capstones_ok = all(cap in run_state.completed_capstones for cap in criteria.required_capstones)

    ready = (
        len(mastered) >= criteria.min_mastered_concepts
        and avg_score >= criteria.min_average_score
        and avg_conf >= criteria.min_average_confidence
        and capstones_ok
    )
    return {
        "ready": ready,
        "mastered_concepts": len(mastered),
        "average_score": avg_score,
        "average_confidence": avg_conf,
        "capstones_ok": capstones_ok,
    }
