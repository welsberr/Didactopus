from pathlib import Path

from didactopus.ocw_rolemesh_transcript_demo import _looks_truncated, run_ocw_rolemesh_transcript_demo


def test_looks_truncated_detects_prose_cutoff_before_numbered_list() -> None:
    text = (
        "Suppose we have a binary symmetric channel with crossover\n\n"
        "1. Estimate the error probability.\n"
        "2. Relate it to capacity."
    )
    assert _looks_truncated(text) is True


def test_looks_truncated_detects_common_cutoff_phrase() -> None:
    assert _looks_truncated("Furthermore") is True
    assert _looks_truncated("Compare the entropy of one roll with the") is True


def test_ocw_rolemesh_transcript_demo_writes_artifacts(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    payload = run_ocw_rolemesh_transcript_demo(
        root / "configs" / "config.example.yaml",
        root / "skills" / "ocw-information-entropy-agent",
        tmp_path,
    )

    assert payload["provider"] == "stub"
    assert len(payload["transcript"]) >= 16
    assert len(payload["curriculum_path_titles"]) >= 8
    assert payload["graph_grounding_summary"]["node_count"] >= 1
    assert payload["role_fallbacks"] == {}
    assert payload["status_updates"] == []
    assert any(turn["speaker"] == "Didactopus Evaluator" for turn in payload["transcript"])
    assert any("channel" in turn["content"].lower() for turn in payload["transcript"])
    assert any("thermodynamic" in turn["content"].lower() for turn in payload["transcript"])
    assert any("supporting lessons" in turn["content"].lower() or "grounding fragments" in turn["content"].lower() for turn in payload["transcript"])
    assert all(not _looks_truncated(turn["content"]) for turn in payload["transcript"])
    assert (tmp_path / "rolemesh_transcript.json").exists()
    assert (tmp_path / "rolemesh_transcript.md").exists()
    assert "Pending Status Examples" not in (tmp_path / "rolemesh_transcript.md").read_text(encoding="utf-8")
