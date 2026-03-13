import argparse
import os
from pathlib import Path

from .artifact_registry import check_pack_dependencies, detect_dependency_cycles, discover_domain_packs
from .config import load_config
from .graph_builder import build_concept_graph, suggest_semantic_links
from .planner import PlannerWeights, rank_next_concepts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Didactopus graph-aware planner")
    parser.add_argument("--target", default="bayes-extension::posterior")
    parser.add_argument("--mastered", nargs="*", default=[])
    parser.add_argument("--export-dot", default="")
    parser.add_argument("--export-cytoscape", default="")
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

    graph = build_concept_graph(results, config.platform.default_dimension_thresholds)
    mastered = set(args.mastered)

    weak_dimensions_by_concept = {
        "bayes-extension::prior": ["explanation", "transfer"],
    }
    fragile_concepts = {"bayes-extension::prior"}

    ranked = rank_next_concepts(
        graph=graph,
        mastered=mastered,
        targets=[args.target],
        weak_dimensions_by_concept=weak_dimensions_by_concept,
        fragile_concepts=fragile_concepts,
        project_catalog=[
            {
                "id": "bayes-extension::bayes-mini-project",
                "prerequisites": ["bayes-extension::prior"],
            },
            {
                "id": "applied-inference::inference-project",
                "prerequisites": ["applied-inference::model-checking"],
            },
        ],
        weights=PlannerWeights(
            readiness_bonus=config.planner.readiness_bonus,
            target_distance_weight=config.planner.target_distance_weight,
            weak_dimension_bonus=config.planner.weak_dimension_bonus,
            fragile_review_bonus=config.planner.fragile_review_bonus,
            project_unlock_bonus=config.planner.project_unlock_bonus,
            semantic_similarity_weight=config.planner.semantic_similarity_weight,
        ),
    )

    print("== Didactopus Graph-Aware Planner ==")
    print(f"Target concept: {args.target}")
    print()
    print("Curriculum path from current mastery:")
    for item in graph.curriculum_path_to_target(mastered, args.target):
        print(f"- {item}")
    print()
    print("Ready concepts:")
    for item in graph.ready_concepts(mastered):
        print(f"- {item}")
    print()
    print("Ranked next concepts:")
    for item in ranked:
        print(f"- {item['concept']}: {item['score']:.2f}")
        for name, value in item["components"].items():
            print(f"  * {name}: {value:.2f}")
    print()
    print("Suggested semantic links:")
    for a, b, score in suggest_semantic_links(graph, minimum_similarity=0.10)[:8]:
        print(f"- {a} <-> {b} : {score:.2f}")

    if args.export_dot:
        graph.export_graphviz(args.export_dot)
        print(f"Exported Graphviz DOT to {args.export_dot}")
    if args.export_cytoscape:
        graph.export_cytoscape_json(args.export_cytoscape)
        print(f"Exported Cytoscape JSON to {args.export_cytoscape}")


if __name__ == "__main__":
    main()
