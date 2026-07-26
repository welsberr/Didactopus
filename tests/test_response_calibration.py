from __future__ import annotations

import json
from pathlib import Path

from didactopus.ai_learner_benchmark import ClaimItem, score_row, write_outputs as write_benchmark_outputs
from didactopus.response_calibration import (
    RESPONSE_CALIBRATION_POLICY,
    build_response_calibration_reports,
    calibration_samples_from_rows,
)


def _row(item_id: str, answer: str, confidence: float, y: int, *, phase: str = "post") -> dict:
    item = ClaimItem(item_id, "C", f"claim {item_id}", y, "anchor")
    row = score_row("model-a", phase, item, {"answer": answer, "confidence": confidence, "justification": ""}, "raw")
    row["run_id"] = "run-a"
    return row


def test_response_confidence_and_p_true_are_separate_calibration_events() -> None:
    false_claim_correctly_rejected = _row("false-claim", "false", 0.8, 0)

    response = calibration_samples_from_rows(
        [false_claim_correctly_rejected],
        event="selected_answer_correct",
        dimension="response_correctness",
    )[0]
    truth = calibration_samples_from_rows(
        [false_claim_correctly_rejected],
        event="claim_is_true",
        dimension="claim_truth_probability",
    )[0]

    assert response.predicted == 0.8
    assert response.observed == 1.0
    assert truth.predicted == 0.2
    assert truth.observed == 0.0
    assert response.metadata["excluded_from_mastery_progression"] is True


def test_calibration_reports_cover_perfect_underconfident_overconfident_and_abstaining_rows() -> None:
    rows = [
        _row("perfect-true", "true", 1.0, 1),
        _row("perfect-false", "false", 1.0, 0),
        _row("underconfident", "true", 0.6, 1),
        _row("overconfident", "true", 0.9, 0),
        _row("abstain", "unknown", 0.5, 1, phase="pre"),
    ]

    reports = build_response_calibration_reports(rows)
    response = reports["response_correctness"]
    truth = reports["claim_truth_probability"]

    assert response["sample_count"] == 5
    assert truth["sample_count"] == 5
    assert response["abstention"]["abstention_count"] == 1
    assert response["discrimination"]["positive_count"] == 3
    assert response["discrimination"]["negative_count"] == 2
    assert response["calibration"]["brier_score"] is not None
    assert truth["calibration"]["brier_score"] is not None


def test_small_samples_warn_before_policy_changes() -> None:
    reports = build_response_calibration_reports([_row("one", "true", 0.9, 1)])

    assert any("do not change mentoring or stop-policy thresholds" in warning for warning in reports["response_correctness"]["warnings"])
    assert RESPONSE_CALIBRATION_POLICY["minimum_samples_for_policy_change"] == 20


def test_benchmark_outputs_write_calibration_artifacts_and_reconstruct_policy(tmp_path: Path) -> None:
    rows = [_row("one", "true", 0.9, 1), _row("two", "false", 0.8, 0)]
    payload = {
        "run_id": "run-a",
        "condition": "fixture",
        "ollama_base_url": "http://127.0.0.1:11434",
        "models": [
            {
                "model_id": "model-a",
                "rows": rows,
                "interactions": [],
                "skill_artifact": "Title: Fixture\n",
                "skill_score": {"score": 1.0},
                "metrics": {
                    "pre": {"accuracy": 0.0, "unknown_rate": 0.0},
                    "post": {"accuracy": 1.0, "unknown_rate": 0.0},
                    "G_pre": {"G": 0.0},
                    "G_post": {"G": 1.0},
                    "delta_G": 1.0,
                },
            }
        ],
    }

    artifacts = write_benchmark_outputs(payload, tmp_path)

    manifest = json.loads(Path(artifacts["manifest"]).read_text(encoding="utf-8"))
    assert Path(artifacts["response_correctness_json"]).exists()
    assert Path(artifacts["claim_truth_probability_json"]).exists()
    assert manifest["calibration_policy"]["policy_id"] == "didactopus_response_calibration.v1"
    assert manifest["calibration"]["policy"] == manifest["calibration_policy"]
    assert manifest["calibration"]["reports"]["response_correctness"]["sample_count"] == 2
