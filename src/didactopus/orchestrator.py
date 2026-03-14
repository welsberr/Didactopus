from __future__ import annotations
from .learner_state import LearnerState, EvidenceEvent
from .orchestration_models import RunState, SessionPlan, StopCriteria
from .recommendations import recommend_next_concepts, recommend_reinforcement_targets
from .progression_engine import apply_evidence
from .stop_criteria import assess_claim_readiness
from .ux_feedback import format_recommendation_card, format_reward_message

def run_learning_cycle(
    learner_state: LearnerState,
    run_state: RunState,
    concepts: list[dict],
    stop_criteria: StopCriteria,
) -> dict:
    next_concepts = recommend_next_concepts(learner_state, concepts)
    reinforcement = recommend_reinforcement_targets(learner_state)
    cards = [format_recommendation_card(item) for item in next_concepts[:3]]

    readiness = assess_claim_readiness(learner_state, run_state, stop_criteria)
    if readiness["ready"]:
        run_state.status = "claimed_expertise"
        run_state.milestone_log.append(format_reward_message("milestone", "usable expertise threshold met"))
    elif next_concepts:
        run_state.status = "active"
    elif reinforcement:
        run_state.status = "active"
    else:
        run_state.status = "blocked"

    return {
        "run_status": run_state.status,
        "recommendation_cards": cards,
        "reinforcement_targets": reinforcement[:5],
        "claim_readiness": readiness,
    }

def apply_demo_evidence(learner_state: LearnerState, concept_id: str, timestamp: str) -> LearnerState:
    event = EvidenceEvent(
        concept_id=concept_id,
        dimension="mastery",
        score=0.82,
        confidence_hint=0.75,
        timestamp=timestamp,
        kind="checkpoint",
        source_id=f"demo-{concept_id}",
    )
    return apply_evidence(learner_state, event)
