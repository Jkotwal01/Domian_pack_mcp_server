"""Patch operation schemas for domain configuration editing."""
from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict, Any


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
    ] = Field(description="Type of operation to perform")
    
    target_name: Optional[str] = Field(
        None, 
        description="Name of target entity/relationship/attribute/pattern"
    )
    
    parent_name: Optional[str] = Field(
        None,
        description="Parent entity/relationship name (for nested operations)"
    )
    
    attribute_name: Optional[str] = Field(
        None,
        description="Attribute name (for attribute-level operations)"
    )
    
    old_value: Optional[str] = Field(
        None,
        description="Current value (for update operations on array items)"
    )
    
    new_value: Optional[Any] = Field(
        None,
        description="New value for the operation"
    )
    
    payload: Optional[Dict[str, Any]] = Field(
        None,
        description="Complete data object (for add operations)"
    )
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "operation": "add_entity_attribute",
                    "parent_name": "User",
                    "payload": {
                        "name": "email",
                        "description": "User email address",
                        "examples": ["user@example.com"]
                    }
                },
                {
                    "operation": "add_entity_attribute_example",
                    "parent_name": "User",
                    "attribute_name": "email",
                    "new_value": "admin@example.com"
                },
                {
                    "operation": "update_entity_synonym",
                    "parent_name": "User",
                    "old_value": "customer",
                    "new_value": "client"
                },
                {
                    "operation": "update_relationship_from",
                    "target_name": "OWNS",
                    "new_value": "Customer"
                }
            ]
        }
