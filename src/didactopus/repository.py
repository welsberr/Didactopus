from __future__ import annotations
import json
from datetime import datetime, timezone
from sqlalchemy import select
from .db import SessionLocal
from .orm import (
    UserORM, PackORM, LearnerORM, MasteryRecordORM,
    KnowledgeCandidateORM, ReviewRecordORM, PromotionRecordORM, SynthesisCandidateORM
)
from .auth import verify_password

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

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

def list_packs():
    with SessionLocal() as db:
        return db.execute(select(PackORM).order_by(PackORM.id)).scalars().all()

def get_pack(pack_id: str):
    with SessionLocal() as db:
        return db.get(PackORM, pack_id)

def create_learner(owner_user_id: int, learner_id: str, display_name: str = ""):
    with SessionLocal() as db:
        if db.get(LearnerORM, learner_id) is None:
            db.add(LearnerORM(id=learner_id, owner_user_id=owner_user_id, display_name=display_name))
            db.commit()

def learner_owned_by_user(user_id: int, learner_id: str) -> bool:
    with SessionLocal() as db:
        learner = db.get(LearnerORM, learner_id)
        return learner is not None and learner.owner_user_id == user_id

def list_mastery_records(learner_id: str):
    with SessionLocal() as db:
        rows = db.execute(select(MasteryRecordORM).where(MasteryRecordORM.learner_id == learner_id)).scalars().all()
        return [{
            "concept_id": r.concept_id,
            "dimension": r.dimension,
            "score": r.score,
            "confidence": r.confidence,
            "evidence_count": r.evidence_count,
            "last_updated": r.last_updated,
        } for r in rows]

def create_candidate(payload):
    with SessionLocal() as db:
        row = KnowledgeCandidateORM(
            source_type=payload.source_type,
            source_artifact_id=payload.source_artifact_id,
            learner_id=payload.learner_id,
            pack_id=payload.pack_id,
            candidate_kind=payload.candidate_kind,
            title=payload.title,
            summary=payload.summary,
            structured_payload_json=json.dumps(payload.structured_payload),
            evidence_summary=payload.evidence_summary,
            confidence_hint=payload.confidence_hint,
            novelty_score=payload.novelty_score,
            synthesis_score=payload.synthesis_score,
            triage_lane=payload.triage_lane,
            current_status="triaged",
            created_at=now_iso(),
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return row.id

def list_candidates():
    with SessionLocal() as db:
        rows = db.execute(select(KnowledgeCandidateORM).order_by(KnowledgeCandidateORM.id.desc())).scalars().all()
        return [{
            "candidate_id": r.id,
            "source_type": r.source_type,
            "source_artifact_id": r.source_artifact_id,
            "learner_id": r.learner_id,
            "pack_id": r.pack_id,
            "candidate_kind": r.candidate_kind,
            "title": r.title,
            "summary": r.summary,
            "structured_payload": json.loads(r.structured_payload_json or "{}"),
            "evidence_summary": r.evidence_summary,
            "confidence_hint": r.confidence_hint,
            "novelty_score": r.novelty_score,
            "synthesis_score": r.synthesis_score,
            "triage_lane": r.triage_lane,
            "current_status": r.current_status,
            "created_at": r.created_at,
        } for r in rows]

def get_candidate(candidate_id: int):
    with SessionLocal() as db:
        r = db.get(KnowledgeCandidateORM, candidate_id)
        if r is None:
            return None
        return {
            "candidate_id": r.id,
            "source_type": r.source_type,
            "source_artifact_id": r.source_artifact_id,
            "learner_id": r.learner_id,
            "pack_id": r.pack_id,
            "candidate_kind": r.candidate_kind,
            "title": r.title,
            "summary": r.summary,
            "structured_payload": json.loads(r.structured_payload_json or "{}"),
            "evidence_summary": r.evidence_summary,
            "confidence_hint": r.confidence_hint,
            "novelty_score": r.novelty_score,
            "synthesis_score": r.synthesis_score,
            "triage_lane": r.triage_lane,
            "current_status": r.current_status,
            "created_at": r.created_at,
        }

def update_candidate(candidate_id: int, triage_lane=None, current_status=None):
    with SessionLocal() as db:
        row = db.get(KnowledgeCandidateORM, candidate_id)
        if row is None:
            return None
        if triage_lane is not None:
            row.triage_lane = triage_lane
        if current_status is not None:
            row.current_status = current_status
        db.commit()
        db.refresh(row)
        return row

def create_review(candidate_id: int, reviewer_id: int, payload):
    with SessionLocal() as db:
        row = ReviewRecordORM(
            candidate_id=candidate_id,
            reviewer_id=reviewer_id,
            review_kind=payload.review_kind,
            verdict=payload.verdict,
            rationale=payload.rationale,
            requested_changes=payload.requested_changes,
            created_at=now_iso(),
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return row.id

def list_reviews(candidate_id: int):
    with SessionLocal() as db:
        rows = db.execute(select(ReviewRecordORM).where(ReviewRecordORM.candidate_id == candidate_id).order_by(ReviewRecordORM.id.desc())).scalars().all()
        return [{
            "review_id": r.id,
            "candidate_id": r.candidate_id,
            "reviewer_id": r.reviewer_id,
            "review_kind": r.review_kind,
            "verdict": r.verdict,
            "rationale": r.rationale,
            "requested_changes": r.requested_changes,
            "created_at": r.created_at,
        } for r in rows]

def create_promotion(candidate_id: int, promoted_by: int, payload):
    with SessionLocal() as db:
        row = PromotionRecordORM(
            candidate_id=candidate_id,
            promotion_target=payload.promotion_target,
            target_object_id=payload.target_object_id,
            promotion_status=payload.promotion_status,
            promoted_by=promoted_by,
            created_at=now_iso(),
        )
        db.add(row)
        candidate = db.get(KnowledgeCandidateORM, candidate_id)
        if candidate:
            candidate.current_status = "promoted"
            candidate.triage_lane = payload.promotion_target
        db.commit()
        db.refresh(row)
        return row.id

def list_promotions():
    with SessionLocal() as db:
        rows = db.execute(select(PromotionRecordORM).order_by(PromotionRecordORM.id.desc())).scalars().all()
        return [{
            "promotion_id": r.id,
            "candidate_id": r.candidate_id,
            "promotion_target": r.promotion_target,
            "target_object_id": r.target_object_id,
            "promotion_status": r.promotion_status,
            "promoted_by": r.promoted_by,
            "created_at": r.created_at,
        } for r in rows]

def create_synthesis_candidate(
    source_concept_id: str,
    target_concept_id: str,
    source_pack_id: str,
    target_pack_id: str,
    synthesis_kind: str,
    score_semantic: float,
    score_structural: float,
    score_trajectory: float,
    score_review_history: float,
    explanation: str,
    evidence: dict
):
    score_total = 0.35 * score_semantic + 0.25 * score_structural + 0.20 * score_trajectory + 0.10 * score_review_history + 0.10 * evidence.get("novelty", 0.0)
    with SessionLocal() as db:
        row = SynthesisCandidateORM(
            source_concept_id=source_concept_id,
            target_concept_id=target_concept_id,
            source_pack_id=source_pack_id,
            target_pack_id=target_pack_id,
            synthesis_kind=synthesis_kind,
            score_total=score_total,
            score_semantic=score_semantic,
            score_structural=score_structural,
            score_trajectory=score_trajectory,
            score_review_history=score_review_history,
            explanation=explanation,
            evidence_json=json.dumps(evidence),
            current_status="proposed",
            created_at=now_iso(),
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return row.id

def list_synthesis_candidates():
    with SessionLocal() as db:
        rows = db.execute(select(SynthesisCandidateORM).order_by(SynthesisCandidateORM.score_total.desc(), SynthesisCandidateORM.id.desc())).scalars().all()
        return [{
            "synthesis_id": r.id,
            "source_concept_id": r.source_concept_id,
            "target_concept_id": r.target_concept_id,
            "source_pack_id": r.source_pack_id,
            "target_pack_id": r.target_pack_id,
            "synthesis_kind": r.synthesis_kind,
            "score_total": r.score_total,
            "score_semantic": r.score_semantic,
            "score_structural": r.score_structural,
            "score_trajectory": r.score_trajectory,
            "score_review_history": r.score_review_history,
            "explanation": r.explanation,
            "evidence": json.loads(r.evidence_json or "{}"),
            "current_status": r.current_status,
            "created_at": r.created_at,
        } for r in rows]

def get_synthesis_candidate(synthesis_id: int):
    with SessionLocal() as db:
        r = db.get(SynthesisCandidateORM, synthesis_id)
        if r is None:
            return None
        return {
            "synthesis_id": r.id,
            "source_concept_id": r.source_concept_id,
            "target_concept_id": r.target_concept_id,
            "source_pack_id": r.source_pack_id,
            "target_pack_id": r.target_pack_id,
            "synthesis_kind": r.synthesis_kind,
            "score_total": r.score_total,
            "score_semantic": r.score_semantic,
            "score_structural": r.score_structural,
            "score_trajectory": r.score_trajectory,
            "score_review_history": r.score_review_history,
            "explanation": r.explanation,
            "evidence": json.loads(r.evidence_json or "{}"),
            "current_status": r.current_status,
            "created_at": r.created_at,
        }
