from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GraphBundle:
    knowledge_graph: dict
    source_corpus: dict


def concept_node_id(concept_id: str) -> str:
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
