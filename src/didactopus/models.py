from __future__ import annotations
from pydantic import BaseModel, Field

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

class GraphPosition(BaseModel):
    x: float
    y: float

class CrossPackLink(BaseModel):
    source_concept_id: str
    target_pack_id: str
    target_concept_id: str
    relationship: str = "related"

class PackConcept(BaseModel):
    id: str
    title: str
    prerequisites: list[str] = Field(default_factory=list)
    masteryDimension: str = "mastery"
    exerciseReward: str = ""
    position: GraphPosition | None = None
    cross_pack_links: list[CrossPackLink] = Field(default_factory=list)

class PackData(BaseModel):
    id: str
    title: str
    subtitle: str = ""
    level: str = "novice-friendly"
    concepts: list[PackConcept] = Field(default_factory=list)
    onboarding: dict = Field(default_factory=dict)
    compliance: dict = Field(default_factory=dict)

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
    kind: str = "exercise"
    source_id: str = ""

class LearnerState(BaseModel):
    learner_id: str
    records: list[MasteryRecord] = Field(default_factory=list)
    history: list[EvidenceEvent] = Field(default_factory=list)

class MediaRenderRequest(BaseModel):
    learner_id: str
    pack_id: str
    format: str = "gif"
    fps: int = 2
    theme: str = "default"
    retention_class: str = "standard"
    retention_days: int = 30

class ArtifactRetentionUpdate(BaseModel):
    retention_class: str
    retention_days: int | None = None

class KnowledgeExportRequest(BaseModel):
    learner_id: str
    pack_id: str
    export_kind: str = "knowledge_snapshot"
