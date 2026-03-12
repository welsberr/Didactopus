from pathlib import Path
from pydantic import BaseModel, Field
import yaml


class ProviderEndpoint(BaseModel):
    backend: str = "ollama"
    endpoint: str = "http://localhost:11434"
    model_name: str = "llama3.1:8b"


class RemoteProvider(BaseModel):
    enabled: bool = False
    provider_name: str = "none"
    endpoint: str = ""
    model_name: str = ""


class ModelProviderConfig(BaseModel):
    mode: str = Field(default="local_first")
    local: ProviderEndpoint = Field(default_factory=ProviderEndpoint)
    remote: RemoteProvider = Field(default_factory=RemoteProvider)


class PlatformConfig(BaseModel):
    verification_required: bool = True
    require_learner_explanations: bool = True
    permit_direct_answers: bool = False
    mastery_threshold: float = 0.8


class ArtifactConfig(BaseModel):
    local_pack_dirs: list[str] = Field(default_factory=lambda: ["domain-packs"])
    allow_third_party_packs: bool = True


class AppConfig(BaseModel):
    model_provider: ModelProviderConfig = Field(default_factory=ModelProviderConfig)
    platform: PlatformConfig = Field(default_factory=PlatformConfig)
    artifacts: ArtifactConfig = Field(default_factory=ArtifactConfig)


def load_config(path: str | Path) -> AppConfig:
    with open(path, "r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return AppConfig.model_validate(data)
