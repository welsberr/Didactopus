from pathlib import Path
from pydantic import BaseModel, Field
import yaml


class CourseIngestConfig(BaseModel):
    default_pack_author: str = "Unknown"
    default_license: str = "REVIEW-REQUIRED"
    min_term_length: int = 4
    max_terms_per_lesson: int = 8


class RulePolicyConfig(BaseModel):
    enable_prerequisite_order_rule: bool = True
    enable_duplicate_term_merge_rule: bool = True
    enable_project_detection_rule: bool = True
    enable_review_flags: bool = True


class AppConfig(BaseModel):
    course_ingest: CourseIngestConfig = Field(default_factory=CourseIngestConfig)
    rule_policy: RulePolicyConfig = Field(default_factory=RulePolicyConfig)


def load_config(path: str | Path) -> AppConfig:
    with open(path, "r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return AppConfig.model_validate(data)
