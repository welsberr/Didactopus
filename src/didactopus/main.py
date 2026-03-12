import argparse
import os
from pathlib import Path

from .config import load_config
from .model_provider import ModelProvider
from .artifact_registry import discover_domain_packs
from .domain_map import build_demo_domain_map
from .curriculum import generate_initial_roadmap
from .mentor import generate_socratic_prompt
from .practice import generate_practice_task
from .project_advisor import suggest_capstone
from .evaluation import generate_rubric


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Didactopus mastery scaffold")
    parser.add_argument("--domain", required=True, help="Target domain of study")
    parser.add_argument("--goal", required=True, help="Learning goal")
    parser.add_argument(
        "--config",
        default=os.environ.get("DIDACTOPUS_CONFIG", "configs/config.example.yaml"),
        help="Path to configuration YAML",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    config = load_config(Path(args.config))
    provider = ModelProvider(config.model_provider)
    packs = discover_domain_packs(config.artifacts.local_pack_dirs)

    dmap = build_demo_domain_map(args.domain)
    roadmap = generate_initial_roadmap(dmap, args.goal)

    print("== Didactopus ==")
    print("Many arms, one goal — mastery.")
    print()
    print("== Provider ==")
    print(provider.describe())
    print()
    print("== Installed Domain Packs ==")
    if packs:
        for pack_dir, manifest in packs:
            print(f"- {manifest.display_name} ({manifest.name} {manifest.version}) @ {pack_dir}")
    else:
        print("- none found")
    print()
    print("== Domain Map Sequence ==")
    for concept in dmap.topological_sequence():
        print(f"- {concept}")
    print()
    print("== Roadmap ==")
    for stage in roadmap:
        print(f"- {stage.title}: {stage.mastery_goal}")
    print()
    focus_concept = dmap.topological_sequence()[1]
    print("== Mentor Prompt ==")
    print(generate_socratic_prompt(provider, focus_concept))
    print()
    print("== Practice Task ==")
    print(generate_practice_task(provider, focus_concept))
    print()
    print("== Capstone Suggestion ==")
    print(suggest_capstone(provider, args.domain))
    print()
    print("== Evaluation Rubric ==")
    print(generate_rubric(provider, focus_concept))


if __name__ == "__main__":
    main()
