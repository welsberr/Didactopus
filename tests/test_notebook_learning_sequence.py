import json
from pathlib import Path

from didactopus.notebook_learning_sequence import (
    build_notebook_sequence_session_plan,
    load_notebook_learning_sequence,
    load_notebook_scaffold_selection_policy,
    select_scaffold_record_for_step,
)


def _write_sequence_fixture(path: Path) -> None:
    payload = {
        "schema": "evo-edu.notebook.didactopus_learning_sequence.v1",
        "id": "notebook.learning-paths.test-sequence",
        "title": "Test Sequence",
        "sequence_kind": "guided_core_concepts",
        "learner_model": {
            "intended_use": "test sequence for guided mentorship",
            "mentor_style": ["ask for observable claims"],
            "success_condition": "learner can distinguish the two concepts",
        },
        "sequence": [
            {
                "position": 1,
                "concept_id": "notebook.concepts.alpha",
                "title": "Alpha",
                "url": "/notebook/concepts/alpha.html",
                "session_goal": "Define alpha clearly.",
                "mentor_opening": "What counts as alpha here?",
                "evidence_focus": "definitions and examples",
                "next_transition": "Move to beta as a contrast case.",
            },
            {
                "position": 2,
                "concept_id": "notebook.concepts.beta",
                "title": "Beta",
                "url": "/notebook/concepts/beta.html",
                "session_goal": "Contrast beta with alpha.",
                "mentor_opening": "How is beta not just alpha renamed?",
                "evidence_focus": "contrastive examples",
                "next_transition": "Move to the next cluster.",
            },
        ],
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_load_notebook_learning_sequence_reads_expected_schema(tmp_path: Path) -> None:
    path = tmp_path / "sequence.json"
    _write_sequence_fixture(path)

    payload = load_notebook_learning_sequence(path)

    assert payload["id"] == "notebook.learning-paths.test-sequence"
    assert len(payload["sequence"]) == 2


def test_load_notebook_scaffold_selection_policy_reads_expected_schema() -> None:
    payload = load_notebook_scaffold_selection_policy()

    assert payload["schema"] == "didactopus.notebook_scaffold_selection_policy.v1"
    assert "notebook.concepts.natural-selection" in payload["concept_type_preferences"]
    assert payload["trigger_type_preferences"]


def test_build_notebook_sequence_session_plan_exposes_session_fields(tmp_path: Path) -> None:
    path = tmp_path / "sequence.json"
    _write_sequence_fixture(path)

    plan = build_notebook_sequence_session_plan(path)

    assert plan["sequence_title"] == "Test Sequence"
    assert plan["learner_goal"] == "test sequence for guided mentorship"
    assert plan["mentor_style"] == ["ask for observable claims"]
    assert plan["session_count"] == 2
    assert plan["sessions"][0]["title"] == "Alpha"
    assert plan["sessions"][0]["mentor_opening"] == "What counts as alpha here?"
    assert plan["sessions"][1]["next_transition"] == "Move to the next cluster."


def test_build_notebook_sequence_session_plan_enriches_real_notebook_scaffold_fields() -> None:
    root = Path(__file__).resolve().parents[1]
    plan = build_notebook_sequence_session_plan(
        root.parent / "evo-edu.org" / "notebook" / "learning-paths" / "foundations-first-ring.didactopus.json"
    )

    first = plan["sessions"][0]
    assert first["scaffold_record_count"] >= 1
    assert first["scaffold_pending_source_slots"] >= 1
    assert first["scaffold_record"]["verification_prompt"]
    assert first["scaffold_record"]["misconception_guard"]
    assert first["scaffold_record"]["didactopus_prompt_seed"]
    assert first["scaffold_record"]["type"] == "definition-check"


def test_select_scaffold_record_for_step_prefers_type_fit_over_raw_overlap() -> None:
    step = {
        "title": "Adaptation",
        "session_goal": "Train the learner not to confuse usefulness or prevalence with a complete adaptive explanation.",
        "mentor_opening": "Ask what evidence is still missing before the learner should call a trait adaptive.",
        "evidence_focus": "rival explanations and context dependence",
        "next_transition": "Move from local trait interpretation to lineage-level divergence.",
    }
    scaffold = {
        "records": [
            {
                "id": "ad-001",
                "type": "definition-check",
                "question": "What is adaptation?",
                "answer_summary": "Adaptation refers to a trait or variant whose prevalence is explained by selection in a relevant environment.",
                "verification_prompt": "State the trait, the environment, and the evidence linking it to differential success.",
                "misconception_guard": "Do not use adaptation as a synonym for any interesting trait.",
                "didactopus_prompt_seed": "Rewrite the claim so the trait and environment are both explicit.",
            },
            {
                "id": "ad-004",
                "type": "alternative-check",
                "question": "Why compare alternatives?",
                "answer_summary": "Adaptive reasoning is stronger when it identifies rival processes and says what evidence would distinguish them.",
                "verification_prompt": "Name at least one non-adaptive or mixed explanation and how it could be tested.",
                "misconception_guard": "Do not treat adaptation as the default answer before alternatives are examined.",
                "didactopus_prompt_seed": "Add one rival explanation and one observation that would weaken the adaptive story.",
            },
        ]
    }

    selected = select_scaffold_record_for_step(step, scaffold)

    assert selected is not None
    assert selected["id"] == "ad-004"


def test_real_natural_selection_step_prefers_evidence_or_mechanism_records() -> None:
    root = Path(__file__).resolve().parents[1]
    plan = build_notebook_sequence_session_plan(
        root.parent / "evo-edu.org" / "notebook" / "learning-paths" / "foundations-first-ring.didactopus.json"
    )

    natural_selection = next(
        session for session in plan["sessions"] if session["concept_id"] == "notebook.concepts.natural-selection"
    )

    assert natural_selection["scaffold_record"]["type"] in {
        "evidence-check",
        "mechanism-contrast",
        "environment-check",
        "mixed-mechanism",
    }
