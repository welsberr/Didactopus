from pathlib import Path
import yaml

REQUIRED_FILES = ["pack.yaml","concepts.yaml","roadmap.yaml","projects.yaml","rubrics.yaml"]

def _safe_load_yaml(path: Path, errors: list[str], label: str):
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        errors.append(f"Could not parse {label}: {exc}")
        return {}

def load_pack_artifacts(source_dir):
    source = Path(source_dir)
    errors = []
    if not source.exists():
        return {"ok": False, "errors": [f"Source directory does not exist: {source}"], "warnings": [], "summary": {}, "artifacts": {}}
    if not source.is_dir():
        return {"ok": False, "errors": [f"Source path is not a directory: {source}"], "warnings": [], "summary": {}, "artifacts": {}}
    for fn in REQUIRED_FILES:
        if not (source/fn).exists():
            errors.append(f"Missing required file: {fn}")
    if errors:
        return {"ok": False, "errors": errors, "warnings": [], "summary": {}, "artifacts": {}}
    return {
        "ok": True, "errors": [], "warnings": [], "summary": {},
        "artifacts": {
            "pack": _safe_load_yaml(source/"pack.yaml", errors, "pack.yaml"),
            "concepts": _safe_load_yaml(source/"concepts.yaml", errors, "concepts.yaml"),
            "roadmap": _safe_load_yaml(source/"roadmap.yaml", errors, "roadmap.yaml"),
            "projects": _safe_load_yaml(source/"projects.yaml", errors, "projects.yaml"),
            "rubrics": _safe_load_yaml(source/"rubrics.yaml", errors, "rubrics.yaml"),
        }
    }

def validate_pack_directory(source_dir):
    loaded = load_pack_artifacts(source_dir)
    errors = list(loaded["errors"]); warnings = list(loaded["warnings"]); summary = dict(loaded["summary"])
    if not loaded["ok"]:
        return {"ok": False, "errors": errors, "warnings": warnings, "summary": summary}
    pack = loaded["artifacts"]["pack"]; concepts = loaded["artifacts"]["concepts"].get("concepts", []) or []
    roadmap = loaded["artifacts"]["roadmap"].get("stages", []) or []
    projects = loaded["artifacts"]["projects"].get("projects", []) or []
    rubrics = loaded["artifacts"]["rubrics"].get("rubrics", []) or []
    for field in ["name","display_name","version"]:
        if field not in pack:
            warnings.append(f"pack.yaml has no '{field}' field.")
    ids = []
    for i, c in enumerate(concepts):
        cid = c.get("id","")
        if not cid:
            errors.append(f"Concept at index {i} has no id.")
        else:
            ids.append(cid)
        if len(str(c.get("description","")).strip()) < 12:
            warnings.append(f"Concept '{cid or i}' has a very thin description.")
    seen = set()
    for cid in ids:
        if cid in seen:
            errors.append(f"Duplicate concept id: {cid}")
        seen.add(cid)
    idset = set(ids)
    for stage in roadmap:
        for cid in stage.get("concepts", []) or []:
            if cid not in idset:
                errors.append(f"roadmap.yaml references missing concept id: {cid}")
    for project in projects:
        for cid in project.get("prerequisites", []) or []:
            if cid not in idset:
                errors.append(f"projects.yaml references missing prerequisite concept id: {cid}")
    for i, rubric in enumerate(rubrics):
        crit = rubric.get("criteria", [])
        if not rubric.get("id"):
            warnings.append(f"Rubric at index {i} has no id.")
        if crit is None:
            warnings.append(f"Rubric '{rubric.get('id', i)}' has null criteria.")
        elif isinstance(crit, list) and len(crit) == 0:
            warnings.append(f"Rubric '{rubric.get('id', i)}' has empty criteria.")
        elif not isinstance(crit, list):
            errors.append(f"Rubric '{rubric.get('id', i)}' criteria is not a list.")
    summary = {"pack_name": pack.get("name",""), "display_name": pack.get("display_name",""), "version": pack.get("version",""), "concept_count": len(concepts), "roadmap_stage_count": len(roadmap), "project_count": len(projects), "rubric_count": len(rubrics)}
    return {"ok": len(errors)==0, "errors": errors, "warnings": warnings, "summary": summary}
