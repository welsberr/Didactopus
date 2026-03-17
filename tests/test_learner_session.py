from pathlib import Path

from didactopus.config import load_config
from didactopus.learner_session import build_graph_grounded_session
from didactopus.learner_session_demo import run_learner_session_demo
from didactopus.model_provider import ModelProvider
from didactopus.ocw_skill_agent_demo import load_ocw_skill_context


def test_build_graph_grounded_session_uses_grounded_steps() -> None:
    root = Path(__file__).resolve().parents[1]
    context = load_ocw_skill_context(root / "skills" / "ocw-information-entropy-agent")
    provider = ModelProvider(load_config(root / "configs" / "config.example.yaml").model_provider)

    payload = build_graph_grounded_session(
        context=context,
        provider=provider,
        learner_goal="Help me connect Shannon entropy and channel capacity.",
        learner_submission="Entropy measures uncertainty because unlikely outcomes carry more information, but one limitation is that idealized source models may not match physical systems.",
    )

    assert payload["study_plan"]["steps"]
    assert payload["primary_concept"]["supporting_lessons"]
    assert payload["evaluation"]["verdict"] in {"acceptable", "needs_revision"}
    assert len(payload["turns"]) == 6
    assert any("Grounding fragments" in turn["content"] or "Concept:" in turn["content"] for turn in payload["turns"])


def test_run_learner_session_demo_writes_output(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    payload = run_learner_session_demo(
        root / "configs" / "config.example.yaml",
        root / "skills" / "ocw-information-entropy-agent",
        tmp_path / "session.json",
    )

    assert (tmp_path / "session.json").exists()
    assert payload["practice_task"]
    assert payload["evaluation"]["aggregated"]
