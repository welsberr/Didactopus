from __future__ import annotations
import json
from datetime import datetime, timezone
from sqlalchemy import select
from .db import SessionLocal
from .orm import UserORM, RefreshTokenORM, PackORM, PackVersionORM, ReviewCommentORM, ContributionSubmissionORM, ReviewTaskORM, LearnerORM, MasteryRecordORM, EvidenceEventORM, EvaluatorJobORM
from .models import PackData, LearnerState, MasteryRecord, EvidenceEvent, DeploymentPolicyProfile
from .auth import verify_password
from .config import load_settings

settings = load_settings()

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def deployment_policy_profile() -> DeploymentPolicyProfile:
    profile = settings.deployment_policy_profile
    if profile == "community_repo":
        return DeploymentPolicyProfile(
            profile_name="community_repo",
            default_personal_lane_enabled=True,
            default_community_lane_enabled=True,
            community_publish_requires_approval=True,
            personal_publish_direct=True,
            reviewer_assignment_required=True,
            description="Shared repository deployment with stronger community controls."
        )
    if profile == "team_lab":
        return DeploymentPolicyProfile(
            profile_name="team_lab",
            default_personal_lane_enabled=True,
            default_community_lane_enabled=True,
            community_publish_requires_approval=True,
            personal_publish_direct=True,
            reviewer_assignment_required=False,
            description="Team deployment with shared review but moderate overhead."
        )
    return DeploymentPolicyProfile(
        profile_name="single_user",
        default_personal_lane_enabled=True,
        default_community_lane_enabled=True,
        community_publish_requires_approval=True,
        personal_publish_direct=True,
        reviewer_assignment_required=False,
        description="Single-user/private-first deployment."
    )

def pack_diff(old_pack: dict | None, new_pack: dict) -> dict:
    old_pack = old_pack or {}
    old_concepts = {c.get("id"): c for c in old_pack.get("concepts", [])}
    new_concepts = {c.get("id"): c for c in new_pack.get("concepts", [])}
    added = sorted([cid for cid in new_concepts if cid not in old_concepts])
    removed = sorted([cid for cid in old_concepts if cid not in new_concepts])
    changed = sorted([cid for cid in new_concepts if cid in old_concepts and new_concepts[cid] != old_concepts[cid]])
    return {
        "title_changed": old_pack.get("title") != new_pack.get("title"),
        "subtitle_changed": old_pack.get("subtitle") != new_pack.get("subtitle"),
        "concepts_added": added,
        "concepts_removed": removed,
        "concepts_changed": changed,
        "onboarding_changed": old_pack.get("onboarding") != new_pack.get("onboarding"),
        "compliance_changed": old_pack.get("compliance") != new_pack.get("compliance"),
    }

def gate_summary(validation: dict, provenance: dict) -> dict:
    warnings = list(validation.get("warnings", []) or [])
    errors = list(validation.get("errors", []) or [])
    restrictive_flags = list(provenance.get("restrictive_flags", []) or [])
    qa_ok = validation.get("ok", False) and len(errors) == 0
    provenance_ok = provenance.get("source_count", 0) >= 0
    ready_for_review = qa_ok and provenance_ok
    return {
        "qa_ok": qa_ok,
        "provenance_ok": provenance_ok,
        "ready_for_review": ready_for_review,
        "warnings": warnings,
        "errors": errors,
        "restrictive_flags": restrictive_flags,
    }

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

def list_pack_admin_rows():
    with SessionLocal() as db:
        rows = db.execute(select(PackORM).order_by(PackORM.id)).scalars().all()
        return [{"id": r.id, "title": r.title, "policy_lane": r.policy_lane, "is_published": r.is_published, "subtitle": r.subtitle, "governance_state": r.governance_state, "current_version": r.current_version} for r in rows]

def get_pack(pack_id: str):
    with SessionLocal() as db:
        row = db.get(PackORM, pack_id)
        return None if row is None else PackData.model_validate(json.loads(row.data_json))

def get_pack_row(pack_id: str):
    with SessionLocal() as db:
        return db.get(PackORM, pack_id)

def get_pack_validation(pack_id: str):
    with SessionLocal() as db:
        row = db.get(PackORM, pack_id)
        return {} if row is None else json.loads(row.validation_json or "{}")

def get_pack_provenance(pack_id: str):
    with SessionLocal() as db:
        row = db.get(PackORM, pack_id)
        return {} if row is None else json.loads(row.provenance_json or "{}")

def validation_and_provenance_for_pack(pack: PackData):
    validation = {
        "ok": len(pack.concepts) > 0,
        "warnings": [] if len(pack.concepts) > 0 else ["Pack has no concepts."],
        "errors": [],
        "summary": {"concept_count": len(pack.concepts), "has_onboarding": bool(pack.onboarding)}
    }
    provenance = {
        "source_count": pack.compliance.sources,
        "licenses_present": ["CC BY-NC-SA 4.0"] if pack.compliance.shareAlikeRequired or pack.compliance.noncommercialOnly else [],
        "restrictive_flags": list(pack.compliance.flags),
        "sources": [
            {"source_id": "sample-source-1", "title": f"Provenance placeholder for {pack.title}", "license_id": "CC BY-NC-SA 4.0" if pack.compliance.shareAlikeRequired or pack.compliance.noncommercialOnly else "unspecified", "attribution_text": "Sample attribution text placeholder"}
        ] if pack.compliance.sources else []
    }
    return validation, provenance

def upsert_pack(pack: PackData, submitted_by_user_id: int, policy_lane: str = "personal", is_published: bool = False, change_summary: str = ""):
    validation, provenance = validation_and_provenance_for_pack(pack)
    with SessionLocal() as db:
        row = db.get(PackORM, pack.id)
        payload = json.dumps(pack.model_dump())
        if row is None:
            row = PackORM(
                id=pack.id,
                owner_user_id=submitted_by_user_id if policy_lane == "personal" else None,
                policy_lane=policy_lane,
                title=pack.title, subtitle=pack.subtitle, level=pack.level,
                data_json=payload, validation_json=json.dumps(validation), provenance_json=json.dumps(provenance),
                governance_state="draft" if policy_lane == "community" else "personal_ready",
                current_version=1, is_published=is_published if policy_lane == "personal" else False
            )
            db.add(row)
            version_number = 1
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
            row.governance_state = "draft" if policy_lane == "community" else "personal_ready"
            if policy_lane == "personal":
                row.is_published = is_published
            version_number = row.current_version
        db.flush()
        db.add(PackVersionORM(
            pack_id=pack.id,
            version_number=version_number,
            submitted_by_user_id=submitted_by_user_id,
            policy_lane=policy_lane,
            status="draft" if policy_lane == "community" else "personal_ready",
            data_json=payload,
            change_summary=change_summary,
            created_at=now_iso(),
            review_summary=""
        ))
        db.commit()

def create_submission(pack: PackData, contributor_user_id: int, submission_summary: str):
    validation, provenance = validation_and_provenance_for_pack(pack)
    with SessionLocal() as db:
        current_pack = db.get(PackORM, pack.id)
        current_payload = json.loads(current_pack.data_json) if current_pack is not None else None
        current_version = current_pack.current_version if current_pack is not None else 0
        proposed_version = current_version + 1
        proposed_payload = pack.model_dump()
        diff = pack_diff(current_payload, proposed_payload)
        gates = gate_summary(validation, provenance)
        task_note = "Community submission awaiting reviewer attention"
        if deployment_policy_profile().reviewer_assignment_required:
            task_note += " (reviewer assignment required by deployment policy)"
        sub = ContributionSubmissionORM(
            pack_id=pack.id,
            policy_lane="community",
            proposed_version_number=proposed_version,
            contributor_user_id=contributor_user_id,
            status="submitted",
            submission_summary=submission_summary,
            proposed_data_json=json.dumps(proposed_payload),
            diff_json=json.dumps(diff),
            gate_json=json.dumps(gates),
            created_at=now_iso(),
        )
        db.add(sub)
        db.flush()
        db.add(ReviewTaskORM(
            submission_id=sub.id,
            reviewer_user_id=None,
            task_status="open",
            task_note=task_note,
            created_at=now_iso(),
        ))
        db.commit()
        return sub.id

def list_submissions():
    with SessionLocal() as db:
        rows = db.execute(select(ContributionSubmissionORM).order_by(ContributionSubmissionORM.id.desc())).scalars().all()
        return [{
            "submission_id": r.id,
            "pack_id": r.pack_id,
            "policy_lane": r.policy_lane,
            "proposed_version_number": r.proposed_version_number,
            "contributor_user_id": r.contributor_user_id,
            "status": r.status,
            "submission_summary": r.submission_summary,
            "created_at": r.created_at,
        } for r in rows]

def get_submission_diff(submission_id: int):
    with SessionLocal() as db:
        row = db.get(ContributionSubmissionORM, submission_id)
        return {} if row is None else json.loads(row.diff_json or "{}")

def get_submission_gates(submission_id: int):
    with SessionLocal() as db:
        row = db.get(ContributionSubmissionORM, submission_id)
        return {} if row is None else json.loads(row.gate_json or "{}")

def list_review_tasks():
    with SessionLocal() as db:
        rows = db.execute(select(ReviewTaskORM).order_by(ReviewTaskORM.id.desc())).scalars().all()
        return [{
            "task_id": r.id,
            "submission_id": r.submission_id,
            "reviewer_user_id": r.reviewer_user_id,
            "task_status": r.task_status,
            "task_note": r.task_note,
            "created_at": r.created_at,
        } for r in rows]

def can_publish_pack(pack_id: str) -> tuple[bool, str]:
    with SessionLocal() as db:
        row = db.get(PackORM, pack_id)
        if row is None:
            return False, "Pack not found"
        if row.policy_lane == "personal":
            return True, "Personal lane pack may publish directly"
        if deployment_policy_profile().community_publish_requires_approval and row.governance_state != "approved":
            return False, "Community lane pack must be approved before publication"
        validation = json.loads(row.validation_json or "{}")
        provenance = json.loads(row.provenance_json or "{}")
        gates = gate_summary(validation, provenance)
        if not gates.get("ready_for_review", False):
            return False, "Community lane gates not satisfied"
        return True, "Community lane pack passed publish gates"

def set_pack_publication(pack_id: str, is_published: bool):
    with SessionLocal() as db:
        row = db.get(PackORM, pack_id)
        if row is None:
            return False, "Pack not found"
        if is_published:
            ok, reason = can_publish_pack(pack_id)
            if not ok:
                return False, reason
        row.is_published = is_published
        db.commit()
        return True, "Updated"

def set_governance_state(pack_id: str, status: str, review_summary: str):
    with SessionLocal() as db:
        row = db.get(PackORM, pack_id)
        if row is None:
            return False
        if row.policy_lane == "personal":
            row.governance_state = status
        else:
            validation = json.loads(row.validation_json or "{}")
            provenance = json.loads(row.provenance_json or "{}")
            gates = gate_summary(validation, provenance)
            if status == "approved" and not gates.get("ready_for_review", False):
                return False
            row.governance_state = status
        version = db.execute(select(PackVersionORM).where(PackVersionORM.pack_id == pack_id, PackVersionORM.version_number == row.current_version)).scalar_one_or_none()
        if version is not None:
            version.status = status
            version.review_summary = review_summary
        db.commit()
        return True

def list_pack_versions(pack_id: str):
    with SessionLocal() as db:
        rows = db.execute(select(PackVersionORM).where(PackVersionORM.pack_id == pack_id).order_by(PackVersionORM.version_number.desc())).scalars().all()
        return [{
            "version_number": r.version_number,
            "policy_lane": r.policy_lane,
            "status": r.status,
            "change_summary": r.change_summary,
            "created_at": r.created_at,
            "review_summary": r.review_summary,
            "submitted_by_user_id": r.submitted_by_user_id
        } for r in rows]

def add_review_comment(pack_id: str, version_number: int, reviewer_user_id: int, comment_text: str, disposition: str):
    with SessionLocal() as db:
        db.add(ReviewCommentORM(pack_id=pack_id, version_number=version_number, reviewer_user_id=reviewer_user_id, comment_text=comment_text, disposition=disposition, created_at=now_iso()))
        db.commit()

def list_review_comments(pack_id: str):
    with SessionLocal() as db:
        rows = db.execute(select(ReviewCommentORM).where(ReviewCommentORM.pack_id == pack_id).order_by(ReviewCommentORM.id.desc())).scalars().all()
        return [{
            "version_number": r.version_number,
            "reviewer_user_id": r.reviewer_user_id,
            "comment_text": r.comment_text,
            "disposition": r.disposition,
            "created_at": r.created_at
        } for r in rows]

def create_learner(owner_user_id: int, learner_id: str, display_name: str = ""):
    with SessionLocal() as db:
        if db.get(LearnerORM, learner_id) is None:
            db.add(LearnerORM(id=learner_id, owner_user_id=owner_user_id, display_name=display_name))
            db.commit()

def list_learners_for_user(user_id: int, is_admin: bool = False):
    with SessionLocal() as db:
        stmt = select(LearnerORM).order_by(LearnerORM.id)
        if not is_admin:
            stmt = stmt.where(LearnerORM.owner_user_id == user_id)
        rows = db.execute(stmt).scalars().all()
        return [{"learner_id": r.id, "display_name": r.display_name, "owner_user_id": r.owner_user_id} for r in rows]

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
        trace = {"rubric_dimension_scores": [{"dimension": "mastery", "score": 0.0}], "notes": ["Job queued", "Awaiting evaluator"], "token_count_estimate": len(submitted_text.split())}
        job = EvaluatorJobORM(learner_id=learner_id, pack_id=pack_id, concept_id=concept_id, submitted_text=submitted_text, status="queued", trace_json=json.dumps(trace))
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
