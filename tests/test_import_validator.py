from pathlib import Path
from didactopus.import_validator import preview_draft_pack_import

def test_preview_includes_graph_warnings(tmp_path: Path) -> None:
    (tmp_path / "pack.yaml").write_text("name: p\ndisplay_name: P\nversion: 0.1.0\n", encoding="utf-8")
    (tmp_path / "concepts.yaml").write_text(
        "concepts:\n  - id: a\n    title: A\n    description: description long enough\n    prerequisites: [b]\n  - id: b\n    title: B\n    description: description long enough\n    prerequisites: [a]\n",
        encoding="utf-8"
    )
    (tmp_path / "roadmap.yaml").write_text("stages:\n  - id: s1\n    title: One\n    concepts: [a,b]\n", encoding="utf-8")
    (tmp_path / "projects.yaml").write_text("projects: []\n", encoding="utf-8")
    (tmp_path / "rubrics.yaml").write_text("rubrics: []\n", encoding="utf-8")
    preview = preview_draft_pack_import(tmp_path, "ws1")
    assert isinstance(preview.graph_warnings, list)
