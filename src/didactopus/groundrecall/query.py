from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .store import GroundRecallStore


def _normalize(text: str) -> str:
    return " ".join(text.lower().split())


def _matches(query: str, *values: str) -> bool:
    needle = _normalize(query)
    return any(needle in _normalize(value) for value in values if value)


def query_concept(store_dir: str | Path, concept_ref: str) -> dict[str, Any] | None:
    store = GroundRecallStore(store_dir)
    concepts = store.list_concepts()
    concept = next(
        (
            item
            for item in concepts
            if concept_ref == item.concept_id
            or concept_ref == item.concept_id.replace("concept::", "", 1)
            or _matches(concept_ref, item.title, item.description, *item.aliases)
        ),
        None,
    )
    if concept is None:
        return None

    claims = [item for item in store.list_claims() if concept.concept_id in item.concept_ids and item.current_status != "rejected"]
    relations = [
        item
        for item in store.list_relations()
        if (item.source_id == concept.concept_id or item.target_id == concept.concept_id) and item.current_status != "rejected"
    ]
    artifacts = {item.artifact_id: item for item in store.list_artifacts()}
    observations = {item.observation_id: item for item in store.list_observations()}

    supporting_observations = []
    for claim in claims:
        for observation_id in claim.source_observation_ids:
            observation = observations.get(observation_id)
            if observation is not None:
                supporting_observations.append(
                    {
                        "observation_id": observation.observation_id,
                        "text": observation.text,
                        "role": observation.role,
                        "origin_path": observation.provenance.origin_path,
                        "grounding_status": observation.provenance.grounding_status,
                    }
                )

    related_concept_ids = sorted(
        {
            relation.target_id if relation.source_id == concept.concept_id else relation.source_id
            for relation in relations
            if relation.source_id != relation.target_id
        }
    )
    related_concepts = [item.model_dump() for item in concepts if item.concept_id in related_concept_ids]

    source_artifacts = [
        artifact.model_dump()
        for artifact in artifacts.values()
        if artifact.artifact_id in set(concept.source_artifact_ids)
    ]

    return {
        "query_type": "concept",
        "concept": concept.model_dump(),
        "claims": [item.model_dump() for item in claims],
        "relations": [item.model_dump() for item in relations],
        "related_concepts": related_concepts,
        "supporting_observations": supporting_observations,
        "source_artifacts": source_artifacts,
    }


def search_claims(
    store_dir: str | Path,
    text: str,
    include_rejected: bool = False,
    limit: int = 20,
) -> dict[str, Any]:
    store = GroundRecallStore(store_dir)
    concepts = {item.concept_id: item for item in store.list_concepts()}
    matches = []
    for claim in store.list_claims():
        if not include_rejected and claim.current_status == "rejected":
            continue
        concept_titles = [concepts[concept_id].title for concept_id in claim.concept_ids if concept_id in concepts]
        if _matches(text, claim.claim_text, *concept_titles):
            matches.append(
                {
                    "claim": claim.model_dump(),
                    "concept_titles": concept_titles,
                    "provenance": claim.provenance.model_dump(),
                }
            )
        if len(matches) >= limit:
            break
    return {
        "query_type": "claim_search",
        "query": text,
        "matches": matches,
    }


def query_provenance(
    store_dir: str | Path,
    origin_path: str | None = None,
    source_url: str | None = None,
) -> dict[str, Any]:
    store = GroundRecallStore(store_dir)
    claims = []
    observations = []
    for claim in store.list_claims():
        if origin_path and claim.provenance.origin_path == origin_path:
            claims.append(claim.model_dump())
            continue
        if source_url and claim.provenance.source_url == source_url:
            claims.append(claim.model_dump())
    for observation in store.list_observations():
        if origin_path and observation.provenance.origin_path == origin_path:
            observations.append(observation.model_dump())
            continue
        if source_url and observation.provenance.source_url == source_url:
            observations.append(observation.model_dump())
    return {
        "query_type": "provenance",
        "origin_path": origin_path or "",
        "source_url": source_url or "",
        "claims": claims,
        "observations": observations,
    }


def build_query_bundle_for_concept(store_dir: str | Path, concept_ref: str) -> dict[str, Any] | None:
    payload = query_concept(store_dir, concept_ref)
    if payload is None:
        return None
    claims = payload["claims"]
    contradictions = [item for item in claims if item.get("contradicts_claim_ids")]
    supersessions = [item for item in claims if item.get("supersedes_claim_ids")]
    return {
        "bundle_kind": "groundrecall_query_bundle",
        "query_type": "concept",
        "concept": payload["concept"],
        "relevant_claims": claims,
        "supporting_observations": payload["supporting_observations"],
        "related_concepts": payload["related_concepts"],
        "contradictions": contradictions,
        "supersessions": supersessions,
        "suggested_next_actions": [
            "Review promoted claims with low review confidence.",
            "Inspect supporting observations before exporting assistant context.",
            "Check related concepts for hidden prerequisite or contradiction edges.",
        ],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Query canonical GroundRecall objects.")
    parser.add_argument("store_dir")
    parser.add_argument("query")
    parser.add_argument("--kind", choices=["concept", "claim", "provenance", "bundle"], default="concept")
    parser.add_argument("--source-url", default=None)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.kind == "concept":
        payload = query_concept(args.store_dir, args.query)
    elif args.kind == "claim":
        payload = search_claims(args.store_dir, args.query)
    elif args.kind == "provenance":
        payload = query_provenance(args.store_dir, origin_path=args.query, source_url=args.source_url)
    else:
        payload = build_query_bundle_for_concept(args.store_dir, args.query)
    print(json.dumps(payload, indent=2))
