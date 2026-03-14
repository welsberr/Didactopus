from pathlib import Path
from didactopus.import_validator import preview_draft_pack_import

def test_valid_preview(tmp_path: Path) -> None:
    (tmp_path / "pack.yaml").write_text("name: p\ndisplay_name: P\nversion: 0.1.0\n", encoding="utf-8")
    (tmp_path / "concepts.yaml").write_text("concepts:\n  - id: c1\n    title: C1\n    description: A full enough description.\n", encoding="utf-8")
    (tmp_path / "roadmap.yaml").write_text("stages: []\n", encoding="utf-8")
    (tmp_path / "projects.yaml").write_text("projects: []\n", encoding="utf-8")
    (tmp_path / "rubrics.yaml").write_text("rubrics: []\n", encoding="utf-8")
    preview = preview_draft_pack_import(tmp_path, "ws1")
    assert preview.ok is True
    assert preview.summary["concept_count"] == 1

def test_missing_required_file(tmp_path: Path) -> None:
    (tmp_path / "pack.yaml").write_text("name: p\n", encoding="utf-8")
    preview = preview_draft_pack_import(tmp_path, "ws1")
    assert preview.ok is False
