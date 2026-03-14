from pathlib import Path
from didactopus.import_validator import preview_draft_pack_import

def test_valid_preview(tmp_path: Path) -> None:
    src = tmp_path / "src"
    src.mkdir()
    (src / "pack.yaml").write_text("name: p\ndisplay_name: P\nversion: 0.1.0\n", encoding="utf-8")
    (src / "concepts.yaml").write_text("concepts: []\n", encoding="utf-8")
    preview = preview_draft_pack_import(src, "ws1")
    assert preview.ok is True
    assert preview.summary["concept_count"] == 0

def test_missing_required_file(tmp_path: Path) -> None:
    src = tmp_path / "src"
    src.mkdir()
    (src / "pack.yaml").write_text("name: p\n", encoding="utf-8")
    preview = preview_draft_pack_import(src, "ws1")
    assert preview.ok is False
    assert any("Missing required file" in e for e in preview.errors)
