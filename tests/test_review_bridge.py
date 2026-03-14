from pathlib import Path
from didactopus.review_bridge import ReviewWorkspaceBridge

def _make_workspace(base: Path):
    draft = base / "draft_pack"
    draft.mkdir(parents=True, exist_ok=True)
    (draft / "pack.yaml").write_text("name: test\nversion: 0.1.0-draft\n", encoding="utf-8")
    (draft / "concepts.yaml").write_text(
        "concepts:\n  - id: c1\n    title: Concept One\n    description: Desc\n    prerequisites: []\n    mastery_signals: []\n",
        encoding="utf-8",
    )
    (draft / "conflict_report.md").write_text("# Conflict Report\n\n- One conflict\n", encoding="utf-8")

def test_bridge_load_and_save(tmp_path: Path) -> None:
    _make_workspace(tmp_path)
    bridge = ReviewWorkspaceBridge(tmp_path, reviewer="R")
    session = bridge.load_session()
    assert session.reviewer == "R"
    bridge.save_session(session)
    assert (tmp_path / "review_session.json").exists()
