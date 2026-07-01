from pathlib import Path

from didactopus.ocw_provider_transcript_demo import run_ocw_provider_transcript_demo
from didactopus.ocw_rolemesh_transcript_demo import _looks_truncated


def test_ocw_provider_transcript_demo_writes_artifacts(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    payload = run_ocw_provider_transcript_demo(
        root / "configs" / "config.example.yaml",
        root / "skills" / "ocw-information-entropy-agent",
        tmp_path,
    )

    assert payload["provider"] == "stub"
    assert len(payload["transcript"]) >= 16
    assert payload["model_fallbacks"] == {}
    assert payload["role_fallbacks"] == {}
    assert payload["provider_diagnostics"]["provider"] == "stub"
    assert payload["provider_diagnostics"]["role_model_overrides"] == {}
    assert (tmp_path / "provider_transcript.json").exists()
    assert (tmp_path / "provider_transcript.md").exists()
    assert all(not _looks_truncated(turn["content"]) for turn in payload["transcript"])
