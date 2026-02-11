"""Domain configuration schemas."""
from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import List, Optional, Dict, Any


class AttributeSchema(BaseModel):
    """Schema for entity/relationship attributes."""
    name: str
    description: str


class EntitySchema(BaseModel):
    """Schema for domain entities."""
    name: str
    type: str
    description: str
    attributes: List[AttributeSchema] = []
    synonyms: List[str] = []


class RelationshipSchema(BaseModel):
    """Schema for entity relationships."""
    name: str
    from_: str  # Using from_ to avoid Python keyword
    to: str
    description: str
    attributes: List[AttributeSchema] = []
    
    class Config:
        populate_by_name = True
        fields = {'from_': 'from'}


class ExtractionPatternSchema(BaseModel):
    """Schema for extraction patterns."""
    pattern: str
    entity_type: str
    attribute: str
    extract_full_match: bool = True
    confidence: float = 0.9


class DomainConfigCreate(BaseModel):
    """Schema for creating a new domain config."""
    name: str
    description: Optional[str] = None
    version: str = "1.0.0"


class DomainConfigUpdate(BaseModel):
    """Schema for updating domain config."""
    name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    config_json: Optional[Dict[str, Any]] = None


class DomainConfigResponse(BaseModel):
    """Schema for domain config response."""
    id: UUID4
    owner_user_id: UUID4
    name: str
    description: Optional[str]
    version: str
    config_json: Dict[str, Any]
    entity_count: int
    relationship_count: int
    extraction_pattern_count: int
    key_term_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DomainConfigList(BaseModel):
    """Schema for domain config list item (without full config_json)."""
    id: UUID4
    name: str
    description: Optional[str]
    entity_count: int
    relationship_count: int
    extraction_pattern_count: int
    key_term_count: int
    updated_at: datetime
    
    class Config:
        from_attributes = True
