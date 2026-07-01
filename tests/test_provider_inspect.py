from pathlib import Path

from didactopus.provider_inspect import inspect_provider


def test_inspect_provider_writes_output(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    payload = inspect_provider(
        root / "configs" / "config.example.yaml",
        kind="chat",
        out_path=tmp_path / "provider_inspect.json",
    )

    assert (tmp_path / "provider_inspect.json").exists()
    assert payload["provider"] == "stub"
    assert payload["kind"] == "chat"
    assert payload["role_model_overrides"] == {}
