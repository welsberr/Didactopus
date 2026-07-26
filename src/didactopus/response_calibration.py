from __future__ import annotations

from pathlib import Path
from typing import Any

from epistemap import CalibrationSample, calibration_report, write_calibration_report, write_calibration_report_markdown


RESPONSE_CALIBRATION_POLICY = {
    "policy_id": "didactopus_response_calibration.v1",
    "version": "1.0",
    "confidence_interpretation": "confidence is the predicted probability that the selected answer is correct",
    "p_true_interpretation": "p is the transformed probability that the evaluated claim is true",
    "unknown_policy": "answer=unknown is an abstention; its response confidence is coerced to 0.5",
    "minimum_samples_for_policy_change": 20,
    "graph_support_policy": "graph posterior support must not be consumed as learner mastery evidence coverage",
}


def calibration_samples_from_rows(rows: list[dict[str, Any]], *, event: str, dimension: str) -> list[CalibrationSample]:
    samples = []
    for row in rows:
        if dimension == "response_correctness":
            predicted = float(row["confidence"])
            observed = float(row["correct"])
        elif dimension == "claim_truth_probability":
            predicted = float(row["p"])
            observed = float(row["y"])
        else:
            raise ValueError(f"unsupported Didactopus calibration dimension: {dimension}")
        samples.append(
            CalibrationSample(
                subject_id=_subject_id(row),
                predicted=predicted,
                observed=observed,
                dimension=dimension,
                event=event,
                metadata={
                    "run_id": row.get("run_id", ""),
                    "model_id": row.get("model_id", ""),
                    "condition": row.get("condition", ""),
                    "phase": row.get("phase", ""),
                    "item_id": row.get("item_id", ""),
                    "answer": row.get("answer", ""),
                    "abstained": row.get("answer") == "unknown" or bool(int(row.get("unknown", 0))),
                    "p_true": float(row.get("p", 0.5)),
                    "claim_truth": int(row.get("y", 0)),
                    "correct": int(row.get("correct", 0)),
                    "evidence_coverage": row.get("evidence_coverage"),
                    "explicit_probabilistic_interpretation": True,
                    "excluded_from_mastery_progression": True,
                },
            )
        )
    return samples


def build_response_calibration_reports(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    response_samples = calibration_samples_from_rows(
        rows,
        event="selected_answer_correct",
        dimension="response_correctness",
    )
    truth_samples = calibration_samples_from_rows(
        rows,
        event="claim_is_true",
        dimension="claim_truth_probability",
    )
    reports = {
        "response_correctness": calibration_report(
            response_samples,
            event="selected_answer_correct",
            dimension="response_correctness",
            predicted_event="selected answer is correct",
            outcome_interpretation="observed=1 means the selected answer is correct; observed=0 means selected true/false is wrong or the model abstained",
            sample_selection_policy="all Didactopus scored response rows with parsed confidence",
            minimum_bin_size=RESPONSE_CALIBRATION_POLICY["minimum_samples_for_policy_change"],
        ),
        "claim_truth_probability": calibration_report(
            truth_samples,
            event="claim_is_true",
            dimension="claim_truth_probability",
            predicted_event="evaluated claim is true",
            outcome_interpretation="observed=1 means the evaluated claim is true; observed=0 means it is false",
            sample_selection_policy="all Didactopus scored claim rows after true/false/unknown p_true transform",
            minimum_bin_size=RESPONSE_CALIBRATION_POLICY["minimum_samples_for_policy_change"],
        ),
    }
    for report in reports.values():
        _append_policy_warning(report)
    return reports


def write_response_calibration_reports(rows: list[dict[str, Any]], out_dir: str | Path) -> dict[str, str]:
    target = Path(out_dir)
    target.mkdir(parents=True, exist_ok=True)
    reports = build_response_calibration_reports(rows)
    paths: dict[str, str] = {}
    for name, report in reports.items():
        json_path = target / f"calibration_{name}.json"
        markdown_path = target / f"calibration_{name}.md"
        write_calibration_report(report, json_path)
        write_calibration_report_markdown(report, markdown_path)
        paths[f"{name}_json"] = str(json_path)
        paths[f"{name}_markdown"] = str(markdown_path)
    return paths


def summarize_calibration_reports(rows: list[dict[str, Any]]) -> dict[str, Any]:
    reports = build_response_calibration_reports(rows)
    return {
        "policy": dict(RESPONSE_CALIBRATION_POLICY),
        "reports": {
            name: {
                "report_kind": report["report_kind"],
                "event": report["event"],
                "dimension": report["dimension"],
                "sample_count": report["sample_count"],
                "brier_score": report["brier_score"],
                "expected_calibration_error": report["expected_calibration_error"],
                "discrimination": report["discrimination"],
                "abstention": report["abstention"],
                "evidence_coverage": report["evidence_coverage"],
                "warnings": report["warnings"],
            }
            for name, report in reports.items()
        },
    }


def _append_policy_warning(report: dict[str, Any]) -> None:
    minimum = RESPONSE_CALIBRATION_POLICY["minimum_samples_for_policy_change"]
    if int(report.get("sample_count", 0)) < minimum:
        report.setdefault("warnings", []).append(
            f"Sample count below {minimum}; do not change mentoring or stop-policy thresholds from this run alone."
        )


def _subject_id(row: dict[str, Any]) -> str:
    parts = [
        row.get("run_id", ""),
        row.get("model_id", ""),
        row.get("condition", ""),
        row.get("phase", ""),
        row.get("item_id", ""),
    ]
    return "::".join(str(part) for part in parts if str(part))
