from typing import Any
from pydantic import BaseModel, Field


class DependencySpec(BaseModel):
    name: str
    min_version: str = "0.0.0"
    max_version: str = "9999.9999.9999"


class MasteryProfileSpec(BaseModel):
    template: str | None = None
    required_dimensions: list[str] = Field(default_factory=list)
    dimension_threshold_overrides: dict[str, float] = Field(default_factory=dict)


class CrossPackLinkSpec(BaseModel):
    source_concept: str
    target_concept: str
    relation: str


class ProfileTemplateSpec(BaseModel):
    required_dimensions: list[str] = Field(default_factory=list)
    dimension_threshold_overrides: dict[str, float] = Field(default_factory=dict)


class PackManifest(BaseModel):
    name: str
    display_name: str
    version: str
    schema_version: str
    didactopus_min_version: str
    didactopus_max_version: str
    description: str = ""
    author: str = ""
    license: str = "unspecified"
    dependencies: list[DependencySpec] = Field(default_factory=list)
    overrides: list[str] = Field(default_factory=list)
    profile_templates: dict[str, ProfileTemplateSpec] = Field(default_factory=dict)
    cross_pack_links: list[CrossPackLinkSpec] = Field(default_factory=list)


class ConceptEntry(BaseModel):
    id: str
    title: str
    description: str = ""
    prerequisites: list[str] = Field(default_factory=list)
    mastery_signals: list[str] = Field(default_factory=list)
    source_role: str = ""
    distinctions: list[str] = Field(default_factory=list)
    definition_candidates: list[str] = Field(default_factory=list)
    qualification_candidates: list[str] = Field(default_factory=list)
    constraint_candidates: list[str] = Field(default_factory=list)
    mastery_profile: MasteryProfileSpec = Field(default_factory=MasteryProfileSpec)


class ConceptsFile(BaseModel):
    concepts: list[ConceptEntry]


class RoadmapStageEntry(BaseModel):
    id: str
    title: str
    concepts: list[str] = Field(default_factory=list)
    checkpoint: list[str] = Field(default_factory=list)


class RoadmapFile(BaseModel):
    stages: list[RoadmapStageEntry]


class ProjectEntry(BaseModel):
    id: str
    title: str
    difficulty: str = ""
    prerequisites: list[str] = Field(default_factory=list)
    deliverables: list[str] = Field(default_factory=list)


class ProjectsFile(BaseModel):
    projects: list[ProjectEntry]


class RubricsFile(BaseModel):
    rubrics: list[dict[str, Any]]
