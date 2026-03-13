from didactopus.agentic_loop import run_agentic_learning_loop
from didactopus.artifact_registry import discover_domain_packs
from didactopus.config import load_config
from didactopus.graph_builder import build_concept_graph
from didactopus.learning_graph import build_merged_learning_graph
from didactopus.planner import PlannerWeights


def test_agentic_loop_runs() -> None:
    config = load_config("configs/config.example.yaml")
    results = discover_domain_packs(["domain-packs"])
    merged = build_merged_learning_graph(results, config.platform.default_dimension_thresholds)
    graph = build_concept_graph(results, config.platform.default_dimension_thresholds)

    state = run_agentic_learning_loop(
        graph=graph,
        project_catalog=merged.project_catalog,
        target_concepts=["bayes-extension::posterior"],
        weights=PlannerWeights(),
        max_steps=4,
    )

    assert len(state.attempt_history) >= 1
