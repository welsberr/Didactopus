from __future__ import annotations
import json
from sqlalchemy import select
from .db import SessionLocal
from .orm import UserORM, RefreshTokenORM, PackORM, LearnerORM, MasteryRecordORM, EvidenceEventORM, EvaluatorJobORM
from .models import PackData, LearnerState, MasteryRecord, EvidenceEvent
from .auth import verify_password

def get_user_by_username(username: str):
    with SessionLocal() as db:
        return db.execute(select(UserORM).where(UserORM.username == username)).scalar_one_or_none()

def get_user_by_id(user_id: int):
    with SessionLocal() as db:
        return db.get(UserORM, user_id)

def authenticate_user(username: str, password: str):
    user = get_user_by_username(username)
    if user is None or not verify_password(password, user.password_hash) or not user.is_active:
        return None
    return user

def store_refresh_token(user_id: int, token_id: str):
    with SessionLocal() as db:
        db.add(RefreshTokenORM(user_id=user_id, token_id=token_id, is_revoked=False))
        db.commit()

def refresh_token_active(token_id: str) -> bool:
    with SessionLocal() as db:
        row = db.execute(select(RefreshTokenORM).where(RefreshTokenORM.token_id == token_id)).scalar_one_or_none()
        return row is not None and not row.is_revoked

def revoke_refresh_token(token_id: str):
    with SessionLocal() as db:
        row = db.execute(select(RefreshTokenORM).where(RefreshTokenORM.token_id == token_id)).scalar_one_or_none()
        if row:
            row.is_revoked = True
            db.commit()

def list_packs(include_unpublished: bool = False) -> list[PackData]:
    with SessionLocal() as db:
        stmt = select(PackORM)
        if not include_unpublished:
            stmt = stmt.where(PackORM.is_published == True)
        rows = db.execute(stmt).scalars().all()
        return [PackData.model_validate(json.loads(r.data_json)) for r in rows]

def get_pack(pack_id: str):
    with SessionLocal() as db:
        row = db.get(PackORM, pack_id)
        return None if row is None else PackData.model_validate(json.loads(row.data_json))

def upsert_pack(pack: PackData, is_published: bool = True):
    with SessionLocal() as db:
        row = db.get(PackORM, pack.id)
        payload = json.dumps(pack.model_dump())
        if row is None:
            db.add(PackORM(id=pack.id, title=pack.title, subtitle=pack.subtitle, level=pack.level, data_json=payload, is_published=is_published))
        else:
            row.title = pack.title
            row.subtitle = pack.subtitle
            row.level = pack.level
            row.data_json = payload
            row.is_published = is_published
        db.commit()

def create_learner(owner_user_id: int, learner_id: str, display_name: str = ""):
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
            records=[MasteryRecord(concept_id=r.concept_id, dimension=r.dimension, score=r.score, confidence=r.confidence, evidence_count=r.evidence_count, last_updated=r.last_updated) for r in records],
            history=[EvidenceEvent(concept_id=h.concept_id, dimension=h.dimension, score=h.score, confidence_hint=h.confidence_hint, timestamp=h.timestamp, kind=h.kind, source_id=h.source_id) for h in history],
        )

def save_learner_state(state: LearnerState):
    with SessionLocal() as db:
        db.query(MasteryRecordORM).filter(MasteryRecordORM.learner_id == state.learner_id).delete()
        db.query(EvidenceEventORM).filter(EvidenceEventORM.learner_id == state.learner_id).delete()
        for r in state.records:
            db.add(MasteryRecordORM(learner_id=state.learner_id, concept_id=r.concept_id, dimension=r.dimension, score=r.score, confidence=r.confidence, evidence_count=r.evidence_count, last_updated=r.last_updated))
        for h in state.history:
            db.add(EvidenceEventORM(learner_id=state.learner_id, concept_id=h.concept_id, dimension=h.dimension, score=h.score, confidence_hint=h.confidence_hint, timestamp=h.timestamp, kind=h.kind, source_id=h.source_id))
        db.commit()
    return state

def create_evaluator_job(learner_id: str, pack_id: str, concept_id: str, submitted_text: str) -> int:
    with SessionLocal() as db:
        job = EvaluatorJobORM(learner_id=learner_id, pack_id=pack_id, concept_id=concept_id, submitted_text=submitted_text, status="queued")
        db.add(job)
        db.commit()
        db.refresh(job)
        return job.id

def list_evaluator_jobs_for_learner(learner_id: str) -> list[EvaluatorJobORM]:
    with SessionLocal() as db:
        return db.execute(select(EvaluatorJobORM).where(EvaluatorJobORM.learner_id == learner_id).order_by(EvaluatorJobORM.id.desc())).scalars().all()

def get_evaluator_job(job_id: int):
    with SessionLocal() as db:
        return db.get(EvaluatorJobORM, job_id)

def update_evaluator_job(job_id: int, status: str, score: float | None = None, confidence_hint: float | None = None, notes: str = ""):
    with SessionLocal() as db:
        job = db.get(EvaluatorJobORM, job_id)
        if job is None:
            return
        job.status = status
        job.result_score = score
        job.result_confidence_hint = confidence_hint
        job.result_notes = notes
        db.commit()
