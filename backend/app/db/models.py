"""
Database models for Domain Pack Authoring System
"""
from datetime import datetime
from typing import Optional
from uuid import uuid4
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text,
    ForeignKey, Enum as SQLEnum, Index, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import enum

Base = declarative_base()


class UserRole(str, enum.Enum):
    """User roles for RBAC"""
    EDITOR = "editor"
    REVIEWER = "reviewer"
    ADMIN = "admin"


class ProposalStatus(str, enum.Enum):
    """Proposal lifecycle states"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    COMMITTED = "committed"
    ABORTED = "aborted"


class MemoryType(str, enum.Enum):
    """Types of memory entries"""
    PREFERENCE = "preference"
    DECISION = "decision"
    PATTERN = "pattern"


class MemoryScope(str, enum.Enum):
    """Scope of memory entries"""
    GLOBAL = "global"
    DOMAIN = "domain"
    SESSION = "session"


class MemorySource(str, enum.Enum):
    """Source of memory entries"""
    USER_CONFIRMED = "user_confirmed"
    INFERRED = "inferred"


class EventType(str, enum.Enum):
    """Audit log event types"""
    PROPOSAL_CREATED = "proposal_created"
    PROPOSAL_CONFIRMED = "proposal_confirmed"
    PROPOSAL_REJECTED = "proposal_rejected"
    COMMIT_SUCCESS = "commit_success"
    COMMIT_FAILED = "commit_failed"
    ROLLBACK_CREATED = "rollback_created"
    MEMORY_CREATED = "memory_created"
    MEMORY_UPDATED = "memory_updated"
    SESSION_STARTED = "session_started"
    SESSION_ENDED = "session_ended"


class User(Base):
    """User model for authentication and RBAC"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.EDITOR)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    memory_entries = relationship("MemoryEntry", back_populates="user", cascade="all, delete-orphan")
    domain_packs = relationship("DomainPack", back_populates="creator")
    
    def __repr__(self):
        return f"<User {self.email}>"


class Session(Base):
    """User session for conversation management"""
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    thread_id = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid4, index=True)
    domain_pack_id = Column(UUID(as_uuid=True), ForeignKey("domain_packs.id", ondelete="SET NULL"), nullable=True)
    details = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    domain_pack = relationship("DomainPack")
    proposals = relationship("Proposal", back_populates="session", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_session_user_active", "user_id", "ended_at"),
    )
    
    def __repr__(self):
        return f"<Session {self.thread_id}>"


class DomainPack(Base):
    """Domain Pack metadata and current state"""
    __tablename__ = "domain_packs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    current_version_id = Column(UUID(as_uuid=True), ForeignKey("versions.id", use_alter=True), nullable=True)
    base_template = Column(JSONB, nullable=False)
    domain_schema = Column(JSONB, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    creator = relationship("User", back_populates="domain_packs")
    versions = relationship("Version", back_populates="domain_pack", foreign_keys="Version.domain_pack_id")
    current_version = relationship("Version", foreign_keys=[current_version_id], post_update=True)
    
    def __repr__(self):
        return f"<DomainPack {self.name}>"


class Version(Base):
    """Immutable version snapshots with diffs"""
    __tablename__ = "versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    domain_pack_id = Column(UUID(as_uuid=True), ForeignKey("domain_packs.id", ondelete="CASCADE"), nullable=False)
    version_number = Column(Integer, nullable=False)
    snapshot = Column(JSONB, nullable=False)
    diff_from_previous = Column(JSONB, nullable=True)
    proposal_id = Column(UUID(as_uuid=True), ForeignKey("proposals.id", use_alter=True), nullable=True)
    committed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    commit_message = Column(Text, nullable=True)
    is_rollback = Column(Boolean, default=False, nullable=False)
    rollback_of_version_id = Column(UUID(as_uuid=True), ForeignKey("versions.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    domain_pack = relationship("DomainPack", back_populates="versions", foreign_keys=[domain_pack_id])
    proposal = relationship("Proposal", back_populates="committed_version", foreign_keys=[proposal_id])
    committer = relationship("User")
    rollback_of = relationship("Version", remote_side=[id])
    
    __table_args__ = (
        UniqueConstraint("domain_pack_id", "version_number", name="uq_domain_pack_version"),
        Index("idx_version_domain_pack", "domain_pack_id", "version_number"),
    )
    
    def __repr__(self):
        return f"<Version {self.domain_pack_id}:v{self.version_number}>"


class Proposal(Base):
    """Proposal for domain pack changes (HITL workflow)"""
    __tablename__ = "proposals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE", use_alter=True), nullable=False)
    base_version_id = Column(UUID(as_uuid=True), ForeignKey("versions.id", use_alter=True), nullable=False)
    intent_summary = Column(Text, nullable=False)
    operations = Column(JSONB, nullable=False)
    affected_paths = Column(JSONB, nullable=False)
    diff_preview = Column(Text, nullable=True)
    questions = Column(JSONB, nullable=True)
    confidence_score = Column(Float, nullable=True)
    suggested_by = Column(String(255), nullable=True)
    status = Column(SQLEnum(ProposalStatus), nullable=False, default=ProposalStatus.PENDING)
    requires_confirmation = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    confirmed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Relationships
    session = relationship("Session", back_populates="proposals")
    base_version = relationship("Version", foreign_keys=[base_version_id])
    confirmer = relationship("User", foreign_keys=[confirmed_by])
    committed_version = relationship("Version", back_populates="proposal", foreign_keys="Version.proposal_id", uselist=False)
    
    __table_args__ = (
        Index("idx_proposal_session_status", "session_id", "status"),
        Index("idx_proposal_expires", "expires_at"),
    )
    
    def __repr__(self):
        return f"<Proposal {self.id} - {self.status.value}>"


class MemoryEntry(Base):
    """Long-term and short-term memory storage"""
    __tablename__ = "memory_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(SQLEnum(MemoryType), nullable=False)
    scope = Column(SQLEnum(MemoryScope), nullable=False)
    summary = Column(Text, nullable=False)
    details = Column(JSONB, nullable=True)
    confidence = Column(Float, nullable=True)
    embedding = Column(JSONB, nullable=True)
    last_confirmed_at = Column(DateTime(timezone=True), nullable=True)
    source = Column(SQLEnum(MemorySource), nullable=False, default=MemorySource.INFERRED)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="memory_entries")
    
    __table_args__ = (
        Index("idx_memory_user_scope", "user_id", "scope"),
        Index("idx_memory_expires", "expires_at"),
    )
    
    def __repr__(self):
        return f"<MemoryEntry {self.type.value} - {self.summary[:50]}>"


class AuditLog(Base):
    """Immutable audit trail for all significant events"""
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    event_type = Column(SQLEnum(EventType), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", use_alter=True), nullable=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", use_alter=True), nullable=True)
    proposal_id = Column(UUID(as_uuid=True), ForeignKey("proposals.id", use_alter=True), nullable=True)
    version_id = Column(UUID(as_uuid=True), ForeignKey("versions.id", use_alter=True), nullable=True)
    details = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User")
    session = relationship("Session")
    proposal = relationship("Proposal")
    version = relationship("Version")
    
    __table_args__ = (
        Index("idx_audit_event_time", "event_type", "created_at"),
        Index("idx_audit_user_time", "user_id", "created_at"),
    )
    
    def __repr__(self):
        return f"<AuditLog {self.event_type.value} at {self.created_at}>"
