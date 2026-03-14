from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Literal

EvidenceKind = Literal["checkpoint", "project", "exercise", "review"]

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

    def get_record(self, concept_id: str, dimension: str) -> MasteryRecord | None:
        for rec in self.records:
            if rec.concept_id == concept_id and rec.dimension == dimension:
                return rec
        return None
