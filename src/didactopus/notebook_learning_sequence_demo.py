from __future__ import annotations

import json
from pathlib import Path

from .notebook_learning_sequence import build_notebook_sequence_session_plan


def run_notebook_learning_sequence_demo(
    sequence_path: str | Path,
    out_path: str | Path | None = None,
    *,
    learner_goal: str | None = None,
) -> dict:
    payload = build_notebook_sequence_session_plan(
        sequence_path,
        learner_goal=learner_goal,
    )
    if out_path is not None:
        Path(out_path).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main() -> None:
    import argparse

    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(
        description="Emit a deterministic Didactopus session plan from a Notebook learning-sequence artifact."
    )
    parser.add_argument(
        "--sequence",
        default=str(
            root.parent
            / "evo-edu.org"
            / "notebook"
            / "learning-paths"
            / "foundations-first-ring.didactopus.json"
        ),
    )
    parser.add_argument(
        "--out",
        default=str(root / "examples" / "notebook-foundations-first-ring-session-plan.json"),
    )
    parser.add_argument("--learner-goal")
    args = parser.parse_args()
    payload = run_notebook_learning_sequence_demo(
        args.sequence,
        args.out,
        learner_goal=args.learner_goal,
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
