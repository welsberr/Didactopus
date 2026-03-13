from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from pathlib import Path
import json
import networkx as nx

REL_PREREQ = "prerequisite"
REL_EQUIVALENT = "equivalent_to"
REL_RELATED = "related_to"
REL_EXTENDS = "extends"
REL_DEPENDS = "depends_on"


@dataclass
class ConceptGraph:
    graph: nx.MultiDiGraph = field(default_factory=nx.MultiDiGraph)

    def add_concept(self, concept_key: str, metadata: dict[str, Any] | None = None) -> None:
        self.graph.add_node(concept_key, **(metadata or {}))

    def add_edge(self, source: str, target: str, relation: str) -> None:
        self.graph.add_edge(source, target, relation=relation)

    def add_prerequisite(self, prereq: str, concept: str) -> None:
        self.add_edge(prereq, concept, REL_PREREQ)

    def add_cross_link(self, source: str, target: str, relation: str) -> None:
        self.add_edge(source, target, relation)

    def prerequisite_subgraph(self) -> nx.DiGraph:
        g = nx.DiGraph()
        for node, data in self.graph.nodes(data=True):
            g.add_node(node, **data)
        for u, v, data in self.graph.edges(data=True):
            if data.get("relation") == REL_PREREQ:
                g.add_edge(u, v)
        return g

    def prerequisites(self, concept: str) -> list[str]:
        return list(self.prerequisite_subgraph().predecessors(concept))

    def prerequisite_chain(self, concept: str) -> list[str]:
        return list(nx.ancestors(self.prerequisite_subgraph(), concept))

    def dependents(self, concept: str) -> list[str]:
        return list(self.prerequisite_subgraph().successors(concept))

    def learning_path(self, start: str, target: str) -> list[str] | None:
        try:
            return nx.shortest_path(self.prerequisite_subgraph(), start, target)
        except nx.NetworkXNoPath:
            return None

    def curriculum_path_to_target(self, mastered: set[str], target: str) -> list[str]:
        pg = self.prerequisite_subgraph()
        needed = set(nx.ancestors(pg, target)) | {target}
        ordered = [n for n in nx.topological_sort(pg) if n in needed]
        return [n for n in ordered if n not in mastered]

    def ready_concepts(self, mastered: set[str]) -> list[str]:
        pg = self.prerequisite_subgraph()
        ready = []
        for node in pg.nodes:
            if node in mastered:
                continue
            if set(pg.predecessors(node)).issubset(mastered):
                ready.append(node)
        return ready

    def related_concepts(self, concept: str, relation_types: set[str] | None = None) -> list[str]:
        relation_types = relation_types or {REL_EQUIVALENT, REL_RELATED, REL_EXTENDS, REL_DEPENDS}
        found = []
        for _, v, data in self.graph.out_edges(concept, data=True):
            if data.get("relation") in relation_types:
                found.append(v)
        return found

    def export_graphviz(self, path: str) -> None:
        lines = ["digraph Didactopus {"]
        for node in self.graph.nodes:
            lines.append(f'  "{node}";')
        for u, v, data in self.graph.edges(data=True):
            lines.append(f'  "{u}" -> "{v}" [label="{data.get("relation", "")}"];')
        lines.append("}")
        Path(path).write_text("\n".join(lines), encoding="utf-8")

    def export_cytoscape_json(self, path: str) -> None:
        data = {
            "nodes": [{"data": {"id": n, **attrs}} for n, attrs in self.graph.nodes(data=True)],
            "edges": [{"data": {"source": u, "target": v, **attrs}} for u, v, attrs in self.graph.edges(data=True)],
        }
        Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")
