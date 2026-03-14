from __future__ import annotations
from pathlib import Path
import yaml
from .review_schema import ImportPreview

REQUIRED_FILES = ["pack.yaml", "concepts.yaml"]

def preview_draft_pack_import(source_dir: str | Path, workspace_id: str, overwrite_required: bool = False) -> ImportPreview:
    source = Path(source_dir)
    preview = ImportPreview(source_dir=str(source), workspace_id=workspace_id, overwrite_required=overwrite_required)

    if not source.exists():
        preview.errors.append(f"Source directory does not exist: {source}")
        return preview
    if not source.is_dir():
        preview.errors.append(f"Source path is not a directory: {source}")
        return preview

    for filename in REQUIRED_FILES:
        if not (source / filename).exists():
            preview.errors.append(f"Missing required file: {filename}")

    pack_data = {}
    concepts_data = {}
    if not preview.errors:
        try:
            pack_data = yaml.safe_load((source / "pack.yaml").read_text(encoding="utf-8")) or {}
        except Exception as exc:
            preview.errors.append(f"Could not parse pack.yaml: {exc}")
        try:
            concepts_data = yaml.safe_load((source / "concepts.yaml").read_text(encoding="utf-8")) or {}
        except Exception as exc:
            preview.errors.append(f"Could not parse concepts.yaml: {exc}")

    if not preview.errors:
        if "name" not in pack_data:
            preview.warnings.append("pack.yaml has no 'name' field.")
        if "display_name" not in pack_data:
            preview.warnings.append("pack.yaml has no 'display_name' field.")
        concepts = concepts_data.get("concepts", [])
        if not isinstance(concepts, list):
            preview.errors.append("concepts.yaml top-level 'concepts' is not a list.")
        else:
            preview.summary = {
                "pack_name": pack_data.get("name", ""),
                "display_name": pack_data.get("display_name", ""),
                "version": pack_data.get("version", ""),
                "concept_count": len(concepts),
                "has_conflict_report": (source / "conflict_report.md").exists(),
                "has_review_report": (source / "review_report.md").exists(),
            }
            if len(concepts) == 0:
                preview.warnings.append("concepts.yaml contains zero concepts.")

    preview.ok = len(preview.errors) == 0
    return preview
