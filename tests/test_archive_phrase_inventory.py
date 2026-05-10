from __future__ import annotations

import json
from pathlib import Path

from didactopus.archive_phrase_inventory import build_archive_phrase_inventory
from didactopus.archive_phrase_inventory import write_archive_phrase_inventory_report


def test_build_archive_phrase_inventory_prioritizes_repeated_seeded_distinctions(tmp_path: Path) -> None:
    docs = tmp_path / "bundle" / "documents"
    (docs / "intro").mkdir(parents=True)
    (docs / "drift").mkdir(parents=True)
    (docs / "intro" / "document.md").write_text(
        "# Introduction to Evolutionary Biology\n\n"
        "Natural selection is not identical to genetic drift. "
        "Common descent refers to the branching history of populations.\n"
    )
    (docs / "drift" / "document.md").write_text(
        "# Drift and Selection\n\n"
        "Genetic drift can change allele frequencies. "
        "Natural selection and genetic drift should be distinguished in explanation.\n"
    )

    report = build_archive_phrase_inventory(
        [tmp_path / "bundle"],
        seed_terms=["natural selection", "genetic drift", "common descent"],
        top_n=10,
    )

    phrases = [item["phrase"] for item in report["prioritized_concepts"]]
    assert "natural selection" in phrases
    assert "genetic drift" in phrases
    row = next(item for item in report["prioritized_concepts"] if item["phrase"] == "genetic drift")
    assert row["seed_match"] is True
    assert row["translation_priority"] is True
    assert row["document_count"] >= 2


def test_write_archive_phrase_inventory_report_writes_json_and_markdown(tmp_path: Path) -> None:
    source = tmp_path / "notes.md"
    source.write_text(
        "# Heritable Change\n\n"
        "Phenotypic plasticity does not by itself imply heritable evolutionary change.\n"
    )
    out = tmp_path / "report.json"
    summary = write_archive_phrase_inventory_report(
        [source],
        out,
        seed_terms=["phenotypic plasticity"],
        top_n=5,
    )

    assert out.exists()
    assert out.with_suffix(".md").exists()
    payload = json.loads(out.read_text())
    assert payload["summary"]["document_count"] == 1
    assert summary["summary"]["distinct_phrase_count"] >= 1


def test_bundle_control_files_are_skipped(tmp_path: Path) -> None:
    bundle = tmp_path / "augmentation"
    snippets = bundle / "snippets"
    snippets.mkdir(parents=True)
    (bundle / "bundle.yaml").write_text("title: test\n")
    (snippets / "concept-alignment.yaml").write_text("items: []\n")
    (snippets / "plasticity.md").write_text(
        "# Plasticity\n\nPlasticity can mislead evolutionary inference if heredity is not checked.\n"
    )

    report = build_archive_phrase_inventory([bundle], top_n=10)
    assert report["summary"]["document_count"] == 1
    phrases = [item["phrase"] for item in report["prioritized_concepts"]]
    assert any("plasticity" in phrase or "evolutionary inference" in phrase for phrase in phrases)
