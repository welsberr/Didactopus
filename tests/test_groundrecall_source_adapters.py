from __future__ import annotations

from pathlib import Path

import didactopus.groundrecall.source_adapters  # noqa: F401
from didactopus.groundrecall.source_adapters.base import detect_source_adapter, list_source_adapters
from didactopus.groundrecall.ingest import run_groundrecall_import


def test_groundrecall_source_adapter_registry_lists_expected_adapters() -> None:
    names = set(list_source_adapters())
    assert "llmwiki" in names
    assert "markdown_notes" in names
    assert "transcript" in names
    assert "didactopus_pack" in names


def test_detect_llmwiki_adapter(tmp_path: Path) -> None:
    (tmp_path / "wiki").mkdir()
    adapter = detect_source_adapter(tmp_path)
    assert adapter.name == "llmwiki"
    assert adapter.import_intent() == "grounded_knowledge"


def test_detect_didactopus_pack_adapter(tmp_path: Path) -> None:
    (tmp_path / "pack.yaml").write_text("name: p\n", encoding="utf-8")
    (tmp_path / "concepts.yaml").write_text("concepts: []\n", encoding="utf-8")
    adapter = detect_source_adapter(tmp_path)
    assert adapter.name == "didactopus_pack"
    assert adapter.import_intent() == "both"


def test_groundrecall_import_records_adapter_and_intent(tmp_path: Path) -> None:
    (tmp_path / "wiki").mkdir()
    (tmp_path / "wiki" / "note.md").write_text("# Title\n\n- A note.\n", encoding="utf-8")
    result = run_groundrecall_import(tmp_path, mode="quick", import_id="adapter-test")
    assert result.manifest["source_adapter"] == "llmwiki"
    assert result.manifest["import_intent"] == "grounded_knowledge"


def test_didactopus_pack_import_generates_structured_concepts_and_relations(tmp_path: Path) -> None:
    (tmp_path / "pack.yaml").write_text(
        "\n".join(
            [
                "name: sample-pack",
                "display_name: Sample Pack",
                "version: 0.1.0",
                "schema_version: 0.1.0",
                "didactopus_min_version: 0.1.0",
                "didactopus_max_version: 9.9.9",
            ]
        ),
        encoding="utf-8",
    )
    (tmp_path / "concepts.yaml").write_text(
        "\n".join(
            [
                "concepts:",
                "  - id: basics",
                "    title: Basics",
                "    description: Foundational concept.",
                "    mastery_signals: [Explain the foundation.]",
                "  - id: advanced",
                "    title: Advanced",
                "    description: Builds on basics.",
                "    prerequisites: [basics]",
            ]
        ),
        encoding="utf-8",
    )
    (tmp_path / "roadmap.yaml").write_text(
        "\n".join(
            [
                "stages:",
                "  - id: stage1",
                "    title: Stage One",
                "    concepts: [basics, advanced]",
            ]
        ),
        encoding="utf-8",
    )

    result = run_groundrecall_import(tmp_path, mode="quick", import_id="pack-test")
    assert result.manifest["source_adapter"] == "didactopus_pack"
    assert result.manifest["import_intent"] == "both"
    concept_ids = {item["concept_id"] for item in result.concepts}
    assert "concept::basics" in concept_ids
    assert "concept::advanced" in concept_ids
    relation_targets = {(item["source_id"], item["target_id"], item["relation_type"]) for item in result.relations}
    assert ("concept::basics", "concept::advanced", "prerequisite") in relation_targets
    claim_ids = {item["claim_id"] for item in result.claims}
    assert "clm_pack_basics" in claim_ids
    assert "clm_stage_stage1_basics" in claim_ids
