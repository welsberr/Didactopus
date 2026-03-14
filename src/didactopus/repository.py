from __future__ import annotations
import json
from datetime import datetime, timezone
from sqlalchemy import select
from .db import SessionLocal
from .orm import UserORM, ServiceAccountORM, AgentAuditLogORM, RefreshTokenORM, PackORM, LearnerORM, MasteryRecordORM, EvidenceEventORM, EvaluatorJobORM
from .models import PackData, LearnerState, MasteryRecord, EvidenceEvent, DeploymentPolicyProfile
from .auth import verify_password, hash_password
from .config import load_settings

settings = load_settings()

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def deployment_policy_profile() -> DeploymentPolicyProfile:
    return DeploymentPolicyProfile(
        profile_name=settings.deployment_policy_profile,
        default_personal_lane_enabled=True,
        default_community_lane_enabled=True,
        community_publish_requires_approval=True,
        personal_publish_direct=True,
        reviewer_assignment_required=False,
        description="Deployment policy scaffold."
    )

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

def create_service_account(name: str, owner_user_id: int | None, description: str, scopes: list[str], secret: str):
    with SessionLocal() as db:
        sa = ServiceAccountORM(
            name=name,
            owner_user_id=owner_user_id,
            description=description,
            scopes_json=json.dumps(scopes),
            secret_hash=hash_password(secret),
            is_active=True,
        )
        db.add(sa)
        db.commit()
        db.refresh(sa)
        return sa

def list_service_accounts():
    with SessionLocal() as db:
        rows = db.execute(select(ServiceAccountORM).order_by(ServiceAccountORM.id)).scalars().all()
        return [{"id": r.id, "name": r.name, "owner_user_id": r.owner_user_id, "description": r.description, "scopes": json.loads(r.scopes_json or "[]"), "is_active": r.is_active} for r in rows]

def get_service_account_by_name(name: str):
    with SessionLocal() as db:
        return db.execute(select(ServiceAccountORM).where(ServiceAccountORM.name == name)).scalar_one_or_none()

def authenticate_service_account(name: str, secret: str):
    sa = get_service_account_by_name(name)
    if sa is None or not sa.is_active or not verify_password(secret, sa.secret_hash):
        return None
    return sa

def rotate_service_account_secret(name: str, new_secret: str):
    with SessionLocal() as db:
        sa = db.execute(select(ServiceAccountORM).where(ServiceAccountORM.name == name)).scalar_one_or_none()
        if sa is None:
            return None
        sa.secret_hash = hash_password(new_secret)
        db.commit()
        db.refresh(sa)
        return sa

def set_service_account_active(name: str, is_active: bool):
    with SessionLocal() as db:
        sa = db.execute(select(ServiceAccountORM).where(ServiceAccountORM.name == name)).scalar_one_or_none()
        if sa is None:
            return None
        sa.is_active = is_active
        db.commit()
        db.refresh(sa)
        return sa

def add_agent_audit_log(service_account_id: int, service_account_name: str, action: str, target: str, outcome: str, detail: dict):
    with SessionLocal() as db:
        db.add(AgentAuditLogORM(
            service_account_id=service_account_id,
            service_account_name=service_account_name,
            action=action,
            target=target,
            outcome=outcome,
            detail_json=json.dumps(detail),
            created_at=now_iso(),
        ))
        db.commit()

def list_agent_audit_logs(limit: int = 200):
    with SessionLocal() as db:
        rows = db.execute(select(AgentAuditLogORM).order_by(AgentAuditLogORM.id.desc())).scalars().all()[:limit]
        return [{
            "id": r.id,
            "service_account_id": r.service_account_id,
            "service_account_name": r.service_account_name,
            "action": r.action,
            "target": r.target,
            "outcome": r.outcome,
            "detail": json.loads(r.detail_json or "{}"),
            "created_at": r.created_at,
        } for r in rows]

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

def upsert_pack(pack: PackData, submitted_by_user_id: int, policy_lane: str = "personal", is_published: bool = False, change_summary: str = ""):
    validation = {"ok": len(pack.concepts) > 0, "warnings": [] if len(pack.concepts) > 0 else ["Pack has no concepts."], "errors": []}
    provenance = {"source_count": pack.compliance.sources, "restrictive_flags": list(pack.compliance.flags)}
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
                validation_json=json.dumps(validation),
                provenance_json=json.dumps(provenance),
                governance_state="personal_ready" if policy_lane == "personal" else "draft",
                current_version=1,
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
            row.validation_json = json.dumps(validation)
            row.provenance_json = json.dumps(provenance)
            row.current_version += 1
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

def create_evaluator_job(learner_id: str, pack_id: str, concept_id: str, submitted_text: str):
    with SessionLocal() as db:
        job = EvaluatorJobORM(learner_id=learner_id, pack_id=pack_id, concept_id=concept_id, submitted_text=submitted_text, status="queued", trace_json=json.dumps({"notes": ["Job queued"]}))
        db.add(job)
        db.commit()
        db.refresh(job)
        return job.id

def list_evaluator_jobs_for_learner(learner_id: str):
    with SessionLocal() as db:
        return db.execute(select(EvaluatorJobORM).where(EvaluatorJobORM.learner_id == learner_id).order_by(EvaluatorJobORM.id.desc())).scalars().all()

def get_evaluator_job(job_id: int):
    with SessionLocal() as db:
        return db.get(EvaluatorJobORM, job_id)

def update_evaluator_job(job_id: int, status: str, score: float | None = None, confidence_hint: float | None = None, notes: str = "", trace: dict | None = None):
    with SessionLocal() as db:
        job = db.get(EvaluatorJobORM, job_id)
        if job is None:
            return
        job.status = status
        job.result_score = score
        job.result_confidence_hint = confidence_hint
        job.result_notes = notes
        if trace is not None:
            job.trace_json = json.dumps(trace)
        db.commit()
