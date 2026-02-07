
from sqlalchemy import Column, Integer, String, TIMESTAMP, text, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.session import engine
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime

Base = declarative_base()


class DomainPack(Base):
    __tablename__ = "domain_packs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String)
    version = Column(String, nullable=False, default="1.0.0")
    created_at = Column(TIMESTAMP, server_default=text("NOW()"), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=text("NOW()"), onupdate=datetime.now, nullable=False)
    is_template = Column(Integer, default=0) # 0=Instance, 1=Template
    
    entities = relationship("Entity", back_populates="domain", cascade="all, delete-orphan")
    patterns = relationship("ExtractionPattern", back_populates="domain", cascade="all, delete-orphan")
    terms = relationship("KeyTerm", back_populates="domain", cascade="all, delete-orphan")
    relationships = relationship("Relationship", back_populates="domain", cascade="all, delete-orphan")
    versions = relationship("VersionHistory", back_populates="domain", cascade="all, delete-orphan")

class Entity(Base):
    __tablename__ = "entities"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    domain_id = Column(UUID(as_uuid=True), ForeignKey("domain_packs.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    attributes = Column(JSONB, nullable=False) # List of strings
    synonyms = Column(JSONB) # List of strings
    
    domain = relationship("DomainPack", back_populates="entities")

class ExtractionPattern(Base):
    __tablename__ = "extraction_patterns"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    domain_id = Column(UUID(as_uuid=True), ForeignKey("domain_packs.id", ondelete="CASCADE"), nullable=False)
    pattern = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)
    attribute = Column(String, nullable=False)
    confidence = Column(Integer) # Percentage 0-100
    
    domain = relationship("DomainPack", back_populates="patterns")

class KeyTerm(Base):
    __tablename__ = "key_terms"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    domain_id = Column(UUID(as_uuid=True), ForeignKey("domain_packs.id", ondelete="CASCADE"), nullable=False)
    term = Column(String, nullable=False)
    
    domain = relationship("DomainPack", back_populates="terms")

class Relationship(Base):
    __tablename__ = "relationships"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    domain_id = Column(UUID(as_uuid=True), ForeignKey("domain_packs.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    from_entity = Column(String, nullable=False)
    to_entity = Column(String, nullable=False)
    attributes = Column(JSONB)
    synonyms = Column(JSONB)
    
    domain = relationship("DomainPack", back_populates="relationships")

class VersionHistory(Base):
    __tablename__ = "version_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    domain_id = Column(UUID(as_uuid=True), ForeignKey("domain_packs.id", ondelete="CASCADE"), nullable=False)
    version_number = Column(Integer, nullable=False)
    content = Column(JSONB, nullable=False) # Full snapshot YAML/JSON
    created_at = Column(TIMESTAMP, server_default=text("NOW()"), nullable=False)
    
    domain = relationship("DomainPack", back_populates="versions")

