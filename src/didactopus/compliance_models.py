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
    attribution_text: str = ""
    excluded_from_upstream_license: bool = False
    exclusion_notes: str = ""

class PackComplianceManifest(BaseModel):
    pack_id: str
    display_name: str
    derived_from_sources: list[str] = Field(default_factory=list)
    attribution_required: bool = True
    share_alike_required: bool = False
    noncommercial_only: bool = False
    restrictive_flags: list[str] = Field(default_factory=list)
    redistribution_notes: list[str] = Field(default_factory=list)

class SourceInventory(BaseModel):
    sources: list[SourceRecord] = Field(default_factory=list)
