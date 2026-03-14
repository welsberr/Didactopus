from __future__ import annotations
from pydantic import BaseModel, Field

class SourceRecord(BaseModel):
    source_id: str
    title: str
    url: str
    publisher: str = ""
    creator: str = ""
    license_id: str = ""
    license_url: str = ""
    retrieved_at: str = ""
    adapted: bool = False
    adaptation_notes: str = ""
    attribution_text: str = ""
    excluded_from_upstream_license: bool = False
    exclusion_notes: str = ""
    tags: list[str] = Field(default_factory=list)

class SourceInventory(BaseModel):
    sources: list[SourceRecord] = Field(default_factory=list)
