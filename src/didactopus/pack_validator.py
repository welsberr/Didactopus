from __future__ import annotations
from pathlib import Path
import yaml

REQUIRED_FILES = ["pack.yaml", "concepts.yaml", "roadmap.yaml", "projects.yaml", "rubrics.yaml"]

def _safe_load_yaml(path: Path, errors: list[str], label: str):
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        errors.append(f"Could not parse {label}: {exc}")
        return {}

def validate_pack_directory(source_dir: str | Path) -> dict:
    source = Path(source_dir)
    errors: list[str] = []
    warnings: list[str] = []
    summary: dict = {}

    if not source.exists():
        return {"ok": False, "errors": [f"Source directory does not exist: {source}"], "warnings": [], "summary": {}}
    if not source.is_dir():
        return {"ok": False, "errors": [f"Source path is not a directory: {source}"], "warnings": [], "summary": {}}

    for filename in REQUIRED_FILES:
        if not (source / filename).exists():
            errors.append(f"Missing required file: {filename}")

    if errors:
        return {"ok": False, "errors": errors, "warnings": warnings, "summary": summary}

    pack_data = _safe_load_yaml(source / "pack.yaml", errors, "pack.yaml")
    concepts_data = _safe_load_yaml(source / "concepts.yaml", errors, "concepts.yaml")
    roadmap_data = _safe_load_yaml(source / "roadmap.yaml", errors, "roadmap.yaml")
    projects_data = _safe_load_yaml(source / "projects.yaml", errors, "projects.yaml")
    rubrics_data = _safe_load_yaml(source / "rubrics.yaml", errors, "rubrics.yaml")

    if errors:
        return {"ok": False, "errors": errors, "warnings": warnings, "summary": summary}

    for field in ["name", "display_name", "version"]:
        if field not in pack_data:
            warnings.append(f"pack.yaml has no '{field}' field.")

    concepts = concepts_data.get("concepts", [])
    roadmap_stages = roadmap_data.get("stages", [])
    projects = projects_data.get("projects", [])
    rubrics = rubrics_data.get("rubrics", [])

    if not isinstance(concepts, list):
        errors.append("concepts.yaml top-level 'concepts' is not a list.")
        concepts = []
    if not isinstance(roadmap_stages, list):
        errors.append("roadmap.yaml top-level 'stages' is not a list.")
        roadmap_stages = []
    if not isinstance(projects, list):
        errors.append("projects.yaml top-level 'projects' is not a list.")
        projects = []
    if not isinstance(rubrics, list):
        errors.append("rubrics.yaml top-level 'rubrics' is not a list.")
        rubrics = []

    concept_ids = []
    for idx, concept in enumerate(concepts):
        cid = concept.get("id", "")
        if not cid:
            errors.append(f"Concept at index {idx} has no id.")
        else:
            concept_ids.append(cid)
        if not concept.get("title"):
            warnings.append(f"Concept '{cid or idx}' has no title.")
        desc = str(concept.get("description", "") or "")
        if len(desc.strip()) < 12:
            warnings.append(f"Concept '{cid or idx}' has a very thin description.")

    seen = set()
    dups = set()
    for cid in concept_ids:
        if cid in seen:
            dups.add(cid)
        seen.add(cid)
    for cid in sorted(dups):
        errors.append(f"Duplicate concept id: {cid}")

    concept_id_set = set(concept_ids)

    for stage in roadmap_stages:
        for cid in stage.get("concepts", []) or []:
            if cid not in concept_id_set:
                errors.append(f"roadmap.yaml references missing concept id: {cid}")

    for project in projects:
        if not project.get("id"):
            warnings.append("A project entry has no id.")
        for cid in project.get("prerequisites", []) or []:
            if cid not in concept_id_set:
                errors.append(f"projects.yaml references missing prerequisite concept id: {cid}")

    for idx, rubric in enumerate(rubrics):
        if not rubric.get("id"):
            warnings.append(f"Rubric at index {idx} has no id.")
        criteria = rubric.get("criteria", [])
        if criteria is None:
            warnings.append(f"Rubric '{rubric.get('id', idx)}' has null criteria.")
        elif isinstance(criteria, list) and len(criteria) == 0:
            warnings.append(f"Rubric '{rubric.get('id', idx)}' has empty criteria.")
        elif not isinstance(criteria, list):
            errors.append(f"Rubric '{rubric.get('id', idx)}' criteria is not a list.")

    summary = {
        "pack_name": pack_data.get("name", ""),
        "display_name": pack_data.get("display_name", ""),
        "version": pack_data.get("version", ""),
        "concept_count": len(concepts),
        "roadmap_stage_count": len(roadmap_stages),
        "project_count": len(projects),
        "rubric_count": len(rubrics),
        "error_count": len(errors),
        "warning_count": len(warnings),
    }
    return {"ok": len(errors) == 0, "errors": errors, "warnings": warnings, "summary": summary}
