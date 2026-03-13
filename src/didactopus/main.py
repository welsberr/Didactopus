import argparse
import os
from pathlib import Path

from .artifact_registry import check_pack_dependencies, discover_domain_packs
from .config import load_config
from .curriculum import generate_initial_roadmap
from .domain_map import build_demo_domain_map
from .evaluation import generate_rubric
from .mentor import generate_socratic_prompt
from .model_provider import ModelProvider
from .practice import generate_practice_task
from .project_advisor import suggest_capstone


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Didactopus mastery scaffold")
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

    dmap = build_demo_domain_map(args.domain)
    roadmap = generate_initial_roadmap(dmap, args.goal)
    focus_concept = dmap.topological_sequence()[1]

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
    print("== Roadmap ==")
    for stage in roadmap:
        print(f"- {stage.title}: {stage.mastery_goal}")
    print()
    print(generate_socratic_prompt(provider, focus_concept))
    print(generate_practice_task(provider, focus_concept))
    print(suggest_capstone(provider, args.domain))
    print(generate_rubric(provider, focus_concept))
