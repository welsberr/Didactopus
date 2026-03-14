from __future__ import annotations
import json
from fastapi import FastAPI, HTTPException, Header, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from .config import load_settings
from .db import Base, engine
from .models import LoginRequest, ServiceAccountLoginRequest, ServiceAccountCreateRequest, ServiceToken, RefreshRequest, TokenPair, CreateLearnerRequest, LearnerState, EvidenceEvent, EvaluatorSubmission, EvaluatorJobStatus, CreatePackRequest, ContributionSubmissionCreate, AgentCapabilityManifest, AgentLearnerPlanRequest, AgentLearnerPlanResponse
from .repository import authenticate_user, get_user_by_id, create_service_account, list_service_accounts, authenticate_service_account, store_refresh_token, refresh_token_active, revoke_refresh_token, deployment_policy_profile, list_packs_for_user, get_pack, get_pack_row, upsert_pack, create_learner, learner_owned_by_user, load_learner_state, save_learner_state, create_evaluator_job, get_evaluator_job, list_evaluator_jobs_for_learner
from .engine import apply_evidence, recommend_next
from .auth import issue_access_token, issue_refresh_token, issue_service_access_token, decode_token, new_token_id, new_secret
from .worker import process_job

settings = load_settings()
Base.metadata.create_all(bind=engine)

SERVICE_SCOPE_MAP = {
    "packs:read": "packs:read",
    "packs:write_personal": "packs:write_personal",
    "contributions:submit": "contributions:submit",
    "learners:read": "learners:read",
    "learners:write": "learners:write",
    "recommendations:read": "recommendations:read",
    "evaluators:submit": "evaluators:submit",
    "evaluators:read": "evaluators:read",
    "governance:read": "governance:read",
    "governance:write": "governance:write",
}

app = FastAPI(title="Didactopus API Prototype")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def current_actor(authorization: str = Header(default="")):
    token = authorization.removeprefix("Bearer ").strip()
    payload = decode_token(token) if token else None
    if not payload:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if payload.get("kind") == "access":
        user = get_user_by_id(int(payload["sub"]))
        if user is None or not user.is_active:
            raise HTTPException(status_code=401, detail="Unauthorized")
        return {"actor_type": "user", "user": user, "scopes": None}
    if payload.get("kind") == "service":
        return {"actor_type": "service", "service_account_id": int(payload["sub"]), "service_account_name": payload.get("service_account_name"), "scopes": payload.get("scopes", [])}
    raise HTTPException(status_code=401, detail="Unauthorized")

def require_user(actor = Depends(current_actor)):
    if actor["actor_type"] != "user":
        raise HTTPException(status_code=403, detail="Human user required")
    return actor["user"]

def require_admin(actor = Depends(current_actor)):
    if actor["actor_type"] != "user" or actor["user"].role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    return actor["user"]

def require_scope(scope: str):
    def inner(actor = Depends(current_actor)):
        if actor["actor_type"] == "user":
            return actor
        scopes = set(actor.get("scopes") or [])
        if scope not in scopes:
            raise HTTPException(status_code=403, detail=f"Missing scope: {scope}")
        return actor
    return inner

def ensure_learner_access(actor, learner_id: str):
    if actor["actor_type"] == "service":
        return
    user = actor["user"]
    if user.role == "admin":
        return
    if not learner_owned_by_user(user.id, learner_id):
        raise HTTPException(status_code=403, detail="Learner not accessible by this actor")

def ensure_pack_access(actor, pack_id: str):
    row = get_pack_row(pack_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Pack not found")
    if actor["actor_type"] == "service":
        return row
    user = actor["user"]
    if user.role == "admin":
        return row
    if row.policy_lane == "community":
        return row
    if row.owner_user_id == user.id:
        return row
    raise HTTPException(status_code=403, detail="Pack not accessible by this actor")

@app.post("/api/login", response_model=TokenPair)
def login(payload: LoginRequest):
    user = authenticate_user(payload.username, payload.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token_id = new_token_id()
    store_refresh_token(user.id, token_id)
    return TokenPair(access_token=issue_access_token(user.id, user.username, user.role), refresh_token=issue_refresh_token(user.id, user.username, user.role, token_id), username=user.username, role=user.role)

@app.post("/api/service-accounts/login", response_model=ServiceToken)
def service_login(payload: ServiceAccountLoginRequest):
    sa = authenticate_service_account(payload.name, payload.secret)
    if sa is None:
        raise HTTPException(status_code=401, detail="Invalid service account credentials")
    scopes = json.loads(sa.scopes_json or "[]")
    return ServiceToken(access_token=issue_service_access_token(sa.id, sa.name, scopes), service_account_name=sa.name, scopes=scopes)

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
    return TokenPair(access_token=issue_access_token(user.id, user.username, user.role), refresh_token=issue_refresh_token(user.id, user.username, user.role, new_jti), username=user.username, role=user.role)

@app.get("/api/deployment-policy")
def api_deployment_policy(actor = Depends(current_actor)):
    return deployment_policy_profile().model_dump()

@app.get("/api/agent/capabilities", response_model=AgentCapabilityManifest)
def api_agent_capabilities(actor = Depends(current_actor)):
    return AgentCapabilityManifest()

@app.post("/api/agent/learner-plan", response_model=AgentLearnerPlanResponse)
def api_agent_learner_plan(payload: AgentLearnerPlanRequest, actor = Depends(require_scope("recommendations:read"))):
    ensure_learner_access(actor, payload.learner_id)
    ensure_pack_access(actor, payload.pack_id)
    state = load_learner_state(payload.learner_id)
    pack = get_pack(payload.pack_id)
    if pack is None:
        raise HTTPException(status_code=404, detail="Pack not found")
    cards = recommend_next(state, pack)
    return AgentLearnerPlanResponse(learner_id=payload.learner_id, pack_id=payload.pack_id, next_cards=cards, suggested_actions=["Read learner state", "Choose next card", "Submit evidence", "Refresh recommendations"])

@app.post("/api/admin/service-accounts")
def api_create_service_account(payload: ServiceAccountCreateRequest, user = Depends(require_admin)):
    secret = new_secret()
    sa = create_service_account(payload.name, user.id, payload.description, payload.scopes, secret)
    return {"id": sa.id, "name": sa.name, "scopes": payload.scopes, "secret": secret}

@app.get("/api/admin/service-accounts")
def api_list_service_accounts(user = Depends(require_admin)):
    return list_service_accounts()

@app.get("/api/packs")
def api_list_packs(actor = Depends(require_scope("packs:read"))):
    user_id = actor["user"].id if actor["actor_type"] == "user" else None
    return [p.model_dump() for p in list_packs_for_user(user_id, include_unpublished=(actor["actor_type"] == "user" and actor["user"].role == "admin"))]

@app.post("/api/packs")
def api_upsert_personal_pack(payload: CreatePackRequest, actor = Depends(require_scope("packs:write_personal"))):
    if payload.policy_lane != "personal":
        raise HTTPException(status_code=403, detail="This endpoint is for personal-lane write access")
    if actor["actor_type"] != "user":
        raise HTTPException(status_code=403, detail="Service accounts may not own personal packs in this scaffold")
    upsert_pack(payload.pack, submitted_by_user_id=actor["user"].id, policy_lane="personal", is_published=payload.is_published, change_summary=payload.change_summary)
    return {"ok": True, "pack_id": payload.pack.id, "policy_lane": "personal"}

@app.post("/api/contributions")
def api_create_contribution(payload: ContributionSubmissionCreate, actor = Depends(require_scope("contributions:submit"))):
    contributor_id = actor["user"].id if actor["actor_type"] == "user" else 0
    return {"ok": True, "note": "Contribution flow placeholder for this scaffold", "contributor_id": contributor_id}

@app.post("/api/learners")
def api_create_learner(payload: CreateLearnerRequest, actor = Depends(require_scope("learners:write"))):
    if actor["actor_type"] != "user":
        raise HTTPException(status_code=403, detail="Service accounts do not create learners in this scaffold")
    create_learner(actor["user"].id, payload.learner_id, payload.display_name)
    return {"ok": True, "learner_id": payload.learner_id}

@app.get("/api/learners/{learner_id}/state")
def api_get_learner_state(learner_id: str, actor = Depends(require_scope("learners:read"))):
    ensure_learner_access(actor, learner_id)
    return load_learner_state(learner_id).model_dump()

@app.put("/api/learners/{learner_id}/state")
def api_put_learner_state(learner_id: str, state: LearnerState, actor = Depends(require_scope("learners:write"))):
    ensure_learner_access(actor, learner_id)
    if learner_id != state.learner_id:
        raise HTTPException(status_code=400, detail="Learner ID mismatch")
    return save_learner_state(state).model_dump()

@app.post("/api/learners/{learner_id}/evidence")
def api_post_evidence(learner_id: str, event: EvidenceEvent, actor = Depends(require_scope("learners:write"))):
    ensure_learner_access(actor, learner_id)
    state = load_learner_state(learner_id)
    state = apply_evidence(state, event)
    save_learner_state(state)
    return state.model_dump()

@app.get("/api/learners/{learner_id}/recommendations/{pack_id}")
def api_get_recommendations(learner_id: str, pack_id: str, actor = Depends(require_scope("recommendations:read"))):
    ensure_learner_access(actor, learner_id)
    ensure_pack_access(actor, pack_id)
    state = load_learner_state(learner_id)
    pack = get_pack(pack_id)
    if pack is None:
        raise HTTPException(status_code=404, detail="Pack not found")
    return {"cards": recommend_next(state, pack)}

@app.post("/api/learners/{learner_id}/evaluator-jobs", response_model=EvaluatorJobStatus)
def api_submit_evaluator_job(learner_id: str, payload: EvaluatorSubmission, background_tasks: BackgroundTasks, actor = Depends(require_scope("evaluators:submit"))):
    ensure_learner_access(actor, learner_id)
    ensure_pack_access(actor, payload.pack_id)
    job_id = create_evaluator_job(learner_id, payload.pack_id, payload.concept_id, payload.submitted_text)
    background_tasks.add_task(process_job, job_id)
    return EvaluatorJobStatus(job_id=job_id, status="queued")

@app.get("/api/evaluator-jobs/{job_id}", response_model=EvaluatorJobStatus)
def api_get_evaluator_job(job_id: int, actor = Depends(require_scope("evaluators:read"))):
    job = get_evaluator_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return EvaluatorJobStatus(job_id=job.id, status=job.status, result_score=job.result_score, result_confidence_hint=job.result_confidence_hint, result_notes=job.result_notes)

@app.get("/api/learners/{learner_id}/evaluator-history")
def api_get_evaluator_history(learner_id: str, actor = Depends(require_scope("evaluators:read"))):
    ensure_learner_access(actor, learner_id)
    jobs = list_evaluator_jobs_for_learner(learner_id)
    return [{"job_id": j.id, "status": j.status, "concept_id": j.concept_id, "result_score": j.result_score, "result_confidence_hint": j.result_confidence_hint, "result_notes": j.result_notes} for j in jobs]

def main():
    uvicorn.run(app, host=settings.host, port=settings.port)
