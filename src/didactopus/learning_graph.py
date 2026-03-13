from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .artifact_registry import PackValidationResult, topological_pack_order
from .profile_templates import resolve_mastery_profile


def namespaced_concept(pack_name: str, concept_id: str) -> str:
    return f"{pack_name}::{concept_id}"


@dataclass
class MergedLearningGraph:
    concept_data: dict[str, dict[str, Any]] = field(default_factory=dict)
    project_catalog: list[dict[str, Any]] = field(default_factory=list)
    load_order: list[str] = field(default_factory=list)


def build_merged_learning_graph(
    results: list[PackValidationResult],
    default_dimension_thresholds: dict[str, float],
) -> MergedLearningGraph:
    merged = MergedLearningGraph()
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
            key = namespaced_concept(pack_name, concept.id)
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
