from __future__ import annotations

import json
from pathlib import Path

import didactopus.ensemble_ingest as ensemble_ingest
from didactopus.ensemble_ingest import discover_ensemble_sources, run_ensemble_ingest


def _read_jsonl(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    return [json.loads(line) for line in text.splitlines()]


def test_ensemble_ingest_continues_after_source_error(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "a.md").write_text(
        "# First Topic\n\n"
        "- First claim because the source says so.\n"
        "What evidence is missing?\n",
        encoding="utf-8",
    )
    (source / "bad.txt").write_bytes(b"\xff\xfe\x00\x00")
    (source / "c.md").write_text(
        "# Later Topic\n\n"
        "- Later claim proves ingestion reached the final file.\n",
        encoding="utf-8",
    )

    original_adapt_document = ensemble_ingest.adapt_document

    def fail_for_bad_source(path, *args, **kwargs):
        if Path(path).name == "bad.txt":
            raise UnicodeDecodeError("utf-8", b"\xff", 0, 1, "forced test failure")
        return original_adapt_document(path, *args, **kwargs)

    monkeypatch.setattr(ensemble_ingest, "adapt_document", fail_for_bad_source)

    result = run_ensemble_ingest(
        source_root=source,
        out_dir=tmp_path / "out",
        ingest_id="ensemble-test",
        checkpoint_every="chunk",
        max_chunk_chars=400,
    )

    manifest = result.manifest
    assert manifest["non_interactive"] is True
    assert manifest["stop_policy"] == "never_block_on_extracted_claim_or_concept"
    assert manifest["counts"]["source_count"] == 3
    assert manifest["counts"]["processed_source_count"] == 2
    assert manifest["counts"]["failed_source_count"] == 1
    assert manifest["errors"]

    claims = _read_jsonl(result.out_dir / "claims.jsonl")
    assert any("First claim" in claim["claim_text"] for claim in claims)
    assert any("Later claim" in claim["claim_text"] for claim in claims)

    sources = _read_jsonl(result.out_dir / "sources.jsonl")
    assert {source_row["path"] for source_row in sources} == {"a.md", "bad.txt", "c.md"}
    assert all(not Path(source_row["path"]).is_absolute() for source_row in sources)

    review_queue = json.loads((result.out_dir / "review_queue.json").read_text(encoding="utf-8"))
    assert review_queue["queue_length"] >= len(claims)
    assert any(item["candidate_type"] == "claim" for item in review_queue["items"])
    assert any(item["candidate_type"] == "observation" for item in review_queue["items"])

    checkpoint = json.loads((result.out_dir / "checkpoint.json").read_text(encoding="utf-8"))
    assert checkpoint["completed"] is True
    checkpoints = _read_jsonl(result.out_dir / "checkpoints.jsonl")
    assert any(item["event"] == "source_error" and item["source_path"] == "bad.txt" for item in checkpoints)
    assert any(item["event"] == "chunk_processed" and item["source_path"] == "c.md" for item in checkpoints)


def test_discover_ensemble_sources_skips_output_tree(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "lesson.md").write_text("# Lesson\n", encoding="utf-8")
    out_dir = source / "out"
    out_dir.mkdir()
    (out_dir / "generated.md").write_text("# Generated\n", encoding="utf-8")

    paths = discover_ensemble_sources(source, out_dir=out_dir)

    assert paths == [source / "lesson.md"]
