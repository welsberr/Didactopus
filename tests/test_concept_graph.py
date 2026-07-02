from didactopus.artifact_registry import discover_domain_packs
from didactopus.config import load_config
from didactopus.graph_builder import build_concept_graph


def test_curriculum_path_to_target() -> None:
    config = load_config("configs/config.example.yaml")
    results = discover_domain_packs(["domain-packs"])
    graph = build_concept_graph(results, config.platform.default_dimension_thresholds)
    path = graph.curriculum_path_to_target(set(), "bayes-extension::posterior")
    assert "bayes-extension::prior" in path
    assert "bayes-extension::posterior" in path
    assert graph.prerequisite_shortest_path("bayes-extension::prior", "bayes-extension::posterior")
