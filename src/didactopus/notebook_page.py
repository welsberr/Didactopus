from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


_ANTECEDENT_TYPES = {"prerequisite", "historical_predecessor"}
_DERIVATIVE_TYPES = {"historical_successor"}


def _concept_entry(concept: dict[str, Any], relation_types: set[str] | None = None) -> dict[str, Any]:
    entry = {
        "concept_id": concept.get("concept_id", ""),
        "title": concept.get("title", ""),
        "description": concept.get("description", ""),
    }
    if relation_types:
        entry["relation_types"] = sorted(relation_types)
    return entry


def _bucket_relation(
    relation: dict[str, Any],
    concept_id: str,
    concepts_by_id: dict[str, dict[str, Any]],
) -> tuple[str | None, dict[str, Any] | None]:
    source_id = str(relation.get("source_id", ""))
    target_id = str(relation.get("target_id", ""))
    relation_type = str(relation.get("relation_type", "")).strip() or "related_to"
    if concept_id not in {source_id, target_id}:
        return None, None

    other_id = target_id if source_id == concept_id else source_id
    other = concepts_by_id.get(other_id)
    if other is None:
        return None, None

    if relation_type in _ANTECEDENT_TYPES:
        bucket = "antecedent_concepts" if target_id == concept_id else "derivative_concepts"
    elif relation_type in _DERIVATIVE_TYPES:
        bucket = "derivative_concepts" if source_id == concept_id else "antecedent_concepts"
    else:
        bucket = "closer_concepts"

    return bucket, _concept_entry(other, {relation_type})


def _merge_bucket_entries(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for item in items:
        concept_id = str(item.get("concept_id", ""))
        if not concept_id:
            continue
        existing = merged.setdefault(
            concept_id,
            {
                "concept_id": concept_id,
                "title": item.get("title", ""),
                "description": item.get("description", ""),
                "relation_types": [],
            },
        )
        existing["relation_types"] = sorted(set(existing["relation_types"]) | set(item.get("relation_types", [])))
    return list(merged.values())


def _review_context(bundle: dict[str, Any]) -> dict[str, Any]:
    review_candidates = bundle.get("review_candidates", []) or []
    claims = bundle.get("relevant_claims", []) or []
    graph_codes = sorted(
        {
            code
            for item in review_candidates
            for code in item.get("finding_codes", []) or []
            if "concept" in str(code) or "bridge" in str(code) or "component" in str(code)
        }
    )
    top_rationales = [str(item.get("rationale", "")).strip() for item in review_candidates if str(item.get("rationale", "")).strip()][:3]
    definition_candidates = 0
    qualification_candidates = 0
    constraint_candidates = 0
    quote_candidates = 0
    distinction_candidates = []
    for claim in claims:
        metadata = claim.get("metadata", {}) or {}
        text = str(claim.get("claim_text", "")).strip()
        lowered = text.lower()
        distinction = claim.get("distinction")
        if isinstance(distinction, dict):
            distinction_candidates.append(
                {
                    "claim_id": distinction.get("claim_id", claim.get("claim_id", "")),
                    "distinction_type": distinction.get("distinction_type", ""),
                    "cue": distinction.get("cue", ""),
                    "text": distinction.get("text", text),
                }
            )
        if metadata.get("definition_candidate") or any(token in lowered for token in (" defined as ", " refers to ", " means ", " describes ")):
            definition_candidates += 1
        if metadata.get("qualification_candidate") or any(token in lowered for token in ("however", "although", "unless", "only if", "may not", "does not always")):
            qualification_candidates += 1
        if metadata.get("constraint_candidate") or any(token in lowered for token in ("must", "requires", "cannot", "depends on", "limited to", "constraint")):
            constraint_candidates += 1
        if metadata.get("quote_candidate") or (len(text) >= 140 and text.endswith((".", "!", '"', "”"))):
            quote_candidates += 1
    return {
        "review_candidate_count": len(review_candidates),
        "graph_codes": graph_codes,
        "top_rationales": top_rationales,
        "secondary_products": {
            "definition_candidates": definition_candidates,
            "qualification_candidates": qualification_candidates,
            "constraint_candidates": constraint_candidates,
            "quote_candidates": quote_candidates,
        },
        "source_role_summary": bundle.get("source_role_summary", {}) or {},
        "key_distinctions": distinction_candidates[:6] or (bundle.get("key_distinctions", []) or [])[:6],
        "public_output_policy": {
            "quotes_require_attribution": True,
            "public_prose_should_be_paraphrastic": True,
            "unmarked_source_wording_is_not_allowed": True,
        },
    }


def _supporting_sources(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    artifacts = bundle.get("source_artifacts", []) or []
    observations = bundle.get("supporting_observations", []) or []
    by_origin: dict[str, int] = {}
    for observation in observations:
        origin_path = str(observation.get("origin_path", "")).strip()
        if origin_path:
            by_origin[origin_path] = by_origin.get(origin_path, 0) + 1

    sources = []
    for artifact in artifacts:
        path = str(artifact.get("path", "")).strip()
        sources.append(
            {
                "artifact_id": artifact.get("artifact_id", ""),
                "title": artifact.get("title", ""),
                "path": path,
                "artifact_kind": artifact.get("artifact_kind", ""),
                "source_role": artifact.get("source_role", ""),
                "supporting_observation_count": by_origin.get(path, 0),
            }
        )
    return sources


def _illustration_opportunities(bundle: dict[str, Any], navigation: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    concept = bundle.get("concept", {}) or {}
    concept_title = str(concept.get("title", "")).strip() or str(concept.get("concept_id", "")).strip()
    opportunities = []
    if navigation["antecedent_concepts"] or navigation["derivative_concepts"]:
        opportunities.append(
            {
                "kind": "concept_path",
                "target_concept_id": concept.get("concept_id", ""),
                "purpose": f"Show how {concept_title} fits into a prerequisite or downstream concept path.",
                "status": "planned",
            }
        )
    if navigation["closer_concepts"]:
        titles = ", ".join(item["title"] for item in navigation["closer_concepts"][:3] if item.get("title"))
        opportunities.append(
            {
                "kind": "comparison",
                "target_concept_id": concept.get("concept_id", ""),
                "purpose": f"Compare {concept_title} with nearby concepts: {titles}." if titles else f"Compare {concept_title} with nearby concepts.",
                "status": "planned",
            }
        )
    if bundle.get("supporting_observations"):
        opportunities.append(
            {
                "kind": "evidence_trace",
                "target_concept_id": concept.get("concept_id", ""),
                "purpose": f"Trace the evidence and claims currently grounding {concept_title}.",
                "status": "planned",
            }
        )
    return opportunities


def build_notebook_page_from_groundrecall_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    concept = bundle.get("concept", {}) or {}
    concept_id = str(concept.get("concept_id", "")).strip()
    concepts_by_id = {concept_id: concept}
    for item in bundle.get("related_concepts", []) or []:
        item_id = str(item.get("concept_id", "")).strip()
        if item_id:
            concepts_by_id[item_id] = item

    navigation: dict[str, list[dict[str, Any]]] = {
        "antecedent_concepts": [],
        "closer_concepts": [],
        "derivative_concepts": [],
    }
    for relation in bundle.get("relations", []) or []:
        bucket, entry = _bucket_relation(relation, concept_id, concepts_by_id)
        if bucket and entry:
            navigation[bucket].append(entry)

    navigation = {key: _merge_bucket_entries(items) for key, items in navigation.items()}
    supporting_observations = bundle.get("supporting_observations", []) or []
    supporting_excerpts = [
        {
            "observation_id": item.get("observation_id", ""),
            "text": item.get("text", ""),
            "origin_path": item.get("origin_path", ""),
            "grounding_status": item.get("grounding_status", ""),
        }
        for item in supporting_observations[:5]
    ]

    return {
        "page_kind": "didactopus_notebook_page",
        "concept": {
            "concept_id": concept.get("concept_id", ""),
            "title": concept.get("title", ""),
            "description": concept.get("description", ""),
            "aliases": concept.get("aliases", []) or [],
        },
        "summary": {
            "claim_count": len(bundle.get("relevant_claims", []) or []),
            "supporting_observation_count": len(supporting_observations),
            "related_concept_count": len(bundle.get("related_concepts", []) or []),
            "source_role_count": len(bundle.get("source_role_summary", {}) or {}),
            "distinction_count": len(bundle.get("key_distinctions", []) or []),
        },
        "graph_navigation": navigation,
        "source_role_summary": bundle.get("source_role_summary", {}) or {},
        "distinctions": (bundle.get("key_distinctions", []) or [])[:6],
        "supporting_sources": _supporting_sources(bundle),
        "supporting_excerpts": supporting_excerpts,
        "review_context": _review_context(bundle),
        "illustration_opportunities": _illustration_opportunities(bundle, navigation),
        "suggested_next_actions": bundle.get("suggested_next_actions", []) or [],
    }


def export_notebook_page_from_groundrecall_bundle(bundle_path: str | Path, out_path: str | Path) -> dict[str, Any]:
    bundle_file = Path(bundle_path)
    payload = json.loads(bundle_file.read_text(encoding="utf-8"))
    page = build_notebook_page_from_groundrecall_bundle(payload)
    target = Path(out_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(page, indent=2), encoding="utf-8")
    return {"page_path": str(target), "page": page}


def export_notebook_page_from_groundrecall_store(
    store_dir: str | Path,
    concept_ref: str,
    out_dir: str | Path,
) -> dict[str, Any]:
    export_groundrecall_query_bundle = _load_groundrecall_export()
    target = Path(out_dir)
    target.mkdir(parents=True, exist_ok=True)
    exported = export_groundrecall_query_bundle(store_dir, concept_ref, target)
    page_path = target / "notebook_page.json"
    page_result = export_notebook_page_from_groundrecall_bundle(exported["bundle_path"], page_path)
    page_result["groundrecall_query_bundle_path"] = exported["bundle_path"]
    page_result["concept_ref"] = concept_ref
    return page_result


def _load_groundrecall_export():
    groundrecall_src = Path("/home/netuser/bin/GroundRecall/src")
    if groundrecall_src.exists():
        sys.path.insert(0, str(groundrecall_src))
    from groundrecall.export import export_groundrecall_query_bundle  # type: ignore

    return export_groundrecall_query_bundle
