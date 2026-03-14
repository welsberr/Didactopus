from sqlalchemy import String, Integer, Float, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base

class UserORM(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50), default="learner")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

class RefreshTokenORM(Base):
    __tablename__ = "refresh_tokens"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    token_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)

class PackORM(Base):
    __tablename__ = "packs"
    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    subtitle: Mapped[str] = mapped_column(Text, default="")
    level: Mapped[str] = mapped_column(String(100), default="novice-friendly")
    data_json: Mapped[str] = mapped_column(Text)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)

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

class EvidenceEventORM(Base):
    __tablename__ = "evidence_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    learner_id: Mapped[str] = mapped_column(ForeignKey("learners.id"), index=True)
    concept_id: Mapped[str] = mapped_column(String(100), index=True)
    dimension: Mapped[str] = mapped_column(String(100), default="mastery")
    score: Mapped[float] = mapped_column(Float, default=0.0)
    confidence_hint: Mapped[float] = mapped_column(Float, default=0.5)
    timestamp: Mapped[str] = mapped_column(String(100), default="")
    kind: Mapped[str] = mapped_column(String(50), default="exercise")
    source_id: Mapped[str] = mapped_column(String(255), default="")

class EvaluatorJobORM(Base):
    __tablename__ = "evaluator_jobs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    learner_id: Mapped[str] = mapped_column(ForeignKey("learners.id"), index=True)
    pack_id: Mapped[str] = mapped_column(ForeignKey("packs.id"), index=True)
    concept_id: Mapped[str] = mapped_column(String(100), index=True)
    submitted_text: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(50), default="queued")
    result_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    result_confidence_hint: Mapped[float | None] = mapped_column(Float, nullable=True)
    result_notes: Mapped[str] = mapped_column(Text, default="")
