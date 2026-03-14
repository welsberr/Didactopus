from pathlib import Path
from didactopus.import_validator import preview_draft_pack_import

def test_preview_includes_path_warnings(tmp_path: Path) -> None:
    (tmp_path / "pack.yaml").write_text("name: p\ndisplay_name: P\nversion: 0.1.0\n", encoding="utf-8")
    (tmp_path / "concepts.yaml").write_text("concepts:\n  - id: c1\n    title: Foundations\n    description: foundations description enough\n    prerequisites: []\n", encoding="utf-8")
    (tmp_path / "roadmap.yaml").write_text("stages:\n  - id: s1\n    title: One\n    concepts: [c1]\n    checkpoint: []\n", encoding="utf-8")
    (tmp_path / "projects.yaml").write_text("projects: []\n", encoding="utf-8")
    (tmp_path / "rubrics.yaml").write_text("rubrics: []\n", encoding="utf-8")
    preview = preview_draft_pack_import(tmp_path, "ws1")
    assert isinstance(preview.path_warnings, list)
