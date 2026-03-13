from __future__ import annotations

from dataclasses import dataclass
from math import inf

from .concept_graph import ConceptGraph
from .semantic_similarity import concept_similarity


@dataclass
class PlannerWeights:
    readiness_bonus: float = 2.0
    target_distance_weight: float = 1.0
    weak_dimension_bonus: float = 1.2
    fragile_review_bonus: float = 1.5
    project_unlock_bonus: float = 0.8
    semantic_similarity_weight: float = 1.0


def _distance_bonus(graph: ConceptGraph, concept: str, targets: list[str]) -> float:
    pg = graph.prerequisite_subgraph()
    best = inf
    for target in targets:
        try:
            import networkx as nx
            dist = len(nx.shortest_path(pg, concept, target)) - 1
            best = min(best, dist)
        except Exception:
            continue
    if best is inf:
        return 0.0
    return 1.0 / (1.0 + best)


def _project_unlock_bonus(concept: str, project_catalog: list[dict]) -> float:
    return float(sum(1 for project in project_catalog if concept in project.get("prerequisites", [])))


def _semantic_bonus(graph: ConceptGraph, concept: str, targets: list[str]) -> float:
    data_a = graph.graph.nodes[concept]
    best = 0.0
    for target in targets:
        if target not in graph.graph.nodes:
            continue
        data_b = graph.graph.nodes[target]
        best = max(best, concept_similarity(data_a, data_b))
    return best


def rank_next_concepts(
    graph: ConceptGraph,
    mastered: set[str],
    targets: list[str],
    weak_dimensions_by_concept: dict[str, list[str]],
    fragile_concepts: set[str],
    project_catalog: list[dict],
    weights: PlannerWeights,
) -> list[dict]:
    ready = graph.ready_concepts(mastered)
    ranked = []

    for concept in ready:
        score = 0.0
        components = {}

        readiness = weights.readiness_bonus
        score += readiness
        components["readiness"] = readiness

        distance = weights.target_distance_weight * _distance_bonus(graph, concept, targets)
        score += distance
        components["target_distance"] = distance

        weak = weights.weak_dimension_bonus * len(weak_dimensions_by_concept.get(concept, []))
        score += weak
        components["weak_dimensions"] = weak

        fragile = weights.fragile_review_bonus if concept in fragile_concepts else 0.0
        score += fragile
        components["fragile_review"] = fragile

        project = weights.project_unlock_bonus * _project_unlock_bonus(concept, project_catalog)
        score += project
        components["project_unlock"] = project

        semantic = weights.semantic_similarity_weight * _semantic_bonus(graph, concept, targets)
        score += semantic
        components["semantic_similarity"] = semantic

        ranked.append({"concept": concept, "score": score, "components": components})

    ranked.sort(key=lambda item: item["score"], reverse=True)
    return ranked
