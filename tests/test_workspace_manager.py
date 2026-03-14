from pathlib import Path
from didactopus.workspace_manager import WorkspaceManager

def test_import_preview_and_overwrite_warning(tmp_path: Path) -> None:
    src = tmp_path / "srcpack"
    src.mkdir()
    (src / "pack.yaml").write_text("name: x\ndisplay_name: X\nversion: 0.1.0\n", encoding="utf-8")
    (src / "concepts.yaml").write_text("concepts: []\n", encoding="utf-8")
    mgr = WorkspaceManager(tmp_path / "registry.json", tmp_path / "roots")
    mgr.create_workspace("ws2", "Workspace Two")
    preview = mgr.preview_import(src, "ws2")
    assert preview.overwrite_required is True

def test_import_draft_pack_requires_overwrite_flag(tmp_path: Path) -> None:
    src = tmp_path / "srcpack"
    src.mkdir()
    (src / "pack.yaml").write_text("name: x\ndisplay_name: X\nversion: 0.1.0\n", encoding="utf-8")
    (src / "concepts.yaml").write_text("concepts: []\n", encoding="utf-8")
    mgr = WorkspaceManager(tmp_path / "registry.json", tmp_path / "roots")
    mgr.create_workspace("ws2", "Workspace Two")
    try:
        mgr.import_draft_pack(src, "ws2", title="Workspace Two", allow_overwrite=False)
        assert False, "Expected FileExistsError"
    except FileExistsError:
        assert True
