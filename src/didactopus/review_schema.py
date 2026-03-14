from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Literal

TrustStatus = Literal["trusted","provisional","rejected","needs_review"]

class ConceptReviewEntry(BaseModel):
    concept_id: str
    title: str
    description: str = ""
    prerequisites: list[str] = Field(default_factory=list)
    mastery_signals: list[str] = Field(default_factory=list)
    status: TrustStatus = "needs_review"
    notes: list[str] = Field(default_factory=list)

class DraftPackData(BaseModel):
    pack: dict = Field(default_factory=dict)
    concepts: list[ConceptReviewEntry] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)
    review_flags: list[str] = Field(default_factory=list)
    attribution: dict = Field(default_factory=dict)

class ReviewAction(BaseModel):
    action_type: str
    target: str = ""
    payload: dict = Field(default_factory=dict)
    rationale: str = ""

class ReviewLedgerEntry(BaseModel):
    reviewer: str
    action: ReviewAction

class ReviewSession(BaseModel):
    reviewer: str
    draft_pack: DraftPackData
    ledger: list[ReviewLedgerEntry] = Field(default_factory=list)

class WorkspaceMeta(BaseModel):
    workspace_id: str
    title: str
    path: str
    created_at: str
    last_opened_at: str
    notes: str = ""

class WorkspaceRegistry(BaseModel):
    workspaces: list[WorkspaceMeta] = Field(default_factory=list)
    recent_workspace_ids: list[str] = Field(default_factory=list)

class ImportPreview(BaseModel):
    ok: bool = False
    source_dir: str
    workspace_id: str
    overwrite_required: bool = False
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    summary: dict = Field(default_factory=dict)
    semantic_warnings: list[str] = Field(default_factory=list)
    graph_warnings: list[str] = Field(default_factory=list)
    path_warnings: list[str] = Field(default_factory=list)
    coverage_warnings: list[str] = Field(default_factory=list)
