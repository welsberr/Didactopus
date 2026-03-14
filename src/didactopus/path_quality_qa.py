from __future__ import annotations

from .pack_validator import load_pack_artifacts


def path_quality_for_pack(source_dir):
    loaded = load_pack_artifacts(source_dir)
    if not loaded["ok"]:
        return {"warnings": [], "summary": {"path_warning_count": 0}}

    arts = loaded["artifacts"]
    concepts = arts["concepts"].get("concepts", []) or []
    roadmap = arts["roadmap"].get("stages", []) or []
    projects = arts["projects"].get("projects", []) or []

    assessed = set()
    warnings = []

    for stage in roadmap:
        stage_concepts = stage.get("concepts", []) or []
        checkpoint = stage.get("checkpoint", []) or []
        if checkpoint:
            assessed.update(stage_concepts)
        else:
            warnings.append(f"Stage '{stage.get('id', 'unknown')}' has no checkpoint.")

    for project in projects:
        assessed.update(project.get("prerequisites", []) or [])

    for concept in concepts:
        concept_id = concept.get("id", "")
        if concept_id and concept_id not in assessed:
            warnings.append(f"Concept '{concept_id}' is not visibly assessed in roadmap checkpoints or project prerequisites.")

    return {
        "warnings": warnings,
        "summary": {
            "path_warning_count": len(warnings),
            "stage_count": len(roadmap),
            "project_count": len(projects),
        },
    }
