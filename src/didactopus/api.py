from __future__ import annotations
from fastapi import FastAPI, HTTPException, Header, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn
from datetime import datetime, timedelta, timezone
from pathlib import Path
from .db import Base, engine
from .models import LoginRequest, RefreshRequest, TokenPair, CreateLearnerRequest, LearnerState, MediaRenderRequest, ArtifactRetentionUpdate, KnowledgeExportRequest
from .repository import (
    authenticate_user, get_user_by_id, store_refresh_token, refresh_token_active, revoke_refresh_token,
    list_packs_for_user, get_pack, get_pack_row, create_learner, learner_owned_by_user, load_learner_state, save_learner_state,
    create_render_job, list_render_jobs, list_artifacts, get_artifact, update_artifact_retention, soft_delete_artifact
)
from .auth import issue_access_token, issue_refresh_token, decode_token, new_token_id
from .engine import build_graph_frames, stable_layout
from .worker import process_render_job
from .knowledge_export import build_knowledge_snapshot

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Didactopus API Prototype")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def current_user(authorization: str = Header(default="")):
    token = authorization.removeprefix("Bearer ").strip()
    payload = decode_token(token) if token else None
    if not payload or payload.get("kind") != "access":
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = get_user_by_id(int(payload["sub"]))
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user

def ensure_learner_access(user, learner_id: str):
    if user.role == "admin":
        return
    if not learner_owned_by_user(user.id, learner_id):
        raise HTTPException(status_code=403, detail="Learner not accessible by this user")

def ensure_pack_access(user, pack_id: str):
    row = get_pack_row(pack_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Pack not found")
    if user.role == "admin":
        return row
    if row.policy_lane == "community":
        return row
    if row.owner_user_id == user.id:
        return row
    raise HTTPException(status_code=403, detail="Pack not accessible by this user")

def future_iso(days: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()

@app.post("/api/login", response_model=TokenPair)
def login(payload: LoginRequest):
    user = authenticate_user(payload.username, payload.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token_id = new_token_id()
    store_refresh_token(user.id, token_id)
    return TokenPair(access_token=issue_access_token(user.id, user.username, user.role), refresh_token=issue_refresh_token(user.id, user.username, user.role, token_id), username=user.username, role=user.role)

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

@app.get("/api/packs")
def api_list_packs(user = Depends(current_user)):
    return [p.model_dump() for p in list_packs_for_user(user.id, include_unpublished=(user.role == "admin"))]

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

@app.get("/api/packs/{pack_id}/layout")
def api_pack_layout(pack_id: str, user = Depends(current_user)):
    ensure_pack_access(user, pack_id)
    pack = get_pack(pack_id)
    return {"pack_id": pack_id, "layout": stable_layout(pack)} if pack else {"pack_id": pack_id, "layout": {}}

@app.get("/api/learners/{learner_id}/graph-animation/{pack_id}")
def api_graph_animation(learner_id: str, pack_id: str, user = Depends(current_user)):
    ensure_learner_access(user, learner_id)
    ensure_pack_access(user, pack_id)
    pack = get_pack(pack_id)
    state = load_learner_state(learner_id)
    frames = build_graph_frames(state, pack)
    return {
        "learner_id": learner_id,
        "pack_id": pack_id,
        "pack_title": pack.title if pack else "",
        "frames": frames,
        "concepts": [{"id": c.id, "title": c.title, "prerequisites": c.prerequisites, "cross_pack_links": [l.model_dump() for l in c.cross_pack_links]} for c in pack.concepts] if pack else [],
    }

@app.post("/api/learners/{learner_id}/render-jobs/{pack_id}")
def api_render_job(learner_id: str, pack_id: str, payload: MediaRenderRequest, background_tasks: BackgroundTasks, user = Depends(current_user)):
    ensure_learner_access(user, learner_id)
    ensure_pack_access(user, pack_id)
    pack = get_pack(pack_id)
    state = load_learner_state(learner_id)
    animation = {
        "learner_id": learner_id,
        "pack_id": pack_id,
        "pack_title": pack.title if pack else "",
        "frames": build_graph_frames(state, pack),
    }
    job_id = create_render_job(learner_id, pack_id, payload.format, payload.fps, payload.theme)
    background_tasks.add_task(process_render_job, job_id, learner_id, pack_id, payload.format, payload.fps, payload.theme, payload.retention_class, payload.retention_days, animation)
    return {"job_id": job_id, "status": "queued"}

@app.get("/api/render-jobs")
def api_list_render_jobs(learner_id: str | None = None, user = Depends(current_user)):
    if learner_id:
        ensure_learner_access(user, learner_id)
    return list_render_jobs(learner_id)

@app.get("/api/artifacts")
def api_list_artifacts(learner_id: str | None = None, user = Depends(current_user)):
    if learner_id:
        ensure_learner_access(user, learner_id)
    return list_artifacts(learner_id)

@app.get("/api/artifacts/{artifact_id}/download")
def api_download_artifact(artifact_id: int, user = Depends(current_user)):
    artifact = get_artifact(artifact_id)
    if artifact is None or artifact.is_deleted:
        raise HTTPException(status_code=404, detail="Artifact not found")
    ensure_learner_access(user, artifact.learner_id)
    path = Path(artifact.path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Artifact path missing")
    if path.is_dir():
        manifest = path / "render_manifest.json"
        if not manifest.exists():
            raise HTTPException(status_code=404, detail="Artifact manifest missing")
        return FileResponse(str(manifest), filename=f"artifact-{artifact_id}-manifest.json")
    return FileResponse(str(path), filename=path.name)

@app.post("/api/artifacts/{artifact_id}/retention")
def api_update_artifact_retention(artifact_id: int, payload: ArtifactRetentionUpdate, user = Depends(current_user)):
    artifact = get_artifact(artifact_id)
    if artifact is None or artifact.is_deleted:
        raise HTTPException(status_code=404, detail="Artifact not found")
    ensure_learner_access(user, artifact.learner_id)
    expires_at = "" if payload.retention_days is None else future_iso(payload.retention_days)
    updated = update_artifact_retention(artifact_id, payload.retention_class, expires_at)
    return {"artifact_id": updated.id, "retention_class": updated.retention_class, "expires_at": updated.expires_at}

@app.delete("/api/artifacts/{artifact_id}")
def api_delete_artifact(artifact_id: int, user = Depends(current_user)):
    artifact = get_artifact(artifact_id)
    if artifact is None or artifact.is_deleted:
        raise HTTPException(status_code=404, detail="Artifact not found")
    ensure_learner_access(user, artifact.learner_id)
    updated = soft_delete_artifact(artifact_id)
    return {"artifact_id": updated.id, "is_deleted": updated.is_deleted}

@app.post("/api/learners/{learner_id}/knowledge-export/{pack_id}")
def api_knowledge_export(learner_id: str, pack_id: str, payload: KnowledgeExportRequest, user = Depends(current_user)):
    ensure_learner_access(user, learner_id)
    ensure_pack_access(user, pack_id)
    snapshot = build_knowledge_snapshot(learner_id, pack_id)
    snapshot["requested_export_kind"] = payload.export_kind
    return snapshot

def main():
    uvicorn.run(app, host="127.0.0.1", port=8011)
