from __future__ import annotations
import warnings

from pydantic import BaseModel, Field, model_validator
from typing import Literal

RunStatus = Literal["not_started", "onboarding", "active", "blocked", "ready_for_capstone", "claimed_expertise"]

class LearnerProfile(BaseModel):
    learner_id: str
    display_name: str = ""
    target_domain: str = ""
    prior_experience: str = "unknown"
    preferred_session_minutes: int = 25
    motivation_notes: str = ""
    wants_fun_feedback: bool = True
    wants_concise_guidance: bool = True

class SessionPlan(BaseModel):
    headline: str
    next_action: str
    why_now: str
    estimated_minutes: int = 20
    tasks: list[str] = Field(default_factory=list)
    reward_note: str = ""

class StopCriteria(BaseModel):
    min_mastered_concepts: int = 0
    min_average_score: float = 0.75
    min_average_evidence_coverage: float = 0.60
    required_capstones: list[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def _migrate_legacy_confidence(cls, data):
        if isinstance(data, dict) and "min_average_confidence" in data and "min_average_evidence_coverage" not in data:
            warnings.warn(
                "StopCriteria.min_average_confidence is deprecated; use min_average_evidence_coverage.",
                DeprecationWarning,
                stacklevel=2,
            )
            data = dict(data)
            data["min_average_evidence_coverage"] = data.pop("min_average_confidence")
        return data

    @property
    def min_average_confidence(self) -> float:
        warnings.warn(
            "StopCriteria.min_average_confidence is deprecated; use min_average_evidence_coverage.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.min_average_evidence_coverage

    @min_average_confidence.setter
    def min_average_confidence(self, value: float) -> None:
        warnings.warn(
            "StopCriteria.min_average_confidence is deprecated; use min_average_evidence_coverage.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.min_average_evidence_coverage = value

class RunState(BaseModel):
    profile: LearnerProfile
    status: RunStatus = "not_started"
    unlocked_concepts: list[str] = Field(default_factory=list)
    active_concepts: list[str] = Field(default_factory=list)
    blocked_concepts: list[str] = Field(default_factory=list)
    completed_projects: list[str] = Field(default_factory=list)
    completed_capstones: list[str] = Field(default_factory=list)
    milestone_log: list[str] = Field(default_factory=list)
