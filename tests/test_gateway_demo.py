from pathlib import Path

from didactopus.gateway_demo import run_gateway_demo


def test_run_gateway_demo_writes_output(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    payload = run_gateway_demo(
        root / "configs" / "config.example.yaml",
        tmp_path / "gateway_demo.json",
    )

    assert (tmp_path / "gateway_demo.json").exists()
    assert payload["provider"] == "stub"
    assert payload["provider_diagnostics"]["provider"] == "stub"
    assert payload["provider_diagnostics"]["role_model_overrides"] == {}
    assert "mentor" in payload["mentor_prompt"]
