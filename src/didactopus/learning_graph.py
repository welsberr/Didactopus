from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import networkx as nx

from .artifact_registry import PackValidationResult, topological_pack_order
from .profile_templates import resolve_mastery_profile


def namespaced_concept(pack_name: str, concept_id: str) -> str:
    return f"{pack_name}::{concept_id}"


@dataclass
class MergedLearningGraph:
    concept_data: dict[str, dict[str, Any]] = field(default_factory=dict)
    stage_catalog: list[dict[str, Any]] = field(default_factory=list)
    project_catalog: list[dict[str, Any]] = field(default_factory=list)
    load_order: list[str] = field(default_factory=list)
    graph: nx.DiGraph = field(default_factory=nx.DiGraph)


def build_merged_learning_graph(
    results: list[PackValidationResult],
    default_dimension_thresholds: dict[str, float] | None = None,
) -> MergedLearningGraph:
    merged = MergedLearningGraph()
    default_dimension_thresholds = default_dimension_thresholds or {
        "correctness": 0.8,
        "explanation": 0.75,
        "transfer": 0.7,
        "project_execution": 0.75,
        "critique": 0.7,
    }
    valid = {r.manifest.name: r for r in results if r.manifest is not None and r.is_valid}
    merged.load_order = topological_pack_order(results)

    for pack_name in merged.load_order:
        result = valid[pack_name]
        templates = {
            name: {
                "required_dimensions": list(spec.required_dimensions),
                "dimension_threshold_overrides": dict(spec.dimension_threshold_overrides),
            }
            for name, spec in result.manifest.profile_templates.items()
        }
        for concept in result.loaded_files["concepts"].concepts:
            override_key = next(
                (
                    override
                    for override in result.manifest.overrides
                    if override.split("::")[-1] == concept.id
                ),
                None,
            )
            key = override_key or namespaced_concept(pack_name, concept.id)
            resolved_profile = resolve_mastery_profile(
                concept.mastery_profile.model_dump(),
                templates,
                default_dimension_thresholds,
            )
            merged.concept_data[key] = {
                "id": concept.id,
                "title": concept.title,
                "description": concept.description,
                "pack": pack_name,
                "prerequisites": [namespaced_concept(pack_name, p) for p in concept.prerequisites],
                "mastery_signals": list(concept.mastery_signals),
                "mastery_profile": resolved_profile,
            }
        for stage in result.loaded_files["roadmap"].stages:
            merged.stage_catalog.append({
                "id": f"{pack_name}::{stage.id}",
                "pack": pack_name,
                "title": stage.title,
                "concepts": [
                    next(
                        (
                            override
                            for override in result.manifest.overrides
                            if override.split("::")[-1] == concept_id
                        ),
                        namespaced_concept(pack_name, concept_id),
                    )
                    for concept_id in stage.concepts
                ],
                "checkpoint": list(stage.checkpoint),
            })
        for project in result.loaded_files["projects"].projects:
            merged.project_catalog.append({
                "id": f"{pack_name}::{project.id}",
                "pack": pack_name,
                "title": project.title,
                "difficulty": project.difficulty,
                "prerequisites": [namespaced_concept(pack_name, p) for p in project.prerequisites],
                "deliverables": list(project.deliverables),
            })

    for concept_key, concept in merged.concept_data.items():
        merged.graph.add_node(concept_key)
        for prereq in concept["prerequisites"]:
            if prereq in merged.concept_data:
                merged.graph.add_edge(prereq, concept_key)
    return merged


def generate_learner_roadmap(merged: MergedLearningGraph) -> list[dict[str, Any]]:
    roadmap: list[dict[str, Any]] = []
    for stage in merged.stage_catalog:
        for concept_key in stage["concepts"]:
            if concept_key not in merged.concept_data:
                continue
            concept = merged.concept_data[concept_key]
            roadmap.append({
                "stage_id": stage["id"],
                "stage_title": stage["title"],
                "concept_key": concept_key,
                "title": concept["title"],
                "pack": concept["pack"],
            })
    return roadmap
