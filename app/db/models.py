"""Initial SQLAlchemy models for Ojo de Dios."""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utc_now() -> datetime:
    """Return the current UTC datetime."""
    return datetime.now(timezone.utc)


class Role(Base):
    """Application role."""

    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    users: Mapped[list["User"]] = relationship(back_populates="role")


class User(Base):
    """Application user."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(512), nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    role: Mapped[Role] = relationship(back_populates="users")




class UserSession(Base):
    """Persisted login session with hashed token storage."""

    __tablename__ = "user_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    user_agent: Mapped[str] = mapped_column(Text, nullable=False, default="")
    ip_address: Mapped[str] = mapped_column(String(64), nullable=False, default="")

    user: Mapped[User] = relationship()


class Setting(Base):
    """Runtime setting stored in the database."""

    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)


class AuditLog(Base):
    """Audit log entry."""

    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_type: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    actor_username: Mapped[str | None] = mapped_column(String(150), nullable=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)


class Target(Base):
    """Stored target definition."""

    __tablename__ = "targets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    target_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    target_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_value: Mapped[str] = mapped_column(Text, nullable=False)
    mode: Mapped[str] = mapped_column(String(32), nullable=False)
    allowed_modules_json: Mapped[str] = mapped_column(Text, nullable=False)
    limits_json: Mapped[str] = mapped_column(Text, nullable=False)
    noise_profile: Mapped[str] = mapped_column(String(64), nullable=False)
    evidence_profile: Mapped[str] = mapped_column(String(64), nullable=False)
    require_confirmations: Mapped[bool] = mapped_column(Boolean, nullable=False)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[str | None] = mapped_column(String(150), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)


class TargetFingerprintModel(Base):
    """Stored target fingerprint."""

    __tablename__ = "target_fingerprints"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    target_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(64), nullable=False)
    original_value: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_value: Mapped[str] = mapped_column(Text, nullable=False)
    fingerprint_json: Mapped[str] = mapped_column(Text, nullable=False)
    tags_json: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)


class Job(Base):
    """Persisted job lifecycle summary."""

    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    target_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    created_by: Mapped[str] = mapped_column(String(150), nullable=False)
    mode: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    selected_modules_json: Mapped[str] = mapped_column(Text, nullable=False)
    selected_techniques_json: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    result_status: Mapped[str] = mapped_column(String(64), nullable=False)
    evidence_ids_json: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Evidence(Base):
    """Stored evidence metadata."""

    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    evidence_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    run_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    target_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    technique_id: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    module_id: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    evidence_type: Mapped[str] = mapped_column(String(64), nullable=False)
    quality: Mapped[str] = mapped_column(String(64), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(String(150), nullable=False)
    demo: Mapped[bool] = mapped_column(Boolean, nullable=False)
    real_execution: Mapped[bool] = mapped_column(Boolean, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    content_path: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)


class EvidenceFile(Base):
    """Stored evidence file metadata."""

    __tablename__ = "evidence_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    evidence_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    file_type: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)


class ScoringHistory(Base):
    """Persisted scoring updates for technique results."""

    __tablename__ = "scoring_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    score_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    target_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    technique_id: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    module_id: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    run_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    result_status: Mapped[str] = mapped_column(String(64), nullable=False)
    evidence_quality: Mapped[str] = mapped_column(String(64), nullable=False)
    evidence_ids_json: Mapped[str] = mapped_column(Text, nullable=False)
    score_before: Mapped[float] = mapped_column(Float, nullable=False)
    score_after: Mapped[float] = mapped_column(Float, nullable=False)
    delta: Mapped[float] = mapped_column(Float, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    demo: Mapped[bool] = mapped_column(Boolean, nullable=False)
    real_execution: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)



class VersionLock(Base):
    """Persisted recommended and resolved tool version metadata."""

    __tablename__ = "version_locks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tool_id: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    tool_name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    module_id: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    recommended_version: Mapped[str] = mapped_column(String(150), nullable=False)
    resolved_version: Mapped[str] = mapped_column(String(150), nullable=False)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    runtime: Mapped[str] = mapped_column(String(64), nullable=False)
    binary_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    locked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    status: Mapped[str] = mapped_column(String(64), nullable=False)
