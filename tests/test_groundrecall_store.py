from __future__ import annotations

from pathlib import Path

from didactopus.groundrecall.models import (
    ClaimRecord,
    ConceptRecord,
    GroundRecallSnapshot,
    PromotionRecord,
    ProvenanceRecord,
    RelationRecord,
    ReviewCandidateRecord,
    SourceRecord,
)
from didactopus.groundrecall.store import GroundRecallStore


def test_groundrecall_store_round_trips_canonical_objects(tmp_path: Path) -> None:
    store = GroundRecallStore(tmp_path / "groundrecall")

    source = store.save_source(
        SourceRecord(
            source_id="src_001",
            title="Channel Notes",
            source_type="markdown",
            path="wiki/channel-capacity.md",
            current_status="promoted",
        )
    )
    claim = store.save_claim(
        ClaimRecord(
            claim_id="clm_001",
            claim_text="Channel capacity bounds reliable communication rate.",
            claim_kind="definition",
            concept_ids=["concept::channel-capacity"],
            confidence_hint=0.72,
            provenance=ProvenanceRecord(
                origin_artifact_id="ia_001",
                origin_path="wiki/channel-capacity.md",
                support_kind="derived_from_page",
                grounding_status="partially_grounded",
            ),
            current_status="reviewed",
        )
    )
    concept = store.save_concept(
        ConceptRecord(
            concept_id="concept::channel-capacity",
            title="Channel Capacity",
            description="Imported concept.",
            current_status="promoted",
        )
    )
    relation = store.save_relation(
        RelationRecord(
            relation_id="rel_001",
            source_id="concept::channel-capacity",
            target_id="concept::shannon-entropy",
            relation_type="references",
            current_status="draft",
        )
    )
    review_candidate = store.save_review_candidate(
        ReviewCandidateRecord(
            review_candidate_id="rc_001",
            candidate_type="claim",
            candidate_id="clm_001",
            triage_lane="knowledge_capture",
            priority=10,
            current_status="triaged",
        )
    )
    promotion = store.save_promotion(
        PromotionRecord(
            promotion_id="pr_001",
            candidate_type="claim",
            candidate_id="clm_001",
            reviewer="R",
            promoted_object_ids=["clm_001"],
            promoted_at="2026-04-17T12:00:00Z",
        )
    )

    assert store.get_source(source.source_id) is not None
    assert store.get_claim(claim.claim_id) is not None
    assert store.get_concept(concept.concept_id) is not None
    assert store.get_relation(relation.relation_id) is not None
    assert store.get_review_candidate(review_candidate.review_candidate_id) is not None
    assert store.get_promotion(promotion.promotion_id) is not None


def test_groundrecall_store_builds_and_persists_snapshot(tmp_path: Path) -> None:
    store = GroundRecallStore(tmp_path / "groundrecall")
    store.save_source(SourceRecord(source_id="src_001", title="T", current_status="promoted"))
    store.save_claim(
        ClaimRecord(
            claim_id="clm_001",
            claim_text="A grounded claim.",
            concept_ids=["concept::c1"],
            current_status="promoted",
        )
    )
    store.save_concept(ConceptRecord(concept_id="concept::c1", title="C1", current_status="promoted"))

    snapshot = store.build_snapshot(
        snapshot_id="snap_001",
        created_at="2026-04-17T12:00:00Z",
        metadata={"export_kind": "canonical"},
    )
    saved = store.save_snapshot(snapshot)

    loaded = store.get_snapshot(saved.snapshot_id)
    assert loaded is not None
    assert isinstance(loaded, GroundRecallSnapshot)
    assert loaded.metadata["export_kind"] == "canonical"
    assert len(loaded.sources) == 1
    assert len(loaded.claims) == 1
    assert len(loaded.concepts) == 1


def test_groundrecall_models_remain_assistant_neutral() -> None:
    claim_fields = set(ClaimRecord.model_fields)
    concept_fields = set(ConceptRecord.model_fields)
    snapshot_fields = set(GroundRecallSnapshot.model_fields)
    forbidden = {"assistant", "assistant_name", "codex", "claude", "skill_bundle", "prompt_text"}

    assert claim_fields.isdisjoint(forbidden)
    assert concept_fields.isdisjoint(forbidden)
    assert snapshot_fields.isdisjoint(forbidden)
