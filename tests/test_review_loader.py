from pathlib import Path
from didactopus.review_loader import load_draft_pack


def test_load_draft_pack(tmp_path: Path) -> None:
    (tmp_path / "pack.yaml").write_text("name: test\n", encoding="utf-8")
    (tmp_path / "concepts.yaml").write_text(
        "concepts:\n  - id: c1\n    title: Concept One\n    description: Desc\n    prerequisites: []\n    mastery_signals: []\n",
        encoding="utf-8",
    )
    (tmp_path / "conflict_report.md").write_text("# Conflict Report\n\n- One conflict\n", encoding="utf-8")
    data = load_draft_pack(tmp_path)
    assert data.pack["name"] == "test"
    assert len(data.concepts) == 1
    assert len(data.conflicts) == 1
