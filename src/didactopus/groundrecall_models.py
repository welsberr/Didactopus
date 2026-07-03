from __future__ import annotations

"""Legacy flat GroundRecall models module.

Compatibility path retained during the internal namespace migration.
Prefer imports under ``didactopus.groundrecall.models`` for new code.
"""

from pydantic import BaseModel, Field
from typing import Literal


LifecycleStatus = Literal["draft", "triaged", "reviewed", "promoted", "superseded", "archived", "rejected"]
GroundingStatus = Literal["grounded", "partially_grounded", "ungrounded"]
SupportKind = Literal["direct_source", "derived_from_page", "derived_from_session", "inferred", "unknown"]


class ProvenanceRecord(BaseModel):
    origin_artifact_id: str = ""
    origin_path: str = ""
    origin_section: str = ""
    source_url: str = ""
    retrieval_date: str = ""
    machine_id: str = ""
    session_id: str = ""
    support_kind: SupportKind = "unknown"
    grounding_status: GroundingStatus = "ungrounded"


class SourceRecord(BaseModel):
    source_id: str
    title: str = ""
    source_type: str = "document"
    path: str = ""
    url: str = ""
    retrieved_at: str = ""
    metadata: dict = Field(default_factory=dict)
    current_status: LifecycleStatus = "draft"


class FragmentRecord(BaseModel):
    fragment_id: str
    source_id: str
    text: str
    section: str = ""
    line_start: int = 0
    line_end: int = 0
    metadata: dict = Field(default_factory=dict)
    current_status: LifecycleStatus = "draft"


class ArtifactRecord(BaseModel):
    artifact_id: str
    artifact_kind: str
    title: str = ""
    path: str = ""
    sha256: str = ""
    created_at: str = ""
    metadata: dict = Field(default_factory=dict)
    current_status: LifecycleStatus = "draft"


class ObservationRecord(BaseModel):
    observation_id: str
    artifact_id: str = ""
    role: str
    text: str
    provenance: ProvenanceRecord = Field(default_factory=ProvenanceRecord)
    confidence_hint: float = 0.0
    current_status: LifecycleStatus = "draft"


class ClaimRecord(BaseModel):
    claim_id: str
    claim_text: str
    claim_kind: str = "statement"
    source_observation_ids: list[str] = Field(default_factory=list)
    supporting_fragment_ids: list[str] = Field(default_factory=list)
    concept_ids: list[str] = Field(default_factory=list)
    contradicts_claim_ids: list[str] = Field(default_factory=list)
    supersedes_claim_ids: list[str] = Field(default_factory=list)
    confidence_hint: float = 0.0
    review_confidence: float = 0.0
    last_confirmed_at: str = ""
    provenance: ProvenanceRecord = Field(default_factory=ProvenanceRecord)
    current_status: LifecycleStatus = "draft"


class ConceptRecord(BaseModel):
    concept_id: str
    title: str
    aliases: list[str] = Field(default_factory=list)
    description: str = ""
    source_artifact_ids: list[str] = Field(default_factory=list)
    current_status: LifecycleStatus = "draft"


class RelationRecord(BaseModel):
    relation_id: str
    source_id: str
    target_id: str
    relation_type: str
    evidence_ids: list[str] = Field(default_factory=list)
    provenance: ProvenanceRecord = Field(default_factory=ProvenanceRecord)
    current_status: LifecycleStatus = "draft"


class ReviewCandidateRecord(BaseModel):
    review_candidate_id: str
    candidate_type: Literal["claim", "concept", "relation"]
    candidate_id: str
    triage_lane: str = "knowledge_capture"
    priority: int = 50
    finding_codes: list[str] = Field(default_factory=list)
    rationale: str = ""
    current_status: LifecycleStatus = "draft"


class PromotionRecord(BaseModel):
    promotion_id: str
    candidate_type: Literal["claim", "concept", "relation"]
    candidate_id: str
    promotion_target: str = "groundrecall_store"
    verdict: Literal["approved", "rejected", "superseded"] = "approved"
    reviewer: str = ""
    promoted_object_ids: list[str] = Field(default_factory=list)
    notes: str = ""
    promoted_at: str = ""


class GroundRecallSnapshot(BaseModel):
    snapshot_id: str
    created_at: str
    sources: list[SourceRecord] = Field(default_factory=list)
    fragments: list[FragmentRecord] = Field(default_factory=list)
    artifacts: list[ArtifactRecord] = Field(default_factory=list)
    observations: list[ObservationRecord] = Field(default_factory=list)
    claims: list[ClaimRecord] = Field(default_factory=list)
    concepts: list[ConceptRecord] = Field(default_factory=list)
    relations: list[RelationRecord] = Field(default_factory=list)
    promotions: list[PromotionRecord] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
