import pytest

from didactopus.pedagogy import PedagogyContractError, activity_template


def test_templates_are_deterministic_and_declare_boundaries():
    item = activity_template("interview", title="Ask", consent_required=True, public_release=False)
    assert item["consent_required"] and item["privacy"] == "local-only"
    assert item["accessibility_options"] == ["text-only"]


def test_simulation_requires_debrief():
    with pytest.raises(PedagogyContractError, match="debrief"):
        activity_template("role-play", title="Simulate")
