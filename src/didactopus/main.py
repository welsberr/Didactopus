import argparse
import os
from pathlib import Path

from .agentic_loop import run_agentic_learning_loop
from .artifact_registry import check_pack_dependencies, detect_dependency_cycles, discover_domain_packs
from .config import load_config
from .graph_builder import build_concept_graph
from .learning_graph import build_merged_learning_graph
from .planner import PlannerWeights


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Didactopus agentic learner loop")
    parser.add_argument("--target", default="bayes-extension::posterior")
    parser.add_argument("--steps", type=int, default=5)
    parser.add_argument("--config", default=os.environ.get("DIDACTOPUS_CONFIG", "configs/config.example.yaml"))
    return parser


def main() -> None:
    args = build_parser().parse_args()
    config = load_config(Path(args.config))
    results = discover_domain_packs(["domain-packs"])
    dep_errors = check_pack_dependencies(results)
    cycles = detect_dependency_cycles(results)

    if dep_errors:
        print("Dependency errors:")
        for err in dep_errors:
            print(f"- {err}")
    if cycles:
        print("Dependency cycles:")
        for cycle in cycles:
            print(f"- {' -> '.join(cycle)}")
        return

    merged = build_merged_learning_graph(results, config.platform.default_dimension_thresholds)
    graph = build_concept_graph(results, config.platform.default_dimension_thresholds)

    state = run_agentic_learning_loop(
        graph=graph,
        project_catalog=merged.project_catalog,
        target_concepts=[args.target],
        weights=PlannerWeights(
            readiness_bonus=config.planner.readiness_bonus,
            target_distance_weight=config.planner.target_distance_weight,
            weak_dimension_bonus=config.planner.weak_dimension_bonus,
            fragile_review_bonus=config.planner.fragile_review_bonus,
            project_unlock_bonus=config.planner.project_unlock_bonus,
            semantic_similarity_weight=config.planner.semantic_similarity_weight,
        ),
        max_steps=args.steps,
    )

    print("== Didactopus Agentic Learner Loop ==")
    print(f"Target: {args.target}")
    print(f"Steps executed: {len(state.attempt_history)}")
    print()
    print("Mastered concepts:")
    if state.mastered_concepts:
        for item in sorted(state.mastered_concepts):
            print(f"- {item}")
    else:
        print("- none")
    print()
    print("Attempt history:")
    for item in state.attempt_history:
        weak = ", ".join(item["weak_dimensions"]) if item["weak_dimensions"] else "none"
        print(f"- {item['concept']}: mastered={item['mastered']}, weak={weak}")
