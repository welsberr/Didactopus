from __future__ import annotations

import json
from pathlib import Path

from didactopus.groundrecall.export import export_canonical_bundle, export_query_bundle
from didactopus.groundrecall.models import (
    ArtifactRecord,
    ClaimRecord,
    ConceptRecord,
    ObservationRecord,
    ProvenanceRecord,
    RelationRecord,
    SourceRecord,
)
from didactopus.groundrecall.store import GroundRecallStore


def _read_jsonl(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    return [json.loads(line) for line in text.splitlines()]


def _seed_store(store: GroundRecallStore) -> None:
    store.save_source(SourceRecord(source_id="src_001", title="Source", current_status="promoted"))
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


def test_export_canonical_bundle_writes_expected_files(tmp_path: Path) -> None:
    store = GroundRecallStore(tmp_path / "groundrecall")
    _seed_store(store)

    out_dir = tmp_path / "exports"
    payload = export_canonical_bundle(
        store_dir=store.base_dir,
        out_dir=out_dir,
        concept_refs=["channel-capacity"],
        snapshot_id="snap_export_001",
    )

    assert (out_dir / "groundrecall_snapshot.json").exists()
    assert (out_dir / "claims.jsonl").exists()
    assert (out_dir / "concepts.jsonl").exists()
    assert (out_dir / "relations.jsonl").exists()
    assert (out_dir / "provenance_manifest.json").exists()
    assert (out_dir / "export_manifest.json").exists()
    assert (out_dir / "query_bundle__channel-capacity.json").exists()

    snapshot = json.loads((out_dir / "groundrecall_snapshot.json").read_text(encoding="utf-8"))
    manifest = json.loads((out_dir / "export_manifest.json").read_text(encoding="utf-8"))
    claims = _read_jsonl(out_dir / "claims.jsonl")
    assert snapshot["snapshot_id"] == "snap_export_001"
    assert manifest["export_kind"] == "canonical"
    assert len(manifest["query_bundles"]) == 1
    assert claims[0]["claim_id"] == "clm_001"
    assert payload["query_bundles"]


def test_export_query_bundle_is_assistant_neutral(tmp_path: Path) -> None:
    store = GroundRecallStore(tmp_path / "groundrecall")
    _seed_store(store)

    out_path = tmp_path / "bundle.json"
    payload = export_query_bundle(store.base_dir, "channel capacity", out_path)
    assert out_path.exists()
    assert payload["bundle_kind"] == "groundrecall_query_bundle"
    forbidden = {"assistant", "codex", "claude", "prompt_text"}
    assert set(payload).isdisjoint(forbidden)
