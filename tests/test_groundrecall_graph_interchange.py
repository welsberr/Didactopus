from __future__ import annotations

import json
from pathlib import Path

import pytest

from didactopus.graph_retrieval import (
    claims_for_concept,
    concept_neighborhood,
    evidence_fragments_for_concept,
    get_concept_node,
    graph_quality_summary,
    load_groundrecall_graph_interchange,
)


def _interchange_bundle() -> dict:
    return {
        "bundle_kind": "groundrecall_graph_interchange",
        "schema_version": "groundrecall.graph_interchange.v1",
        "snapshot_id": "snap-test",
        "created_at": "2026-07-01T00:00:00Z",
        "nodes": [
            {
                "node_id": "concept::channel-capacity",
                "node_kind": "concept",
                "title": "Channel Capacity",
                "description": "Reliable communication limit.",
                "aliases": [],
                "source_artifact_ids": ["art_001"],
                "status": "promoted",
            },
            {
                "node_id": "concept::shannon-entropy",
                "node_kind": "concept",
                "title": "Shannon Entropy",
                "description": "Average uncertainty.",
                "aliases": [],
                "source_artifact_ids": ["art_001"],
                "status": "promoted",
            },
        ],
        "edges": [
            {
                "edge_id": "rel_001",
                "edge_kind": "relation",
                "source_id": "concept::channel-capacity",
                "target_id": "concept::shannon-entropy",
                "relation_type": "co_occurs_with",
                "evidence_ids": ["obs_001"],
                "support_kind": "inferred",
                "grounding_status": "partially_grounded",
                "status": "draft",
            }
        ],
        "claims": [
            {
                "claim_id": "clm_001",
                "claim_text": "Channel capacity and Shannon entropy are compared in coding theorem examples.",
                "claim_kind": "statement",
                "concept_ids": ["concept::channel-capacity", "concept::shannon-entropy"],
                "source_observation_ids": ["obs_001"],
                "support_kind": "derived_from_page",
                "grounding_status": "partially_grounded",
                "status": "triaged",
            }
        ],
        "observations": [
            {
                "observation_id": "obs_001",
                "artifact_id": "art_001",
                "role": "claim",
                "text": "Channel capacity and Shannon entropy are compared in coding theorem examples.",
                "support_kind": "derived_from_page",
                "grounding_status": "partially_grounded",
                "origin_path": "wiki/channel-capacity.md",
                "origin_section": "Channel Capacity",
                "status": "draft",
            }
        ],
        "diagnostics": {
            "quality_summary": {
                "inferred_relation_count": 1,
                "weakly_grounded_relation_count": 1,
                "unsupported_claim_count": 0,
            }
        },
        "consumer_notes": ["Inferred edges are candidates unless downstream review confirms them."],
    }


def test_load_groundrecall_graph_interchange_normalizes_graph_bundle(tmp_path: Path) -> None:
    path = tmp_path / "graph_interchange.json"
    path.write_text(json.dumps(_interchange_bundle()), encoding="utf-8")

    bundle = load_groundrecall_graph_interchange(path)

    node = get_concept_node(bundle, "channel-capacity")
    assert node is not None
    assert node["id"] == "concept::channel-capacity"
    assert node["title"] == "Channel Capacity"
    assert get_concept_node(bundle, "concept::channel-capacity") == node

    neighborhood = concept_neighborhood(bundle, "channel-capacity")
    assert neighborhood["outgoing"][0]["type"] == "co_occurs_with"
    assert neighborhood["outgoing_nodes"][0]["title"] == "Shannon Entropy"

    assert graph_quality_summary(bundle)["inferred_relation_count"] == 1
    assert claims_for_concept(bundle, "channel-capacity")[0]["claim_id"] == "clm_001"
    assert evidence_fragments_for_concept(bundle, "channel-capacity")[0]["origin_path"] == "wiki/channel-capacity.md"


def test_load_groundrecall_graph_interchange_rejects_unknown_schema(tmp_path: Path) -> None:
    payload = _interchange_bundle()
    payload["schema_version"] = "groundrecall.graph_interchange.v999"
    path = tmp_path / "graph_interchange.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported GroundRecall graph interchange schema"):
        load_groundrecall_graph_interchange(path)
