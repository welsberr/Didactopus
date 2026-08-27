from didactopus.pedagogy import export_diagnostics, record_diagnostic


def test_diagnostics_are_private_ungraded_and_redacted_by_default():
    record = record_diagnostic("path", "entry", "I am unsure", activity_id="start")
    assert record["private"] and not record["graded"] and record["status"] == "draft"
    exported = export_diagnostics([record])
    assert "response" not in exported["records"][0]
    assert exported["redacted_fields"]
    assert export_diagnostics([record], include_private=True)["records"][0]["response"] == "I am unsure"
