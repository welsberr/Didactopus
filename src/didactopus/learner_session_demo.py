from __future__ import annotations

import json
from pathlib import Path

from .config import load_config
from .learner_session import (
    build_graph_grounded_session,
    build_notebook_sequence_grounded_session,
)
from .model_provider import ModelProvider
from .notebook_learning_sequence import build_notebook_sequence_session_plan
from .ocw_skill_agent_demo import load_ocw_skill_context
from .provider_policy import effective_provider_for_kind, provider_diagnostics_for_kind


def run_learner_session_demo(
    config_path: str | Path,
    skill_dir: str | Path,
    out_path: str | Path | None = None,
    *,
    sequence_path: str | Path | None = None,
    step_index: int = 0,
    learner_goal: str | None = None,
    learner_submission: str | None = None,
) -> dict:
    config = load_config(config_path)
    base_provider = ModelProvider(config.model_provider)
    provider = effective_provider_for_kind(base_provider, kind="chat")
    if sequence_path is not None:
        session_plan = build_notebook_sequence_session_plan(sequence_path, learner_goal=learner_goal)
        payload = build_notebook_sequence_grounded_session(
            session_plan=session_plan,
            provider=provider,
            step_index=step_index,
            learner_submission=learner_submission
            or "Allele frequencies changed across generations, and I would compare whether the shift reflects chance sampling or another mechanism before naming a cause.",
            learner_goal=learner_goal,
        )
    else:
        context = load_ocw_skill_context(skill_dir)
        payload = build_graph_grounded_session(
            context=context,
            provider=provider,
            learner_goal=learner_goal
            or "Help me understand how Shannon entropy leads into channel capacity and thermodynamic entropy.",
            learner_submission=learner_submission
            or "Entropy measures uncertainty because more possible outcomes require more information to describe, but one limitation is that thermodynamic entropy is not identical to Shannon entropy.",
        )
    payload["provider_diagnostics"] = provider_diagnostics_for_kind(base_provider, kind="chat")
    if out_path is not None:
        Path(out_path).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main() -> None:
    import argparse

    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Run a graph-grounded learner session demo for Didactopus.")
    parser.add_argument("--config", default=str(root / "configs" / "config.example.yaml"))
    parser.add_argument("--skill-dir", default=str(root / "skills" / "ocw-information-entropy-agent"))
    parser.add_argument("--out", default=str(root / "examples" / "ocw-information-entropy-session.json"))
    parser.add_argument("--sequence")
    parser.add_argument("--step-index", type=int, default=0)
    parser.add_argument("--learner-goal")
    parser.add_argument("--learner-submission")
    args = parser.parse_args()
    payload = run_learner_session_demo(
        args.config,
        args.skill_dir,
        args.out,
        sequence_path=args.sequence,
        step_index=args.step_index,
        learner_goal=args.learner_goal,
        learner_submission=args.learner_submission,
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
