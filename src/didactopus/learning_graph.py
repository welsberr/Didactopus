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
    stage_catalog: list[dict[str, Any]] = field(default_factory=list)
    project_catalog: list[dict[str, Any]] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    load_order: list[str] = field(default_factory=list)


def _build_override_targets(results: list[PackValidationResult]) -> set[str]:
    targets: set[str] = set()
    for result in results:
        if result.manifest is None or not result.is_valid:
            continue
        targets.update(result.manifest.overrides)
    return targets


def build_merged_learning_graph(results: list[PackValidationResult]) -> MergedLearningGraph:
    merged = MergedLearningGraph()
    valid = {
        r.manifest.name: r
        for r in results
        if r.manifest is not None and r.is_valid
    }
    merged.load_order = topological_pack_order(results)
    override_targets = _build_override_targets(results)

    # Add concepts
    for pack_name in merged.load_order:
        result = valid[pack_name]
        concepts_file = result.loaded_files.get("concepts")
        if concepts_file is None:
            continue

        for concept in concepts_file.concepts:
            local_key = namespaced_concept(pack_name, concept.id)

            # explicit override support: same local concept ID may replace one namespaced target
            replaced = False
            for target in result.manifest.overrides:
                if target.split("::")[-1] == concept.id and target in merged.concept_data:
                    merged.concept_data[target] = {
                        "id": concept.id,
                        "title": concept.title,
                        "pack": pack_name,
                        "prerequisites": [],
                        "mastery_signals": list(concept.mastery_signals),
                        "overridden_by": local_key,
                    }
                    replaced = True
                    break

            if replaced:
                continue

            if local_key in merged.concept_data:
                merged.conflicts.append(f"duplicate namespaced concept key: {local_key}")
                continue

            merged.concept_data[local_key] = {
                "id": concept.id,
                "title": concept.title,
                "pack": pack_name,
                "prerequisites": list(concept.prerequisites),
                "mastery_signals": list(concept.mastery_signals),
            }
            merged.graph.add_node(local_key)

    # Add prerequisite edges within each pack
    for pack_name in merged.load_order:
        result = valid[pack_name]
        concepts_file = result.loaded_files.get("concepts")
        if concepts_file is None:
            continue
        for concept in concepts_file.concepts:
            concept_key = namespaced_concept(pack_name, concept.id)
            if concept_key not in merged.graph:
                continue
            for prereq in concept.prerequisites:
                prereq_key = namespaced_concept(pack_name, prereq)
                if prereq_key in merged.graph:
                    merged.graph.add_edge(prereq_key, concept_key)
                else:
                    merged.conflicts.append(
                        f"missing namespaced prerequisite '{prereq_key}' for concept '{concept_key}'"
                    )

    # Merge stage catalog
    for pack_name in merged.load_order:
        result = valid[pack_name]
        roadmap_file = result.loaded_files.get("roadmap")
        if roadmap_file is None:
            continue
        for stage in roadmap_file.stages:
            merged.stage_catalog.append(
                {
                    "id": f"{pack_name}::{stage.id}",
                    "pack": pack_name,
                    "title": stage.title,
                    "concepts": [namespaced_concept(pack_name, c) for c in stage.concepts],
                    "checkpoint": list(stage.checkpoint),
                }
            )

    # Merge project catalog
    for pack_name in merged.load_order:
        result = valid[pack_name]
        projects_file = result.loaded_files.get("projects")
        if projects_file is None:
            continue
        for project in projects_file.projects:
            merged.project_catalog.append(
                {
                    "id": f"{pack_name}::{project.id}",
                    "pack": pack_name,
                    "title": project.title,
                    "difficulty": project.difficulty,
                    "prerequisites": [namespaced_concept(pack_name, p) for p in project.prerequisites],
                    "deliverables": list(project.deliverables),
                }
            )

    return merged


def generate_learner_roadmap(merged: MergedLearningGraph) -> list[dict[str, Any]]:
    roadmap: list[dict[str, Any]] = []
    for i, concept_key in enumerate(nx.topological_sort(merged.graph), start=1):
        data = merged.concept_data[concept_key]
        roadmap.append(
            {
                "stage_number": i,
                "concept_key": concept_key,
                "title": data["title"],
                "pack": data["pack"],
                "prerequisites": list(merged.graph.predecessors(concept_key)),
            }
        )
    return roadmap
