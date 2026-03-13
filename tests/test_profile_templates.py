from didactopus.profile_templates import resolve_mastery_profile


def test_template_resolution() -> None:
    templates = {
        "foundation": {
            "required_dimensions": ["correctness", "explanation"],
            "dimension_threshold_overrides": {"explanation": 0.8},
        }
    }
    resolved = resolve_mastery_profile(
        {"template": "foundation"},
        templates,
        {"correctness": 0.8, "explanation": 0.75, "transfer": 0.7},
    )
    assert resolved["required_dimensions"] == ["correctness", "explanation"]
    assert resolved["effective_thresholds"]["correctness"] == 0.8
    assert resolved["effective_thresholds"]["explanation"] == 0.8
