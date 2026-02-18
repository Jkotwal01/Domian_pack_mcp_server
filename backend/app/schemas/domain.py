"""Domain configuration schemas."""
from pydantic import BaseModel, UUID4, Field
from datetime import datetime
from typing import List, Optional, Dict, Any, Union


class AttributeSchema(BaseModel):
    """Schema for entity/relationship attributes matching strict template."""
    name: str
    description: str
    examples: List[str] = []


class EntitySchema(BaseModel):
    """Schema for domain entities. Supports flexible descriptions."""
    name: str
    type: str
    description: Optional[str] = ""
    attributes: List[Union[str, AttributeSchema]] = []
    synonyms: List[str] = []


class RelationshipSchema(BaseModel):
    """Schema for entity relationships. Supports both strict and legacy formats."""
    name: Optional[str] = None
    type: Optional[str] = None
    from_: str = Field(alias="from")
    to: str
    description: Optional[str] = ""
    attributes: List[Union[str, AttributeSchema]] = []
    properties: List[Union[str, AttributeSchema]] = []
    
    class Config:
        populate_by_name = True

    @property
    def relationship_name(self) -> str:
        return self.name or self.type or "unnamed"

    @property
    def relationship_attributes(self) -> List[Any]:
        return self.attributes or self.properties or []


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
