from didactopus.adaptive_engine import LearnerProfile
from didactopus.evidence_engine import (
    EvidenceItem,
    EvidenceState,
    add_evidence_item,
    confidence_from_weight,
    evidence_weight,
    ingest_evidence_bundle,
)


def test_evidence_weighting_by_type_and_recency() -> None:
    item = EvidenceItem("c1", "project", 0.9, is_recent=True)
    w = evidence_weight(
        item,
        {"explanation": 1.0, "problem": 1.5, "project": 2.5, "transfer": 2.0},
        1.35,
    )
    assert abs(w - 3.375) < 1e-9


def test_confidence_increases_with_weight() -> None:
    assert confidence_from_weight(0.0) == 0.0
    assert confidence_from_weight(1.0) < confidence_from_weight(3.0)


def test_weighted_summary_promotes_mastery() -> None:
    profile = LearnerProfile(learner_id="u1")
    state = ingest_evidence_bundle(
        profile,
        [
            EvidenceItem("c1", "project", 0.9, is_recent=True),
            EvidenceItem("c1", "problem", 0.85, is_recent=False),
        ],
        mastery_threshold=0.8,
        resurfacing_threshold=0.55,
        confidence_threshold=0.75,
        type_weights={"explanation": 1.0, "problem": 1.5, "project": 2.5, "transfer": 2.0},
        recent_multiplier=1.35,
    )
    assert "c1" in profile.mastered_concepts
    assert state.summary_by_concept["c1"].weighted_mean_score >= 0.8
    assert state.summary_by_concept["c1"].confidence >= 0.75


def test_recent_weak_evidence_can_resurface() -> None:
    profile = LearnerProfile(learner_id="u1", mastered_concepts={"c1"})
    state = ingest_evidence_bundle(
        profile,
        [
            EvidenceItem("c1", "project", 0.3, is_recent=True),
            EvidenceItem("c1", "explanation", 0.5, is_recent=True),
        ],
        mastery_threshold=0.8,
        resurfacing_threshold=0.55,
        confidence_threshold=0.75,
        type_weights={"explanation": 1.0, "problem": 1.5, "project": 2.5, "transfer": 2.0},
        recent_multiplier=1.35,
    )
    assert "c1" not in profile.mastered_concepts
    assert "c1" in state.resurfaced_concepts


def test_dimension_means_present() -> None:
    profile = LearnerProfile(learner_id="u1")
    state = ingest_evidence_bundle(
        profile,
        [
            EvidenceItem(
                "c1",
                "problem",
                0.8,
                rubric_dimensions={"correctness": 0.9, "clarity": 0.7},
            )
        ],
        mastery_threshold=0.8,
        resurfacing_threshold=0.55,
        confidence_threshold=0.1,
        type_weights={"explanation": 1.0, "problem": 1.5, "project": 2.5, "transfer": 2.0},
        recent_multiplier=1.35,
    )
    summary = state.summary_by_concept["c1"]
    assert abs(summary.dimension_means["correctness"] - 0.9) < 1e-9
    assert abs(summary.dimension_means["clarity"] - 0.7) < 1e-9
