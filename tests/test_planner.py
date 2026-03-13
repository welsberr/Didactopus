from didactopus.artifact_registry import discover_domain_packs
from didactopus.config import load_config
from didactopus.graph_builder import build_concept_graph
from didactopus.planner import PlannerWeights, rank_next_concepts


def test_rank_next_concepts() -> None:
    config = load_config("configs/config.example.yaml")
    results = discover_domain_packs(["domain-packs"])
    graph = build_concept_graph(results, config.platform.default_dimension_thresholds)

    ranked = rank_next_concepts(
        graph=graph,
        mastered=set(),
        targets=["bayes-extension::posterior"],
        weak_dimensions_by_concept={"bayes-extension::prior": ["transfer"]},
        fragile_concepts={"bayes-extension::prior"},
        project_catalog=[{"id": "p1", "prerequisites": ["bayes-extension::prior"]}],
        weights=PlannerWeights(),
    )

    assert len(ranked) >= 1
    assert ranked[0]["score"] >= ranked[-1]["score"]
