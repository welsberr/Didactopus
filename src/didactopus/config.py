from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class Settings(BaseModel):
    database_url: str = os.getenv("DIDACTOPUS_DATABASE_URL", "sqlite+pysqlite:///:memory:")
    host: str = os.getenv("DIDACTOPUS_HOST", "127.0.0.1")
    port: int = int(os.getenv("DIDACTOPUS_PORT", "8011"))
    jwt_secret: str = os.getenv("DIDACTOPUS_JWT_SECRET", "change-me")
    jwt_algorithm: str = "HS256"


class ReviewConfig(BaseModel):
    default_reviewer: str = "Unknown Reviewer"
    write_promoted_pack: bool = True


class BridgeConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8765
    registry_path: str = "workspace_registry.json"
    default_workspace_root: str = "workspaces"


class PlatformConfig(BaseModel):
    dimension_thresholds: dict[str, float] = Field(
        default_factory=lambda: {
            "correctness": 0.8,
            "explanation": 0.75,
            "transfer": 0.7,
            "project_execution": 0.75,
            "critique": 0.7,
        }
    )
    confidence_threshold: float = 0.8

    @property
    def default_dimension_thresholds(self) -> dict[str, float]:
        return self.dimension_thresholds


class LocalProviderConfig(BaseModel):
    backend: str = "stub"
    model_name: str = "local-demo"


class RoleMeshProviderConfig(BaseModel):
    base_url: str = os.getenv("DIDACTOPUS_ROLEMESH_BASE_URL", "http://127.0.0.1:8000")
    api_key: str = os.getenv("DIDACTOPUS_ROLEMESH_API_KEY", "")
    default_model: str = "planner"
    role_to_model: dict[str, str] = Field(
        default_factory=lambda: {
            "mentor": "planner",
            "learner": "writer",
            "practice": "writer",
            "project_advisor": "planner",
            "evaluator": "reviewer",
        }
    )
    timeout_seconds: float = 30.0


class ModelProviderConfig(BaseModel):
    provider: str = "stub"
    local: LocalProviderConfig = Field(default_factory=LocalProviderConfig)
    rolemesh: RoleMeshProviderConfig = Field(default_factory=RoleMeshProviderConfig)


class AppConfig(BaseModel):
    review: ReviewConfig = Field(default_factory=ReviewConfig)
    bridge: BridgeConfig = Field(default_factory=BridgeConfig)
    platform: PlatformConfig = Field(default_factory=PlatformConfig)
    model_provider: ModelProviderConfig = Field(default_factory=ModelProviderConfig)


def load_settings() -> Settings:
    return Settings()


def load_config(path: str | Path) -> AppConfig:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    return AppConfig.model_validate(_with_platform_defaults(data))


def _with_platform_defaults(data: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(data)
    if "platform" not in normalized:
        normalized["platform"] = {}
    if "model_provider" not in normalized:
        normalized["model_provider"] = {}
    return normalized
