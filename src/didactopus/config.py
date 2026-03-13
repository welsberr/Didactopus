from pathlib import Path
from pydantic import BaseModel, Field
import yaml


class PlatformConfig(BaseModel):
    default_dimension_thresholds: dict[str, float] = Field(
        default_factory=lambda: {
            "correctness": 0.8,
            "explanation": 0.75,
            "transfer": 0.7,
            "project_execution": 0.75,
            "critique": 0.7,
        }
    )


class PlannerConfig(BaseModel):
    readiness_bonus: float = 2.0
    target_distance_weight: float = 1.0
    weak_dimension_bonus: float = 1.2
    fragile_review_bonus: float = 1.5
    project_unlock_bonus: float = 0.8
    semantic_similarity_weight: float = 1.0


class EvidenceConfig(BaseModel):
    resurfacing_threshold: float = 0.55
    confidence_threshold: float = 0.8
    evidence_weights: dict[str, float] = Field(
        default_factory=lambda: {
            "explanation": 1.0,
            "problem": 1.5,
            "project": 2.5,
            "transfer": 2.0,
        }
    )
    recent_evidence_multiplier: float = 1.35


class AppConfig(BaseModel):
    platform: PlatformConfig = Field(default_factory=PlatformConfig)
    planner: PlannerConfig = Field(default_factory=PlannerConfig)
    evidence: EvidenceConfig = Field(default_factory=EvidenceConfig)


def load_config(path: str | Path) -> AppConfig:
    with open(path, "r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return AppConfig.model_validate(data)
