from __future__ import annotations

from dataclasses import dataclass

from epistemap import (
    Edge,
    GraphBundle as EpistemapBundle,
    Node,
    claim_status_at,
    evidence_available_at,
    fair_play_diagnostic,
    graph_at,
    epistemic_summary,
    neighborhood,
    stale_claims_after,
    tenability_window,
    timeline_events,
)


@dataclass
class GraphBundle:
    knowledge_graph: dict
    source_corpus: dict


def concept_node_id(concept_id: str) -> str:
    return f"concept::{concept_id}"


def _node_index(bundle: GraphBundle) -> dict[str, dict]:
    return {node["id"]: node for node in bundle.knowledge_graph.get("nodes", [])}


def _epistemap_bundle(bundle: GraphBundle) -> EpistemapBundle:
    return EpistemapBundle(
        graph_id=str(bundle.knowledge_graph.get("graph_id", "")),
        title=str(bundle.knowledge_graph.get("title") or bundle.knowledge_graph.get("course_title", "")),
        nodes=[
            Node(
                id=str(node["id"]),
                type=str(node.get("type", "")),
                title=str(node.get("title", "")),
                description=str(node.get("description", "")),
                metadata={key: value for key, value in node.items() if key not in {"id", "type", "title", "description"}},
            )
            for node in bundle.knowledge_graph.get("nodes", [])
            if "id" in node
        ],
        edges=[
            Edge(
                source=str(edge["source"]),
                target=str(edge["target"]),
                type=str(edge.get("type", "")),
                justification=str(edge.get("justification", "")),
                confidence=edge.get("confidence"),
                metadata={key: value for key, value in edge.items() if key not in {"source", "target", "type", "justification", "confidence"}},
            )
            for edge in bundle.knowledge_graph.get("edges", [])
            if "source" in edge and "target" in edge
        ],
        metadata={key: value for key, value in bundle.knowledge_graph.items() if key not in {"nodes", "edges"}},
    )


def get_concept_node(bundle: GraphBundle, concept_id: str) -> dict | None:
    return _node_index(bundle).get(concept_node_id(concept_id))


def concept_neighborhood(bundle: GraphBundle, concept_id: str) -> dict:
    node_id = concept_node_id(concept_id)
    payload = neighborhood(_epistemap_bundle(bundle), node_id)
    return {
        "concept": _node_dict(payload["node"]),
        "incoming": [_edge_dict(edge) for edge in payload["incoming"]],
        "outgoing": [_edge_dict(edge) for edge in payload["outgoing"]],
        "incoming_nodes": [_node_dict(node) for node in payload["incoming_nodes"]],
        "outgoing_nodes": [_node_dict(node) for node in payload["outgoing_nodes"]],
    }


def concept_epistemic_summary(bundle: GraphBundle, concept_id: str) -> dict:
    """Return Epistemap epistemic and Bayesian reliability context for a concept."""

    return epistemic_summary(_epistemap_bundle(bundle), concept_node_id(concept_id))


def temporal_graph_slice(bundle: GraphBundle, when) -> dict:
    """Return a Didactopus-friendly knowledge graph slice available by `when`."""

    sliced = graph_at(_epistemap_bundle(bundle), when)
    return {
        "graph_id": sliced.graph_id,
        "title": sliced.title,
        "description": sliced.description,
        "nodes": [_node_dict(node) for node in sliced.nodes],
        "edges": [_edge_dict(edge) for edge in sliced.edges],
        "summary": {
            "node_count": len(sliced.nodes),
            "edge_count": len(sliced.edges),
        },
        "metadata": dict(sliced.metadata),
    }


def temporal_summary(bundle: GraphBundle, *, when=None) -> dict:
    """Summarize dated graph events and stale claims for a course graph."""

    epistemap = _epistemap_bundle(bundle)
    active = graph_at(epistemap, when) if when is not None else epistemap
    events = timeline_events(active)
    reveal_at = events[-1]["time"] if events else None
    return {
        "at": str(when) if when is not None else "",
        "summary": {
            "node_count": len(active.nodes),
            "edge_count": len(active.edges),
            "timeline_event_count": len(events),
        },
        "events": events[:24],
        "stale_claims": stale_claims_after(active, reveal_at) if reveal_at else [],
        "fair_play_diagnostic": (
            fair_play_diagnostic(active, reveal_at=reveal_at)
            if reveal_at
            else {"rating": "no_timeline", "summary": {"claim_count": 0}, "claims": []}
        ),
    }


def temporal_claim_context(bundle: GraphBundle, claim_id: str, when) -> dict:
    """Return temporal status and evidence context for a claim-like node."""

    epistemap = _epistemap_bundle(bundle)
    return {
        "claim_id": claim_id,
        "at": str(when),
        "status": claim_status_at(epistemap, claim_id, when),
        "evidence": evidence_available_at(epistemap, claim_id, when),
        "tenability_window": tenability_window(epistemap, claim_id),
    }


def _node_dict(node: Node | None) -> dict:
    if node is None:
        return {}
    payload = node.model_dump(exclude_none=True)
    metadata = payload.pop("metadata", {})
    payload.update(metadata)
    return payload


def _edge_dict(edge: Edge) -> dict:
    payload = edge.model_dump(exclude_none=True)
    metadata = payload.pop("metadata", {})
    payload.update(metadata)
    return payload


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
