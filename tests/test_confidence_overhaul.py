from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from didactopus.confidence import (
    CANDIDATE_POLICY_ID,
    CITATION_POLICY_ID,
    candidate_extraction_assessment,
    migrate_sqlite_confidence,
    with_candidate_assessment,
)
from didactopus.confidence_inventory import scan_confidence_inventory
from didactopus.citation_extract import _citation_occurrence_row
from didactopus.db import Base
from didactopus.models import KnowledgeCandidateCreate, MasteryRecord
from didactopus.notebook_page import build_notebook_page_from_groundrecall_bundle
from didactopus.orm import KnowledgeCandidateORM, MasteryRecordORM


ROOT = Path(__file__).resolve().parents[1]


def test_confidence_inventory_matches_checked_in_report() -> None:
    current = scan_confidence_inventory(ROOT / "src" / "didactopus")
    checked_in = json.loads((ROOT / "docs" / "confidence-inventory.json").read_text(encoding="utf-8"))

    assert current == checked_in
    assert {entry["category"] for entry in current["entries"] if entry["category"] == "unclassified"} == set()
    assert {
        "api_or_orm_boundary",
        "candidate_extraction_hint",
        "citation_extraction_hint",
        "confidence_contract_tooling",
        "graph_extraction_assessment",
        "groundrecall_bridge_legacy",
        "learner_state_mastery",
    } <= {entry["category"] for entry in current["entries"]}


def test_pydantic_api_preserves_missing_vs_explicit_zero_confidence() -> None:
    missing = KnowledgeCandidateCreate(
        learner_id="learner-1",
        pack_id="pack-1",
        candidate_kind="concept",
        title="Missing confidence",
    )
    explicit_zero = KnowledgeCandidateCreate(
        learner_id="learner-1",
        pack_id="pack-1",
        candidate_kind="concept",
        title="Explicit zero confidence",
        confidence_hint=0.0,
    )

    assert missing.confidence_hint is None
    assert explicit_zero.confidence_hint == 0.0
    assert missing.model_dump()["confidence_hint"] is None
    assert explicit_zero.model_dump()["confidence_hint"] == 0.0
    assert MasteryRecord(concept_id="c1", dimension="mastery").confidence is None
    assert MasteryRecord(concept_id="c1", dimension="mastery", confidence=0.0).confidence == 0.0


def test_orm_round_trip_preserves_null_and_zero_confidence() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        session.add_all(
            [
                MasteryRecordORM(learner_id="l1", concept_id="c1", dimension="mastery", confidence=None),
                MasteryRecordORM(learner_id="l1", concept_id="c2", dimension="mastery", confidence=0.0),
                KnowledgeCandidateORM(
                    learner_id="l1",
                    pack_id="p1",
                    candidate_kind="concept",
                    title="Missing confidence",
                    structured_payload_json="{}",
                    confidence_hint=None,
                    confidence_assessments_json="[]",
                ),
                KnowledgeCandidateORM(
                    learner_id="l1",
                    pack_id="p1",
                    candidate_kind="concept",
                    title="Explicit zero confidence",
                    structured_payload_json="{}",
                    confidence_hint=0.0,
                    confidence_assessments_json="[]",
                ),
            ]
        )
        session.commit()

        mastery = session.query(MasteryRecordORM).order_by(MasteryRecordORM.concept_id).all()
        candidates = session.query(KnowledgeCandidateORM).order_by(KnowledgeCandidateORM.title).all()

    assert [row.confidence for row in mastery] == [None, 0.0]
    assert [row.confidence_hint for row in candidates] == [0.0, None]
    assert [json.loads(row.confidence_assessments_json) for row in candidates] == [[], []]


def test_candidate_and_citation_hints_convert_to_typed_assessments() -> None:
    candidate = {
        "id": 42,
        "title": "Candidate",
        "pack_id": "pack-1",
        "source_artifact_id": 7,
        "confidence_hint": 0.72,
    }

    assessment = candidate_extraction_assessment(candidate)
    again = candidate_extraction_assessment(candidate)
    wrapped = with_candidate_assessment(candidate)
    citation = _citation_occurrence_row(
        "Smith 2024",
        "in_text_citation",
        {
            "source_id": "source-1",
            "source_path": "source.md",
            "fragment_id": "frag-1",
            "section": "Body",
            "ingest_id": "ingest-1",
        },
        1,
        11,
        0.64,
    )

    assert assessment is not None
    assert again is not None
    assert assessment.method.policy_id == CANDIDATE_POLICY_ID
    assert assessment.basis_hash == again.basis_hash
    assert wrapped["confidence_assessments"][0]["dimension"] == "extraction_fidelity"
    assert wrapped["confidence_assessments"][0]["metadata"]["not_source_truth"] is True
    assert citation["confidence_assessments"][0]["method"]["policy_id"] == CITATION_POLICY_ID
    assert citation["confidence_assessments"][0]["metadata"]["not_mastery"] is True


def test_sqlite_confidence_migration_reports_legacy_zero_ambiguity(tmp_path: Path) -> None:
    database = tmp_path / "didactopus.sqlite"
    conn = sqlite3.connect(database)
    conn.execute(
        """
        CREATE TABLE knowledge_candidates (
            id INTEGER PRIMARY KEY,
            title TEXT,
            pack_id TEXT,
            source_artifact_id INTEGER,
            confidence_hint REAL,
            created_at TEXT
        )
        """
    )
    conn.executemany(
        "INSERT INTO knowledge_candidates (id, title, pack_id, source_artifact_id, confidence_hint, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        [
            (1, "Missing", "pack-1", 1, None, "2026-07-25T00:00:00Z"),
            (2, "Explicit zero", "pack-1", 2, 0.0, "2026-07-25T00:00:00Z"),
            (3, "Non-zero", "pack-1", 3, 0.7, "2026-07-25T00:00:00Z"),
        ],
    )
    conn.commit()
    conn.close()

    dry_run = migrate_sqlite_confidence(database, apply=False)
    applied = migrate_sqlite_confidence(database, apply=True)

    assert any(op["operation"] == "add_column" for op in dry_run["operations"])
    assert dry_run["zero_ambiguity_count"] == 1
    assert applied["zero_ambiguity_count"] == 1

    conn = sqlite3.connect(database)
    rows = {
        row[0]: json.loads(row[1] or "[]")
        for row in conn.execute("SELECT id, confidence_assessments_json FROM knowledge_candidates ORDER BY id")
    }
    conn.close()

    assert rows[1] == []
    assert rows[2] == []
    assert rows[3][0]["dimension"] == "extraction_fidelity"
    assert rows[3][0]["value"] == 0.7


def test_groundrecall_confidence_profile_is_preserved_without_flattening() -> None:
    profile = {
        "schema_version": "1.0",
        "confidence_profile": {
            "overall": {"value": 0.78, "band": "medium"},
            "components": [{"dimension": "source_grounding", "value": 0.9}],
        },
    }
    page = build_notebook_page_from_groundrecall_bundle(
        {
            "concept": {"concept_id": "concept::x", "title": "Concept X"},
            "confidence_profile": profile,
        }
    )

    assert page["confidence_profile"] == profile
