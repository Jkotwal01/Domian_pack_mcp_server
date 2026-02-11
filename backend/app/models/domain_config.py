"""Domain configuration model."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base


class DomainConfig(Base):
    """Domain configuration model storing domain pack data."""
    
    __tablename__ = "domain_configs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    version = Column(String(50), default="1.0.0", nullable=False)
    config_json = Column(JSONB, nullable=False)
    
    # Cached counts for performance
    entity_count = Column(Integer, default=0, nullable=False)
    relationship_count = Column(Integer, default=0, nullable=False)
    extraction_pattern_count = Column(Integer, default=0, nullable=False)
    key_term_count = Column(Integer, default=0, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="domain_configs")
    chat_sessions = relationship("ChatSession", back_populates="domain_config", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<DomainConfig(id={self.id}, name={self.name}, owner_id={self.owner_user_id})>"
    
    def update_counts(self):
        """Update cached counts from config_json."""
        self.entity_count = len(self.config_json.get("entities", []))
        self.relationship_count = len(self.config_json.get("relationships", []))
        self.extraction_pattern_count = len(self.config_json.get("extraction_patterns", []))
        self.key_term_count = len(self.config_json.get("key_terms", []))
