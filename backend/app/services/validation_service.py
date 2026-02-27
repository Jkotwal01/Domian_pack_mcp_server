"""Validation service for domain configuration."""
from typing import Dict, Any, List, Set
from fastapi import HTTPException, status
from pydantic import ValidationError
from app.schemas.domain import EntitySchema, RelationshipSchema, ExtractionPatternSchema
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
    def validate_domain_config(config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate entire domain config using Pydantic schemas.
        Returns validation result dict instead of raising exceptions.
        
        Args:
            config: Domain configuration to validate
            
        Returns:
            {"valid": bool, "errors": List[str]}
        """
        errors = []
        
        try:
            # Validate basic structure
            required_fields = ["name", "description", "version"]
            for field in required_fields:
                if field not in config:
                    errors.append(f"Missing required field: {field}")
            
            # Validate entities
            entity_names = set()
            entity_types = set()
            for entity in config.get("entities", []):
                try:
                    EntitySchema(**entity)
                    
                    # Check for duplicate names
                    if entity["name"] in entity_names:
                        errors.append(f"Duplicate entity name: {entity['name']}")
                    entity_names.add(entity["name"])
                    
                    # Check for duplicate types
                    if entity["type"] in entity_types:
                        errors.append(f"Duplicate entity type: {entity['type']}")
                    entity_types.add(entity["type"])
                    
                except ValidationError as e:
                    for err in e.errors():
                        errors.append(f"Entity '{entity.get('name', 'unknown')}': {err['msg']}")
            
            # Validate relationships
            for rel in config.get("relationships", []):
                try:
                    RelationshipSchema(**rel)
                    
                    # Check entity references (usually reference the 'type')
                    if rel.get("from") not in entity_types:
                        errors.append(
                            f"Relationship '{rel.get('name', 'unknown')}' references "
                            f"unknown entity type '{rel.get('from')}'"
                        )
                    if rel.get("to") not in entity_types:
                        errors.append(
                            f"Relationship '{rel.get('name', 'unknown')}' references "
                            f"unknown entity type '{rel.get('to')}'"
                        )
                        
                except ValidationError as e:
                    for err in e.errors():
                        errors.append(f"Relationship '{rel.get('name', 'unknown')}': {err['msg']}")
            
            # Validate extraction patterns
            for pattern in config.get("extraction_patterns", []):
                try:
                    ExtractionPatternSchema(**pattern)
                    
                    # Check entity reference
                    if pattern.get("entity_type") not in entity_types:
                         errors.append(f"Pattern references unknown entity type: {pattern.get('entity_type')}")
                    
                    # Validate regex
                    try:
                        re.compile(pattern.get("pattern", ""))
                    except re.error as e:
                        errors.append(f"Invalid regex pattern: {str(e)}")
                        
                except ValidationError as e:
                    for err in e.errors():
                        errors.append(f"Extraction pattern: {err['msg']}")
            
        except Exception as e:
            errors.append(f"Unexpected validation error: {str(e)}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
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

            # Validate relationship attributes if present
            if "attributes" in rel:
                for attr in rel["attributes"]:
                    if "name" not in attr or "description" not in attr:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Attribute in relationship '{rel['name']}' missing name or description"
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
