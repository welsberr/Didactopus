from didactopus.artifact_registry import discover_domain_packs
from didactopus.config import load_config
from didactopus.graph_builder import build_concept_graph, suggest_semantic_links


def test_concept_graph_builds() -> None:
    config = load_config("configs/config.example.yaml")
    results = discover_domain_packs(["domain-packs"])
    graph = build_concept_graph(results, config.platform.default_dimension_thresholds)
    assert "foundations-statistics::probability-basics" in graph.graph.nodes
    assert "bayes-extension::posterior" in graph.graph.nodes


def test_prerequisite_path() -> None:
    config = load_config("configs/config.example.yaml")
    results = discover_domain_packs(["domain-packs"])
    graph = build_concept_graph(results, config.platform.default_dimension_thresholds)
    path = graph.learning_path("bayes-extension::prior", "bayes-extension::posterior")
    assert path == ["bayes-extension::prior", "bayes-extension::posterior"]


def test_curriculum_path_to_target() -> None:
    config = load_config("configs/config.example.yaml")
    results = discover_domain_packs(["domain-packs"])
    graph = build_concept_graph(results, config.platform.default_dimension_thresholds)
    path = graph.curriculum_path_to_target(set(), "bayes-extension::posterior")
    assert "bayes-extension::prior" in path
    assert "bayes-extension::posterior" in path


def test_declared_cross_pack_links_exist() -> None:
    config = load_config("configs/config.example.yaml")
    results = discover_domain_packs(["domain-packs"])
    graph = build_concept_graph(results, config.platform.default_dimension_thresholds)
    related = graph.related_concepts("bayes-extension::posterior")
    assert "applied-inference::model-checking" in related


def test_semantic_link_suggestions() -> None:
    config = load_config("configs/config.example.yaml")
    results = discover_domain_packs(["domain-packs"])
    graph = build_concept_graph(results, config.platform.default_dimension_thresholds)
    suggestions = suggest_semantic_links(graph, minimum_similarity=0.10)
    assert len(suggestions) >= 1
