from didactopus.learner_state import LearnerState, EvidenceEvent
from didactopus.progression_engine import apply_evidence
from didactopus.orchestration_models import LearnerProfile, RunState, StopCriteria
from didactopus.orchestrator import run_learning_cycle

def test_learning_cycle_returns_recommendations():
    concepts = [
        {"id": "a", "title": "A", "prerequisites": []},
        {"id": "b", "title": "B", "prerequisites": ["a"]},
    ]
    learner = LearnerState(learner_id="u1")
    apply_evidence(learner, EvidenceEvent(concept_id="a", dimension="mastery", score=0.9, confidence_hint=0.9, timestamp="2026-03-13T12:00:00+00:00"))
    run = RunState(profile=LearnerProfile(learner_id="u1"))
    crit = StopCriteria(min_mastered_concepts=10, min_average_score=0.8, min_average_confidence=0.7)
    result = run_learning_cycle(learner, run, concepts, crit)
    assert "recommendation_cards" in result
