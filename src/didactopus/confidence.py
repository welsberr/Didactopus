from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any, Iterable, Literal

from epistemap import AssessmentMethodRef, ConfidenceAssessment, confidence_band, deterministic_hash


MIGRATION_VERSION = "didactopus.confidence_migration.v1"
CANDIDATE_POLICY_ID = "didactopus_candidate_extraction_hint.v1"
CITATION_POLICY_ID = "didactopus_citation_extraction_hint.v1"


def _bounded(value: Any) -> float | None:
    if value in ("", None):
        return None
    numeric = float(value)
    if numeric < 0.0 or numeric > 1.0:
        raise ValueError(f"confidence value must be between 0 and 1: {numeric}")
    return numeric


def basis_hash(values: Iterable[str]) -> str:
    return deterministic_hash({"basis_record_ids": sorted(str(value) for value in values if str(value))})


def extraction_assessment(
    *,
    subject_id: str,
    value: float | None,
    basis_record_ids: list[str],
    policy_id: str,
    method_name: str,
    rationale: str,
    extracted_field: str = "confidence_hint",
    recorded_at: str = "2026-07-25T00:00:00Z",
) -> ConfidenceAssessment | None:
    numeric = _bounded(value)
    if numeric is None:
        return None
    return ConfidenceAssessment(
        assessment_id=f"{subject_id}::extraction_fidelity::{policy_id}",
        subject_id=subject_id,
        dimension="extraction_fidelity",
        value=numeric,
        band=confidence_band(numeric),
        method=AssessmentMethodRef(name=method_name, version="1.0", policy_id=policy_id),
        basis_record_ids=list(basis_record_ids),
        basis_hash=basis_hash(basis_record_ids),
        rationale=rationale,
        recorded_at=recorded_at,
        metadata={
            "migration_version": MIGRATION_VERSION,
            "extracted_field": extracted_field,
            "not_mastery": True,
            "not_source_truth": True,
        },
    )


def candidate_extraction_assessment(candidate: dict[str, Any], *, recorded_at: str = "2026-07-25T00:00:00Z") -> ConfidenceAssessment | None:
    candidate_id = str(candidate.get("candidate_id") or candidate.get("id") or candidate.get("title") or "candidate")
    basis_ids = [
        f"candidate::{candidate_id}",
        str(candidate.get("source_artifact_id") or ""),
        str(candidate.get("pack_id") or ""),
    ]
    return extraction_assessment(
        subject_id=f"knowledge_candidate::{candidate_id}",
        value=candidate.get("confidence_hint"),
        basis_record_ids=[item for item in basis_ids if item],
        policy_id=CANDIDATE_POLICY_ID,
        method_name="didactopus.knowledge_candidate.confidence_hint",
        rationale="Legacy Didactopus knowledge-candidate confidence_hint migrated as extraction fidelity.",
        recorded_at=recorded_at,
    )


def citation_extraction_assessment(candidate: dict[str, Any], *, recorded_at: str = "2026-07-25T00:00:00Z") -> ConfidenceAssessment | None:
    candidate_id = str(
        candidate.get("citation_candidate_id")
        or candidate.get("reference_candidate_id")
        or candidate.get("citation_occurrence_id")
        or candidate.get("candidate_key")
        or "citation"
    )
    return extraction_assessment(
        subject_id=f"citation_candidate::{candidate_id}",
        value=candidate.get("confidence_hint"),
        basis_record_ids=[
            f"citation_candidate::{candidate_id}",
            str(candidate.get("fragment_id") or ""),
            str(candidate.get("source_id") or ""),
        ],
        policy_id=CITATION_POLICY_ID,
        method_name="didactopus.citation_candidate.confidence_hint",
        rationale="Legacy Didactopus citation confidence_hint migrated as extraction fidelity.",
        recorded_at=recorded_at,
    )


def with_candidate_assessment(candidate: dict[str, Any]) -> dict[str, Any]:
    payload = dict(candidate)
    existing = list(payload.get("confidence_assessments") or [])
    assessment = candidate_extraction_assessment(payload)
    if assessment is not None and assessment.assessment_id not in {str(item.get("assessment_id", "")) for item in existing if isinstance(item, dict)}:
        existing.append(assessment.model_dump())
    payload["confidence_assessments"] = existing
    return payload


def with_citation_assessment(candidate: dict[str, Any]) -> dict[str, Any]:
    payload = dict(candidate)
    existing = list(payload.get("confidence_assessments") or [])
    assessment = citation_extraction_assessment(payload)
    if assessment is not None and assessment.assessment_id not in {str(item.get("assessment_id", "")) for item in existing if isinstance(item, dict)}:
        existing.append(assessment.model_dump())
    payload["confidence_assessments"] = existing
    return payload


def migrate_sqlite_confidence(database_path: str | Path, *, apply: bool = False) -> dict[str, Any]:
    path = Path(database_path)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        columns = _columns(conn, "knowledge_candidates")
        operations: list[dict[str, Any]] = []
        if "confidence_assessments_json" not in columns:
            operations.append({"operation": "add_column", "table": "knowledge_candidates", "column": "confidence_assessments_json"})
            if apply:
                conn.execute("ALTER TABLE knowledge_candidates ADD COLUMN confidence_assessments_json TEXT DEFAULT '[]'")
        if "confidence_hint" in columns:
            for row in conn.execute("SELECT * FROM knowledge_candidates ORDER BY id"):
                value = _bounded(row["confidence_hint"])
                if value is None:
                    continue
                assessment = candidate_extraction_assessment(dict(row), recorded_at=_row_get(row, "created_at") or "2026-07-25T00:00:00Z")
                if assessment is None:
                    continue
                code = "legacy_zero_ambiguous" if value == 0.0 else "append_assessment"
                operation = {
                    "operation": "append_assessment",
                    "table": "knowledge_candidates",
                    "candidate_id": row["id"],
                    "assessment_id": assessment.assessment_id,
                    "value": value,
                    "code": code,
                }
                operations.append(operation)
                if apply and code != "legacy_zero_ambiguous":
                    existing = _json_list(row["confidence_assessments_json"] if "confidence_assessments_json" in row.keys() else "[]")
                    if assessment.assessment_id not in {str(item.get("assessment_id", "")) for item in existing if isinstance(item, dict)}:
                        existing.append(assessment.model_dump())
                    conn.execute(
                        "UPDATE knowledge_candidates SET confidence_assessments_json = ? WHERE id = ?",
                        (json.dumps(existing, sort_keys=True), row["id"]),
                    )
        if apply:
            conn.commit()
        return {
            "report_kind": "didactopus_confidence_migration",
            "schema_version": MIGRATION_VERSION,
            "database_path": str(path),
            "apply": apply,
            "operation_count": len(operations),
            "zero_ambiguity_count": sum(1 for item in operations if item.get("code") == "legacy_zero_ambiguous"),
            "operations": operations,
        }
    finally:
        conn.close()


def _columns(conn: sqlite3.Connection, table: str) -> set[str]:
    return {str(row["name"]) for row in conn.execute(f"PRAGMA table_info({table})")}


def _row_get(row: sqlite3.Row, key: str) -> Any:
    return row[key] if key in row.keys() else None


def _json_list(value: str | None) -> list[dict[str, Any]]:
    if not value:
        return []
    loaded = json.loads(value)
    return loaded if isinstance(loaded, list) else []


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Migrate Didactopus confidence hints into typed assessment JSON.")
    parser.add_argument("database")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--report", default=None)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    payload = migrate_sqlite_confidence(args.database, apply=args.apply)
    if args.report:
        Path(args.report).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
