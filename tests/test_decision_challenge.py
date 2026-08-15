from didactopus.decision_challenge import classify_decision_challenge


def test_routine_learner_turn_is_not_challenged() -> None:
    result = classify_decision_challenge("mentor_turn")

    assert result["review_level"] == "none"
    assert result["challenge_required"] is False


def test_mastery_promotion_gets_bounded_standard_review() -> None:
    result = classify_decision_challenge("promote_mastery", durable_memory_change=True)

    assert result["review_level"] == "standard"
    assert "durable_memory_change" in result["trigger_codes"]
    assert "classification only" in result["authority"]
    assert "separate" in result["authority"]


def test_private_learner_record_deletion_is_escalated() -> None:
    result = classify_decision_challenge("delete_learner_record", destructive=True)

    assert result["review_level"] == "escalated"
    assert result["trigger_codes"] == ["destructive_action"]
