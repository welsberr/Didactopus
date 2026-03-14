from pathlib import Path
from didactopus.workspace_manager import WorkspaceManager

def test_create_and_get_workspace(tmp_path: Path) -> None:
    mgr = WorkspaceManager(tmp_path / "registry.json", tmp_path / "roots")
    meta = mgr.create_workspace("ws1", "Workspace One")
    assert meta.workspace_id == "ws1"
    got = mgr.get_workspace("ws1")
    assert got is not None
    assert got.title == "Workspace One"

def test_import_draft_pack(tmp_path: Path) -> None:
    src = tmp_path / "srcpack"
    src.mkdir()
    (src / "pack.yaml").write_text("name: x\n", encoding="utf-8")
    (src / "concepts.yaml").write_text("concepts: []\n", encoding="utf-8")
    mgr = WorkspaceManager(tmp_path / "registry.json", tmp_path / "roots")
    meta = mgr.import_draft_pack(src, "ws2", title="Workspace Two")
    assert meta.workspace_id == "ws2"
    assert (tmp_path / "roots" / "ws2" / "draft_pack" / "pack.yaml").exists()
