from didactopus.pedagogy import audit_optional_ai


def test_optional_ai_audit_is_offline_and_fail_closed():
    report = audit_optional_ai(allowed_capabilities=["local-model"],
                               requested_routes=["local-model", "external-network"])
    assert report["provider_invoked"] is False
    assert report["prohibited_routes"] == ["external-network"]
    assert report["fallback"] == "deterministic-only"
