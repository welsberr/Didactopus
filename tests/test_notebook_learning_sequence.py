import json
from pathlib import Path

from didactopus.notebook_learning_sequence import (
    DEFAULT_NOTEBOOK_ROOT,
    DEFAULT_SELECTION_POLICY_PATH,
    DEFAULT_SEQUENCE_PATH,
    build_notebook_sequence_session_plan,
    load_notebook_learning_sequence,
    load_notebook_scaffold_selection_policy,
    scaffold_path_for_concept_url,
    select_scaffold_record_for_step,
)


def _write_sequence_fixture(path: Path) -> None:
    payload = {
        "schema": "didactopus.notebook.learning_sequence.v1",
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
    assert "didactopus.examples.observation" in payload["concept_type_preferences"]
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


def test_build_notebook_sequence_session_plan_enriches_repository_fixture() -> None:
    plan = build_notebook_sequence_session_plan(DEFAULT_SEQUENCE_PATH)

    first = plan["sessions"][0]
    assert first["scaffold_record_count"] >= 1
    assert first["scaffold_pending_source_slots"] == 0
    assert first["scaffold_record"]["verification_prompt"]
    assert first["scaffold_record"]["misconception_guard"]
    assert first["scaffold_record"]["didactopus_prompt_seed"]
    assert first["scaffold_record"]["type"] == "observation-check"


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

    selected = select_scaffold_record_for_step(
        step,
        scaffold,
        selection_policy={
            "concept_type_preferences": {},
            "trigger_type_preferences": [
                {
                    "trigger_terms": ["alternatives", "rival", "adaptive"],
                    "preferred_types": ["alternative-check"],
                }
            ],
        },
    )

    assert selected is not None
    assert selected["id"] == "ad-004"


def test_repository_fixture_is_self_contained() -> None:
    plan = build_notebook_sequence_session_plan(
        DEFAULT_SEQUENCE_PATH,
        notebook_root=DEFAULT_NOTEBOOK_ROOT,
        selection_policy_path=DEFAULT_SELECTION_POLICY_PATH,
    )

    assert plan["session_count"] == 3
    assert all(Path(item["scaffold_path"]).is_file() for item in plan["sessions"])
    assert [item["scaffold_record"]["type"] for item in plan["sessions"]] == [
        "observation-check",
        "alternative-check",
        "calibration-check",
    ]


def test_legacy_producer_schema_remains_readable(tmp_path: Path) -> None:
    path = tmp_path / "legacy-sequence.json"
    _write_sequence_fixture(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["schema"] = "evo-edu.notebook.didactopus_learning_sequence.v1"
    path.write_text(json.dumps(payload), encoding="utf-8")

    assert load_notebook_learning_sequence(path)["title"] == "Test Sequence"


def test_scaffold_url_resolution_is_rooted_and_accepts_absolute_urls(tmp_path: Path) -> None:
    path = scaffold_path_for_concept_url(
        "https://learning.example/notebook/concepts/alpha.html?language=en#start",
        notebook_root=tmp_path,
    )

    assert path == tmp_path / "concepts" / "alpha.scaffold.json"


def test_explicit_scaffold_path_cannot_escape_root(tmp_path: Path) -> None:
    sequence_path = tmp_path / "sequence.json"
    _write_sequence_fixture(sequence_path)
    payload = json.loads(sequence_path.read_text(encoding="utf-8"))
    payload["sequence"][0]["scaffold_path"] = "../outside.scaffold.json"
    sequence_path.write_text(json.dumps(payload), encoding="utf-8")

    try:
        build_notebook_sequence_session_plan(
            sequence_path,
            notebook_root=tmp_path,
            selection_policy_path=None,
        )
    except ValueError as exc:
        assert "escapes notebook root" in str(exc)
    else:
        raise AssertionError("Expected an escaping scaffold path to be rejected")
