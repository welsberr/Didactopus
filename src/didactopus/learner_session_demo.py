from __future__ import annotations

import json
from pathlib import Path

from .config import load_config
from .learner_accessibility import render_accessible_session_outputs
from .learner_session import build_graph_grounded_session
from .model_provider import ModelProvider
from .ocw_skill_agent_demo import load_ocw_skill_context


def run_learner_session_demo(
    config_path: str | Path,
    skill_dir: str | Path,
    out_path: str | Path | None = None,
    accessible_html_path: str | Path | None = None,
    accessible_text_path: str | Path | None = None,
    language: str = "en",
) -> dict:
    config = load_config(config_path)
    provider = ModelProvider(config.model_provider)
    context = load_ocw_skill_context(skill_dir)
    payload = build_graph_grounded_session(
        context=context,
        provider=provider,
        learner_goal="Help me understand how Shannon entropy leads into channel capacity and thermodynamic entropy.",
        learner_submission="Entropy measures uncertainty because more possible outcomes require more information to describe, but one limitation is that thermodynamic entropy is not identical to Shannon entropy.",
        language=language,
        source_language="en",
    )
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
    parser.add_argument("--out", default=str(root / "examples" / "ocw-information-entropy-session.json"))
    parser.add_argument("--accessible-html", default=None)
    parser.add_argument("--accessible-text", default=None)
    parser.add_argument("--language", default="en")
    args = parser.parse_args()
    payload = run_learner_session_demo(
        args.config,
        args.skill_dir,
        args.out,
        args.accessible_html,
        args.accessible_text,
        args.language,
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
