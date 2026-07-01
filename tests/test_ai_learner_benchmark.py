from __future__ import annotations

from didactopus.ai_learner_benchmark import (
    ClaimItem,
    clean_skill_artifact,
    g_estimate,
    normalize_skill_artifact,
    parse_answer,
    probability_true,
    score_row,
    score_skill_artifact,
    strip_model_reasoning,
)


def test_parse_answer_json_and_probability_true() -> None:
    parsed = parse_answer('{"answer": "false", "confidence": 0.8, "justification": "source says otherwise"}')

    assert parsed["answer"] == "false"
    assert parsed["confidence"] == 0.8
    assert probability_true(parsed["answer"], parsed["confidence"]) == 0.19999999999999996


def test_unknown_answer_uses_half_probability() -> None:
    parsed = parse_answer('{"answer": "unknown", "confidence": 0.9, "justification": "not given"}')

    assert parsed["answer"] == "unknown"
    assert parsed["confidence"] == 0.5
    assert probability_true(parsed["answer"], parsed["confidence"]) == 0.5


def test_g_estimate_uses_clean_and_target_rows() -> None:
    rows = []
    items = [
        ClaimItem("c1", "C", "clean true", 1, ""),
        ClaimItem("c2", "C", "clean false", 0, ""),
        ClaimItem("k1", "K", "target true", 1, ""),
        ClaimItem("k2", "K", "target false", 0, ""),
    ]
    answers = [
        {"answer": "true", "confidence": 0.9, "justification": ""},
        {"answer": "false", "confidence": 0.9, "justification": ""},
        {"answer": "true", "confidence": 0.8, "justification": ""},
        {"answer": "false", "confidence": 0.8, "justification": ""},
    ]
    for item, answer in zip(items, answers):
        rows.append(score_row("model-a", "post", item, answer, "raw"))

    estimate = g_estimate(rows, "post")

    assert estimate["G"] > 0.7
    assert estimate["n"] == {"clean": 2, "target": 2}


def test_skill_artifact_scoring_rewards_structure_and_penalizes_hallucination() -> None:
    artifact = """
    Title: The Glass Orchard
    Source spine: Mara, Ivo, and Pilgrim move through the lighthouse sequence.
    Summary: Mara saves the root ledger, a real apple seed makes a living leaf, and the jar hums in C-sharp.
    Retrieval questions with answer key:
    1. Who is the apprentice? Ivo.
    Guardrail: mark details unknown when unsupported.
    """

    score = score_skill_artifact(artifact)

    assert score["score"] > 0.75
    assert not score["hallucinations"]


def test_strip_model_reasoning_removes_visible_think_preamble() -> None:
    text = "private reasoning that should not be persisted\n</think>\n\n**Title**\nSource spine: Mara and Ivo."

    assert strip_model_reasoning(text) == "**Title**\nSource spine: Mara and Ivo."


def test_clean_skill_artifact_starts_at_title_marker() -> None:
    text = "I will plan the response first.\n\nTitle: Glass Orchard\nSource Spine:\n- Mara keeps the orchard."

    assert clean_skill_artifact(text) == "Title: Glass Orchard\nSource Spine:\n- Mara keeps the orchard.\n"


def test_normalize_skill_artifact_renders_json_payload() -> None:
    text = """
    {
      "title": "Glass Orchard",
      "source_spine": ["Mara keeps the orchard", "Pilgrim is a clockwork moth"],
      "source_summary": "Mara tends a glass orchard.",
      "retrieval_questions": [
        {"question": "Who is Pilgrim?", "answer": "A clockwork moth"}
      ],
      "guardrail": "Mark unsupported details unknown."
    }
    """

    artifact = normalize_skill_artifact(text)

    assert artifact.startswith("Title: Glass Orchard")
    assert "Source Spine:" in artifact
    assert "Answer Key:\n1. A clockwork moth" in artifact
    assert "Guardrail:\nMark unsupported details unknown." in artifact
