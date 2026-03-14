from pathlib import Path
from didactopus.import_validator import preview_draft_pack_import

def test_preview_includes_semantic_warnings(tmp_path: Path) -> None:
    (tmp_path / "pack.yaml").write_text("name: p\ndisplay_name: P\nversion: 0.1.0\n", encoding="utf-8")
    (tmp_path / "concepts.yaml").write_text(
        "concepts:\n  - id: c1\n    title: Prior and Posterior\n    description: Beliefs before and after evidence.\n  - id: c2\n    title: Posterior Analysis\n    description: Beliefs before and after evidence.\n",
        encoding="utf-8"
    )
    (tmp_path / "roadmap.yaml").write_text("stages:\n  - id: s1\n    title: Foundations\n    concepts: [c1]\n  - id: s2\n    title: Advanced Inference\n    concepts: [c2]\n", encoding="utf-8")
    (tmp_path / "projects.yaml").write_text("projects: []\n", encoding="utf-8")
    (tmp_path / "rubrics.yaml").write_text("rubrics: []\n", encoding="utf-8")
    preview = preview_draft_pack_import(tmp_path, "ws1")
    assert isinstance(preview.semantic_warnings, list)
