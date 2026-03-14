from pathlib import Path
from pydantic import BaseModel, Field
import yaml

class ReviewConfig(BaseModel):
    default_reviewer: str = "Unknown Reviewer"

class BridgeConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8765
    registry_path: str = "workspace_registry.json"
    default_workspace_root: str = "workspaces"

class AppConfig(BaseModel):
    review: ReviewConfig = Field(default_factory=ReviewConfig)
    bridge: BridgeConfig = Field(default_factory=BridgeConfig)

def load_config(path: str | Path) -> AppConfig:
    with open(path, "r", encoding="utf-8") as handle:
        return AppConfig.model_validate(yaml.safe_load(handle) or {})
