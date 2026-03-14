from __future__ import annotations

from .pack_validator import load_pack_artifacts


def coverage_alignment_for_pack(source_dir):
    loaded = load_pack_artifacts(source_dir)
    if not loaded["ok"]:
        return {"warnings": [], "summary": {"coverage_warning_count": 0}}

    arts = loaded["artifacts"]
    concepts = arts["concepts"].get("concepts", []) or []
    roadmap = arts["roadmap"].get("stages", []) or []
    projects = arts["projects"].get("projects", []) or []

    covered = set()
    for stage in roadmap:
        covered.update(stage.get("concepts", []) or [])
    for project in projects:
        covered.update(project.get("prerequisites", []) or [])

    warnings = []
    for concept in concepts:
        concept_id = concept.get("id", "")
        if concept_id and concept_id not in covered:
            warnings.append(f"Concept '{concept_id}' is not covered by the roadmap or project prerequisites.")

    return {
        "warnings": warnings,
        "summary": {
            "coverage_warning_count": len(warnings),
            "concept_count": len(concepts),
            "covered_concept_count": len(covered),
        },
    }
