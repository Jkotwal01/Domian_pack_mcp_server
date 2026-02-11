"""Validation service for domain configuration."""
from typing import Dict, Any, List, Set
from fastapi import HTTPException, status
import re


class ValidationService:
    """Service for validating domain configurations."""
    
    @staticmethod
    def validate_config(config_json: Dict[str, Any]) -> None:
        """
        Validate complete domain configuration.
        
        Args:
            config_json: Domain configuration to validate
            
        Raises:
            HTTPException: If validation fails
        """
        ValidationService._validate_schema(config_json)
        ValidationService._validate_entities(config_json.get("entities", []))
        ValidationService._validate_relationships(
            config_json.get("relationships", []),
            config_json.get("entities", [])
        )
        ValidationService._validate_patterns(
            config_json.get("extraction_patterns", []),
            config_json.get("entities", [])
        )
    
    @staticmethod
    def _validate_schema(config_json: Dict[str, Any]) -> None:
        """Validate basic schema structure."""
        required_fields = ["name", "description", "version", "entities", "relationships", 
                          "extraction_patterns", "key_terms"]
        
        for field in required_fields:
            if field not in config_json:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required field: {field}"
                )
    
    @staticmethod
    def _validate_entities(entities: List[Dict[str, Any]]) -> None:
        """Validate entities for uniqueness and required fields."""
        entity_names: Set[str] = set()
        entity_types: Set[str] = set()
        
        for entity in entities:
            # Check required fields
            if "name" not in entity or "type" not in entity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Entity missing required fields (name, type)"
                )
            
            # Check uniqueness
            if entity["name"] in entity_names:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Duplicate entity name: {entity['name']}"
                )
            
            if entity["type"] in entity_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Duplicate entity type: {entity['type']}"
                )
            
            entity_names.add(entity["name"])
            entity_types.add(entity["type"])
            
            # Validate attributes
            if "attributes" in entity:
                for attr in entity["attributes"]:
                    if "name" not in attr or "description" not in attr:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Attribute in entity '{entity['name']}' missing name or description"
                        )
    
    @staticmethod
    def _validate_relationships(
        relationships: List[Dict[str, Any]],
        entities: List[Dict[str, Any]]
    ) -> None:
        """Validate relationships reference existing entities."""
        entity_types = {e["type"] for e in entities}
        
        for rel in relationships:
            # Check required fields
            if "from" not in rel or "to" not in rel or "name" not in rel:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Relationship missing required fields (name, from, to)"
                )
            
            # Check entity references
            if rel["from"] not in entity_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Relationship '{rel['name']}' references unknown entity type: {rel['from']}"
                )
            
            if rel["to"] not in entity_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Relationship '{rel['name']}' references unknown entity type: {rel['to']}"
                )
    
    @staticmethod
    def _validate_patterns(
        patterns: List[Dict[str, Any]],
        entities: List[Dict[str, Any]]
    ) -> None:
        """Validate extraction patterns."""
        entity_types = {e["type"] for e in entities}
        
        for pattern in patterns:
            # Check required fields
            if "pattern" not in pattern or "entity_type" not in pattern:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Extraction pattern missing required fields (pattern, entity_type)"
                )
            
            # Validate regex
            try:
                re.compile(pattern["pattern"])
            except re.error as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid regex pattern: {pattern['pattern']} - {str(e)}"
                )
            
            # Check entity reference
            if pattern["entity_type"] not in entity_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Pattern references unknown entity type: {pattern['entity_type']}"
                )
