from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Literal

TrustStatus = Literal["trusted", "provisional", "rejected", "needs_review"]
ActionType = Literal[
    "set_status",
    "edit_prerequisites",
    "edit_title",
    "edit_description",
    "merge_concepts",
    "split_concept",
    "resolve_conflict",
    "note",
]


class ConceptReviewEntry(BaseModel):
    concept_id: str
    title: str
    description: str = ""
    prerequisites: list[str] = Field(default_factory=list)
    mastery_signals: list[str] = Field(default_factory=list)
    status: TrustStatus = "needs_review"
    notes: list[str] = Field(default_factory=list)


class ReviewAction(BaseModel):
    action_type: ActionType
    target: str
    payload: dict = Field(default_factory=dict)
    rationale: str = ""


class ReviewLedgerEntry(BaseModel):
    reviewer: str
    action: ReviewAction


class DraftPackData(BaseModel):
    pack: dict = Field(default_factory=dict)
    concepts: list[ConceptReviewEntry] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)
    review_flags: list[str] = Field(default_factory=list)
    attribution: dict = Field(default_factory=dict)


class ReviewSession(BaseModel):
    reviewer: str
    draft_pack: DraftPackData
    ledger: list[ReviewLedgerEntry] = Field(default_factory=list)
