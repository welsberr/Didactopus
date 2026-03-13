from dataclasses import dataclass, field
import networkx as nx


@dataclass
class ConceptNode:
    name: str
    description: str = ""
    prerequisites: list[str] = field(default_factory=list)


class DomainMap:
    def __init__(self, domain_name: str) -> None:
        self.domain_name = domain_name
        self.graph = nx.DiGraph()

    def add_concept(self, node: ConceptNode) -> None:
        self.graph.add_node(node.name, data=node)
        for prereq in node.prerequisites:
            self.graph.add_edge(prereq, node.name)

    def prerequisites_for(self, concept: str) -> list[str]:
        return list(nx.ancestors(self.graph, concept))

    def topological_sequence(self) -> list[str]:
        return list(nx.topological_sort(self.graph))


def build_demo_domain_map(domain_name: str) -> DomainMap:
    dmap = DomainMap(domain_name)
    dmap.add_concept(ConceptNode("foundations", "Core assumptions and terminology"))
    dmap.add_concept(ConceptNode("methods", "Basic methods", ["foundations"]))
    dmap.add_concept(ConceptNode("analysis", "Applying methods", ["methods"]))
    dmap.add_concept(ConceptNode("projects", "Real-world capstones", ["analysis"]))
    return dmap
