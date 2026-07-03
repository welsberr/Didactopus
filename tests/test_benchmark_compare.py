import json
from pathlib import Path

from didactopus.benchmark_compare import compare_g_summary_files


def _summary(path: Path, experiment_id: str, g_value: float) -> Path:
    payload = {
        "summary_kind": "epistemap_g_experiment_summary",
        "manifest": {
            "experiment_id": experiment_id,
            "name": experiment_id,
            "evaluation_target": "grounded_role_behavior",
        },
        "overall": {
            "G": g_value,
            "n": {"clean": 2, "target": 2},
        },
        "row_count": 4,
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_compare_g_summary_files_ranks_and_writes_output(tmp_path: Path) -> None:
    weak = _summary(tmp_path / "weak_g_summary.json", "weak", 0.2)
    strong = _summary(tmp_path / "strong_g_summary.json", "strong", 0.8)
    out_path = tmp_path / "comparison.json"

    comparison = compare_g_summary_files([weak, strong], baseline_id="weak", out_path=out_path)

    assert comparison["comparison_kind"] == "epistemap_g_summary_comparison"
    assert comparison["summaries"][0]["experiment_id"] == "strong"
    assert comparison["summaries"][0]["delta_from_baseline"] > 0
    assert out_path.exists()
    assert json.loads(out_path.read_text(encoding="utf-8"))["baseline_id"] == "weak"
