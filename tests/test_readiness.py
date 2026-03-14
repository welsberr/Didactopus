from didactopus.learner_state import LearnerState, EvidenceEvent
from didactopus.progression_engine import apply_evidence
from didactopus.readiness import concept_ready

def test_concept_ready_true_when_prereq_met():
    state = LearnerState(learner_id="u1")
    apply_evidence(state, EvidenceEvent(
        concept_id="p1", dimension="mastery", score=0.9, confidence_hint=0.9,
        timestamp="2026-03-13T12:00:00+00:00"
    ))
    assert concept_ready(state, "c2", ["p1"], min_score=0.5, min_confidence=0.2)

def test_concept_ready_false_when_prereq_missing():
    state = LearnerState(learner_id="u1")
    assert not concept_ready(state, "c2", ["p1"], min_score=0.5, min_confidence=0.2)
