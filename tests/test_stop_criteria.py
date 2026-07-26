import pytest

from didactopus.learner_state import LearnerState, MasteryRecord
from didactopus.orchestration_models import LearnerProfile, RunState, StopCriteria
from didactopus.stop_criteria import assess_claim_readiness

def test_claim_readiness_true_when_threshold_met():
    learner = LearnerState(
        learner_id="u1",
        records=[MasteryRecord(concept_id="c1", dimension="mastery", score=0.9, evidence_coverage=0.8, evidence_count=3, last_updated="2026-03-13T12:00:00+00:00")]
    )
    run = RunState(profile=LearnerProfile(learner_id="u1"))
    crit = StopCriteria(min_mastered_concepts=1, min_average_score=0.7, min_average_evidence_coverage=0.6)
    result = assess_claim_readiness(learner, run, crit)
    assert result["ready"] is True
    assert result["average_evidence_coverage"] == 0.8
    assert result["average_confidence"] == 0.8


def test_legacy_stop_criteria_confidence_alias_warns() -> None:
    with pytest.warns(DeprecationWarning, match="min_average_evidence_coverage"):
        crit = StopCriteria(min_average_confidence=0.7)

    assert crit.min_average_evidence_coverage == 0.7
