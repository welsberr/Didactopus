from pathlib import Path
from .review_schema import ImportPreview
from .pack_validator import validate_pack_directory
from .semantic_qa import semantic_qa_for_pack
from .graph_qa import graph_qa_for_pack
from .path_quality_qa import path_quality_for_pack
from .coverage_alignment_qa import coverage_alignment_for_pack
from .evaluator_alignment_qa import evaluator_alignment_for_pack
from .evidence_flow_ledger_qa import evidence_flow_ledger_for_pack

def preview_draft_pack_import(source_dir, workspace_id, overwrite_required=False):
    result = validate_pack_directory(source_dir)
    semantic = semantic_qa_for_pack(source_dir) if result["ok"] else {"warnings": []}
    graph = graph_qa_for_pack(source_dir) if result["ok"] else {"warnings": []}
    pathq = path_quality_for_pack(source_dir) if result["ok"] else {"warnings": []}
    coverage = coverage_alignment_for_pack(source_dir) if result["ok"] else {"warnings": []}
    evaluator = evaluator_alignment_for_pack(source_dir) if result["ok"] else {"warnings": []}
    ledger = evidence_flow_ledger_for_pack(source_dir) if result["ok"] else {"warnings": []}
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
        coverage_warnings=list(coverage["warnings"]),
        evaluator_warnings=list(evaluator["warnings"]),
        ledger_warnings=list(ledger["warnings"]),
    )
