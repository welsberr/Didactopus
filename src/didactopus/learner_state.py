from __future__ import annotations
import warnings

from pydantic import BaseModel, Field, model_validator
from typing import Literal

EvidenceKind = Literal["checkpoint", "project", "exercise", "review"]

class MasteryRecord(BaseModel):
    concept_id: str
    dimension: str
    score: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence_coverage: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence_count: int = 0
    last_updated: str = ""

    @model_validator(mode="before")
    @classmethod
    def _migrate_legacy_confidence(cls, data):
        if isinstance(data, dict) and "confidence" in data and "evidence_coverage" not in data:
            warnings.warn(
                "MasteryRecord.confidence is deprecated; use evidence_coverage.",
                DeprecationWarning,
                stacklevel=2,
            )
            data = dict(data)
            data["evidence_coverage"] = data.pop("confidence")
        return data

    @property
    def confidence(self) -> float:
        warnings.warn(
            "MasteryRecord.confidence is deprecated; use evidence_coverage.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.evidence_coverage

    @confidence.setter
    def confidence(self, value: float) -> None:
        warnings.warn(
            "MasteryRecord.confidence is deprecated; use evidence_coverage.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.evidence_coverage = value


class EvidenceEvent(BaseModel):
    concept_id: str
    dimension: str
    score: float = Field(ge=0.0, le=1.0)
    confidence_hint: float = Field(default=0.5, ge=0.0, le=1.0)
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
