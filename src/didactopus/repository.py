from __future__ import annotations
import json
from datetime import datetime, timezone
from sqlalchemy import select
from .db import SessionLocal
from .orm import (
    UserORM, PackORM, LearnerORM,
    KnowledgeCandidateORM, ReviewRecordORM, PromotionRecordORM, SynthesisCandidateORM,
    PackPatchProposalORM, CurriculumDraftORM, SkillBundleORM
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

def create_learner(owner_user_id: int, learner_id: str, display_name: str = ""):
    with SessionLocal() as db:
        if db.get(LearnerORM, learner_id) is None:
            db.add(LearnerORM(id=learner_id, owner_user_id=owner_user_id, display_name=display_name))
            db.commit()

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
        out = []
        for r in rows:
            out.append({
                "candidate_id": r.id,
                "source_type": r.source_type,
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
            })
        return out

def get_candidate(candidate_id: int):
    with SessionLocal() as db:
        r = db.get(KnowledgeCandidateORM, candidate_id)
        if r is None:
            return None
        return {
            "candidate_id": r.id,
            "source_type": r.source_type,
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

def create_pack_patch(candidate, reviewer_notes: str = ""):
    with SessionLocal() as db:
        row = PackPatchProposalORM(
            candidate_id=candidate["candidate_id"],
            pack_id=candidate["pack_id"],
            patch_type=candidate["candidate_kind"],
            title=candidate["title"],
            proposed_change_json=json.dumps(candidate["structured_payload"]),
            evidence_summary=candidate["evidence_summary"],
            reviewer_notes=reviewer_notes,
            status="proposed",
            created_at=now_iso(),
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return f"patch:{row.id}"

def create_curriculum_draft(candidate, reviewer_notes: str = ""):
    with SessionLocal() as db:
        payload = candidate["structured_payload"]
        source_concepts = payload.get("source_concepts", [payload.get("affected_concept")] if payload.get("affected_concept") else [])
        content = f"# {candidate['title']}\n\n{candidate['summary']}\n\n## Evidence\n{candidate['evidence_summary']}\n"
        row = CurriculumDraftORM(
            candidate_id=candidate["candidate_id"],
            topic_focus=candidate["title"],
            product_type="lesson_outline",
            audience="general",
            source_concepts_json=json.dumps(source_concepts),
            content_markdown=content,
            editorial_notes=reviewer_notes,
            status="draft",
            created_at=now_iso(),
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return f"curriculum:{row.id}"

def create_skill_bundle(candidate, reviewer_notes: str = ""):
    with SessionLocal() as db:
        payload = candidate["structured_payload"]
        row = SkillBundleORM(
            candidate_id=candidate["candidate_id"],
            skill_name=candidate["title"],
            domain=candidate["pack_id"],
            prerequisites_json=json.dumps(payload.get("prerequisites", [])),
            expected_inputs_json=json.dumps(payload.get("expected_inputs", ["text"])),
            failure_modes_json=json.dumps(payload.get("failure_modes", ["misapplied concept"])),
            validation_checks_json=json.dumps(payload.get("validation_checks", ["can explain concept clearly"])),
            canonical_examples_json=json.dumps(payload.get("canonical_examples", [candidate["summary"]])),
            status="draft",
            created_at=now_iso(),
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return f"skill:{row.id}"

def create_promotion(candidate_id: int, promoted_by: int, payload):
    candidate = get_candidate(candidate_id)
    if candidate is None:
        return None
    target_object_id = payload.target_object_id
    if not target_object_id:
        if payload.promotion_target == "pack_improvement":
            target_object_id = create_pack_patch(candidate)
        elif payload.promotion_target == "curriculum_draft":
            target_object_id = create_curriculum_draft(candidate)
        elif payload.promotion_target == "reusable_skill_bundle":
            target_object_id = create_skill_bundle(candidate)
        elif payload.promotion_target == "archive":
            target_object_id = "archive:auto"
    with SessionLocal() as db:
        row = PromotionRecordORM(
            candidate_id=candidate_id,
            promotion_target=payload.promotion_target,
            target_object_id=target_object_id,
            promotion_status=payload.promotion_status,
            promoted_by=promoted_by,
            created_at=now_iso(),
        )
        db.add(row)
        cand = db.get(KnowledgeCandidateORM, candidate_id)
        if cand:
            cand.current_status = "promoted" if payload.promotion_target != "archive" else "archived"
            cand.triage_lane = payload.promotion_target
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

def list_pack_patches():
    with SessionLocal() as db:
        rows = db.execute(select(PackPatchProposalORM).order_by(PackPatchProposalORM.id.desc())).scalars().all()
        return [{
            "patch_id": r.id,
            "candidate_id": r.candidate_id,
            "pack_id": r.pack_id,
            "patch_type": r.patch_type,
            "title": r.title,
            "proposed_change": json.loads(r.proposed_change_json or "{}"),
            "evidence_summary": r.evidence_summary,
            "reviewer_notes": r.reviewer_notes,
            "status": r.status,
            "created_at": r.created_at,
        } for r in rows]

def list_curriculum_drafts():
    with SessionLocal() as db:
        rows = db.execute(select(CurriculumDraftORM).order_by(CurriculumDraftORM.id.desc())).scalars().all()
        return [{
            "draft_id": r.id,
            "candidate_id": r.candidate_id,
            "topic_focus": r.topic_focus,
            "product_type": r.product_type,
            "audience": r.audience,
            "source_concepts": json.loads(r.source_concepts_json or "[]"),
            "content_markdown": r.content_markdown,
            "editorial_notes": r.editorial_notes,
            "status": r.status,
            "created_at": r.created_at,
        } for r in rows]

def list_skill_bundles():
    with SessionLocal() as db:
        rows = db.execute(select(SkillBundleORM).order_by(SkillBundleORM.id.desc())).scalars().all()
        return [{
            "skill_bundle_id": r.id,
            "candidate_id": r.candidate_id,
            "skill_name": r.skill_name,
            "domain": r.domain,
            "prerequisites": json.loads(r.prerequisites_json or "[]"),
            "expected_inputs": json.loads(r.expected_inputs_json or "[]"),
            "failure_modes": json.loads(r.failure_modes_json or "[]"),
            "validation_checks": json.loads(r.validation_checks_json or "[]"),
            "canonical_examples": json.loads(r.canonical_examples_json or "[]"),
            "status": r.status,
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
