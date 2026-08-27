from didactopus.pedagogy import map_learning_path


def test_mapping_is_deterministic_and_surfaces_missing_prerequisites():
    package = {"producer": "fixture", "activities": [
        {"id": "apply", "title": "Apply", "prerequisites": ["missing"], "time_minutes": 700},
    ]}
    result = map_learning_path(package)
    assert result["steps"][0]["provenance"]["activity_id"] == "apply"
    assert {item["kind"] for item in result["review_prompts"]} == {"missing-prerequisite", "workload"}
