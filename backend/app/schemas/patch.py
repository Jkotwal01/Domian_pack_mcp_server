from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Optional, List, Union

class StrictAttributeSchema(BaseModel):
    """Strict attribute schema for OpenAI compat."""
    name: str
    description: str
    examples: List[str]
    model_config = ConfigDict(extra="forbid")

class StrictPayloadSchema(BaseModel):
    """Strict payload schema to resolve OpenAI 'additionalProperties' error."""
    # Entity fields
    name: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    attributes: Optional[List[StrictAttributeSchema]] = None
    synonyms: Optional[List[str]] = None
    
    # Relationship fields (using aliases for valid JSON keys)
    from_entity: Optional[str] = Field(default=None, alias="from")
    to_entity: Optional[str] = Field(default=None, alias="to")
    
    # Extraction pattern fields
    pattern: Optional[str] = None
    entity_type: Optional[str] = None
    attribute: Optional[str] = None
    extract_full_match: Optional[bool] = None
    confidence: Optional[float] = None
    
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

class PatchOperation(BaseModel):
    """Structured patch operation from LLM supporting hierarchical edits."""
    
    operation: Literal[
        # Domain-level operations
        "update_domain_name",
        "update_domain_description",
        "update_domain_version",
        
        # Entity operations
        "add_entity",
        "update_entity_name",
        "update_entity_type",
        "update_entity_description",
        "delete_entity",
        
        # Entity attribute operations
        "add_entity_attribute",
        "update_entity_attribute_name",
        "update_entity_attribute_description",
        "delete_entity_attribute",
        
        # Entity attribute examples operations (array)
        "add_entity_attribute_example",
        "update_entity_attribute_example",
        "delete_entity_attribute_example",
        
        # Entity synonyms operations (array)
        "add_entity_synonym",
        "update_entity_synonym",
        "delete_entity_synonym",
        
        # Relationship operations
        "add_relationship",
        "update_relationship_name",
        "update_relationship_from",
        "update_relationship_to",
        "update_relationship_description",
        "delete_relationship",
        
        # Relationship attribute operations
        "add_relationship_attribute",
        "update_relationship_attribute_name",
        "update_relationship_attribute_description",
        "delete_relationship_attribute",
        
        # Relationship attribute examples operations (array)
        "add_relationship_attribute_example",
        "update_relationship_attribute_example",
        "delete_relationship_attribute_example",
        
        # Extraction pattern operations
        "add_extraction_pattern",
        "update_extraction_pattern_pattern",
        "update_extraction_pattern_entity_type",
        "update_extraction_pattern_attribute",
        "update_extraction_pattern_extract_full_match",
        "update_extraction_pattern_confidence",
        "delete_extraction_pattern",
        
        # Key terms operations (array)
        "add_key_term",
        "update_key_term",
        "delete_key_term"
    ] = Field(..., alias="type", description="Type of operation to perform")
    
    target_name: Optional[str] = Field(
        default=None, 
        description="Name of target entity/relationship/attribute/pattern"
    )
    
    parent_name: Optional[str] = Field(
        default=None,
        description="Parent entity/relationship name (for nested operations)"
    )
    
    attribute_name: Optional[str] = Field(
        default=None,
        description="Attribute name (for attribute-level operations)"
    )
    
    old_value: Optional[str] = Field(
        default=None,
        description="Current value (for update operations on array items)"
    )
    
    new_value: Optional[Union[str, float, bool]] = Field(
        default=None,
        description="New value for the operation"
    )
    
    payload: Optional[StrictPayloadSchema] = Field(
        default=None,
        description="Complete data object (for add operations)"
    )

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {
                    "type": "add_entity",
                    "payload": {
                        "name": "User",
                        "type": "USER",
                        "description": "A person who uses the system",
                        "attributes": [
                            {
                                "name": "email",
                                "description": "Primary email address",
                                "examples": ["user@example.com"]
                            }
                        ],
                        "synonyms": ["customer", "client"]
                    }
                },
                {
                    "type": "add_entity_attribute_example",
                    "parent_name": "User",
                    "attribute_name": "email",
                    "new_value": "admin@example.com"
                },
                {
                    "type": "add_relationship",
                    "payload": {
                        "name": "OWNS",
                        "from": "User",
                        "to": "Product",
                        "description": "User owns a product",
                        "attributes": []
                    }
                }
            ]
        }
    )

class PatchList(BaseModel):
    """List of patch operations with concise reasoning."""
    reasoning: Optional[str] = Field(None, description="Concise explanation of the plan (1-2 sentences)")
    patches: List[PatchOperation] = Field(..., description="Sequence of patch operations to apply")
    
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "patches": [
                        {
                            "type": "add_key_term",
                            "new_value": "dosage"
                        },
                        {
                            "type": "add_key_term",
                            "new_value": "allergy"
                        }
                    ]
                }
            ]
        }
    )
