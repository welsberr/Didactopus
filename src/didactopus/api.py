from __future__ import annotations
from fastapi import FastAPI, HTTPException, Header, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from .config import load_settings
from .db import Base, engine
from .models import LoginRequest, LoginResponse, CreateLearnerRequest, LearnerState, EvidenceEvent, EvaluatorSubmission, EvaluatorJobStatus
from .repository import (
    authenticate_user, get_user_by_token, list_packs, get_pack, create_learner,
    learner_owned_by_user, load_learner_state, save_learner_state,
    create_evaluator_job, get_evaluator_job, update_evaluator_job
)
from .engine import apply_evidence, recommend_next

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
    user = get_user_by_token(token) if token else None
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user

def ensure_learner_access(user, learner_id: str):
    if not learner_owned_by_user(user.id, learner_id):
        raise HTTPException(status_code=403, detail="Learner not accessible by this user")

def simulate_evaluator_job(job_id: int):
    job = get_evaluator_job(job_id)
    if job is None:
        return
    update_evaluator_job(job_id, "running")
    score = 0.78 if len(job.submitted_text.strip()) > 20 else 0.62
    confidence_hint = 0.72 if len(job.submitted_text.strip()) > 20 else 0.45
    notes = "Prototype evaluator: longer responses scored somewhat higher."
    update_evaluator_job(job_id, "completed", score=score, confidence_hint=confidence_hint, notes=notes)
    state = load_learner_state(job.learner_id)
    state = apply_evidence(state, EvidenceEvent(
        concept_id=job.concept_id,
        dimension="mastery",
        score=score,
        confidence_hint=confidence_hint,
        timestamp="2026-03-13T12:00:00+00:00",
        kind="review",
        source_id=f"evaluator-job-{job_id}",
    ))
    save_learner_state(state)

@app.post("/api/login", response_model=LoginResponse)
def login(payload: LoginRequest):
    user = authenticate_user(payload.username, payload.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return LoginResponse(token=user.token, username=user.username)

@app.get("/api/packs")
def api_list_packs(user = Depends(current_user)):
    return [p.model_dump() for p in list_packs()]

@app.get("/api/packs/{pack_id}")
def api_get_pack(pack_id: str, user = Depends(current_user)):
    pack = get_pack(pack_id)
    if pack is None:
        raise HTTPException(status_code=404, detail="Pack not found")
    return pack.model_dump()

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
    background_tasks.add_task(simulate_evaluator_job, job_id)
    return EvaluatorJobStatus(job_id=job_id, status="queued")

@app.get("/api/evaluator-jobs/{job_id}", response_model=EvaluatorJobStatus)
def api_get_evaluator_job(job_id: int, user = Depends(current_user)):
    job = get_evaluator_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return EvaluatorJobStatus(
        job_id=job.id,
        status=job.status,
        result_score=job.result_score,
        result_confidence_hint=job.result_confidence_hint,
        result_notes=job.result_notes,
    )

def main():
    uvicorn.run(app, host=settings.host, port=settings.port)

if __name__ == "__main__":
    main()
