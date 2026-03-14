from sqlalchemy import String, Integer, Float, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

class UserORM(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50), default="learner")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

class PackORM(Base):
    __tablename__ = "packs"
    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    owner_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    policy_lane: Mapped[str] = mapped_column(String(50), default="personal")
    title: Mapped[str] = mapped_column(String(255))
    subtitle: Mapped[str] = mapped_column(Text, default="")
    level: Mapped[str] = mapped_column(String(100), default="novice-friendly")
    data_json: Mapped[str] = mapped_column(Text)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)

class KnowledgeCandidateORM(Base):
    __tablename__ = "knowledge_candidates"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_type: Mapped[str] = mapped_column(String(50), default="learner_export")
    source_artifact_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    learner_id: Mapped[str] = mapped_column(String(100), index=True)
    pack_id: Mapped[str] = mapped_column(String(100), index=True)
    candidate_kind: Mapped[str] = mapped_column(String(100), index=True)
    title: Mapped[str] = mapped_column(String(255))
    summary: Mapped[str] = mapped_column(Text, default="")
    structured_payload_json: Mapped[str] = mapped_column(Text, default="{}")
    evidence_summary: Mapped[str] = mapped_column(Text, default="")
    confidence_hint: Mapped[float] = mapped_column(Float, default=0.0)
    novelty_score: Mapped[float] = mapped_column(Float, default=0.0)
    synthesis_score: Mapped[float] = mapped_column(Float, default=0.0)
    triage_lane: Mapped[str] = mapped_column(String(50), default="archive")
    current_status: Mapped[str] = mapped_column(String(50), default="captured")
    created_at: Mapped[str] = mapped_column(String(100), default="")

class PromotionRecordORM(Base):
    __tablename__ = "promotion_records"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("knowledge_candidates.id"), index=True)
    promotion_target: Mapped[str] = mapped_column(String(50), index=True)
    target_object_id: Mapped[str] = mapped_column(String(100), default="")
    promotion_status: Mapped[str] = mapped_column(String(50), default="draft")
    promoted_by: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[str] = mapped_column(String(100), default="")

class PackPatchProposalORM(Base):
    __tablename__ = "pack_patch_proposals"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("knowledge_candidates.id"), index=True)
    pack_id: Mapped[str] = mapped_column(String(100), index=True)
    patch_type: Mapped[str] = mapped_column(String(100), default="content_revision")
    title: Mapped[str] = mapped_column(String(255))
    proposed_change_json: Mapped[str] = mapped_column(Text, default="{}")
    evidence_summary: Mapped[str] = mapped_column(Text, default="")
    reviewer_notes: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(50), default="proposed")
    current_version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[str] = mapped_column(String(100), default="")

class CurriculumDraftORM(Base):
    __tablename__ = "curriculum_drafts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("knowledge_candidates.id"), index=True)
    topic_focus: Mapped[str] = mapped_column(String(255), default="")
    product_type: Mapped[str] = mapped_column(String(100), default="lesson_outline")
    audience: Mapped[str] = mapped_column(String(100), default="general")
    source_concepts_json: Mapped[str] = mapped_column(Text, default="[]")
    content_markdown: Mapped[str] = mapped_column(Text, default="")
    editorial_notes: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(50), default="draft")
    current_version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[str] = mapped_column(String(100), default="")

class SkillBundleORM(Base):
    __tablename__ = "skill_bundles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("knowledge_candidates.id"), index=True)
    skill_name: Mapped[str] = mapped_column(String(255))
    domain: Mapped[str] = mapped_column(String(100), default="")
    prerequisites_json: Mapped[str] = mapped_column(Text, default="[]")
    expected_inputs_json: Mapped[str] = mapped_column(Text, default="[]")
    failure_modes_json: Mapped[str] = mapped_column(Text, default="[]")
    validation_checks_json: Mapped[str] = mapped_column(Text, default="[]")
    canonical_examples_json: Mapped[str] = mapped_column(Text, default="[]")
    status: Mapped[str] = mapped_column(String(50), default="draft")
    current_version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[str] = mapped_column(String(100), default="")

class ObjectVersionORM(Base):
    __tablename__ = "object_versions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    object_kind: Mapped[str] = mapped_column(String(50), index=True)
    object_id: Mapped[int] = mapped_column(Integer, index=True)
    version_number: Mapped[int] = mapped_column(Integer, default=1)
    payload_json: Mapped[str] = mapped_column(Text, default="{}")
    editor_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    note: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[str] = mapped_column(String(100), default="")
