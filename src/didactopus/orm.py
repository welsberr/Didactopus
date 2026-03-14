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

class LearnerORM(Base):
    __tablename__ = "learners"
    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    owner_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    display_name: Mapped[str] = mapped_column(String(255), default="")

class MasteryRecordORM(Base):
    __tablename__ = "mastery_records"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    learner_id: Mapped[str] = mapped_column(ForeignKey("learners.id"), index=True)
    concept_id: Mapped[str] = mapped_column(String(100), index=True)
    dimension: Mapped[str] = mapped_column(String(100), default="mastery")
    score: Mapped[float] = mapped_column(Float, default=0.0)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    evidence_count: Mapped[int] = mapped_column(Integer, default=0)
    last_updated: Mapped[str] = mapped_column(String(100), default="")

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

class ReviewRecordORM(Base):
    __tablename__ = "review_records"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("knowledge_candidates.id"), index=True)
    reviewer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    review_kind: Mapped[str] = mapped_column(String(50), default="human_review")
    verdict: Mapped[str] = mapped_column(String(100), default="")
    rationale: Mapped[str] = mapped_column(Text, default="")
    requested_changes: Mapped[str] = mapped_column(Text, default="")
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

class SynthesisCandidateORM(Base):
    __tablename__ = "synthesis_candidates"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_concept_id: Mapped[str] = mapped_column(String(100), index=True)
    target_concept_id: Mapped[str] = mapped_column(String(100), index=True)
    source_pack_id: Mapped[str] = mapped_column(String(100), index=True)
    target_pack_id: Mapped[str] = mapped_column(String(100), index=True)
    synthesis_kind: Mapped[str] = mapped_column(String(100), default="cross_pack_similarity")
    score_total: Mapped[float] = mapped_column(Float, default=0.0)
    score_semantic: Mapped[float] = mapped_column(Float, default=0.0)
    score_structural: Mapped[float] = mapped_column(Float, default=0.0)
    score_trajectory: Mapped[float] = mapped_column(Float, default=0.0)
    score_review_history: Mapped[float] = mapped_column(Float, default=0.0)
    explanation: Mapped[str] = mapped_column(Text, default="")
    evidence_json: Mapped[str] = mapped_column(Text, default="{}")
    current_status: Mapped[str] = mapped_column(String(50), default="proposed")
    created_at: Mapped[str] = mapped_column(String(100), default="")
