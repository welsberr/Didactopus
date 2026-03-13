from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import networkx as nx

from .artifact_registry import PackValidationResult, topological_pack_order


def namespaced_concept(pack_name: str, concept_id: str) -> str:
    return f"{pack_name}::{concept_id}"


@dataclass
class MergedLearningGraph:
    graph: nx.DiGraph = field(default_factory=nx.DiGraph)
    concept_data: dict[str, dict[str, Any]] = field(default_factory=dict)
    project_catalog: list[dict[str, Any]] = field(default_factory=list)
    load_order: list[str] = field(default_factory=list)


def build_merged_learning_graph(results: list[PackValidationResult]) -> MergedLearningGraph:
    merged = MergedLearningGraph()
    valid = {r.manifest.name: r for r in results if r.manifest is not None and r.is_valid}
    merged.load_order = topological_pack_order(results)

    for pack_name in merged.load_order:
        result = valid[pack_name]
        for concept in result.loaded_files["concepts"].concepts:
            key = namespaced_concept(pack_name, concept.id)
            merged.concept_data[key] = {
                "id": concept.id,
                "title": concept.title,
                "pack": pack_name,
                "prerequisites": list(concept.prerequisites),
                "mastery_signals": list(concept.mastery_signals),
            }
            merged.graph.add_node(key)

    for pack_name in merged.load_order:
        result = valid[pack_name]
        for concept in result.loaded_files["concepts"].concepts:
            concept_key = namespaced_concept(pack_name, concept.id)
            for prereq in concept.prerequisites:
                prereq_key = namespaced_concept(pack_name, prereq)
                if prereq_key in merged.graph:
                    merged.graph.add_edge(prereq_key, concept_key)
        for project in result.loaded_files["projects"].projects:
            merged.project_catalog.append({
                "id": f"{pack_name}::{project.id}",
                "pack": pack_name,
                "title": project.title,
                "difficulty": project.difficulty,
                "prerequisites": [namespaced_concept(pack_name, p) for p in project.prerequisites],
                "deliverables": list(project.deliverables),
            })
    return merged
