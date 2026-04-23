from __future__ import annotations

import json
from pathlib import Path

from didactopus.doclift_bundle_demo import run_doclift_bundle_demo


def test_doclift_bundle_demo_generates_pack(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    doc_dir = bundle / "documents" / "lesson-a"
    doc_dir.mkdir(parents=True)
    (bundle / "manifest.json").write_text(
        json.dumps(
            {
                "documents": [
                    {
                        "title": "Lecture 1. Example",
                        "document_kind": "lecture",
                        "output_dir": str(doc_dir),
                        "layout_path": str(doc_dir / "document.layout.json"),
                        "tables_path": str(doc_dir / "document.tables.json"),
                        "figures_path": str(doc_dir / "document.figures.json"),
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    (doc_dir / "document.md").write_text(
        "# Lecture 1. Example\n\n## Module A\n### Lesson A\n- Objective: Explain lesson A.\nBody text.",
        encoding="utf-8",
    )
    (doc_dir / "document.layout.json").write_text("[]", encoding="utf-8")
    (doc_dir / "document.tables.json").write_text(json.dumps({"source_path": "/tmp/source.doc", "tables": []}), encoding="utf-8")
    (doc_dir / "document.figures.json").write_text(json.dumps({"source_path": "/tmp/source.doc", "figure_references": []}), encoding="utf-8")

    summary = run_doclift_bundle_demo(bundle, "Example Course", tmp_path / "pack")

    assert summary["source_document_count"] == 1
    assert (tmp_path / "pack" / "pack.yaml").exists()
    assert (tmp_path / "pack" / "source_corpus.json").exists()
    assert (tmp_path / "pack" / "knowledge_graph.json").exists()
    assert (tmp_path / "pack" / "doclift_bundle_summary.json").exists()
