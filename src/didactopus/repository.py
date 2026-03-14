from __future__ import annotations
import json
from datetime import datetime, timezone
from sqlalchemy import select
from .db import SessionLocal
from .orm import (
    UserORM, PackORM, LearnerORM, KnowledgeCandidateORM, PromotionRecordORM,
    PackPatchProposalORM, CurriculumDraftORM, SkillBundleORM, ObjectVersionORM, SynthesisCandidateORM
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
        } for r in rows]

def get_candidate(candidate_id: int):
    with SessionLocal() as db:
        r = db.get(KnowledgeCandidateORM, candidate_id)
        if r is None:
            return None
        return {
            "candidate_id": r.id,
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
        }

def create_pack_patch(candidate):
    with SessionLocal() as db:
        row = PackPatchProposalORM(
            candidate_id=candidate["candidate_id"],
            pack_id=candidate["pack_id"],
            patch_type=candidate["candidate_kind"],
            title=candidate["title"],
            proposed_change_json=json.dumps(candidate["structured_payload"]),
            evidence_summary=candidate["evidence_summary"],
            reviewer_notes="",
            status="proposed",
            current_version=1,
            created_at=now_iso(),
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        _create_version("pack_patch", row.id, 1, {
            "title": row.title,
            "proposed_change": json.loads(row.proposed_change_json or "{}"),
            "status": row.status,
            "reviewer_notes": row.reviewer_notes,
        }, 1, "Initial version")
        return f"patch:{row.id}"

def create_curriculum_draft(candidate):
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
            editorial_notes="",
            status="draft",
            current_version=1,
            created_at=now_iso(),
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        _create_version("curriculum_draft", row.id, 1, {
            "topic_focus": row.topic_focus,
            "content_markdown": row.content_markdown,
            "product_type": row.product_type,
            "audience": row.audience,
        }, 1, "Initial version")
        return f"curriculum:{row.id}"

def create_skill_bundle(candidate):
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
            current_version=1,
            created_at=now_iso(),
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        _create_version("skill_bundle", row.id, 1, {
            "skill_name": row.skill_name,
            "domain": row.domain,
            "prerequisites": json.loads(row.prerequisites_json or "[]"),
            "expected_inputs": json.loads(row.expected_inputs_json or "[]"),
            "failure_modes": json.loads(row.failure_modes_json or "[]"),
            "validation_checks": json.loads(row.validation_checks_json or "[]"),
            "canonical_examples": json.loads(row.canonical_examples_json or "[]"),
        }, 1, "Initial version")
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
            "current_version": r.current_version,
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
            "current_version": r.current_version,
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
            "current_version": r.current_version,
            "created_at": r.created_at,
        } for r in rows]

def get_pack_patch(patch_id: int):
    with SessionLocal() as db:
        r = db.get(PackPatchProposalORM, patch_id)
        if r is None: return None
        return {
            "patch_id": r.id, "pack_id": r.pack_id, "title": r.title,
            "proposed_change": json.loads(r.proposed_change_json or "{}"),
            "reviewer_notes": r.reviewer_notes, "status": r.status, "current_version": r.current_version
        }

def get_curriculum_draft(draft_id: int):
    with SessionLocal() as db:
        r = db.get(CurriculumDraftORM, draft_id)
        if r is None: return None
        return {
            "draft_id": r.id, "topic_focus": r.topic_focus, "product_type": r.product_type,
            "audience": r.audience, "source_concepts": json.loads(r.source_concepts_json or "[]"),
            "content_markdown": r.content_markdown, "editorial_notes": r.editorial_notes,
            "status": r.status, "current_version": r.current_version
        }

def get_skill_bundle(bundle_id: int):
    with SessionLocal() as db:
        r = db.get(SkillBundleORM, bundle_id)
        if r is None: return None
        return {
            "skill_bundle_id": r.id, "skill_name": r.skill_name, "domain": r.domain,
            "prerequisites": json.loads(r.prerequisites_json or "[]"),
            "expected_inputs": json.loads(r.expected_inputs_json or "[]"),
            "failure_modes": json.loads(r.failure_modes_json or "[]"),
            "validation_checks": json.loads(r.validation_checks_json or "[]"),
            "canonical_examples": json.loads(r.canonical_examples_json or "[]"),
            "status": r.status, "current_version": r.current_version
        }

def _create_version(object_kind: str, object_id: int, version_number: int, payload: dict, editor_id: int, note: str):
    with SessionLocal() as db:
        db.add(ObjectVersionORM(
            object_kind=object_kind,
            object_id=object_id,
            version_number=version_number,
            payload_json=json.dumps(payload),
            editor_id=editor_id,
            note=note,
            created_at=now_iso(),
        ))
        db.commit()

def list_versions(object_kind: str, object_id: int):
    with SessionLocal() as db:
        rows = db.execute(
            select(ObjectVersionORM)
            .where(ObjectVersionORM.object_kind == object_kind, ObjectVersionORM.object_id == object_id)
            .order_by(ObjectVersionORM.version_number.desc())
        ).scalars().all()
        return [{
            "version_id": r.id,
            "object_kind": r.object_kind,
            "object_id": r.object_id,
            "version_number": r.version_number,
            "payload": json.loads(r.payload_json or "{}"),
            "editor_id": r.editor_id,
            "note": r.note,
            "created_at": r.created_at,
        } for r in rows]

def edit_pack_patch(patch_id: int, payload: dict, editor_id: int, note: str):
    with SessionLocal() as db:
        row = db.get(PackPatchProposalORM, patch_id)
        if row is None: return None
        if "title" in payload: row.title = payload["title"]
        if "proposed_change" in payload: row.proposed_change_json = json.dumps(payload["proposed_change"])
        if "reviewer_notes" in payload: row.reviewer_notes = payload["reviewer_notes"]
        if "status" in payload: row.status = payload["status"]
        row.current_version += 1
        db.commit()
        db.refresh(row)
    _create_version("pack_patch", patch_id, row.current_version, {
        "title": row.title,
        "proposed_change": json.loads(row.proposed_change_json or "{}"),
        "reviewer_notes": row.reviewer_notes,
        "status": row.status,
    }, editor_id, note)
    return row

def edit_curriculum_draft(draft_id: int, payload: dict, editor_id: int, note: str):
    with SessionLocal() as db:
        row = db.get(CurriculumDraftORM, draft_id)
        if row is None: return None
        if "topic_focus" in payload: row.topic_focus = payload["topic_focus"]
        if "content_markdown" in payload: row.content_markdown = payload["content_markdown"]
        if "editorial_notes" in payload: row.editorial_notes = payload["editorial_notes"]
        if "status" in payload: row.status = payload["status"]
        row.current_version += 1
        db.commit()
        db.refresh(row)
    _create_version("curriculum_draft", draft_id, row.current_version, {
        "topic_focus": row.topic_focus,
        "content_markdown": row.content_markdown,
        "editorial_notes": row.editorial_notes,
        "status": row.status,
    }, editor_id, note)
    return row

def edit_skill_bundle(bundle_id: int, payload: dict, editor_id: int, note: str):
    with SessionLocal() as db:
        row = db.get(SkillBundleORM, bundle_id)
        if row is None: return None
        if "skill_name" in payload: row.skill_name = payload["skill_name"]
        if "prerequisites" in payload: row.prerequisites_json = json.dumps(payload["prerequisites"])
        if "expected_inputs" in payload: row.expected_inputs_json = json.dumps(payload["expected_inputs"])
        if "failure_modes" in payload: row.failure_modes_json = json.dumps(payload["failure_modes"])
        if "validation_checks" in payload: row.validation_checks_json = json.dumps(payload["validation_checks"])
        if "canonical_examples" in payload: row.canonical_examples_json = json.dumps(payload["canonical_examples"])
        if "status" in payload: row.status = payload["status"]
        row.current_version += 1
        db.commit()
        db.refresh(row)
    _create_version("skill_bundle", bundle_id, row.current_version, {
        "skill_name": row.skill_name,
        "prerequisites": json.loads(row.prerequisites_json or "[]"),
        "expected_inputs": json.loads(row.expected_inputs_json or "[]"),
        "failure_modes": json.loads(row.failure_modes_json or "[]"),
        "validation_checks": json.loads(row.validation_checks_json or "[]"),
        "canonical_examples": json.loads(row.canonical_examples_json or "[]"),
        "status": row.status,
    }, editor_id, note)
    return row

def apply_pack_patch(patch_id: int, editor_id: int, note: str):
    with SessionLocal() as db:
        patch = db.get(PackPatchProposalORM, patch_id)
        if patch is None: return None
        pack = db.get(PackORM, patch.pack_id)
        if pack is None: return None
        pack_data = json.loads(pack.data_json or "{}")
        proposed = json.loads(patch.proposed_change_json or "{}")
        pack_data.setdefault("applied_patches", []).append({
            "patch_id": patch.id,
            "title": patch.title,
            "proposed_change": proposed,
            "applied_at": now_iso(),
        })
        if "affected_concept" in proposed and "suggested_prereq" in proposed:
            for concept in pack_data.get("concepts", []):
                if concept.get("id") == proposed["affected_concept"]:
                    prereqs = concept.setdefault("prerequisites", [])
                    if proposed["suggested_prereq"] not in prereqs:
                        prereqs.append(proposed["suggested_prereq"])
        pack.data_json = json.dumps(pack_data)
        patch.status = "applied"
        db.commit()
        db.refresh(patch)
    _create_version("pack_patch", patch_id, patch.current_version, {
        "title": patch.title,
        "proposed_change": json.loads(patch.proposed_change_json or "{}"),
        "status": patch.status,
    }, editor_id, note)
    return patch

def export_curriculum_draft(draft_id: int):
    draft = get_curriculum_draft(draft_id)
    if draft is None: return None
    return {
        "markdown": draft["content_markdown"],
        "json": json.dumps(draft, indent=2)
    }

def export_skill_bundle(bundle_id: int):
    import yaml
    bundle = get_skill_bundle(bundle_id)
    if bundle is None: return None
    return {
        "json": json.dumps(bundle, indent=2),
        "yaml": yaml.safe_dump(bundle, sort_keys=False)
    }

def create_synthesis_candidate(source_concept_id, target_concept_id, source_pack_id, target_pack_id, synthesis_kind, score_semantic, score_structural, score_trajectory, score_review_history, explanation, evidence):
    score_total = 0.35 * score_semantic + 0.25 * score_structural + 0.20 * score_trajectory + 0.10 * score_review_history + 0.10 * evidence.get("novelty", 0.0)
    with SessionLocal() as db:
        row = SynthesisCandidateORM(
            source_concept_id=source_concept_id, target_concept_id=target_concept_id,
            source_pack_id=source_pack_id, target_pack_id=target_pack_id,
            synthesis_kind=synthesis_kind, score_total=score_total,
            score_semantic=score_semantic, score_structural=score_structural,
            score_trajectory=score_trajectory, score_review_history=score_review_history,
            explanation=explanation, evidence_json=json.dumps(evidence),
            current_status="proposed", created_at=now_iso(),
        )
        db.add(row); db.commit(); db.refresh(row); return row.id

def list_synthesis_candidates():
    with SessionLocal() as db:
        rows = db.execute(select(SynthesisCandidateORM).order_by(SynthesisCandidateORM.score_total.desc(), SynthesisCandidateORM.id.desc())).scalars().all()
        return [{
            "synthesis_id": r.id, "source_concept_id": r.source_concept_id, "target_concept_id": r.target_concept_id,
            "source_pack_id": r.source_pack_id, "target_pack_id": r.target_pack_id, "synthesis_kind": r.synthesis_kind,
            "score_total": r.score_total, "score_semantic": r.score_semantic, "score_structural": r.score_structural,
            "score_trajectory": r.score_trajectory, "score_review_history": r.score_review_history,
            "explanation": r.explanation, "evidence": json.loads(r.evidence_json or "{}"),
            "current_status": r.current_status, "created_at": r.created_at,
        } for r in rows]

def get_synthesis_candidate(synthesis_id: int):
    with SessionLocal() as db:
        r = db.get(SynthesisCandidateORM, synthesis_id)
        if r is None: return None
        return {
            "synthesis_id": r.id, "source_concept_id": r.source_concept_id, "target_concept_id": r.target_concept_id,
            "source_pack_id": r.source_pack_id, "target_pack_id": r.target_pack_id, "synthesis_kind": r.synthesis_kind,
            "score_total": r.score_total, "score_semantic": r.score_semantic, "score_structural": r.score_structural,
            "score_trajectory": r.score_trajectory, "score_review_history": r.score_review_history,
            "explanation": r.explanation, "evidence": json.loads(r.evidence_json or "{}"),
            "current_status": r.current_status, "created_at": r.created_at,
        }
