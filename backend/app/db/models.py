
from sqlalchemy import Column, Integer, String, TIMESTAMP, text, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.session import engine
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime

Base = declarative_base()

class Session(Base):
    __tablename__ = "sessions"
    
    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(TIMESTAMP, server_default=text("NOW()"), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=text("NOW()"), onupdate=datetime.now, nullable=False)
    current_version = Column(Integer, nullable=False, default=1)
    file_type = Column(String(10), nullable=False)
    metadata_ = Column("metadata", JSONB) # 'metadata' is reserved in SQLAlchemy Base

    versions = relationship("Version", back_populates="session", cascade="all, delete-orphan")

class Version(Base):
    __tablename__ = "versions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.session_id", ondelete="CASCADE"), nullable=False)
    version = Column(Integer, nullable=False)
    content = Column(JSONB, nullable=False)
    diff = Column(JSONB)
    reason = Column(String)
    created_at = Column(TIMESTAMP, server_default=text("NOW()"), nullable=False)

    session = relationship("Session", back_populates="versions")

    __table_args__ = (
        UniqueConstraint('session_id', 'version', name='idx_versions_session_version_unique'),
    )
