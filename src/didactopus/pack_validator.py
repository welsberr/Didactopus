from pathlib import Path
import yaml

REQUIRED_FILES = ["pack.yaml","concepts.yaml","roadmap.yaml","projects.yaml","rubrics.yaml","evaluator.yaml","mastery_ledger.yaml"]

def _load(path: Path, errors: list[str], label: str):
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        errors.append(f"Could not parse {label}: {exc}")
        return {}

def load_pack_artifacts(source_dir):
    source = Path(source_dir)
    errors = []
    if not source.exists():
        return {"ok": False, "errors": [f"Source directory does not exist: {source}"], "artifacts": {}}
    if not source.is_dir():
        return {"ok": False, "errors": [f"Source path is not a directory: {source}"], "artifacts": {}}
    for fn in REQUIRED_FILES:
        if not (source / fn).exists():
            errors.append(f"Missing required file: {fn}")
    if errors:
        return {"ok": False, "errors": errors, "artifacts": {}}
    arts = {}
    for stem in ["pack","concepts","roadmap","projects","rubrics","evaluator","mastery_ledger"]:
        arts[stem] = _load(source / f"{stem}.yaml", errors, f"{stem}.yaml")
    return {"ok": len(errors) == 0, "errors": errors, "artifacts": arts}

def validate_pack_directory(source_dir):
    loaded = load_pack_artifacts(source_dir)
    if not loaded["ok"]:
        return {"ok": False, "errors": loaded["errors"], "warnings": [], "summary": {}}
    arts = loaded["artifacts"]
    concepts = arts["concepts"].get("concepts", []) or []
    dims = arts["evaluator"].get("dimensions", []) or []
    summary = {
        "pack_name": arts["pack"].get("name", ""),
        "display_name": arts["pack"].get("display_name", ""),
        "version": arts["pack"].get("version", ""),
        "concept_count": len(concepts),
        "evaluator_dimension_count": len(dims),
        "ledger_field_count": len((arts["mastery_ledger"].get("entry_schema", {}) or {}).keys()),
    }
    return {"ok": True, "errors": [], "warnings": [], "summary": summary}
