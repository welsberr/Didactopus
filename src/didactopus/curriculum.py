from dataclasses import dataclass
from .domain_map import DomainMap


@dataclass
class RoadmapStage:
    title: str
    concepts: list[str]
    mastery_goal: str


def generate_initial_roadmap(domain_map: DomainMap, goal: str) -> list[RoadmapStage]:
    sequence = domain_map.topological_sequence()
    return [
        RoadmapStage(
            title=f"Stage {idx + 1}: {concept.title()}",
            concepts=[concept],
            mastery_goal=f"Demonstrate applied understanding of {concept} toward goal: {goal}",
        )
        for idx, concept in enumerate(sequence)
    ]
