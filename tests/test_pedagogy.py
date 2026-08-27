import pytest

from didactopus.pedagogy import PedagogyContractError, render_activity, validate_learning_contract


def test_optional_contract_is_backward_compatible_and_ids_are_stable():
    old = validate_learning_contract({"title": "old", "activities": []})
    assert old["contract_version"] == "1.0"
    payload = {"promise": "Explain a claim", "outcomes": [{"title": "Explain"}],
               "activities": [{"title": "Observe", "activity_type": "guided-observation",
                               "outcome_ids": [], "reading_questions": ["What changes?"]}]}
    first = validate_learning_contract(payload)
    second = validate_learning_contract(payload)
    assert first["outcomes"][0]["id"] == second["outcomes"][0]["id"]
    assert first["activities"][0]["id"] == second["activities"][0]["id"]


def test_invalid_contract_fails_closed_and_render_is_plain_text():
    with pytest.raises(PedagogyContractError):
        validate_learning_contract({"activities": [{"title": "x", "activity_type": "guessing"}]})
    rendered = render_activity({"id": "a", "title": "Observe", "activity_type": "guided-observation",
                                "invitation": "Connect the observation to the outcome.",
                                "reading_questions": ["What do you notice?"], "evidence": ["a note"]})
    assert "Why this matters" in rendered and "What to notice" in rendered and "What to do next" in rendered
