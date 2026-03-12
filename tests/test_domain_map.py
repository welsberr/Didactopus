from didactopus.domain_map import build_demo_domain_map


def test_demo_domain_map_order() -> None:
    dmap = build_demo_domain_map("statistics")
    sequence = dmap.topological_sequence()
    assert sequence == ["foundations", "methods", "analysis", "projects"]


def test_prerequisites() -> None:
    dmap = build_demo_domain_map("statistics")
    prereqs = set(dmap.prerequisites_for("projects"))
    assert prereqs == {"foundations", "methods", "analysis"}
