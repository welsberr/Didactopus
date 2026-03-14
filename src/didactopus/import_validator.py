from __future__ import annotations
from pathlib import Path
from .review_schema import ImportPreview
from .pack_validator import validate_pack_directory
from .semantic_qa import semantic_qa_for_pack
from .graph_qa import graph_qa_for_pack
from .path_quality_qa import path_quality_for_pack

def preview_draft_pack_import(source_dir: str | Path, workspace_id: str, overwrite_required: bool = False) -> ImportPreview:
    result = validate_pack_directory(source_dir)
    semantic = semantic_qa_for_pack(source_dir) if result["ok"] else {"warnings": []}
    graph = graph_qa_for_pack(source_dir) if result["ok"] else {"warnings": []}
    pathq = path_quality_for_pack(source_dir) if result["ok"] else {"warnings": []}
    return ImportPreview(
        source_dir=str(Path(source_dir)),
        workspace_id=workspace_id,
        overwrite_required=overwrite_required,
        ok=result["ok"],
        errors=list(result["errors"]),
        warnings=list(result["warnings"]),
        summary=dict(result["summary"]),
        semantic_warnings=list(semantic["warnings"]),
        graph_warnings=list(graph["warnings"]),
        path_warnings=list(pathq["warnings"]),
    )
