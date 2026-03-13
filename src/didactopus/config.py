from pathlib import Path
from pydantic import BaseModel, Field
import yaml


class ReviewConfig(BaseModel):
    default_reviewer: str = "Unknown Reviewer"
    allow_provisional_concepts: bool = True
    write_promoted_pack: bool = True
    write_review_ledger: bool = True


class AppConfig(BaseModel):
    review: ReviewConfig = Field(default_factory=ReviewConfig)


def load_config(path: str | Path) -> AppConfig:
    with open(path, "r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return AppConfig.model_validate(data)
