from __future__ import annotations
from fastapi import FastAPI, HTTPException, Header, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from .config import load_settings
from .db import Base, engine
from .models import LoginRequest, RefreshRequest, TokenPair, CreateLearnerRequest, LearnerState, EvidenceEvent, EvaluatorSubmission, EvaluatorJobStatus, CreatePackRequest
from .repository import (
    authenticate_user, get_user_by_id, store_refresh_token, refresh_token_active, revoke_refresh_token,
    list_packs, get_pack, upsert_pack, create_learner, learner_owned_by_user, load_learner_state,
    save_learner_state, create_evaluator_job, get_evaluator_job, list_evaluator_jobs_for_learner
)
from .engine import apply_evidence, recommend_next
from .auth import issue_access_token, issue_refresh_token, decode_token, new_token_id
from .worker import process_job

settings = load_settings()
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Didactopus API Prototype")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def current_user(authorization: str = Header(default="")):
    token = authorization.removeprefix("Bearer ").strip()
    payload = decode_token(token) if token else None
    if not payload or payload.get("kind") != "access":
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = get_user_by_id(int(payload["sub"]))
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user

def require_admin(user = Depends(current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    return user

def ensure_learner_access(user, learner_id: str):
    if user.role == "admin":
        return
    if not learner_owned_by_user(user.id, learner_id):
        raise HTTPException(status_code=403, detail="Learner not accessible by this user")

@app.post("/api/login", response_model=TokenPair)
def login(payload: LoginRequest):
    user = authenticate_user(payload.username, payload.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token_id = new_token_id()
    store_refresh_token(user.id, token_id)
    return TokenPair(
        access_token=issue_access_token(user.id, user.username, user.role),
        refresh_token=issue_refresh_token(user.id, user.username, user.role, token_id),
        username=user.username,
        role=user.role,
    )

@app.post("/api/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest):
    data = decode_token(payload.refresh_token)
    if not data or data.get("kind") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    token_id = data.get("jti")
    if not token_id or not refresh_token_active(token_id):
        raise HTTPException(status_code=401, detail="Refresh token inactive")
    user = get_user_by_id(int(data["sub"]))
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    revoke_refresh_token(token_id)
    new_jti = new_token_id()
    store_refresh_token(user.id, new_jti)
    return TokenPair(
        access_token=issue_access_token(user.id, user.username, user.role),
        refresh_token=issue_refresh_token(user.id, user.username, user.role, new_jti),
        username=user.username,
        role=user.role,
    )

@app.get("/api/packs")
def api_list_packs(user = Depends(current_user)):
    include_unpublished = user.role == "admin"
    return [p.model_dump() for p in list_packs(include_unpublished=include_unpublished)]

@app.get("/api/packs/{pack_id}")
def api_get_pack(pack_id: str, user = Depends(current_user)):
    pack = get_pack(pack_id)
    if pack is None:
        raise HTTPException(status_code=404, detail="Pack not found")
    return pack.model_dump()

@app.post("/api/admin/packs")
def api_upsert_pack(payload: CreatePackRequest, user = Depends(require_admin)):
    upsert_pack(payload.pack, is_published=payload.is_published)
    return {"ok": True, "pack_id": payload.pack.id}

@app.post("/api/learners")
def api_create_learner(payload: CreateLearnerRequest, user = Depends(current_user)):
    create_learner(user.id, payload.learner_id, payload.display_name)
    return {"ok": True, "learner_id": payload.learner_id}

@app.get("/api/learners/{learner_id}/state")
def api_get_learner_state(learner_id: str, user = Depends(current_user)):
    ensure_learner_access(user, learner_id)
    return load_learner_state(learner_id).model_dump()

@app.put("/api/learners/{learner_id}/state")
def api_put_learner_state(learner_id: str, state: LearnerState, user = Depends(current_user)):
    ensure_learner_access(user, learner_id)
    if learner_id != state.learner_id:
        raise HTTPException(status_code=400, detail="Learner ID mismatch")
    return save_learner_state(state).model_dump()

@app.post("/api/learners/{learner_id}/evidence")
def api_post_evidence(learner_id: str, event: EvidenceEvent, user = Depends(current_user)):
    ensure_learner_access(user, learner_id)
    state = load_learner_state(learner_id)
    state = apply_evidence(state, event)
    save_learner_state(state)
    return state.model_dump()

@app.get("/api/learners/{learner_id}/recommendations/{pack_id}")
def api_get_recommendations(learner_id: str, pack_id: str, user = Depends(current_user)):
    ensure_learner_access(user, learner_id)
    state = load_learner_state(learner_id)
    pack = get_pack(pack_id)
    if pack is None:
        raise HTTPException(status_code=404, detail="Pack not found")
    return {"cards": recommend_next(state, pack)}

@app.post("/api/learners/{learner_id}/evaluator-jobs", response_model=EvaluatorJobStatus)
def api_submit_evaluator_job(learner_id: str, payload: EvaluatorSubmission, background_tasks: BackgroundTasks, user = Depends(current_user)):
    ensure_learner_access(user, learner_id)
    job_id = create_evaluator_job(learner_id, payload.pack_id, payload.concept_id, payload.submitted_text)
    background_tasks.add_task(process_job, job_id)
    return EvaluatorJobStatus(job_id=job_id, status="queued")

@app.get("/api/evaluator-jobs/{job_id}", response_model=EvaluatorJobStatus)
def api_get_evaluator_job(job_id: int, user = Depends(current_user)):
    job = get_evaluator_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return EvaluatorJobStatus(job_id=job.id, status=job.status, result_score=job.result_score, result_confidence_hint=job.result_confidence_hint, result_notes=job.result_notes)

@app.get("/api/learners/{learner_id}/evaluator-history")
def api_get_evaluator_history(learner_id: str, user = Depends(current_user)):
    ensure_learner_access(user, learner_id)
    jobs = list_evaluator_jobs_for_learner(learner_id)
    return [{"job_id": j.id, "status": j.status, "concept_id": j.concept_id, "result_score": j.result_score, "result_confidence_hint": j.result_confidence_hint, "result_notes": j.result_notes} for j in jobs]

def main():
    uvicorn.run(app, host=settings.host, port=settings.port)

if __name__ == "__main__":
    main()
