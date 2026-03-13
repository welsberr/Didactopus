from dataclasses import dataclass
import networkx as nx


@dataclass
class RoadmapStage:
    title: str
    concepts: list[str]
    mastery_goal: str


def generate_stages_from_learning_graph(graph: nx.DiGraph) -> list[RoadmapStage]:
    sequence = list(nx.topological_sort(graph))
    return [
        RoadmapStage(
            title=f"Stage {i+1}: {concept.split('::')[-1].replace('-', ' ').title()}",
            concepts=[concept],
            mastery_goal=f"Demonstrate applied understanding of {concept}.",
        )
        for i, concept in enumerate(sequence)
    ]
