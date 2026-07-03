from __future__ import annotations

from pathlib import Path

from didactopus.groundrecall.models import (
    ArtifactRecord,
    ClaimRecord,
    ConceptRecord,
    ObservationRecord,
    ProvenanceRecord,
    RelationRecord,
)
from didactopus.groundrecall.query import (
    build_query_bundle_for_concept,
    query_concept,
    query_provenance,
    search_claims,
)
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
    store.save_claim(
        ClaimRecord(
            claim_id="clm_002",
            claim_text="Shannon entropy can inform channel coding intuition.",
            concept_ids=["concept::shannon-entropy"],
            contradicts_claim_ids=["clm_999"],
            provenance=ProvenanceRecord(
                origin_artifact_id="ia_001",
                origin_path="wiki/channel-capacity.md",
                support_kind="derived_from_page",
                grounding_status="partially_grounded",
            ),
            current_status="reviewed",
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


def test_query_concept_returns_neighborhood_and_support(tmp_path: Path) -> None:
    store = GroundRecallStore(tmp_path / "groundrecall")
    _seed_store(store)

    payload = query_concept(store.base_dir, "channel-capacity")
    assert payload is not None
    assert payload["concept"]["concept_id"] == "concept::channel-capacity"
    assert len(payload["claims"]) == 1
    assert len(payload["relations"]) == 1
    assert any(item["concept_id"] == "concept::shannon-entropy" for item in payload["related_concepts"])
    assert payload["supporting_observations"][0]["origin_path"] == "wiki/channel-capacity.md"


def test_search_claims_matches_text_and_concept_titles(tmp_path: Path) -> None:
    store = GroundRecallStore(tmp_path / "groundrecall")
    _seed_store(store)

    payload = search_claims(store.base_dir, "entropy")
    assert payload["query_type"] == "claim_search"
    assert any(match["claim"]["claim_id"] == "clm_002" for match in payload["matches"])


def test_query_provenance_filters_by_origin_path(tmp_path: Path) -> None:
    store = GroundRecallStore(tmp_path / "groundrecall")
    _seed_store(store)

    payload = query_provenance(store.base_dir, origin_path="wiki/channel-capacity.md")
    assert len(payload["claims"]) == 2
    assert len(payload["observations"]) == 1


def test_build_query_bundle_for_concept_is_assistant_neutral(tmp_path: Path) -> None:
    store = GroundRecallStore(tmp_path / "groundrecall")
    _seed_store(store)

    payload = build_query_bundle_for_concept(store.base_dir, "channel capacity")
    assert payload is not None
    assert payload["bundle_kind"] == "groundrecall_query_bundle"
    assert payload["concept"]["concept_id"] == "concept::channel-capacity"
    assert isinstance(payload["suggested_next_actions"], list)
    forbidden = {"assistant", "codex", "claude", "prompt_text"}
    assert set(payload).isdisjoint(forbidden)


def test_query_bundle_surfaces_contradictions_and_supersessions(tmp_path: Path) -> None:
    store = GroundRecallStore(tmp_path / "groundrecall")
    _seed_store(store)
    store.save_claim(
        ClaimRecord(
            claim_id="clm_003",
            claim_text="Channel capacity is undefined in practice.",
            concept_ids=["concept::channel-capacity"],
            contradicts_claim_ids=["clm_001"],
            provenance=ProvenanceRecord(
                origin_artifact_id="ia_001",
                origin_path="wiki/channel-capacity.md",
                support_kind="derived_from_page",
                grounding_status="partially_grounded",
            ),
            current_status="reviewed",
        )
    )
    store.save_claim(
        ClaimRecord(
            claim_id="clm_004",
            claim_text="Channel capacity should be interpreted relative to a specific channel model.",
            concept_ids=["concept::channel-capacity"],
            supersedes_claim_ids=["clm_001"],
            provenance=ProvenanceRecord(
                origin_artifact_id="ia_001",
                origin_path="wiki/channel-capacity.md",
                support_kind="derived_from_page",
                grounding_status="grounded",
            ),
            current_status="reviewed",
        )
    )

    payload = build_query_bundle_for_concept(store.base_dir, "channel-capacity")
    assert payload is not None
    contradiction_ids = {item["claim_id"] for item in payload["contradictions"]}
    supersession_ids = {item["claim_id"] for item in payload["supersessions"]}
    assert "clm_003" in contradiction_ids
    assert "clm_004" in supersession_ids
