"""Domain configuration schemas."""
from pydantic import BaseModel, UUID4, Field
from datetime import datetime
from typing import List, Optional, Dict, Any, Union


class AttributeSchema(BaseModel):
    """Schema for entity/relationship attributes with LLM hints."""
    name: str = Field(..., description="The name of the attribute (e.g. 'title')")
    description: str = Field(..., description="Description of what this attribute represents")
    examples: List[str] = Field(default_factory=list, description="Realistic examples of the attribute value")


class EntitySchema(BaseModel):
    """Schema for domain entities with LLM hints."""
    name: str = Field(..., description="Readable name of the entity in Title Case (e.g. Legal Issue)")
    type: str = Field(..., description="Type of the entity in UPPERCASE_SNAKE_CASE derived from name (e.g. LEGAL_ISSUE)")
    description: str = Field(..., description="Description of the entity")
    attributes: List[AttributeSchema] = Field(default_factory=list)
    synonyms: List[str] = Field(default_factory=list)


class RelationshipAttributeSchema(BaseModel):
    """Specific schema for relationship attributes."""
    name: str = Field(..., description="Name of the attribute")
    description: str = Field(..., description="Description of the attribute")
    examples: List[str] = Field(default_factory=list, description="Realistic examples")


class RelationshipSchema(BaseModel):
    """Schema for entity relationships with LLM hints."""
    name: str = Field(..., description="Relationship name in UPPERCASE_SNAKE_CASE (e.g. CREATED_BY)")
    from_entity: str = Field(..., alias="from", description="Source entity TYPE in UPPERCASE_SNAKE_CASE (e.g. CASE)")
    to: str = Field(..., description="Target entity TYPE in UPPERCASE_SNAKE_CASE (e.g. COURT)")
    description: str = Field(..., description="Description of the relationship")
    attributes: List[RelationshipAttributeSchema] = Field(default_factory=list)

    class Config:
        populate_by_name = True


class ExtractionPatternSchema(BaseModel):
    """Schema for extraction patterns with LLM hints."""
    pattern: str = Field(..., description="Regex pattern (e.g. \\bITA-\\d+/\\w+/\\d+\\b)")
    entity_type: str = Field(..., description="Entity TYPE the pattern applies to (e.g. CASE)")
    attribute: str = Field(..., description="Attribute name to extract")
    extract_full_match: bool = Field(default=True, description="Whether to extract the full match")
    confidence: float = Field(default=0.8, description="Confidence score between 0 and 1")


class DomainConfigSchema(BaseModel):
    """Full structured domain configuration used for generation and validation."""
    name: str = Field(..., description="The name of the domain (e.g. 'Legal Analysis')")
    description: str = Field(..., description="High-level description of the domain")
    version: str = Field(default="1.0.0", description="Version of the configuration")
    entities: List[EntitySchema] = Field(default_factory=list)
    relationships: List[RelationshipSchema] = Field(default_factory=list)
    extraction_patterns: List[ExtractionPatternSchema] = Field(default_factory=list)
    key_terms: List[str] = Field(default_factory=list)


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
    """Schema for domain config list item."""
    id: UUID4
    name: str
    description: Optional[str]
    version: str
    entity_count: int
    relationship_count: int
    extraction_pattern_count: int
    key_term_count: int
    updated_at: datetime
    
    class Config:
        from_attributes = True
