from __future__ import annotations

from pathlib import Path

from didactopus.source_spine_transfer_experiment import (
    CONDITIONS,
    POST_ITEMS,
    PRE_ITEMS,
    RETENTION_ITEMS,
    intervention_prompt,
    notes_text,
    run_condition,
    score_study_artifact,
    write_human_packets,
)


class FakeClient:
    def chat(self, *, model, messages, temperature=0.1, max_tokens=320, json_mode=False):
        prompt = messages[-1]["content"]
        if "keys study_notes, guardrails, and confidence_advice" in prompt:
            return """
            {
              "study_notes": [
                "The Tidepool Protocol concerns eelgrass seedlings in Alder, Birch, and Cormorant.",
                "Alder had 42 caged trays and 18 open trays with living shoots.",
                "Birch lacked turbidity readings.",
                "Cormorant had late planting after a storm.",
                "The moonlight fertilizer claim was rejected.",
                "Publishing failed plots prevents survivorship bias."
              ],
              "guardrails": [
                "Do not claim countywide proof.",
                "Do not treat one glowing night as a causal test.",
                "Answer unknown when notes do not decide."
              ],
              "confidence_advice": "Use unknown at 0.5 when notes are insufficient."
            }
            """
        if "Create a compact Didactopus study skill artifact" in prompt:
            return """
            {
              "title": "Tidepool Protocol Study Skill",
              "source_spine": [
                "Alder had 42 caged and 18 open surviving trays.",
                "Birch lacked turbidity readings.",
                "Cormorant had late planting after a storm.",
                "Moonlight fertilizer was rejected.",
                "Failed plots reduce survivorship bias."
              ],
              "source_summary": "The eelgrass protocol supports a narrow Alder cage hypothesis, not countywide proof.",
              "retrieval_questions": [
                {"question": "Which cove lacked turbidity?", "answer": "Birch"},
                {"question": "What were the Alder counts?", "answer": "42 caged, 18 open"},
                {"question": "What bias did failed plots address?", "answer": "Survivorship bias"}
              ],
              "guardrail": "Mark unsupported causal or countywide claims unknown."
            }
            """
        if "You have not been given this source" in prompt:
            return '{"answer": "unknown", "confidence": 0.5, "justification": "No source was provided."}'
        claim = prompt.split("Claim:", 1)[1].strip()
        y_by_claim = {item.claim: item.y for item in [*POST_ITEMS, *RETENTION_ITEMS]}
        answer = "true" if y_by_claim.get(claim, 0) == 1 else "false"
        return '{"answer": "' + answer + '", "confidence": 0.9, "justification": "Supported by notes."}'


def test_notes_text_extracts_structured_notes() -> None:
    text = '{"study_notes": ["Alder 42/60 caged"], "guardrails": ["No countywide proof"], "confidence_advice": "Use unknown."}'

    notes = notes_text(text)

    assert "Alder 42/60 caged" in notes
    assert "No countywide proof" in notes
    assert "Use unknown" in notes


def test_run_condition_scores_expected_rows_with_fake_client() -> None:
    result = run_condition(FakeClient(), "fake-model", "full_didactopus", "run-test")

    assert len(result["rows"]) == len(PRE_ITEMS) + len(POST_ITEMS) + len(RETENTION_ITEMS)
    assert result["metrics"]["pre"]["unknown_rate"] == 1.0
    assert result["metrics"]["post"]["accuracy"] == 1.0
    assert result["metrics"]["retention"]["accuracy"] == 1.0
    assert result["skill_score"]["score"] > 0.7


def test_causal_timing_calibration_condition_is_available() -> None:
    prompt = intervention_prompt("causal_timing_calibration")

    assert CONDITIONS["causal_timing_calibration"]["label"] == "Causal Timing + Calibration"
    assert "dairy valve repair happened before planting began" in prompt
    assert "correct answer at 0.5 is not mastery evidence" in prompt


def test_score_study_artifact_penalizes_forbidden_claims() -> None:
    artifact = """
    Source Spine: The protocol covers eelgrass at Alder, Birch, and Cormorant.
    Summary: Alder had 42 and 18. Birch turbidity was missing. Cormorant was late after a storm.
    Retrieval Questions with Answer Key: Moonlight was rejected. Failed plots prevent survivorship bias.
    Guardrail: do not invent.
    The study proved countywide adoption.
    """

    score = score_study_artifact(artifact)

    assert score["score"] < 1.0
    assert score["hallucinations"]


def test_write_human_packets_creates_response_and_answer_key(tmp_path: Path) -> None:
    paths = write_human_packets(tmp_path, "run-test")

    assert Path(paths["human_pilot_packet"]).exists()
    assert Path(paths["human_response_sheet"]).exists()
    answer_key = Path(paths["human_answer_key"]).read_text(encoding="utf-8")
    assert "pre_c_01" in answer_key
    assert "post_k_06" in answer_key
