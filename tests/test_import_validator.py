from pathlib import Path
from didactopus.import_validator import preview_draft_pack_import

def test_preview_includes_ledger_warnings(tmp_path: Path) -> None:
    (tmp_path / "pack.yaml").write_text("name: p\ndisplay_name: P\nversion: 0.1.0\n", encoding="utf-8")
    (tmp_path / "concepts.yaml").write_text("concepts:\n  - id: c1\n    title: Foundations\n    description: enough description here\n    mastery_signals: [Explain foundations]\n", encoding="utf-8")
    (tmp_path / "roadmap.yaml").write_text("stages:\n  - id: s1\n    title: One\n    concepts: [c1]\n    checkpoint: [oral discussion]\n", encoding="utf-8")
    (tmp_path / "projects.yaml").write_text("projects:\n  - id: p1\n    title: Project\n    prerequisites: [c1]\n    deliverables: [memo]\n", encoding="utf-8")
    (tmp_path / "rubrics.yaml").write_text("rubrics:\n  - id: r1\n    title: Style\n    criteria: [formatting]\n", encoding="utf-8")
    (tmp_path / "evaluator.yaml").write_text("dimensions:\n  - name: typography\n    description: page polish\n", encoding="utf-8")
    (tmp_path / "mastery_ledger.yaml").write_text("entry_schema:\n  concept_id: str\n  score: float\n", encoding="utf-8")
    preview = preview_draft_pack_import(tmp_path, "ws1")
    assert isinstance(preview.ledger_warnings, list)
