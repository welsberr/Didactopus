from __future__ import annotations
from pydantic import BaseModel, Field

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    username: str
    role: str

class KnowledgeCandidateCreate(BaseModel):
    source_type: str = "learner_export"
    source_artifact_id: int | None = None
    learner_id: str
    pack_id: str
    candidate_kind: str
    title: str
    summary: str = ""
    structured_payload: dict = Field(default_factory=dict)
    evidence_summary: str = ""
    confidence_hint: float = 0.0
    novelty_score: float = 0.0
    synthesis_score: float = 0.0
    triage_lane: str = "archive"

class KnowledgeCandidateUpdate(BaseModel):
    triage_lane: str | None = None
    current_status: str | None = None

class ReviewCreate(BaseModel):
    review_kind: str = "human_review"
    verdict: str
    rationale: str = ""
    requested_changes: str = ""

class PromoteRequest(BaseModel):
    promotion_target: str
    target_object_id: str = ""
    promotion_status: str = "approved"

class SynthesisRunRequest(BaseModel):
    source_pack_id: str | None = None
    target_pack_id: str | None = None
    limit: int = 20

class SynthesisPromoteRequest(BaseModel):
    promotion_target: str = "pack_improvement"

class CreateLearnerRequest(BaseModel):
    learner_id: str
    display_name: str = ""

class MasteryRecord(BaseModel):
    concept_id: str
    dimension: str
    score: float = 0.0
    confidence: float = 0.0
    evidence_count: int = 0
    last_updated: str = ""

class LearnerState(BaseModel):
    learner_id: str
    records: list[MasteryRecord] = Field(default_factory=list)
