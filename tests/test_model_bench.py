import json

from didactopus.model_bench import run_model_benchmark


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

    json_path = tmp_path / "model_benchmark.json"
    md_path = tmp_path / "model_benchmark.md"
    assert json_path.exists()
    assert md_path.exists()

    written = json.loads(json_path.read_text(encoding="utf-8"))
    assert written["summary"]["overall_adequacy_score"] == payload["summary"]["overall_adequacy_score"]
    assert "Role Results" in md_path.read_text(encoding="utf-8")


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
