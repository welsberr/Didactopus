from __future__ import annotations

import json
from pathlib import Path

from didactopus.notebook_workmap_refresh import run_notebook_workmap_refresh


def test_notebook_workmap_refresh_runs_from_work_map(tmp_path: Path) -> None:
    pilot = tmp_path / "pilot"
    docs_dir = pilot / "normalized" / "seed-bundle" / "documents" / "source-one"
    docs_dir.mkdir(parents=True)
    (docs_dir / "document.md").write_text(
        "# Source One\n\nEvolution is a change in the gene pool of a population over time.\n",
        encoding="utf-8",
    )

    export_dir = pilot / "groundrecall" / "export" / "canonical"
    export_dir.mkdir(parents=True)
    notebook_dir = pilot / "didactopus" / "notebook-page"
    notebook_dir.mkdir(parents=True)
    workmap_dir = pilot / ".groundrecall"
    workmap_dir.mkdir(parents=True)

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
            }
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
            }
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
    (notebook_dir / "notebook_page__hub.json").write_text(json.dumps({"concept": {"concept_id": "concept::hub"}, "summary": {}}), encoding="utf-8")

    binding = {
        "primary_artifacts": {
            "groundrecall_query_bundle": "../../groundrecall/export/canonical/groundrecall_query_bundle__hub.json",
            "notebook_page": "./notebook_page__hub.json",
        },
        "supporting_artifacts": {
            "gene_pool_bundle": "../../groundrecall/export/canonical/query_bundle__gene-pool.json",
        },
    }
    (notebook_dir / "binding.json").write_text(json.dumps(binding), encoding="utf-8")

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

    work_map = {
        "project": "pilot",
        "primary_hub": {
            "binding_path": "didactopus/notebook-page/binding.json",
        },
        "canonical_sources": {
            "normalized_roots": ["normalized/seed-bundle"],
        },
        "groundrecall_paths": {
            "canonical_export_dir": "groundrecall/export/canonical",
            "batch_manifest": "manifests/first-ring-promotion-batch.yaml",
            "pipeline_report_json": "groundrecall/report.json",
            "pipeline_phrase_inventory_json": "groundrecall/phrases.json",
        },
    }
    work_map_path = workmap_dir / "work-map.json"
    work_map_path.write_text(json.dumps(work_map), encoding="utf-8")

    result = run_notebook_workmap_refresh(work_map_path, top_n=10)

    report = json.loads(Path(result["report_path"]).read_text(encoding="utf-8"))
    rebuilt_bundle = json.loads((export_dir / "query_bundle__gene-pool.json").read_text(encoding="utf-8"))
    assert report["batch_promotion"]["weak_node_count"] == 1
    assert report["delta"]["hub"]["related_concept_count"] == 1
    assert len(rebuilt_bundle["relevant_claims"]) == 1
