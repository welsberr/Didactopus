from __future__ import annotations
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from .models import LearnerState, EvidenceEvent
from .storage import FileStorage
from .engine import apply_evidence, recommend_next

BASE_DIR = Path(__file__).resolve().parents[2] / "data"
storage = FileStorage(BASE_DIR)

app = FastAPI(title="Didactopus API Prototype")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/packs")
def list_packs():
    return [p.model_dump() for p in storage.list_packs()]

@app.get("/api/packs/{pack_id}")
def get_pack(pack_id: str):
    pack = storage.get_pack(pack_id)
    if pack is None:
        raise HTTPException(status_code=404, detail="Pack not found")
    return pack.model_dump()

@app.get("/api/learners/{learner_id}/state")
def get_learner_state(learner_id: str):
    return storage.get_learner_state(learner_id).model_dump()

@app.put("/api/learners/{learner_id}/state")
def put_learner_state(learner_id: str, state: LearnerState):
    if learner_id != state.learner_id:
        raise HTTPException(status_code=400, detail="Learner ID mismatch")
    return storage.save_learner_state(state).model_dump()

@app.post("/api/learners/{learner_id}/evidence")
def post_evidence(learner_id: str, event: EvidenceEvent):
    state = storage.get_learner_state(learner_id)
    state = apply_evidence(state, event)
    storage.save_learner_state(state)
    return state.model_dump()

@app.get("/api/learners/{learner_id}/recommendations/{pack_id}")
def get_recommendations(learner_id: str, pack_id: str):
    state = storage.get_learner_state(learner_id)
    pack = storage.get_pack(pack_id)
    if pack is None:
        raise HTTPException(status_code=404, detail="Pack not found")
    return {"cards": recommend_next(state, pack)}

def main():
    uvicorn.run(app, host="127.0.0.1", port=8011)

if __name__ == "__main__":
    main()
