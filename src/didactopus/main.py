import argparse
import os
from pathlib import Path

from .artifact_registry import (
    check_pack_dependencies,
    detect_dependency_cycles,
    discover_domain_packs,
    topological_pack_order,
)
from .config import load_config
from .curriculum import generate_stages_from_learning_graph
from .evaluation import generate_rubric
from .learning_graph import build_merged_learning_graph, generate_learner_roadmap
from .mentor import generate_socratic_prompt
from .model_provider import ModelProvider
from .practice import generate_practice_task
from .project_advisor import suggest_capstone


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Didactopus merged learning graph scaffold")
    parser.add_argument("--domain", required=True)
    parser.add_argument("--goal", required=True)
    parser.add_argument(
        "--config",
        default=os.environ.get("DIDACTOPUS_CONFIG", "configs/config.example.yaml"),
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    config = load_config(Path(args.config))
    provider = ModelProvider(config.model_provider)
    packs = discover_domain_packs(config.artifacts.local_pack_dirs)
    dependency_errors = check_pack_dependencies(packs)
    cycles = detect_dependency_cycles(packs)

    print("== Didactopus ==")
    print("Many arms, one goal — mastery.")
    print()
    print("== Domain Pack Validation ==")
    for pack in packs:
        pack_name = pack.manifest.display_name if pack.manifest else pack.pack_dir.name
        print(f"- {pack_name}: {'valid' if pack.is_valid else 'INVALID'}")
        for err in pack.errors:
            print(f"  * {err}")
    print()
    print("== Dependency Resolution ==")
    if dependency_errors:
        for err in dependency_errors:
            print(f"- {err}")
    else:
        print("- all resolved")
    print()
    print("== Dependency Cycles ==")
    if cycles:
        for cycle in cycles:
            print(f"- cycle: {' -> '.join(cycle)}")
        print("- merged learning graph unavailable while cycles exist")
        return
    print("- none")
    print()
    print("== Pack Load Order ==")
    for name in topological_pack_order(packs):
        print(f"- {name}")
    print()
    merged = build_merged_learning_graph(packs)
    learner_roadmap = generate_learner_roadmap(merged)
    print("== Merged Learning Graph ==")
    print(f"- concepts: {len(merged.concept_data)}")
    print(f"- prerequisite edges: {merged.graph.number_of_edges()}")
    print(f"- roadmap stages: {len(merged.stage_catalog)}")
    print(f"- projects: {len(merged.project_catalog)}")
    if merged.conflicts:
        for conflict in merged.conflicts:
            print(f"  * conflict: {conflict}")
    else:
        print("- no merge conflicts")
    print()
    print("== Learner Roadmap ==")
    for item in learner_roadmap[:8]:
        print(f"- Stage {item['stage_number']}: {item['concept_key']} ({item['title']})")
    print()
    if learner_roadmap:
        focus_concept = learner_roadmap[0]["concept_key"]
    else:
        focus_concept = args.domain
    print(generate_socratic_prompt(provider, focus_concept))
    print(generate_practice_task(provider, focus_concept))
    print(suggest_capstone(provider, args.domain))
    print(generate_rubric(provider, focus_concept))
