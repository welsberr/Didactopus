from didactopus.artifact_registry import discover_domain_packs


def test_discover_example_pack() -> None:
    packs = discover_domain_packs(["domain-packs"])
    assert len(packs) >= 1
    _, manifest = packs[0]
    assert manifest.name == "example-statistics"
    assert manifest.display_name == "Example Statistics Pack"
