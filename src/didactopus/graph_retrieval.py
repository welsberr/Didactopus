from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


@dataclass
class GraphBundle:
    knowledge_graph: dict
    source_corpus: dict


def concept_node_id(concept_id: str) -> str:
    if concept_id.startswith("concept::"):
        return concept_id
    return f"concept::{concept_id}"


def _node_index(bundle: GraphBundle) -> dict[str, dict]:
    return {node["id"]: node for node in bundle.knowledge_graph.get("nodes", [])}


def _edges(bundle: GraphBundle) -> list[dict]:
    return list(bundle.knowledge_graph.get("edges", []))


def get_concept_node(bundle: GraphBundle, concept_id: str) -> dict | None:
    return _node_index(bundle).get(concept_node_id(concept_id))


def concept_neighborhood(bundle: GraphBundle, concept_id: str) -> dict:
    node_id = concept_node_id(concept_id)
    nodes = _node_index(bundle)
    incoming = []
    outgoing = []
    for edge in _edges(bundle):
        if edge["target"] == node_id:
            incoming.append(edge)
        if edge["source"] == node_id:
            outgoing.append(edge)
    return {
        "concept": nodes.get(node_id, {}),
        "incoming": incoming,
        "outgoing": outgoing,
        "incoming_nodes": [nodes[edge["source"]] for edge in incoming if edge["source"] in nodes],
        "outgoing_nodes": [nodes[edge["target"]] for edge in outgoing if edge["target"] in nodes],
    }


def source_fragments_for_concept(bundle: GraphBundle, concept_id: str, limit: int = 3) -> list[dict]:
    neighborhood = concept_neighborhood(bundle, concept_id)
    lesson_titles = {
        node.get("title", "")
        for node in neighborhood["incoming_nodes"]
        if node.get("type") == "lesson"
    }
    lesson_titles.update(
        node.get("title", "")
        for node in neighborhood["outgoing_nodes"]
        if node.get("type") == "lesson"
    )
    fragments = []
    for fragment in bundle.source_corpus.get("fragments", []):
        if fragment.get("lesson_title") in lesson_titles:
            fragments.append(fragment)
        if len(fragments) >= limit:
            break
    return fragments


def prerequisite_titles(bundle: GraphBundle, concept_id: str) -> list[str]:
    neighborhood = concept_neighborhood(bundle, concept_id)
    titles = []
    seen = set()
    for edge, node in zip(neighborhood["incoming"], neighborhood["incoming_nodes"]):
        if edge.get("type") == "prerequisite":
            title = node.get("title", node.get("id", ""))
            if title not in seen:
                seen.add(title)
                titles.append(title)
    return titles


def lesson_titles_for_concept(bundle: GraphBundle, concept_id: str) -> list[str]:
    neighborhood = concept_neighborhood(bundle, concept_id)
    titles = []
    seen = set()
    for edge, node in zip(neighborhood["incoming"], neighborhood["incoming_nodes"]):
        if edge.get("type") in {"supports_concept", "teaches_concept"} and node.get("type") == "lesson":
            title = node.get("title", node.get("id", ""))
            if title not in seen:
                seen.add(title)
                titles.append(title)
    return titles


def load_groundrecall_graph_interchange(path: str | Path) -> GraphBundle:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("bundle_kind") != "groundrecall_graph_interchange":
        raise ValueError("Expected a GroundRecall graph interchange bundle.")
    if payload.get("schema_version") != "groundrecall.graph_interchange.v1":
        raise ValueError(f"Unsupported GroundRecall graph interchange schema: {payload.get('schema_version', '')}")

    nodes = [
        {
            "id": node.get("node_id", ""),
            "type": node.get("node_kind", "concept"),
            "title": node.get("title", ""),
            "description": node.get("description", ""),
            "aliases": list(node.get("aliases", []) or []),
            "status": node.get("status", ""),
            "source_artifact_ids": list(node.get("source_artifact_ids", []) or []),
            "groundrecall": node,
        }
        for node in payload.get("nodes", [])
        if node.get("node_id")
    ]
    edges = [
        {
            "id": edge.get("edge_id", ""),
            "source": edge.get("source_id", ""),
            "target": edge.get("target_id", ""),
            "type": edge.get("relation_type", "related_to"),
            "evidence_ids": list(edge.get("evidence_ids", []) or []),
            "support_kind": edge.get("support_kind", ""),
            "grounding_status": edge.get("grounding_status", ""),
            "status": edge.get("status", ""),
            "groundrecall": edge,
        }
        for edge in payload.get("edges", [])
        if edge.get("source_id") and edge.get("target_id")
    ]
    observations = [
        {
            "fragment_id": observation.get("observation_id", ""),
            "observation_id": observation.get("observation_id", ""),
            "artifact_id": observation.get("artifact_id", ""),
            "lesson_title": observation.get("origin_path", "") or observation.get("artifact_id", ""),
            "text": observation.get("text", ""),
            "role": observation.get("role", ""),
            "origin_path": observation.get("origin_path", ""),
            "origin_section": observation.get("origin_section", ""),
            "support_kind": observation.get("support_kind", ""),
            "grounding_status": observation.get("grounding_status", ""),
            "status": observation.get("status", ""),
        }
        for observation in payload.get("observations", [])
        if observation.get("observation_id")
    ]
    return GraphBundle(
        knowledge_graph={
            "nodes": nodes,
            "edges": edges,
            "diagnostics": payload.get("diagnostics", {}) or {},
            "schema_version": payload.get("schema_version", ""),
            "snapshot_id": payload.get("snapshot_id", ""),
            "consumer_notes": list(payload.get("consumer_notes", []) or []),
        },
        source_corpus={
            "fragments": observations,
            "claims": list(payload.get("claims", []) or []),
            "observations": observations,
        },
    )


def graph_quality_summary(bundle: GraphBundle) -> dict[str, Any]:
    diagnostics = bundle.knowledge_graph.get("diagnostics", {}) or {}
    return diagnostics.get("quality_summary", {}) or {}


def claims_for_concept(bundle: GraphBundle, concept_id: str) -> list[dict[str, Any]]:
    node_id = concept_node_id(concept_id)
    return [
        claim
        for claim in bundle.source_corpus.get("claims", [])
        if node_id in (claim.get("concept_ids", []) or [])
    ]


def evidence_fragments_for_concept(bundle: GraphBundle, concept_id: str, limit: int = 3) -> list[dict[str, Any]]:
    observation_ids = {
        observation_id
        for claim in claims_for_concept(bundle, concept_id)
        for observation_id in (claim.get("source_observation_ids", []) or [])
    }
    fragments = [
        fragment
        for fragment in bundle.source_corpus.get("fragments", [])
        if fragment.get("observation_id") in observation_ids or fragment.get("fragment_id") in observation_ids
    ]
    return fragments[:limit]
