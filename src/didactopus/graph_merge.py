from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .artifact_registry import PackValidationResult, topological_pack_order


@dataclass
class MergedConceptGraph:
    concept_by_id: dict[str, dict[str, Any]] = field(default_factory=dict)
    source_pack_by_concept: dict[str, str] = field(default_factory=dict)
    conflicts: list[str] = field(default_factory=list)
    load_order: list[str] = field(default_factory=list)


def merge_pack_concepts(results: list[PackValidationResult]) -> MergedConceptGraph:
    merged = MergedConceptGraph()
    manifest_by_name = {
        result.manifest.name: result
        for result in results
        if result.manifest is not None and result.is_valid
    }
    merged.load_order = topological_pack_order(results)

    for pack_name in merged.load_order:
        result = manifest_by_name[pack_name]
        concepts_file = result.loaded_files.get("concepts")
        if concepts_file is None:
            continue

        for concept in concepts_file.concepts:
            if concept.id in merged.concept_by_id:
                previous_pack = merged.source_pack_by_concept[concept.id]
                merged.conflicts.append(
                    f"concept '{concept.id}' defined in both '{previous_pack}' and '{pack_name}'"
                )
                continue

            merged.concept_by_id[concept.id] = {
                "id": concept.id,
                "title": concept.title,
                "prerequisites": list(concept.prerequisites),
                "mastery_signals": list(concept.mastery_signals),
            }
            merged.source_pack_by_concept[concept.id] = pack_name

    return merged
