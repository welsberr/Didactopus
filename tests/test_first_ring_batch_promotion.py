from __future__ import annotations

import json
from pathlib import Path

from didactopus.first_ring_batch_promotion import run_first_ring_batch_promotion


def test_first_ring_batch_promotion_reuses_existing_and_synthesizes_missing(tmp_path: Path) -> None:
    canonical = tmp_path / "canonical"
    canonical.mkdir()
    existing_payload = {
        "bundle_kind": "groundrecall_query_bundle",
        "query_type": "concept",
        "concept": {
            "concept_id": "concept::inheritance",
            "title": "Inheritance",
            "aliases": [],
            "description": "Existing bundle.",
            "source_artifact_ids": ["a1"],
            "current_status": "reviewed",
        },
        "relevant_claims": [
            {
                "claim_id": "c1",
                "claim_text": "Inheritance transmits traits across generations.",
                "source_observation_ids": ["o1"],
                "metadata": {},
            }
        ],
        "relations": [],
        "supporting_observations": [{"observation_id": "o1", "text": "Inheritance transmits traits across generations."}],
        "source_artifacts": [{"artifact_id": "a1", "title": "doc"}],
        "related_concepts": [],
    }
    source_payload = {
        "bundle_kind": "groundrecall_query_bundle",
        "query_type": "concept",
        "concept": {
            "concept_id": "concept::selection-and-evolution",
            "title": "Selection and Evolution",
            "aliases": [],
            "description": "Source bundle.",
            "source_artifact_ids": ["a2"],
            "current_status": "reviewed",
        },
        "relevant_claims": [
            {
                "claim_id": "c2",
                "claim_text": "Natural selection can occur without leading to evolution if differences are not genetically based.",
                "source_observation_ids": ["o2"],
                "metadata": {},
            },
            {
                "claim_id": "c3",
                "claim_text": "Selection changes population composition over many generations.",
                "source_observation_ids": ["o3"],
                "metadata": {},
            },
        ],
        "relations": [],
        "supporting_observations": [
            {"observation_id": "o2", "text": "Natural selection can occur without leading to evolution if differences are not genetically based."},
            {"observation_id": "o3", "text": "Selection changes population composition over many generations."},
        ],
        "source_artifacts": [{"artifact_id": "a2", "title": "doc2"}],
        "related_concepts": [],
    }
    (canonical / "query_bundle__inheritance.json").write_text(json.dumps(existing_payload))
    (canonical / "query_bundle__selection-and-evolution.json").write_text(json.dumps(source_payload))

    manifest = tmp_path / "manifest.yaml"
    manifest.write_text(
        """
promotion_priority:
  tier_1:
    - concept: inheritance
      label: Inheritance
    - concept: natural-selection
      label: Natural Selection
      compose_from:
        bundle_refs:
          - query_bundle__selection-and-evolution.json
        keyword_phrases:
          - natural selection
          - selection
"""
    )

    result = run_first_ring_batch_promotion(manifest, canonical)
    report = json.loads((canonical / "first_ring_batch_promotion_report.json").read_text())
    assert result["generated_count"] == 2
    statuses = {item["concept"]: item["status"] for item in report["generated"]}
    assert statuses["inheritance"] == "existing"
    assert statuses["natural-selection"] == "synthesized"
    synth = json.loads((canonical / "query_bundle__natural-selection.json").read_text())
    assert synth["concept"]["concept_id"] == "concept::natural-selection"
    assert len(synth["relevant_claims"]) == 2
