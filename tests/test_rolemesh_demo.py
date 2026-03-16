from pathlib import Path

from didactopus.rolemesh_demo import run_rolemesh_demo


def test_run_rolemesh_demo_writes_output(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    payload = run_rolemesh_demo(
        root / "configs" / "config.example.yaml",
        tmp_path / "rolemesh_demo.json",
    )

    assert (tmp_path / "rolemesh_demo.json").exists()
    assert payload["provider"] == "stub"
    assert "mentor" in payload["mentor_prompt"]
