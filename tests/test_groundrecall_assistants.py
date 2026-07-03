from __future__ import annotations

import json
from pathlib import Path

from didactopus.groundrecall.assistant_export import export_assistant_bundle
from didactopus.groundrecall.assistants.base import get_assistant_adapter, list_assistant_adapters
import didactopus.groundrecall.assistants.codex  # noqa: F401
import didactopus.groundrecall.assistants.claude_code  # noqa: F401
from didactopus.groundrecall.models import (
    ArtifactRecord,
    ClaimRecord,
    ConceptRecord,
    ObservationRecord,
    ProvenanceRecord,
    RelationRecord,
)
from didactopus.groundrecall.query import build_query_bundle_for_concept
from didactopus.groundrecall.store import GroundRecallStore


def _seed_store(store: GroundRecallStore) -> None:
    store.save_artifact(
        ArtifactRecord(
            artifact_id="ia_001",
            artifact_kind="compiled_page",
            title="Channel Capacity",
            path="wiki/channel-capacity.md",
            current_status="reviewed",
        )
    )
    store.save_observation(
        ObservationRecord(
            observation_id="obs_001",
            artifact_id="ia_001",
            role="claim",
            text="Reliable communication rate is bounded by channel capacity.",
            provenance=ProvenanceRecord(
                origin_artifact_id="ia_001",
                origin_path="wiki/channel-capacity.md",
                support_kind="derived_from_page",
                grounding_status="grounded",
            ),
            current_status="reviewed",
        )
    )
    store.save_concept(
        ConceptRecord(
            concept_id="concept::channel-capacity",
            title="Channel Capacity",
            description="Reliable communication limit.",
            source_artifact_ids=["ia_001"],
            current_status="promoted",
        )
    )
    store.save_concept(
        ConceptRecord(
            concept_id="concept::shannon-entropy",
            title="Shannon Entropy",
            description="Average uncertainty.",
            current_status="promoted",
        )
    )
    store.save_claim(
        ClaimRecord(
            claim_id="clm_001",
            claim_text="Channel capacity bounds reliable communication rate.",
            concept_ids=["concept::channel-capacity"],
            source_observation_ids=["obs_001"],
            confidence_hint=0.8,
            review_confidence=0.9,
            provenance=ProvenanceRecord(
                origin_artifact_id="ia_001",
                origin_path="wiki/channel-capacity.md",
                support_kind="derived_from_page",
                grounding_status="grounded",
            ),
            current_status="promoted",
        )
    )
    store.save_relation(
        RelationRecord(
            relation_id="rel_001",
            source_id="concept::channel-capacity",
            target_id="concept::shannon-entropy",
            relation_type="references",
            current_status="promoted",
        )
    )


def test_assistant_adapter_registry_lists_known_adapters() -> None:
    assert "codex" in list_assistant_adapters()
    assert "claude_code" in list_assistant_adapters()


def test_codex_adapter_exports_skill_and_json_bundle(tmp_path: Path) -> None:
    store = GroundRecallStore(tmp_path / "groundrecall")
    _seed_store(store)
    manifest = export_assistant_bundle(store.base_dir, "codex", tmp_path / "codex", concept_refs=["channel-capacity"])

    assert (tmp_path / "codex" / "SKILL.md").exists()
    assert (tmp_path / "codex" / "codex_bundle.json").exists()
    assert (tmp_path / "codex" / "assistant_export_manifest.json").exists()
    assert manifest["assistant"] == "codex"


def test_claude_code_adapter_exports_memory_and_json_bundle(tmp_path: Path) -> None:
    store = GroundRecallStore(tmp_path / "groundrecall")
    _seed_store(store)
    manifest = export_assistant_bundle(store.base_dir, "claude_code", tmp_path / "claude", concept_refs=["channel-capacity"])

    assert (tmp_path / "claude" / "CLAUDE.md").exists()
    assert (tmp_path / "claude" / "claude_code_bundle.json").exists()
    assert manifest["assistant"] == "claude_code"


def test_adapter_contexts_are_derived_from_assistant_neutral_query_bundles(tmp_path: Path) -> None:
    store = GroundRecallStore(tmp_path / "groundrecall")
    _seed_store(store)
    query_bundle = build_query_bundle_for_concept(store.base_dir, "channel-capacity")
    assert query_bundle is not None

    codex = get_assistant_adapter("codex")
    claude = get_assistant_adapter("claude_code")
    codex_context = codex.build_context(query_bundle)
    claude_context = claude.build_context(query_bundle)

    assert codex_context["concept"]["concept_id"] == "concept::channel-capacity"
    assert claude_context["concept"]["concept_id"] == "concept::channel-capacity"
    assert codex_context["assistant"] == "codex"
    assert claude_context["assistant"] == "claude_code"
    assert "relevant_claims" in codex_context
    assert "claims" in claude_context
