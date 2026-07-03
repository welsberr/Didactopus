from __future__ import annotations

import json
from pathlib import Path

from didactopus.citation_extract import run_citations_from_ingest


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


def _make_ensemble_run(tmp_path: Path) -> Path:
    run = tmp_path / "ensemble"
    run.mkdir()
    (run / "manifest.json").write_text(
        json.dumps({"ingest_id": "ensemble-fixture", "counts": {"fragment_count": 2}}),
        encoding="utf-8",
    )
    _write_jsonl(
        run / "sources.jsonl",
        [
            {
                "source_id": "src_fixture",
                "path": "library/example-source.pdf",
                "source_type": "pdf",
            }
        ],
    )
    _write_jsonl(
        run / "fragments.jsonl",
        [
            {
                "fragment_id": "frag_001",
                "source_id": "src_fixture",
                "source_path": "library/example-source.pdf",
                "section": "Main",
                "text": "Selection examples are discussed by Smith (2020) and later reviews (Doe 2021; Roe et al. 2022). DOI 10.1000/example.doi",
            },
            {
                "fragment_id": "frag_002",
                "source_id": "src_fixture",
                "source_path": "library/example-source.pdf",
                "section": "Main",
                "text": "\n".join(
                    [
                        "References",
                        "Smith, J. (2020). Selection examples in context. Journal of Examples, 12, 1-9.",
                        "Doe, A. 2021. Review of evolutionary examples. Example Press.",
                    ]
                ),
            },
        ],
    )
    return run


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_citations_from_ingest_writes_draft_artifacts(tmp_path: Path) -> None:
    run = _make_ensemble_run(tmp_path)
    out_dir = tmp_path / "citations"

    result = run_citations_from_ingest(run, out_dir=out_dir, run_id="citation-fixture", use_citegeist=False)

    assert result.manifest["run_id"] == "citation-fixture"
    assert result.manifest["counts"]["reference_candidate_count"] == 2
    assert result.manifest["counts"]["in_text_citation_count"] >= 3
    assert result.manifest["counts"]["citation_link_count"] >= 5
    assert result.manifest["citegeist"]["status"] == "skipped"

    references = _read_jsonl(out_dir / "reference_candidates.jsonl")
    citations = _read_jsonl(out_dir / "in_text_citations.jsonl")
    links = _read_jsonl(out_dir / "citation_links.jsonl")
    reference_text = (out_dir / "reference_candidates.txt").read_text(encoding="utf-8")

    assert all(row["current_status"] == "draft" for row in references)
    assert any("Selection examples in context" in row["text"] for row in references)
    assert any(row["citation_kind"] == "doi" for row in citations)
    assert any(row["candidate_type"] == "reference_entry" for row in links)
    assert "Smith, J. (2020)" in reference_text


def test_citations_from_ingest_discovers_child_runs(tmp_path: Path) -> None:
    parent = tmp_path / "parent"
    child = parent / "sources" / "child-run"
    child.mkdir(parents=True)
    fixture = _make_ensemble_run(tmp_path)
    for name in ["manifest.json", "sources.jsonl", "fragments.jsonl"]:
        (child / name).write_text((fixture / name).read_text(encoding="utf-8"), encoding="utf-8")

    result = run_citations_from_ingest(parent, out_dir=tmp_path / "out", use_citegeist=False)

    assert result.manifest["processed_run_count"] == 1
    assert result.manifest["counts"]["reference_candidate_count"] == 2
