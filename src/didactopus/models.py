from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Literal

EvidenceKind = Literal["checkpoint", "project", "exercise", "review"]

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    username: str
    role: str

class LoginRequest(BaseModel):
    username: str
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

class PackConcept(BaseModel):
    id: str
    title: str
    prerequisites: list[str] = Field(default_factory=list)
    masteryDimension: str = "mastery"
    exerciseReward: str = ""

class PackCompliance(BaseModel):
    sources: int = 0
    attributionRequired: bool = False
    shareAlikeRequired: bool = False
    noncommercialOnly: bool = False
    flags: list[str] = Field(default_factory=list)

class PackData(BaseModel):
    id: str
    title: str
    subtitle: str = ""
    level: str = "novice-friendly"
    concepts: list[PackConcept] = Field(default_factory=list)
    onboarding: dict = Field(default_factory=dict)
    compliance: PackCompliance = Field(default_factory=PackCompliance)

class CreatePackRequest(BaseModel):
    pack: PackData
    is_published: bool = True

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

class EvidenceEvent(BaseModel):
    concept_id: str
    dimension: str
    score: float
    confidence_hint: float = 0.5
    timestamp: str
    kind: EvidenceKind = "exercise"
    source_id: str = ""

class LearnerState(BaseModel):
    learner_id: str
    records: list[MasteryRecord] = Field(default_factory=list)
    history: list[EvidenceEvent] = Field(default_factory=list)

class EvaluatorSubmission(BaseModel):
    pack_id: str
    concept_id: str
    submitted_text: str
    kind: str = "checkpoint"

class EvaluatorJobStatus(BaseModel):
    job_id: int
    status: str
    result_score: float | None = None
    result_confidence_hint: float | None = None
    result_notes: str = ""
