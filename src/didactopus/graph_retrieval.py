from __future__ import annotations

from dataclasses import dataclass

from epistemap import Edge, GraphBundle as EpistemapBundle, Node, neighborhood


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
