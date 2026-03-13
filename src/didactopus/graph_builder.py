from __future__ import annotations

from .artifact_registry import PackValidationResult
from .concept_graph import ConceptGraph
from .learning_graph import build_merged_learning_graph, namespaced_concept
from .semantic_similarity import concept_similarity


def build_concept_graph(
    results: list[PackValidationResult],
    default_dimension_thresholds: dict[str, float],
) -> ConceptGraph:
    merged = build_merged_learning_graph(results, default_dimension_thresholds)

    graph = ConceptGraph()
    for concept_key, data in merged.concept_data.items():
        graph.add_concept(concept_key, data)

    for concept_key, data in merged.concept_data.items():
        for prereq in data["prerequisites"]:
            if prereq in merged.concept_data:
                graph.add_prerequisite(prereq, concept_key)

    for result in results:
        if result.manifest is None or not result.is_valid:
            continue
        pack_name = result.manifest.name
        for link in result.manifest.cross_pack_links:
            source = link.source_concept if "::" in link.source_concept else namespaced_concept(pack_name, link.source_concept)
            target = link.target_concept
            if source in graph.graph.nodes and target in graph.graph.nodes:
                graph.add_cross_link(source, target, link.relation)

    return graph


def suggest_semantic_links(graph: ConceptGraph, minimum_similarity: float = 0.35) -> list[tuple[str, str, float]]:
    concepts = list(graph.graph.nodes(data=True))
    found = []
    for i in range(len(concepts)):
        key_a, data_a = concepts[i]
        for j in range(i + 1, len(concepts)):
            key_b, data_b = concepts[j]
            if key_a.split("::")[0] == key_b.split("::")[0]:
                continue
            sim = concept_similarity(data_a, data_b)
            if sim >= minimum_similarity:
                found.append((key_a, key_b, sim))
    return sorted(found, key=lambda x: x[2], reverse=True)
