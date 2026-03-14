from pathlib import Path
from didactopus.workspace_manager import WorkspaceManager

def make_valid_pack(src: Path):
    src.mkdir()
    (src / "pack.yaml").write_text("name: x\ndisplay_name: X\nversion: 0.1.0\n", encoding="utf-8")
    (src / "concepts.yaml").write_text("concepts:\n  - id: c1\n    title: C1\n    description: A full enough description.\n", encoding="utf-8")
    (src / "roadmap.yaml").write_text("stages: []\n", encoding="utf-8")
    (src / "projects.yaml").write_text("projects: []\n", encoding="utf-8")
    (src / "rubrics.yaml").write_text("rubrics: []\n", encoding="utf-8")

def test_import_preview_and_overwrite_warning(tmp_path: Path) -> None:
    src = tmp_path / "srcpack"
    make_valid_pack(src)
    mgr = WorkspaceManager(tmp_path / "registry.json", tmp_path / "roots")
    mgr.create_workspace("ws2", "Workspace Two")
    preview = mgr.preview_import(src, "ws2")
    assert preview.overwrite_required is True

def test_import_draft_pack_requires_overwrite_flag(tmp_path: Path) -> None:
    src = tmp_path / "srcpack"
    make_valid_pack(src)
    mgr = WorkspaceManager(tmp_path / "registry.json", tmp_path / "roots")
    mgr.create_workspace("ws2", "Workspace Two")
    try:
        mgr.import_draft_pack(src, "ws2", title="Workspace Two", allow_overwrite=False)
        assert False, "Expected FileExistsError"
    except FileExistsError:
        assert True
