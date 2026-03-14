from didactopus.learner_state import LearnerState, EvidenceEvent
from didactopus.progression_engine import apply_evidence
from didactopus.recommendations import recommend_next_concepts, recommend_reinforcement_targets

def test_recommend_next_concepts():
    concepts = [
        {"id": "a", "title": "A", "prerequisites": []},
        {"id": "b", "title": "B", "prerequisites": ["a"]},
    ]
    state = LearnerState(learner_id="u1")
    apply_evidence(state, EvidenceEvent(
        concept_id="a", dimension="mastery", score=0.9, confidence_hint=0.9,
        timestamp="2026-03-13T12:00:00+00:00"
    ))
    recs = recommend_next_concepts(state, concepts, min_score=0.5, min_confidence=0.2)
    assert any(r["concept_id"] == "b" for r in recs)

def test_recommend_reinforcement_targets():
    state = LearnerState(learner_id="u1")
    apply_evidence(state, EvidenceEvent(
        concept_id="a", dimension="mastery", score=0.3, confidence_hint=0.1,
        timestamp="2026-03-13T12:00:00+00:00"
    ))
    recs = recommend_reinforcement_targets(state, low_confidence_threshold=0.5)
    assert any(r["concept_id"] == "a" for r in recs)
