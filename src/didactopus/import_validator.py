from __future__ import annotations
from pathlib import Path
from .review_schema import ImportPreview
from .pack_validator import validate_pack_directory

def preview_draft_pack_import(source_dir: str | Path, workspace_id: str, overwrite_required: bool = False) -> ImportPreview:
    result = validate_pack_directory(source_dir)
    preview = ImportPreview(
        source_dir=str(Path(source_dir)),
        workspace_id=workspace_id,
        overwrite_required=overwrite_required,
        ok=result["ok"],
        errors=list(result["errors"]),
        warnings=list(result["warnings"]),
        summary=dict(result["summary"]),
    )
    return preview
