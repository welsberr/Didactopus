from pathlib import Path
from pydantic import BaseModel, Field
import yaml


class ProviderEndpoint(BaseModel):
    backend: str = "ollama"
    endpoint: str = "http://localhost:11434"
    model_name: str = "llama3.1:8b"


class ModelProviderConfig(BaseModel):
    mode: str = Field(default="local_first")
    local: ProviderEndpoint = Field(default_factory=ProviderEndpoint)


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


class ArtifactConfig(BaseModel):
    local_pack_dirs: list[str] = Field(default_factory=lambda: ["domain-packs"])


class AppConfig(BaseModel):
    model_provider: ModelProviderConfig = Field(default_factory=ModelProviderConfig)
    platform: PlatformConfig = Field(default_factory=PlatformConfig)
    artifacts: ArtifactConfig = Field(default_factory=ArtifactConfig)


def load_config(path: str | Path) -> AppConfig:
    with open(path, "r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return AppConfig.model_validate(data)
