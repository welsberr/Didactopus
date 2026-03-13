from pathlib import Path
from pydantic import BaseModel, Field
import yaml


class DocumentAdaptersConfig(BaseModel):
    allow_pdf: bool = True
    allow_docx: bool = True
    allow_pptx: bool = True
    allow_html: bool = True
    allow_markdown: bool = True
    allow_text: bool = True


class CourseIngestConfig(BaseModel):
    default_pack_author: str = "Unknown"
    default_license: str = "REVIEW-REQUIRED"
    min_term_length: int = 4
    max_terms_per_lesson: int = 8


class CrossCourseConfig(BaseModel):
    detect_title_overlaps: bool = True
    detect_term_conflicts: bool = True
    detect_order_conflicts: bool = True
    merge_same_named_lessons: bool = True


class AppConfig(BaseModel):
    document_adapters: DocumentAdaptersConfig = Field(default_factory=DocumentAdaptersConfig)
    course_ingest: CourseIngestConfig = Field(default_factory=CourseIngestConfig)
    cross_course: CrossCourseConfig = Field(default_factory=CrossCourseConfig)


def load_config(path: str | Path) -> AppConfig:
    with open(path, "r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return AppConfig.model_validate(data)
