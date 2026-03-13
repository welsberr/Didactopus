from didactopus.adaptive_engine import LearnerProfile
from didactopus.evidence_engine import EvidenceItem, add_evidence_item, ingest_evidence_bundle, EvidenceState


def test_add_evidence_item_updates_mean() -> None:
    state = EvidenceState()
    add_evidence_item(state, EvidenceItem("c1", "problem", 0.8))
    add_evidence_item(state, EvidenceItem("c1", "problem", 0.6))
    assert state.summary_by_concept["c1"].count == 2
    assert abs(state.summary_by_concept["c1"].mean_score - 0.7) < 1e-9


def test_mastery_promotion() -> None:
    profile = LearnerProfile(learner_id="u1")
    state = ingest_evidence_bundle(
        profile,
        [
            EvidenceItem("c1", "explanation", 0.85),
            EvidenceItem("c1", "problem", 0.9),
        ],
        mastery_threshold=0.8,
        resurfacing_threshold=0.55,
    )
    assert "c1" in profile.mastered_concepts
    assert state.resurfaced_concepts == set()


def test_resurfacing() -> None:
    profile = LearnerProfile(learner_id="u1", mastered_concepts={"c1"})
    state = ingest_evidence_bundle(
        profile,
        [
            EvidenceItem("c1", "problem", 0.4),
            EvidenceItem("c1", "transfer", 0.5),
        ],
        mastery_threshold=0.8,
        resurfacing_threshold=0.55,
    )
    assert "c1" not in profile.mastered_concepts
    assert "c1" in state.resurfaced_concepts
