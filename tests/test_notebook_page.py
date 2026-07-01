from __future__ import annotations

import json
from pathlib import Path

from didactopus.notebook_page import (
    build_notebook_page_from_groundrecall_bundle,
    export_notebook_page_from_groundrecall_bundle,
    export_notebook_page_from_groundrecall_store,
)


def _sample_bundle() -> dict:
    return {
        "bundle_kind": "groundrecall_query_bundle",
        "concept": {
            "concept_id": "concept::natural-selection",
            "title": "Natural Selection",
            "description": "Differential survival and reproduction.",
            "aliases": ["selection"],
        },
        "relevant_claims": [
            {
                "claim_id": "clm_001",
                "claim_text": "Selection can change trait frequencies.",
                "source_roles": ["overview"],
            },
            {
                "claim_id": "clm_002",
                "claim_text": "Selection does not imply adaptation.",
                "source_roles": ["overview"],
                "distinction": {
                    "claim_id": "clm_002",
                    "distinction_type": "non_implication",
                    "cue": "does not imply",
                    "text": "Selection does not imply adaptation.",
                },
            },
        ],
        "relations": [
            {
                "relation_id": "rel_001",
                "source_id": "concept::variation",
                "target_id": "concept::natural-selection",
                "relation_type": "prerequisite",
            },
            {
                "relation_id": "rel_002",
                "source_id": "concept::natural-selection",
                "target_id": "concept::adaptation",
                "relation_type": "historical_successor",
            },
            {
                "relation_id": "rel_003",
                "source_id": "concept::natural-selection",
                "target_id": "concept::common-descent",
                "relation_type": "supports",
            },
        ],
        "related_concepts": [
            {
                "concept_id": "concept::variation",
                "title": "Variation",
                "description": "Differences among individuals.",
            },
            {
                "concept_id": "concept::adaptation",
                "title": "Adaptation",
                "description": "Traits fit to local conditions.",
            },
            {
                "concept_id": "concept::common-descent",
                "title": "Common Descent",
                "description": "Shared ancestry of organisms.",
            },
        ],
        "supporting_observations": [
            {
                "observation_id": "obs_001",
                "text": "Population differences can affect survival.",
                "origin_path": "texts/futuyma/ch1.md",
                "grounding_status": "grounded",
            }
        ],
        "source_artifacts": [
            {
                "artifact_id": "art_001",
                "artifact_kind": "compiled_page",
                "title": "Evolutionary Biology Chapter 1",
                "path": "texts/futuyma/ch1.md",
                "source_role": "overview",
            }
        ],
        "source_role_summary": {"overview": 1},
        "key_distinctions": [
            {
                "claim_id": "clm_002",
                "distinction_type": "non_implication",
                "cue": "does not imply",
                "text": "Selection does not imply adaptation.",
            }
        ],
        "review_candidates": [
            {
                "candidate_id": "concept::natural-selection",
                "finding_codes": ["bridge_concept"],
                "rationale": "Natural Selection | lane=conflict_resolution | priority=12 | graph=bridge_concept",
            }
        ],
        "suggested_next_actions": ["Inspect supporting observations before export."],
    }


def test_build_notebook_page_buckets_graph_navigation() -> None:
    page = build_notebook_page_from_groundrecall_bundle(_sample_bundle())

    assert page["page_kind"] == "didactopus_notebook_page"
    assert page["concept"]["title"] == "Natural Selection"
    assert page["summary"]["claim_count"] == 2
    assert page["graph_navigation"]["antecedent_concepts"][0]["title"] == "Variation"
    assert page["graph_navigation"]["derivative_concepts"][0]["title"] == "Adaptation"
    assert page["graph_navigation"]["closer_concepts"][0]["title"] == "Common Descent"
    assert page["supporting_sources"][0]["supporting_observation_count"] == 1
    assert page["supporting_sources"][0]["source_role"] == "overview"
    assert page["summary"]["source_role_count"] == 1
    assert page["summary"]["distinction_count"] == 1
    assert page["source_role_summary"]["overview"] == 1
    assert page["distinctions"][0]["distinction_type"] == "non_implication"
    assert page["review_context"]["graph_codes"] == ["bridge_concept"]
    assert page["review_context"]["source_role_summary"]["overview"] == 1
    assert page["review_context"]["key_distinctions"][0]["distinction_type"] == "non_implication"
    assert page["illustration_opportunities"]


def test_export_notebook_page_writes_json(tmp_path: Path) -> None:
    bundle_path = tmp_path / "groundrecall_query_bundle.json"
    out_path = tmp_path / "notebook_page.json"
    bundle_path.write_text(json.dumps(_sample_bundle()), encoding="utf-8")

    payload = export_notebook_page_from_groundrecall_bundle(bundle_path, out_path)

    assert out_path.exists()
    assert payload["page_path"].endswith("notebook_page.json")
    written = json.loads(out_path.read_text(encoding="utf-8"))
    assert written["concept"]["concept_id"] == "concept::natural-selection"


def test_export_notebook_page_from_groundrecall_store_writes_bundle_and_page(monkeypatch, tmp_path: Path) -> None:
    captured: dict = {}

    def _fake_export(store_dir, concept_ref, out_dir):
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        bundle_path = out_dir / "groundrecall_query_bundle.json"
        bundle_path.write_text(json.dumps(_sample_bundle()), encoding="utf-8")
        captured["store_dir"] = str(store_dir)
        captured["concept_ref"] = concept_ref
        captured["out_dir"] = str(out_dir)
        return {"bundle_path": str(bundle_path), "bundle": _sample_bundle()}

    monkeypatch.setattr("didactopus.notebook_page._load_groundrecall_export", lambda: _fake_export)

    payload = export_notebook_page_from_groundrecall_store(
        tmp_path / "store",
        "natural-selection",
        tmp_path / "out",
    )

    assert captured["concept_ref"] == "natural-selection"
    assert (tmp_path / "out" / "groundrecall_query_bundle.json").exists()
    assert (tmp_path / "out" / "notebook_page.json").exists()
    assert payload["concept_ref"] == "natural-selection"
    assert payload["groundrecall_query_bundle_path"].endswith("groundrecall_query_bundle.json")
