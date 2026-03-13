from typing import Any
from pydantic import BaseModel, Field


class DependencySpec(BaseModel):
    name: str
    min_version: str = "0.0.0"
    max_version: str = "9999.9999.9999"


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


class ConceptEntry(BaseModel):
    id: str
    title: str
    prerequisites: list[str] = Field(default_factory=list)
    mastery_signals: list[str] = Field(default_factory=list)


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
