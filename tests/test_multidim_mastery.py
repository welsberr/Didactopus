from didactopus.adaptive_engine import LearnerProfile
from didactopus.evidence_engine import EvidenceItem, ingest_evidence_bundle


DEFAULT_WEIGHTS = {"explanation": 1.0, "problem": 1.5, "project": 2.5, "transfer": 2.0}
DEFAULT_THRESHOLDS = {
    "correctness": 0.8,
    "explanation": 0.75,
    "transfer": 0.7,
    "project_execution": 0.75,
    "critique": 0.7,
}


def test_full_multidim_mastery() -> None:
    profile = LearnerProfile(learner_id="u1")
    state = ingest_evidence_bundle(
        profile,
        [
            EvidenceItem(
                "c1",
                "project",
                0.9,
                is_recent=True,
                rubric_dimensions={
                    "correctness": 0.88,
                    "explanation": 0.82,
                    "transfer": 0.77,
                    "project_execution": 0.9,
                    "critique": 0.76,
                },
            )
        ],
        resurfacing_threshold=0.55,
        confidence_threshold=0.75,
        type_weights=DEFAULT_WEIGHTS,
        recent_multiplier=1.35,
        dimension_thresholds=DEFAULT_THRESHOLDS,
    )
    assert "c1" in profile.mastered_concepts
    assert state.summary_by_concept["c1"].mastered is True
    assert state.summary_by_concept["c1"].weak_dimensions == []


def test_partial_weakness_blocks_mastery() -> None:
    profile = LearnerProfile(learner_id="u1")
    state = ingest_evidence_bundle(
        profile,
        [
            EvidenceItem(
                "c1",
                "project",
                0.85,
                is_recent=True,
                rubric_dimensions={
                    "correctness": 0.9,
                    "explanation": 0.86,
                    "transfer": 0.52,
                    "project_execution": 0.88,
                    "critique": 0.8,
                },
            )
        ],
        resurfacing_threshold=0.55,
        confidence_threshold=0.75,
        type_weights=DEFAULT_WEIGHTS,
        recent_multiplier=1.35,
        dimension_thresholds=DEFAULT_THRESHOLDS,
    )
    assert "c1" not in profile.mastered_concepts
    assert state.summary_by_concept["c1"].mastered is False
    assert "transfer" in state.summary_by_concept["c1"].weak_dimensions


def test_resurfacing_from_multidim_weakness() -> None:
    profile = LearnerProfile(learner_id="u1", mastered_concepts={"c1"})
    state = ingest_evidence_bundle(
        profile,
        [
            EvidenceItem(
                "c1",
                "problem",
                0.45,
                is_recent=True,
                rubric_dimensions={
                    "correctness": 0.45,
                    "explanation": 0.5,
                    "transfer": 0.4,
                    "critique": 0.42,
                },
            )
        ],
        resurfacing_threshold=0.55,
        confidence_threshold=0.75,
        type_weights=DEFAULT_WEIGHTS,
        recent_multiplier=1.35,
        dimension_thresholds=DEFAULT_THRESHOLDS,
    )
    assert "c1" not in profile.mastered_concepts
    assert "c1" in state.resurfaced_concepts
