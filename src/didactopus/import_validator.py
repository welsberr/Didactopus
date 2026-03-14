from pathlib import Path
from .review_schema import ImportPreview
from .pack_validator import validate_pack_directory
from .evaluator_alignment_qa import evaluator_alignment_for_pack
def preview_draft_pack_import(source_dir, workspace_id, overwrite_required=False):
    result=validate_pack_directory(source_dir)
    evaluator=evaluator_alignment_for_pack(source_dir) if result["ok"] else {"warnings":[]}
    return ImportPreview(source_dir=str(Path(source_dir)),workspace_id=workspace_id,overwrite_required=overwrite_required,ok=result["ok"],errors=list(result["errors"]),warnings=list(result["warnings"]),summary=dict(result["summary"]),evaluator_warnings=list(evaluator["warnings"]))
