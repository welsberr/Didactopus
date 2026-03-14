from pathlib import Path
from didactopus.workspace_manager import WorkspaceManager

def test_create_and_get_workspace(tmp_path: Path) -> None:
    mgr = WorkspaceManager(tmp_path / "registry.json", tmp_path / "roots")
    meta = mgr.create_workspace("ws1", "Workspace One")
    assert meta.workspace_id == "ws1"
    got = mgr.get_workspace("ws1")
    assert got is not None
    assert got.title == "Workspace One"

def test_recent_tracking(tmp_path: Path) -> None:
    mgr = WorkspaceManager(tmp_path / "registry.json", tmp_path / "roots")
    mgr.create_workspace("ws1", "Workspace One")
    mgr.touch_recent("ws1")
    reg = mgr.list_workspaces()
    assert reg.recent_workspace_ids[0] == "ws1"
