from __future__ import annotations
import json
from sqlalchemy import select
from .db import SessionLocal
from .orm import UserORM, PackORM, LearnerORM, MasteryRecordORM, EvidenceEventORM, EvaluatorJobORM
from .models import PackData, LearnerState, MasteryRecord, EvidenceEvent
from .auth import verify_password

def get_user_by_token(token: str) -> UserORM | None:
    with SessionLocal() as db:
        return db.execute(select(UserORM).where(UserORM.token == token)).scalar_one_or_none()

def authenticate_user(username: str, password: str) -> UserORM | None:
    with SessionLocal() as db:
        user = db.execute(select(UserORM).where(UserORM.username == username)).scalar_one_or_none()
        if user is None:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

def list_packs() -> list[PackData]:
    with SessionLocal() as db:
        rows = db.execute(select(PackORM)).scalars().all()
        return [PackData.model_validate(json.loads(r.data_json)) for r in rows]

def get_pack(pack_id: str) -> PackData | None:
    with SessionLocal() as db:
        row = db.get(PackORM, pack_id)
        if row is None:
            return None
        return PackData.model_validate(json.loads(row.data_json))

def create_learner(owner_user_id: int, learner_id: str, display_name: str = "") -> None:
    with SessionLocal() as db:
        if db.get(LearnerORM, learner_id) is None:
            db.add(LearnerORM(id=learner_id, owner_user_id=owner_user_id, display_name=display_name))
            db.commit()

def learner_owned_by_user(user_id: int, learner_id: str) -> bool:
    with SessionLocal() as db:
        learner = db.get(LearnerORM, learner_id)
        return learner is not None and learner.owner_user_id == user_id

def load_learner_state(learner_id: str) -> LearnerState:
    with SessionLocal() as db:
        records = db.execute(select(MasteryRecordORM).where(MasteryRecordORM.learner_id == learner_id)).scalars().all()
        history = db.execute(select(EvidenceEventORM).where(EvidenceEventORM.learner_id == learner_id)).scalars().all()
        return LearnerState(
            learner_id=learner_id,
            records=[
                MasteryRecord(
                    concept_id=r.concept_id,
                    dimension=r.dimension,
                    score=r.score,
                    confidence=r.confidence,
                    evidence_count=r.evidence_count,
                    last_updated=r.last_updated,
                ) for r in records
            ],
            history=[
                EvidenceEvent(
                    concept_id=h.concept_id,
                    dimension=h.dimension,
                    score=h.score,
                    confidence_hint=h.confidence_hint,
                    timestamp=h.timestamp,
                    kind=h.kind,
                    source_id=h.source_id,
                ) for h in history
            ]
        )

def save_learner_state(state: LearnerState) -> LearnerState:
    with SessionLocal() as db:
        db.execute(select(LearnerORM).where(LearnerORM.id == state.learner_id))
        db.query(MasteryRecordORM).filter(MasteryRecordORM.learner_id == state.learner_id).delete()
        db.query(EvidenceEventORM).filter(EvidenceEventORM.learner_id == state.learner_id).delete()
        for r in state.records:
            db.add(MasteryRecordORM(
                learner_id=state.learner_id,
                concept_id=r.concept_id,
                dimension=r.dimension,
                score=r.score,
                confidence=r.confidence,
                evidence_count=r.evidence_count,
                last_updated=r.last_updated,
            ))
        for h in state.history:
            db.add(EvidenceEventORM(
                learner_id=state.learner_id,
                concept_id=h.concept_id,
                dimension=h.dimension,
                score=h.score,
                confidence_hint=h.confidence_hint,
                timestamp=h.timestamp,
                kind=h.kind,
                source_id=h.source_id,
            ))
        db.commit()
    return state

def create_evaluator_job(learner_id: str, pack_id: str, concept_id: str, submitted_text: str) -> int:
    with SessionLocal() as db:
        job = EvaluatorJobORM(
            learner_id=learner_id,
            pack_id=pack_id,
            concept_id=concept_id,
            submitted_text=submitted_text,
            status="queued",
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job.id

def get_evaluator_job(job_id: int) -> EvaluatorJobORM | None:
    with SessionLocal() as db:
        return db.get(EvaluatorJobORM, job_id)

def update_evaluator_job(job_id: int, status: str, score: float | None = None, confidence_hint: float | None = None, notes: str = "") -> None:
    with SessionLocal() as db:
        job = db.get(EvaluatorJobORM, job_id)
        if job is None:
            return
        job.status = status
        job.result_score = score
        job.result_confidence_hint = confidence_hint
        job.result_notes = notes
        db.commit()
