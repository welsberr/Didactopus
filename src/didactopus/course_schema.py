from __future__ import annotations
from pydantic import BaseModel, Field


class Section(BaseModel):
    heading: str
    body: str = ""


class NormalizedDocument(BaseModel):
    source_path: str
    source_type: str
    title: str = ""
    text: str = ""
    sections: list[Section] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class Lesson(BaseModel):
    title: str
    body: str = ""
    objectives: list[str] = Field(default_factory=list)
    exercises: list[str] = Field(default_factory=list)
    key_terms: list[str] = Field(default_factory=list)
    source_refs: list[str] = Field(default_factory=list)


class Module(BaseModel):
    title: str
    lessons: list[Lesson] = Field(default_factory=list)


class NormalizedCourse(BaseModel):
    title: str
    source_name: str = ""
    source_url: str = ""
    rights_note: str = ""
    modules: list[Module] = Field(default_factory=list)
    source_records: list[NormalizedDocument] = Field(default_factory=list)


class TopicBundle(BaseModel):
    topic_title: str
    courses: list[NormalizedCourse] = Field(default_factory=list)


class ConceptCandidate(BaseModel):
    id: str
    title: str
    description: str = ""
    source_modules: list[str] = Field(default_factory=list)
    source_lessons: list[str] = Field(default_factory=list)
    source_courses: list[str] = Field(default_factory=list)
    prerequisites: list[str] = Field(default_factory=list)
    mastery_signals: list[str] = Field(default_factory=list)


class DraftPack(BaseModel):
    pack: dict
    concepts: dict
    roadmap: dict
    projects: dict
    rubrics: dict
    review_report: list[str] = Field(default_factory=list)
    attribution: dict = Field(default_factory=dict)
    conflicts: list[str] = Field(default_factory=list)
