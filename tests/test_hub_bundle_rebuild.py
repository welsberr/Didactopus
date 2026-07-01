from __future__ import annotations

import json
from pathlib import Path

from didactopus.hub_bundle_rebuild import rebuild_hub_bundle_from_binding


def test_rebuild_hub_bundle_from_binding_updates_support_layer(tmp_path: Path) -> None:
    root = tmp_path / "pilot" / "didactopus" / "notebook-page"
    root.mkdir(parents=True)
    export_dir = tmp_path / "pilot" / "groundrecall" / "export" / "canonical"
    export_dir.mkdir(parents=True)

    hub = {
        "bundle_kind": "groundrecall_query_bundle",
        "concept": {
            "concept_id": "concept::hub",
            "title": "Hub",
            "aliases": [],
            "description": "Hub concept",
            "source_artifact_ids": ["ia_hub"],
            "current_status": "reviewed",
        },
        "relevant_claims": [{"claim_id": "hc1", "claim_text": "Hub claim."}],
        "relations": [],
        "supporting_observations": [],
        "source_artifacts": [],
        "related_concepts": [],
        "review_candidates": [],
        "suggested_next_actions": [],
        "bundle_notes": [],
    }
    support = {
        "bundle_kind": "groundrecall_query_bundle",
        "concept": {
            "concept_id": "concept::natural-selection",
            "title": "Natural Selection",
            "aliases": [],
            "description": "Support concept",
            "source_artifact_ids": ["ia_sel"],
            "current_status": "reviewed",
        },
        "relevant_claims": [
            {"claim_id": "c1", "claim_text": "Natural selection can occur without leading to evolution if traits are not inherited."}
        ],
        "relations": [],
        "supporting_observations": [
            {
                "observation_id": "o1",
                "artifact_id": "ia_sel",
                "text": "Natural selection can occur without leading to evolution if traits are not inherited.",
                "role": "claim",
                "origin_path": "documents/selection/document.md",
                "grounding_status": "grounded",
            }
        ],
        "source_artifacts": [
            {
                "artifact_id": "ia_sel",
                "artifact_kind": "doclift_bundle_artifact",
                "title": "document",
                "path": "documents/selection/document.md",
                "current_status": "reviewed",
            }
        ],
        "related_concepts": [],
    }
    (export_dir / "groundrecall_query_bundle__hub.json").write_text(json.dumps(hub))
    (export_dir / "query_bundle__natural-selection.json").write_text(json.dumps(support))
    (root / "notebook_page__hub.json").write_text(json.dumps({"concept": {"concept_id": "concept::hub"}, "summary": {}}))
    binding = {
        "primary_artifacts": {
            "groundrecall_query_bundle": "../../groundrecall/export/canonical/groundrecall_query_bundle__hub.json",
            "notebook_page": "./notebook_page__hub.json",
        },
        "supporting_artifacts": {
            "natural_selection_bundle": "../../groundrecall/export/canonical/query_bundle__natural-selection.json",
        },
    }
    binding_path = root / "binding.json"
    binding_path.write_text(json.dumps(binding))

    result = rebuild_hub_bundle_from_binding(binding_path)

    rebuilt = json.loads((export_dir / "groundrecall_query_bundle__hub.json").read_text())
    assert result["source_artifact_count"] == 1
    assert rebuilt["source_role_summary"]["mechanism"] == 1
    assert len(rebuilt["key_distinctions"]) == 1
    assert rebuilt["related_concepts"][0]["id"] == "concept::natural-selection"
