from __future__ import annotations
import json
from sqlalchemy import select
from .db import SessionLocal
from .orm import UserORM, RefreshTokenORM, PackORM, LearnerORM, MasteryRecordORM, EvidenceEventORM, RenderJobORM, ArtifactORM
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

def list_packs_for_user(user_id: int | None = None, include_unpublished: bool = False):
    with SessionLocal() as db:
        stmt = select(PackORM)
        if not include_unpublished:
            stmt = stmt.where(PackORM.is_published == True)
        rows = db.execute(stmt).scalars().all()
        out = []
        for r in rows:
            if r.policy_lane == "community":
                out.append(PackData.model_validate(json.loads(r.data_json)))
            elif user_id is not None and r.owner_user_id == user_id:
                out.append(PackData.model_validate(json.loads(r.data_json)))
        return out

def get_pack(pack_id: str):
    with SessionLocal() as db:
        row = db.get(PackORM, pack_id)
        return None if row is None else PackData.model_validate(json.loads(row.data_json))

def get_pack_row(pack_id: str):
    with SessionLocal() as db:
        return db.get(PackORM, pack_id)

def upsert_pack(pack: PackData, submitted_by_user_id: int, policy_lane: str = "personal", is_published: bool = False):
    with SessionLocal() as db:
        row = db.get(PackORM, pack.id)
        payload = json.dumps(pack.model_dump())
        if row is None:
            row = PackORM(
                id=pack.id,
                owner_user_id=submitted_by_user_id if policy_lane == "personal" else None,
                policy_lane=policy_lane,
                title=pack.title,
                subtitle=pack.subtitle,
                level=pack.level,
                data_json=payload,
                is_published=is_published if policy_lane == "personal" else False,
            )
            db.add(row)
        else:
            row.owner_user_id = submitted_by_user_id if policy_lane == "personal" else row.owner_user_id
            row.policy_lane = policy_lane
            row.title = pack.title
            row.subtitle = pack.subtitle
            row.level = pack.level
            row.data_json = payload
            if policy_lane == "personal":
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

def load_learner_state(learner_id: str):
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

def create_render_job(learner_id: str, pack_id: str, requested_format: str, fps: int, theme: str):
    with SessionLocal() as db:
        row = RenderJobORM(
            learner_id=learner_id,
            pack_id=pack_id,
            requested_format=requested_format,
            fps=fps,
            theme=theme,
            status="queued",
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return row.id

def update_render_job(job_id: int, **fields):
    with SessionLocal() as db:
        row = db.get(RenderJobORM, job_id)
        if row is None:
            return None
        for k, v in fields.items():
            setattr(row, k, v)
        db.commit()
        db.refresh(row)
        return row

def list_render_jobs(learner_id: str | None = None):
    with SessionLocal() as db:
        stmt = select(RenderJobORM).order_by(RenderJobORM.id.desc())
        if learner_id:
            stmt = stmt.where(RenderJobORM.learner_id == learner_id)
        rows = db.execute(stmt).scalars().all()
        return [{
            "job_id": r.id,
            "learner_id": r.learner_id,
            "pack_id": r.pack_id,
            "requested_format": r.requested_format,
            "fps": r.fps,
            "theme": r.theme,
            "status": r.status,
            "bundle_dir": r.bundle_dir,
            "payload_json": r.payload_json,
            "manifest_path": r.manifest_path,
            "script_path": r.script_path,
            "error_text": r.error_text,
        } for r in rows]

def register_artifact(render_job_id: int, learner_id: str, pack_id: str, artifact_type: str, fmt: str, title: str, path: str, metadata: dict, retention_class: str = "standard", expires_at: str = ""):
    with SessionLocal() as db:
        row = ArtifactORM(
            render_job_id=render_job_id,
            learner_id=learner_id,
            pack_id=pack_id,
            artifact_type=artifact_type,
            format=fmt,
            title=title,
            path=path,
            metadata_json=json.dumps(metadata),
            retention_class=retention_class,
            expires_at=expires_at,
            is_deleted=False,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return row.id

def list_artifacts(learner_id: str | None = None, include_deleted: bool = False):
    with SessionLocal() as db:
        stmt = select(ArtifactORM).order_by(ArtifactORM.id.desc())
        if learner_id:
            stmt = stmt.where(ArtifactORM.learner_id == learner_id)
        if not include_deleted:
            stmt = stmt.where(ArtifactORM.is_deleted == False)
        rows = db.execute(stmt).scalars().all()
        return [{
            "artifact_id": r.id,
            "render_job_id": r.render_job_id,
            "learner_id": r.learner_id,
            "pack_id": r.pack_id,
            "artifact_type": r.artifact_type,
            "format": r.format,
            "title": r.title,
            "path": r.path,
            "retention_class": r.retention_class,
            "expires_at": r.expires_at,
            "is_deleted": r.is_deleted,
            "metadata": json.loads(r.metadata_json or "{}"),
        } for r in rows]

def get_artifact(artifact_id: int):
    with SessionLocal() as db:
        return db.get(ArtifactORM, artifact_id)

def update_artifact_retention(artifact_id: int, retention_class: str, expires_at: str):
    with SessionLocal() as db:
        row = db.get(ArtifactORM, artifact_id)
        if row is None:
            return None
        row.retention_class = retention_class
        row.expires_at = expires_at
        db.commit()
        db.refresh(row)
        return row

def soft_delete_artifact(artifact_id: int):
    with SessionLocal() as db:
        row = db.get(ArtifactORM, artifact_id)
        if row is None:
            return None
        row.is_deleted = True
        db.commit()
        db.refresh(row)
        return row
