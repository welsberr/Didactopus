from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from .config import load_config
from .learner_accessibility import render_accessible_session_outputs
from .learner_session import (
    build_graph_grounded_session,
    build_notebook_sequence_grounded_run,
    build_notebook_sequence_grounded_session,
    resume_notebook_sequence_grounded_run,
)
from .learner_run_storage import load_notebook_learner_run, save_notebook_learner_run
from .model_provider import ModelProvider
from .notebook_learning_sequence import (
    DEFAULT_NOTEBOOK_ROOT,
    DEFAULT_SELECTION_POLICY_PATH,
    build_notebook_sequence_session_plan,
)
from .ocw_skill_agent_demo import load_ocw_skill_context
from .provider_policy import effective_provider_for_kind, provider_diagnostics_for_kind


def run_learner_session_demo(
    config_path: str | Path,
    skill_dir: str | Path,
    out_path: str | Path | None = None,
    accessible_html_path: str | Path | None = None,
    accessible_text_path: str | Path | None = None,
    language: str = "en",
    *,
    sequence_path: str | Path | None = None,
    step_index: int = 0,
    learner_goal: str | None = None,
    learner_submission: str | None = None,
    learner_submissions: list[str] | None = None,
    notebook_root: str | Path = DEFAULT_NOTEBOOK_ROOT,
    selection_policy_path: str | Path | None = DEFAULT_SELECTION_POLICY_PATH,
    learner_id: str = "local-learner",
    learner_kind: Literal["human", "ai_benchmark"] = "human",
    run_state_path: str | Path | None = None,
    resume: bool = False,
) -> dict:
    config = load_config(config_path)
    base_provider = ModelProvider(config.model_provider)
    provider = effective_provider_for_kind(base_provider, kind="chat")
    if sequence_path is not None:
        session_plan = build_notebook_sequence_session_plan(
            sequence_path,
            learner_goal=learner_goal,
            notebook_root=notebook_root,
            selection_policy_path=selection_policy_path,
        )
        if learner_submissions:
            if resume:
                if run_state_path is None:
                    raise ValueError("Resuming requires an explicit run_state_path.")
                payload = resume_notebook_sequence_grounded_run(
                    session_plan=session_plan,
                    provider=provider,
                    previous_run=load_notebook_learner_run(run_state_path),
                    learner_submissions=learner_submissions,
                    language=language,
                    source_language="en",
                )
            else:
                payload = build_notebook_sequence_grounded_run(
                    session_plan=session_plan,
                    provider=provider,
                    learner_submissions=learner_submissions,
                    start_step_index=step_index,
                    learner_goal=learner_goal,
                    language=language,
                    source_language="en",
                    learner_id=learner_id,
                    learner_kind=learner_kind,
                )
        else:
            if resume or run_state_path is not None:
                raise ValueError("Run-state persistence requires repeated step submissions.")
            payload = build_notebook_sequence_grounded_session(
                session_plan=session_plan,
                provider=provider,
                step_index=step_index,
                learner_submission=learner_submission
                or (
                    "I would first state the observation without naming a cause, "
                    "then compare alternative explanations and the evidence that distinguishes them."
                ),
                learner_goal=learner_goal,
                language=language,
                source_language="en",
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
            language=language,
            source_language="en",
        )
    payload["provider_diagnostics"] = provider_diagnostics_for_kind(base_provider, kind="chat")
    if run_state_path is not None:
        save_notebook_learner_run(run_state_path, payload, overwrite=resume)
    if out_path is not None:
        out_path = Path(out_path)
        out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        html_path = Path(accessible_html_path) if accessible_html_path is not None else out_path.with_suffix(".html")
        text_path = Path(accessible_text_path) if accessible_text_path is not None else out_path.with_suffix(".txt")
        render_accessible_session_outputs(payload, out_html=html_path, out_text=text_path)
    return payload


def main() -> None:
    import argparse

    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Run a graph-grounded learner session demo for Didactopus.")
    parser.add_argument("--config", default=str(root / "configs" / "config.example.yaml"))
    parser.add_argument("--skill-dir", default=str(root / "skills" / "ocw-information-entropy-agent"))
    parser.add_argument("--out")
    parser.add_argument("--sequence")
    parser.add_argument("--notebook-root", default=str(DEFAULT_NOTEBOOK_ROOT))
    parser.add_argument("--selection-policy", default=str(DEFAULT_SELECTION_POLICY_PATH))
    parser.add_argument("--step-index", type=int, default=0)
    parser.add_argument("--learner-goal")
    parser.add_argument("--learner-id", default="local-learner")
    parser.add_argument(
        "--learner-kind",
        choices=("human", "ai_benchmark"),
        default="human",
        help="Keep human learner evidence separate from AI benchmark records.",
    )
    parser.add_argument("--learner-submission")
    parser.add_argument(
        "--step-submission",
        action="append",
        dest="learner_submissions",
        help="Learner submission for one sequence step; repeat to run consecutive steps.",
    )
    parser.add_argument("--accessible-html", default=None)
    parser.add_argument("--accessible-text", default=None)
    parser.add_argument("--language", default="en")
    parser.add_argument(
        "--run-state",
        help="Local JSON file for durable multi-step run state and draft learner evidence.",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Load --run-state and append submissions from its next step.",
    )
    args = parser.parse_args()
    if args.learner_submission and args.learner_submissions:
        parser.error("Use either --learner-submission or repeated --step-submission, not both.")
    if args.resume and not args.run_state:
        parser.error("--resume requires --run-state.")
    if args.resume and not args.sequence:
        parser.error("--resume requires --sequence.")
    out_path = args.out
    if out_path is None and args.run_state is None:
        out_path = str(
            root
            / "examples"
            / (
                "notebook-sequence-session.json"
                if args.sequence
                else "ocw-information-entropy-session.json"
            )
        )
    payload = run_learner_session_demo(
        args.config,
        args.skill_dir,
        out_path,
        args.accessible_html,
        args.accessible_text,
        args.language,
        sequence_path=args.sequence,
        step_index=args.step_index,
        learner_goal=args.learner_goal,
        learner_submission=args.learner_submission,
        learner_submissions=args.learner_submissions,
        notebook_root=args.notebook_root,
        selection_policy_path=args.selection_policy or None,
        learner_id=args.learner_id,
        learner_kind=args.learner_kind,
        run_state_path=args.run_state,
        resume=args.resume,
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
