from __future__ import annotations

from pathlib import Path

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
