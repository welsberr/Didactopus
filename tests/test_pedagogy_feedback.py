from didactopus.pedagogy import formative_feedback


def test_feedback_is_bounded_attributable_and_does_not_rewrite():
    result = formative_feedback(strengths=["clear claim"], problems=[
        {"problem": "missing source", "why": "readers cannot check the claim"},
        {"problem": "weak link", "why": "the evidence does not yet connect"},
        {"problem": "ignored", "why": "not selected"}], next_step="Add one source anchor.")
    assert len(result["problems"]) == 2
    assert result["rewrote_artifact"] is False
