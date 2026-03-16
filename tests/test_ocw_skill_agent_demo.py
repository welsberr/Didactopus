from pathlib import Path

from didactopus.ocw_skill_agent_demo import (
    evaluate_submission_with_skill,
    load_ocw_skill_context,
    run_ocw_skill_agent_demo,
)


def test_run_ocw_skill_agent_demo(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    payload = run_ocw_skill_agent_demo(
        root / "skills" / "ocw-information-entropy-agent",
        tmp_path,
    )

    assert (tmp_path / "skill_demo.json").exists()
    assert (tmp_path / "skill_demo.md").exists()
    assert payload["study_plan"]["steps"]
    assert payload["study_plan"]["steps"][0]["supporting_lessons"]
    assert "grounding" in payload["explanation"]
    assert payload["explanation"]["grounding"]["supporting_lessons"]
    assert payload["evaluation"]["verdict"] in {"acceptable", "needs_revision"}


def test_skill_demo_flags_weak_submission() -> None:
    root = Path(__file__).resolve().parents[1]
    context = load_ocw_skill_context(root / "skills" / "ocw-information-entropy-agent")
    result = evaluate_submission_with_skill(
        context,
        "channel-capacity",
        "Channel capacity is good.",
    )

    assert result["verdict"] == "needs_revision"
    assert result["skill_reference"]["supporting_lessons"]
    assert "Rework the answer" in result["follow_up"]
