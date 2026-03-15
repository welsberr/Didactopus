from didactopus.artifact_registry import (
    _version_in_range,
    check_pack_dependencies,
    discover_domain_packs,
    validate_pack,
)


def test_version_range() -> None:
    assert _version_in_range("1.2.0", "1.0.0", "1.9.9") is True
    assert _version_in_range("2.0.0", "1.0.0", "1.9.9") is False


def test_foundations_pack_is_valid() -> None:
    result = validate_pack("domain-packs/foundations-statistics")
    assert result.is_valid is True
    assert result.manifest is not None
    assert result.manifest.name == "foundations-statistics"


def test_incompatible_core_pack_is_invalid() -> None:
    result = validate_pack("domain-packs/incompatible-core")
    assert result.is_valid is False
    assert any("incompatible with Didactopus core version" in err for err in result.errors)


def test_dependency_resolution() -> None:
    results = discover_domain_packs(["domain-packs"])
    errors = check_pack_dependencies(results)
    assert any("depends on missing pack 'nonexistent-pack'" in err for err in errors)
    assert not any("bayes-extension" in err and "foundations-statistics" in err for err in errors)
