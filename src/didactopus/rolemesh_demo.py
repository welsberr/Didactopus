from __future__ import annotations

import json
from pathlib import Path

from .config import load_config
from .mentor import generate_socratic_prompt
from .model_provider import ModelProvider
from .practice import generate_practice_task
from .project_advisor import suggest_capstone
from .role_prompts import evaluator_system_prompt


def run_rolemesh_demo(config_path: str | Path, out_path: str | Path | None = None) -> dict:
    config = load_config(config_path)
    provider = ModelProvider(config.model_provider)

    payload = {
        "provider": config.model_provider.provider,
        "mentor_prompt": generate_socratic_prompt(provider, "channel capacity", ["explanation"]),
        "practice_task": generate_practice_task(provider, "Shannon entropy", ["transfer"]),
        "capstone": suggest_capstone(provider, "information theory"),
        "evaluation_instruction": provider.generate(
            "Evaluate a learner explanation of thermodynamic entropy versus Shannon entropy.",
            role="evaluator",
            system_prompt=evaluator_system_prompt(),
        ).text,
    }

    if out_path is not None:
        Path(out_path).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main() -> None:
    import argparse

    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Run a Didactopus demo against a local RoleMesh-compatible model provider.")
    parser.add_argument(
        "--config",
        default=str(root / "configs" / "config.rolemesh.example.yaml"),
    )
    parser.add_argument(
        "--out",
        default=str(root / "examples" / "rolemesh_demo.json"),
    )
    args = parser.parse_args()
    payload = run_rolemesh_demo(args.config, args.out)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
