from __future__ import annotations

import json
from pathlib import Path
import shutil

from didactopus.doclift_bundle_demo import run_doclift_bundle_demo


def _fixture_bundle() -> Path:
    return Path(__file__).parent / "fixtures" / "doclift_bundle_minimal"


def test_doclift_bundle_demo_generates_pack(tmp_path: Path) -> None:
    summary = run_doclift_bundle_demo(_fixture_bundle(), "Example Course", tmp_path / "pack")

    assert summary["source_document_count"] == 1
    assert (tmp_path / "pack" / "pack.yaml").exists()
    assert (tmp_path / "pack" / "source_corpus.json").exists()
    assert (tmp_path / "pack" / "knowledge_graph.json").exists()
    assert (tmp_path / "pack" / "doclift_bundle_summary.json").exists()


def test_doclift_bundle_demo_carries_groundrecall_query_bundle(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    shutil.copytree(_fixture_bundle(), bundle_dir)
    (bundle_dir / "groundrecall_query_bundle.json").write_text(
        json.dumps(
            {
                "bundle_kind": "groundrecall_query_bundle",
                "concept": {"concept_id": "concept::lecture-1", "title": "Lecture 1"},
                "review_candidates": [{"candidate_id": "concept::lecture-1", "rationale": "Lecture 1 | lane=knowledge_capture | priority=20"}],
            }
        ),
        encoding="utf-8",
    )

    summary = run_doclift_bundle_demo(bundle_dir, "Example Course", tmp_path / "pack")

    assert summary["groundrecall_bundle_included"] is True
    assert (tmp_path / "pack" / "groundrecall_query_bundle.json").exists()
