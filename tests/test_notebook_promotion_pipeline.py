from __future__ import annotations

import json
from pathlib import Path

from didactopus.notebook_promotion_pipeline import run_notebook_promotion_pipeline


def test_notebook_promotion_pipeline_runs_end_to_end(tmp_path: Path) -> None:
    pilot = tmp_path / "pilot"
    docs_dir = pilot / "normalized" / "seed-bundle" / "documents" / "source-one"
    docs_dir.mkdir(parents=True)
    (docs_dir / "document.md").write_text(
        "# Source One\n\nNatural selection can occur without leading to evolution if traits are not inherited. "
        "Evolution is a change in the gene pool of a population over time.\n",
        encoding="utf-8",
    )

    export_dir = pilot / "groundrecall" / "export" / "canonical"
    export_dir.mkdir(parents=True)
    notebook_dir = pilot / "didactopus" / "notebook-page"
    notebook_dir.mkdir(parents=True)

    hub = {
        "bundle_kind": "groundrecall_query_bundle",
        "query_type": "concept",
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
    source_bundle = {
        "bundle_kind": "groundrecall_query_bundle",
        "query_type": "concept",
        "concept": {
            "concept_id": "concept::source",
            "title": "Source Concept",
            "aliases": [],
            "description": "Source concept",
            "source_artifact_ids": ["ia_src"],
            "current_status": "reviewed",
        },
        "relevant_claims": [
            {
                "claim_id": "c1",
                "claim_text": "Evolution is a change in the gene pool of a population over time.",
                "source_observation_ids": ["o1"],
                "metadata": {},
            },
            {
                "claim_id": "c2",
                "claim_text": "Natural selection can occur without leading to evolution if traits are not inherited.",
                "source_observation_ids": ["o2"],
                "metadata": {},
            },
        ],
        "relations": [],
        "supporting_observations": [
            {
                "observation_id": "o1",
                "artifact_id": "ia_src",
                "text": "Evolution is a change in the gene pool of a population over time.",
                "role": "claim",
                "origin_path": "documents/source-one/document.md",
                "grounding_status": "grounded",
            },
            {
                "observation_id": "o2",
                "artifact_id": "ia_src",
                "text": "Natural selection can occur without leading to evolution if traits are not inherited.",
                "role": "claim",
                "origin_path": "documents/source-one/document.md",
                "grounding_status": "grounded",
            },
        ],
        "source_artifacts": [
            {
                "artifact_id": "ia_src",
                "artifact_kind": "doclift_bundle_artifact",
                "title": "document",
                "path": "documents/source-one/document.md",
                "current_status": "reviewed",
            }
        ],
        "related_concepts": [],
    }
    placeholder = {
        "bundle_kind": "groundrecall_query_bundle",
        "query_type": "concept",
        "concept": {
            "concept_id": "concept::gene-pool",
            "title": "Gene Pool",
            "aliases": [],
            "description": "Placeholder",
            "source_artifact_ids": [],
            "current_status": "reviewed",
        },
        "relevant_claims": [],
        "relations": [],
        "supporting_observations": [],
        "source_artifacts": [],
        "related_concepts": [],
        "review_candidates": [],
        "suggested_next_actions": [],
        "bundle_notes": [],
    }
    (export_dir / "groundrecall_query_bundle__hub.json").write_text(json.dumps(hub), encoding="utf-8")
    (export_dir / "query_bundle__source.json").write_text(json.dumps(source_bundle), encoding="utf-8")
    (export_dir / "query_bundle__gene-pool.json").write_text(json.dumps(placeholder), encoding="utf-8")
    (notebook_dir / "notebook_page__hub.json").write_text(json.dumps({"concept": {"concept_id": "concept::hub"}, "summary": {}}))

    binding = {
        "primary_artifacts": {
            "groundrecall_query_bundle": "../../groundrecall/export/canonical/groundrecall_query_bundle__hub.json",
            "notebook_page": "./notebook_page__hub.json",
        },
        "supporting_artifacts": {
            "gene_pool_bundle": "../../groundrecall/export/canonical/query_bundle__gene-pool.json",
        },
    }
    binding_path = notebook_dir / "binding.json"
    binding_path.write_text(json.dumps(binding), encoding="utf-8")

    manifest = pilot / "manifests" / "first-ring-promotion-batch.yaml"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(
        """
promotion_priority:
  tier_3:
    - concept: gene-pool
      label: Gene Pool
      compose_from:
        bundle_refs:
          - query_bundle__source.json
        keyword_phrases:
          - gene pool
""",
        encoding="utf-8",
    )

    report_path = pilot / "reports" / "pipeline.json"
    phrase_path = pilot / "reports" / "phrases.json"
    result = run_notebook_promotion_pipeline(
        binding_path=binding_path,
        manifest_path=manifest,
        canonical_dir=export_dir,
        output_path=report_path,
        phrase_inventory_output=phrase_path,
        phrase_inputs=[pilot / "normalized" / "seed-bundle"],
        seed_terms=["gene pool", "natural selection"],
        top_n=10,
    )

    report = json.loads(report_path.read_text(encoding="utf-8"))
    rebuilt_bundle = json.loads((export_dir / "query_bundle__gene-pool.json").read_text(encoding="utf-8"))
    assert result["report_path"] == str(report_path)
    assert phrase_path.exists()
    assert report["batch_promotion"]["weak_node_count"] == 1
    assert report["delta"]["hub"]["related_concept_count"] == 1
    assert len(rebuilt_bundle["relevant_claims"]) == 1
