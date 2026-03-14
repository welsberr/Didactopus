from __future__ import annotations
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from .db import Base, engine
from .models import (
    LoginRequest, TokenPair, KnowledgeCandidateCreate, PromoteRequest,
    SynthesisRunRequest, SynthesisPromoteRequest, CreateLearnerRequest,
    ObjectEditRequest, PatchApplyRequest
)
from .repository import (
    authenticate_user, get_user_by_id, create_learner, create_candidate, list_candidates, get_candidate,
    create_promotion, list_promotions, list_pack_patches, list_curriculum_drafts, list_skill_bundles,
    list_synthesis_candidates, get_synthesis_candidate,
    edit_pack_patch, edit_curriculum_draft, edit_skill_bundle, list_versions,
    apply_pack_patch, export_curriculum_draft, export_skill_bundle
)
from .auth import issue_access_token, issue_refresh_token, decode_token, new_token_id
from .synthesis import generate_synthesis_candidates

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Didactopus Object Versioning and Export API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
_refresh_tokens = {}

def current_user(authorization: str = Header(default="")):
    token = authorization.removeprefix("Bearer ").strip()
    payload = decode_token(token) if token else None
    if not payload or payload.get("kind") != "access":
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = get_user_by_id(int(payload["sub"]))
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user

def require_reviewer(user = Depends(current_user)):
    if user.role not in {"admin", "reviewer"}:
        raise HTTPException(status_code=403, detail="Reviewer role required")
    return user

@app.post("/api/login", response_model=TokenPair)
def login(payload: LoginRequest):
    user = authenticate_user(payload.username, payload.password)
    if user is None: raise HTTPException(status_code=401, detail="Invalid credentials")
    token_id = new_token_id(); _refresh_tokens[token_id] = user.id
    return TokenPair(access_token=issue_access_token(user.id, user.username, user.role),
                     refresh_token=issue_refresh_token(user.id, user.username, user.role, token_id),
                     username=user.username, role=user.role)

@app.post("/api/learners")
def api_create_learner(payload: CreateLearnerRequest, user = Depends(current_user)):
    create_learner(user.id, payload.learner_id, payload.display_name)
    return {"ok": True, "learner_id": payload.learner_id}

@app.post("/api/knowledge-candidates")
def api_create_candidate(payload: KnowledgeCandidateCreate, reviewer = Depends(require_reviewer)):
    return {"candidate_id": create_candidate(payload)}

@app.get("/api/knowledge-candidates")
def api_list_candidates(reviewer = Depends(require_reviewer)):
    return list_candidates()

@app.post("/api/knowledge-candidates/{candidate_id}/promote")
def api_promote_candidate(candidate_id: int, payload: PromoteRequest, reviewer = Depends(require_reviewer)):
    if get_candidate(candidate_id) is None: raise HTTPException(status_code=404, detail="Candidate not found")
    return {"promotion_id": create_promotion(candidate_id, reviewer.id, payload)}

@app.get("/api/promotions")
def api_list_promotions(reviewer = Depends(require_reviewer)):
    return list_promotions()

@app.get("/api/pack-patches")
def api_list_pack_patches(reviewer = Depends(require_reviewer)):
    return list_pack_patches()

@app.get("/api/curriculum-drafts")
def api_list_curriculum_drafts(reviewer = Depends(require_reviewer)):
    return list_curriculum_drafts()

@app.get("/api/skill-bundles")
def api_list_skill_bundles(reviewer = Depends(require_reviewer)):
    return list_skill_bundles()

@app.post("/api/pack-patches/{patch_id}/edit")
def api_edit_patch(patch_id: int, payload: ObjectEditRequest, reviewer = Depends(require_reviewer)):
    row = edit_pack_patch(patch_id, payload.payload, reviewer.id, payload.note)
    if row is None: raise HTTPException(status_code=404, detail="Patch not found")
    return {"patch_id": row.id, "current_version": row.current_version}

@app.post("/api/curriculum-drafts/{draft_id}/edit")
def api_edit_curriculum(draft_id: int, payload: ObjectEditRequest, reviewer = Depends(require_reviewer)):
    row = edit_curriculum_draft(draft_id, payload.payload, reviewer.id, payload.note)
    if row is None: raise HTTPException(status_code=404, detail="Draft not found")
    return {"draft_id": row.id, "current_version": row.current_version}

@app.post("/api/skill-bundles/{bundle_id}/edit")
def api_edit_skill(bundle_id: int, payload: ObjectEditRequest, reviewer = Depends(require_reviewer)):
    row = edit_skill_bundle(bundle_id, payload.payload, reviewer.id, payload.note)
    if row is None: raise HTTPException(status_code=404, detail="Skill bundle not found")
    return {"skill_bundle_id": row.id, "current_version": row.current_version}

@app.get("/api/object-versions/{object_kind}/{object_id}")
def api_object_versions(object_kind: str, object_id: int, reviewer = Depends(require_reviewer)):
    return list_versions(object_kind, object_id)

@app.post("/api/pack-patches/{patch_id}/apply")
def api_apply_patch(patch_id: int, payload: PatchApplyRequest, reviewer = Depends(require_reviewer)):
    row = apply_pack_patch(patch_id, reviewer.id, payload.note)
    if row is None: raise HTTPException(status_code=404, detail="Patch or pack not found")
    return {"patch_id": row.id, "status": row.status}

@app.get("/api/curriculum-drafts/{draft_id}/export")
def api_export_curriculum(draft_id: int, reviewer = Depends(require_reviewer)):
    out = export_curriculum_draft(draft_id)
    if out is None: raise HTTPException(status_code=404, detail="Draft not found")
    return out

@app.get("/api/skill-bundles/{bundle_id}/export")
def api_export_skill(bundle_id: int, reviewer = Depends(require_reviewer)):
    out = export_skill_bundle(bundle_id)
    if out is None: raise HTTPException(status_code=404, detail="Skill bundle not found")
    return out

@app.post("/api/synthesis/run")
def api_run_synthesis(payload: SynthesisRunRequest, reviewer = Depends(require_reviewer)):
    created = generate_synthesis_candidates(payload.source_pack_id, payload.target_pack_id, payload.limit)
    return {"created_count": len(created), "synthesis_ids": created}

@app.get("/api/synthesis/candidates")
def api_list_synthesis(reviewer = Depends(require_reviewer)):
    return list_synthesis_candidates()

@app.post("/api/synthesis/candidates/{synthesis_id}/promote")
def api_promote_synthesis(synthesis_id: int, payload: SynthesisPromoteRequest, reviewer = Depends(require_reviewer)):
    syn = get_synthesis_candidate(synthesis_id)
    if syn is None: raise HTTPException(status_code=404, detail="Synthesis candidate not found")
    candidate_id = create_candidate(KnowledgeCandidateCreate(
        source_type="synthesis_engine", learner_id="system", pack_id=syn["source_pack_id"],
        candidate_kind="synthesis_proposal",
        title=f"Synthesis: {syn['source_concept_id']} ↔ {syn['target_concept_id']}",
        summary=syn["explanation"], structured_payload=syn,
        evidence_summary="Promoted from synthesis engine candidate",
        confidence_hint=syn["score_total"], novelty_score=syn["evidence"].get("novelty", 0.0),
        synthesis_score=syn["score_total"], triage_lane=payload.promotion_target,
    ))
    promotion_id = create_promotion(candidate_id, reviewer.id, PromoteRequest(promotion_target=payload.promotion_target, target_object_id="", promotion_status="approved"))
    return {"candidate_id": candidate_id, "promotion_id": promotion_id}

def main():
    uvicorn.run(app, host="127.0.0.1", port=8011)
