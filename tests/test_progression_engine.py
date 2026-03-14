from didactopus.learner_state import LearnerState, EvidenceEvent
from didactopus.progression_engine import apply_evidence, decay_confidence

def test_apply_evidence_creates_record():
    state = LearnerState(learner_id="u1")
    event = EvidenceEvent(
        concept_id="c1",
        dimension="mastery",
        score=0.8,
        confidence_hint=0.7,
        timestamp="2026-03-13T12:00:00+00:00",
    )
    apply_evidence(state, event)
    rec = state.get_record("c1", "mastery")
    assert rec is not None
    assert rec.evidence_count == 1
    assert rec.score > 0

def test_decay_confidence_reduces_confidence():
    state = LearnerState(learner_id="u1")
    event = EvidenceEvent(
        concept_id="c1",
        dimension="mastery",
        score=0.9,
        confidence_hint=0.9,
        timestamp="2026-01-01T12:00:00+00:00",
    )
    apply_evidence(state, event)
    before = state.get_record("c1", "mastery").confidence
    decay_confidence(state, "2026-03-13T12:00:00+00:00")
    after = state.get_record("c1", "mastery").confidence
    assert after < before
