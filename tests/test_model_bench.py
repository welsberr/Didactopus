import json

from didactopus.model_bench import model_benchmark_g_evaluation_rows, run_model_benchmark


def test_run_model_benchmark_writes_reports(tmp_path) -> None:
    payload = run_model_benchmark(
        config_path="configs/config.example.yaml",
        skill_dir="skills/ocw-information-entropy-agent",
        out_dir=tmp_path,
        hardware_profile_name="pi-minimal",
        hardware_cpu="cortex-a76",
        hardware_ram_gb=8.0,
        hardware_notes="local stub run for structure verification",
    )

    assert payload["benchmark"]["name"] == "didactopus-local-model-adequacy"
    assert payload["benchmark"]["hardware_profile"]["profile_name"] == "pi-minimal"
    assert len(payload["role_results"]) == 3
    assert {result["role"] for result in payload["role_results"]} == {"mentor", "practice", "evaluator"}
    assert payload["summary"]["overall_adequacy_rating"] in {"adequate", "borderline", "inadequate"}
    assert payload["context"]["output_language"] == "en"

    json_path = tmp_path / "model_benchmark.json"
    md_path = tmp_path / "model_benchmark.md"
    rows_path = tmp_path / "model_benchmark_g_rows.csv"
    manifest_path = tmp_path / "model_benchmark_g_manifest.json"
    summary_path = tmp_path / "model_benchmark_g_summary.json"
    assert json_path.exists()
    assert md_path.exists()
    assert rows_path.exists()
    assert manifest_path.exists()
    assert summary_path.exists()

    written = json.loads(json_path.read_text(encoding="utf-8"))
    assert written["summary"]["overall_adequacy_score"] == payload["summary"]["overall_adequacy_score"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["evaluation_target"] == "grounded_role_behavior"
    assert manifest["row_file"] == "model_benchmark_g_rows.csv"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["summary_kind"] == "epistemap_g_experiment_summary"
    assert summary["manifest"]["experiment_id"] == "didactopus-local-model-adequacy"
    assert "evaluation_target" in rows_path.read_text(encoding="utf-8")
    assert "Role Results" in md_path.read_text(encoding="utf-8")


def test_model_benchmark_g_evaluation_rows_describe_grounded_behavior() -> None:
    rows = model_benchmark_g_evaluation_rows(
        {
            "benchmark": {
                "name": "didactopus-local-model-adequacy",
                "provider": "stub",
                "hardware_profile": {"profile_name": "apple-silicon", "cpu": "m3", "ram_gb": 24},
            },
            "context": {"skill_name": "ocw-information-entropy-agent", "output_language": "en"},
            "role_results": [
                {
                    "role": "practice",
                    "provider": "stub",
                    "model_name": "local-model",
                    "adequacy_score": 0.64,
                    "adequacy_rating": "borderline",
                    "grounded_score": 0.7,
                    "multilingual_score": 1.0,
                    "latency_ms": 5.0,
                    "response_preview": "Grounded practice task.",
                }
            ],
        }
    )

    assert rows[0]["y"] == 0
    assert rows[0]["p"] == 0.64
    assert rows[0]["condition"] == "apple-silicon"
    assert rows[0]["evaluation_target"] == "grounded_role_behavior"


def test_model_benchmark_captures_response_preview_and_latency(tmp_path) -> None:
    payload = run_model_benchmark(
        config_path="configs/config.example.yaml",
        skill_dir="skills/ocw-information-entropy-agent",
        out_dir=tmp_path,
    )

    for result in payload["role_results"]:
        assert result["provider"] == "stub"
        assert result["latency_ms"] >= 0.0
        assert result["response_preview"]
        assert "adequacy_score" in result
        assert "round_trip" in result


def test_model_benchmark_penalizes_stub_for_non_english_output(tmp_path) -> None:
    payload = run_model_benchmark(
        config_path="configs/config.example.yaml",
        skill_dir="skills/ocw-information-entropy-agent",
        out_dir=tmp_path,
        language="es",
    )
    assert payload["context"]["output_language"] == "es"
    assert any(result["multilingual_score"] < 1.0 for result in payload["role_results"])
