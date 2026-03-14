from pathlib import Path
from didactopus.pack_validator import validate_pack_directory

def test_valid_pack(tmp_path: Path) -> None:
    (tmp_path / "pack.yaml").write_text("name: p\ndisplay_name: P\nversion: 0.1.0\n", encoding="utf-8")
    (tmp_path / "concepts.yaml").write_text("concepts:\n  - id: c1\n    title: C1\n    description: A full enough description.\n", encoding="utf-8")
    (tmp_path / "roadmap.yaml").write_text("stages:\n  - id: s1\n    title: S1\n    concepts: [c1]\n", encoding="utf-8")
    (tmp_path / "projects.yaml").write_text("projects: []\n", encoding="utf-8")
    (tmp_path / "rubrics.yaml").write_text("rubrics: []\n", encoding="utf-8")
    result = validate_pack_directory(tmp_path)
    assert result["ok"] is True
