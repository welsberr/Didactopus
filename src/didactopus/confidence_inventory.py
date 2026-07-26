from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


CONFIDENCE_PATTERN = re.compile(r"\bconfidence_hint\b|\bconfidence\b")


def scan_confidence_inventory(src_root: str | Path) -> dict[str, Any]:
    root = Path(src_root)
    entries: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        rel = path.relative_to(root.parent).as_posix()
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            for match in CONFIDENCE_PATTERN.finditer(line):
                entries.append(
                    {
                        "path": rel,
                        "line": lineno,
                        "field": match.group(0),
                        "category": classify_confidence_occurrence(rel, line),
                        "line_text": line.strip(),
                    }
                )
    return {
        "inventory_kind": "didactopus_confidence_inventory",
        "schema_version": "1.0",
        "entry_count": len(entries),
        "entries": entries,
    }


def classify_confidence_occurrence(path: str, line: str) -> str:
    if "confidence.py" in path or "confidence_inventory.py" in path:
        return "confidence_contract_tooling"
    if "ai_learner_benchmark" in path or "source_spine_transfer_experiment" in path:
        return "benchmark_response_probability"
    if "learner_state" in path or "progression_engine" in path or "stop_criteria" in path or "readiness" in path or "recommendations" in path:
        return "learner_state_mastery"
    if "evidence_flow_ledger_qa" in path:
        return "learner_state_confidence_qa"
    if "learner_workbench" in path:
        return "learner_workbench_guidance"
    if "orm.py" in path or "repository.py" in path or "models.py" in path:
        return "api_or_orm_boundary"
    if "groundrecall" in path:
        return "groundrecall_bridge_legacy"
    if "citation_extract" in path:
        return "citation_extraction_hint"
    if "knowledge_graph" in path or "graph_retrieval" in path:
        return "graph_extraction_assessment"
    if "evidence_engine" in path:
        return "evidence_coverage_alias"
    if "knowledge_export" in path:
        return "knowledge_export_legacy"
    if "api.py" in path:
        return "api_or_orm_boundary"
    if "orchestrator" in path or "ensemble_ingest" in path:
        return "candidate_extraction_hint"
    return "unclassified"


def write_confidence_inventory(src_root: str | Path, out_path: str | Path) -> dict[str, Any]:
    payload = scan_confidence_inventory(src_root)
    target = Path(out_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload
