from pathlib import Path

from didactopus.config import load_config
from didactopus.learner_session import (
    _scaffold_instruction_block,
    build_graph_grounded_session,
    build_notebook_sequence_grounded_session,
)
from didactopus.learner_session_demo import run_learner_session_demo
from didactopus.model_provider import ModelProvider
from didactopus.notebook_learning_sequence import (
    DEFAULT_SEQUENCE_PATH,
    build_notebook_sequence_session_plan,
)
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
    assert payload["provider_diagnostics"]["provider"] == "stub"
    assert payload["provider_diagnostics"]["role_model_overrides"] == {}


def test_build_notebook_sequence_grounded_session_uses_sequence_steps() -> None:
    root = Path(__file__).resolve().parents[1]
    provider = ModelProvider(load_config(root / "configs" / "config.example.yaml").model_provider)
    session_plan = build_notebook_sequence_session_plan(DEFAULT_SEQUENCE_PATH)

    payload = build_notebook_sequence_grounded_session(
        session_plan=session_plan,
        provider=provider,
        step_index=0,
        learner_submission="Allele frequencies changed across generations, so I would check whether the pattern reflects observation alone or points to a mechanism like drift or selection.",
    )

    assert payload["study_plan"]["steps"]
    assert payload["primary_concept"]["title"] == "Observation"
    assert payload["secondary_concept"]["title"] == "Alternative Explanations"
    assert payload["evaluation"]["verdict"] in {"acceptable", "needs_revision"}
    assert payload["primary_concept"]["scaffold_record"]["verification_prompt"]
    assert payload["evaluation"]["aggregated"]["verification_prompt"]
    assert len(payload["turns"]) == 6


def test_run_learner_session_demo_supports_notebook_sequence(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    payload = run_learner_session_demo(
        root / "configs" / "config.example.yaml",
        root / "skills" / "ocw-information-entropy-agent",
        tmp_path / "notebook-session.json",
        sequence_path=DEFAULT_SEQUENCE_PATH,
        step_index=1,
        learner_submission="Hardy-Weinberg expectations matter because departures from the null model tell us to ask which assumption failed before we name a cause.",
    )

    assert (tmp_path / "notebook-session.json").exists()
    assert payload["primary_concept"]["title"] == "Alternative Explanations"
    assert payload["secondary_concept"]["title"] == "Qualified Conclusion"
    assert payload["provider_diagnostics"]["provider"] == "stub"


def test_scaffold_instruction_block_uses_verification_seed_and_guard() -> None:
    step = {
        "scaffold_record": {
            "verification_prompt": "Check whether the population and allele are explicit.",
            "didactopus_prompt_seed": "Rewrite the claim so the comparison across generations is visible.",
            "misconception_guard": "Do not confuse individual change with population-level evolution.",
        }
    }

    block = _scaffold_instruction_block(step)

    assert "Use this verification prompt directly" in block
    assert "Use this prompt-seed move directly" in block
    assert "Guard against this misconception explicitly" in block
