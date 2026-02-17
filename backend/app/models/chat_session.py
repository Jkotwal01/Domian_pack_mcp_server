"""Chat session model."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, ENUM, JSONB
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class SessionStatus(str, enum.Enum):
    """Chat session status enum."""
    ACTIVE = "active"
    CLOSED = "closed"


class ChatSession(Base):
    """Chat session model for conversational context."""
    
    __tablename__ = "chat_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    domain_config_id = Column(UUID(as_uuid=True), ForeignKey("domain_configs.id", ondelete="CASCADE"), nullable=False)
    status = Column(
        ENUM(SessionStatus, name='session_status', create_type=False, native_enum=True, values_callable=lambda x: [e.value for e in x]),
        default=SessionStatus.ACTIVE, 
        nullable=False
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_activity_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    session_metadata = Column(JSONB, default=dict, nullable=False)  # Renamed from 'metadata' to avoid SQLAlchemy conflict


    
    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    domain_config = relationship("DomainConfig", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan", order_by="ChatMessage.created_at")
    
    # Partial unique index: Only one active session per user+domain
    __table_args__ = (
        Index('uq_user_domain_active_session', 
              'user_id', 'domain_config_id',
              unique=True,
              postgresql_where=(status == SessionStatus.ACTIVE)),
    )
    
    def __repr__(self):
        return f"<ChatSession(id={self.id}, user_id={self.user_id}, domain_id={self.domain_config_id}, status={self.status})>"
