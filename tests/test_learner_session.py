from pathlib import Path

import pytest

from didactopus.config import load_config
from didactopus.learner_session import (
    _scaffold_instruction_block,
    build_graph_grounded_session,
    build_notebook_sequence_grounded_run,
    build_notebook_sequence_grounded_session,
    resume_notebook_sequence_grounded_run,
)
from didactopus.learner_run_storage import (
    load_notebook_learner_run,
    save_notebook_learner_run,
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


def test_build_notebook_sequence_grounded_run_records_resumable_progress() -> None:
    root = Path(__file__).resolve().parents[1]
    provider = ModelProvider(load_config(root / "configs" / "config.example.yaml").model_provider)
    session_plan = build_notebook_sequence_session_plan(DEFAULT_SEQUENCE_PATH)

    payload = build_notebook_sequence_grounded_run(
        session_plan=session_plan,
        provider=provider,
        learner_submissions=[
            "The observation is the measured change itself, while a cause is an inference that needs separate evidence and uncertainty.",
            "Two explanations can fit one observation, so I would compare a prediction that differs between them before choosing.",
        ],
    )

    assert payload["run_kind"] == "notebook_sequence"
    assert payload["status"] == "in_progress"
    assert payload["completed_session_count"] == 2
    assert payload["total_session_count"] == 3
    assert payload["next_step_index"] == 2
    assert [item["title"] for item in payload["progress"]] == [
        "Observation",
        "Alternative Explanations",
    ]
    assert len(payload["sessions"]) == 2
    assert len(payload["turns"]) == 12
    assert {turn["step_index"] for turn in payload["turns"]} == {0, 1}
    assert len(payload["learner_evidence"]) == 2
    assert payload["learner_evidence"][0]["review_state"] == "draft"
    assert payload["learner_evidence"][0]["mastery_effect"] == "none_until_review"
    assert payload["learner_evidence"][0]["learner_submission"].startswith(
        "The observation"
    )


def test_build_notebook_sequence_grounded_run_rejects_excess_submissions() -> None:
    root = Path(__file__).resolve().parents[1]
    provider = ModelProvider(load_config(root / "configs" / "config.example.yaml").model_provider)
    session_plan = build_notebook_sequence_session_plan(DEFAULT_SEQUENCE_PATH)

    try:
        build_notebook_sequence_grounded_run(
            session_plan=session_plan,
            provider=provider,
            start_step_index=2,
            learner_submissions=["one", "two"],
        )
    except ValueError as exc:
        assert "2 submissions for 1 available steps" in str(exc)
    else:
        raise AssertionError("Expected excess sequence submissions to be rejected")


def test_run_learner_session_demo_writes_multi_step_sequence_run(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    payload = run_learner_session_demo(
        root / "configs" / "config.example.yaml",
        root / "skills" / "ocw-information-entropy-agent",
        tmp_path / "sequence-run.json",
        sequence_path=DEFAULT_SEQUENCE_PATH,
        learner_submissions=[
            "I would describe the observation, measurement, and uncertainty before I propose a causal explanation.",
            "I would compare rival explanations using evidence that produces different predictions under each alternative.",
            "The supported conclusion should state its limitations and what evidence would make me revise it.",
        ],
    )

    assert payload["status"] == "complete"
    assert payload["next_step_index"] is None
    assert payload["completed_session_count"] == 3
    assert (tmp_path / "sequence-run.json").exists()
    assert (tmp_path / "sequence-run.html").exists()
    assert (tmp_path / "sequence-run.txt").exists()


def test_persisted_sequence_run_resumes_and_appends_draft_evidence(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    state_path = tmp_path / "private" / "learner-run.json"
    first = run_learner_session_demo(
        root / "configs" / "config.example.yaml",
        root / "skills" / "ocw-information-entropy-agent",
        tmp_path / "first.json",
        sequence_path=DEFAULT_SEQUENCE_PATH,
        learner_submissions=[
            "I separate the observed allele-frequency change from any proposed cause and state measurement uncertainty first."
        ],
        learner_id="learner-a",
        run_state_path=state_path,
    )

    resumed = run_learner_session_demo(
        root / "configs" / "config.example.yaml",
        root / "skills" / "ocw-information-entropy-agent",
        tmp_path / "resumed.json",
        sequence_path=DEFAULT_SEQUENCE_PATH,
        learner_submissions=[
            "I compare alternative explanations by finding evidence that leads to different predictions under each mechanism.",
            "My qualified conclusion states the supported claim, remaining uncertainty, and the evidence that would trigger revision.",
        ],
        run_state_path=state_path,
        resume=True,
    )

    persisted = load_notebook_learner_run(state_path)
    assert resumed["run_id"] == first["run_id"] == persisted["run_id"]
    assert resumed["learner_id"] == "learner-a"
    assert resumed["status"] == "complete"
    assert resumed["next_step_index"] is None
    assert resumed["completed_session_count"] == 3
    assert len(resumed["learner_evidence"]) == 3
    assert [item["source"]["step_index"] for item in resumed["learner_evidence"]] == [0, 1, 2]
    assert {item["record_scope"] for item in resumed["learner_evidence"]} == {"human_learner"}


def test_run_state_requires_explicit_resume_before_overwrite(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    provider = ModelProvider(load_config(root / "configs" / "config.example.yaml").model_provider)
    session_plan = build_notebook_sequence_session_plan(DEFAULT_SEQUENCE_PATH)
    payload = build_notebook_sequence_grounded_run(
        session_plan=session_plan,
        provider=provider,
        learner_submissions=["A sufficiently detailed observation distinguishes measurement from an inferred causal explanation."],
    )
    state_path = tmp_path / "learner-run.json"
    save_notebook_learner_run(state_path, payload)

    with pytest.raises(FileExistsError, match="Resume it explicitly"):
        save_notebook_learner_run(state_path, payload)


def test_resume_rejects_a_different_sequence() -> None:
    root = Path(__file__).resolve().parents[1]
    provider = ModelProvider(load_config(root / "configs" / "config.example.yaml").model_provider)
    session_plan = build_notebook_sequence_session_plan(DEFAULT_SEQUENCE_PATH)
    payload = build_notebook_sequence_grounded_run(
        session_plan=session_plan,
        provider=provider,
        learner_submissions=["A detailed observation reports the measured pattern before drawing a causal inference about it."],
    )
    different_plan = {**session_plan, "sequence_id": "different-sequence"}

    with pytest.raises(ValueError, match="Sequence mismatch"):
        resume_notebook_sequence_grounded_run(
            session_plan=different_plan,
            provider=provider,
            previous_run=payload,
            learner_submissions=["This submission must not be appended."],
        )


def test_ai_learner_attempts_are_benchmark_only() -> None:
    root = Path(__file__).resolve().parents[1]
    provider = ModelProvider(load_config(root / "configs" / "config.example.yaml").model_provider)
    session_plan = build_notebook_sequence_session_plan(DEFAULT_SEQUENCE_PATH)
    payload = build_notebook_sequence_grounded_run(
        session_plan=session_plan,
        provider=provider,
        learner_submissions=["The model describes the measured observation and distinguishes it from its proposed causal explanation."],
        learner_kind="ai_benchmark",
    )

    assert payload["learner_evidence"][0]["record_scope"] == "benchmark"
    assert payload["learner_evidence"][0]["review_state"] == "benchmark_only"


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
