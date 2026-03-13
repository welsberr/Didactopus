import argparse
import os
from pathlib import Path

from .artifact_registry import check_pack_dependencies, detect_dependency_cycles, discover_domain_packs
from .config import load_config
from .graph_builder import build_concept_graph, suggest_semantic_links


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Didactopus concept graph engine")
    parser.add_argument("--target", default="bayes-extension::posterior")
    parser.add_argument("--mastered", nargs="*", default=[])
    parser.add_argument("--export-dot", default="")
    parser.add_argument("--export-cytoscape", default="")
    parser.add_argument("--config", default=os.environ.get("DIDACTOPUS_CONFIG", "configs/config.example.yaml"))
    return parser


def main() -> None:
    args = build_parser().parse_args()
    config = load_config(Path(args.config))
    results = discover_domain_packs(config.artifacts.local_pack_dirs)
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

    print("== Didactopus Concept Graph Engine ==")
    print(f"concepts: {len(graph.graph.nodes)}")
    print(f"edges: {len(graph.graph.edges)}")
    print()
    print(f"Target concept: {args.target}")
    print("Prerequisite chain:")
    for item in sorted(graph.prerequisite_chain(args.target)):
        print(f"- {item}")
    print()
    print("Curriculum path from current mastery:")
    for item in graph.curriculum_path_to_target(mastered, args.target):
        print(f"- {item}")
    print()
    print("Ready concepts:")
    for item in graph.ready_concepts(mastered):
        print(f"- {item}")
    print()
    print("Declared related concepts for target:")
    for item in graph.related_concepts(args.target):
        print(f"- {item}")
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
