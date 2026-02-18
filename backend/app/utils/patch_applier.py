"""Patch application utilities for domain configuration editing.

This module contains pure Python functions to apply patches at every hierarchical level.
No LLM involvement - all operations are deterministic.
"""
from typing import Dict, Any
from app.schemas.patch import PatchOperation


def apply_patch(config: Dict[str, Any], patch: PatchOperation) -> Dict[str, Any]:
    """
    Main dispatcher for all patch operations.
    
    Args:
        config: Current domain configuration
        patch: Patch operation to apply
        
    Returns:
        Updated configuration
        
    Raises:
        ValueError: If operation fails (entity not found, duplicate, etc.)
    """
    # Create a deep copy to avoid mutating original
    import copy
    config = copy.deepcopy(config)
    
    operation_map = {
        # Domain-level
        "update_domain_name": update_domain_name,
        "update_domain_description": update_domain_description,
        "update_domain_version": update_domain_version,
        
        # Entity operations
        "add_entity": add_entity,
        "update_entity_name": update_entity_name,
        "update_entity_type": update_entity_type,
        "update_entity_description": update_entity_description,
        "delete_entity": delete_entity,
        
        # Entity attribute operations
        "add_entity_attribute": add_entity_attribute,
        "update_entity_attribute_name": update_entity_attribute_name,
        "update_entity_attribute_description": update_entity_attribute_description,
        "delete_entity_attribute": delete_entity_attribute,
        
        # Entity attribute examples
        "add_entity_attribute_example": add_entity_attribute_example,
        "update_entity_attribute_example": update_entity_attribute_example,
        "delete_entity_attribute_example": delete_entity_attribute_example,
        
        # Entity synonyms
        "add_entity_synonym": add_entity_synonym,
        "update_entity_synonym": update_entity_synonym,
        "delete_entity_synonym": delete_entity_synonym,
        
        # Relationship operations
        "add_relationship": add_relationship,
        "update_relationship_name": update_relationship_name,
        "update_relationship_from": update_relationship_from,
        "update_relationship_to": update_relationship_to,
        "update_relationship_description": update_relationship_description,
        "delete_relationship": delete_relationship,
        
        # Relationship attribute operations
        "add_relationship_attribute": add_relationship_attribute,
        "update_relationship_attribute_name": update_relationship_attribute_name,
        "update_relationship_attribute_description": update_relationship_attribute_description,
        "delete_relationship_attribute": delete_relationship_attribute,
        
        # Relationship attribute examples
        "add_relationship_attribute_example": add_relationship_attribute_example,
        "update_relationship_attribute_example": update_relationship_attribute_example,
        "delete_relationship_attribute_example": delete_relationship_attribute_example,
        
        # Extraction patterns
        "add_extraction_pattern": add_extraction_pattern,
        "update_extraction_pattern_pattern": update_extraction_pattern_pattern,
        "update_extraction_pattern_entity_type": update_extraction_pattern_entity_type,
        "update_extraction_pattern_attribute": update_extraction_pattern_attribute,
        "update_extraction_pattern_extract_full_match": update_extraction_pattern_extract_full_match,
        "update_extraction_pattern_confidence": update_extraction_pattern_confidence,
        "delete_extraction_pattern": delete_extraction_pattern,
        
        # Key terms
        "add_key_term": add_key_term,
        "update_key_term": update_key_term,
        "delete_key_term": delete_key_term
    }
    
    # Convert Pydantic model payload to dict for compatibility with handlers
    # that expect dictionary subscripting like patch.payload['name']
    if hasattr(patch, "payload") and patch.payload is not None:
        if hasattr(patch.payload, "model_dump"):
            # Using model_dump (pydantic v2) and excluding None to match dict expectation
            setattr(patch, "payload", patch.payload.model_dump(by_alias=True, exclude_none=True))
        elif hasattr(patch.payload, "dict"):
            setattr(patch, "payload", patch.payload.dict(by_alias=True, exclude_none=True))

    handler = operation_map.get(patch.operation)
    if not handler:
        raise ValueError(f"Unknown operation: {patch.operation}")
    
    return handler(config, patch)


# ============================================================================
# DOMAIN-LEVEL OPERATIONS
# ============================================================================

def update_domain_name(config: Dict[str, Any], patch: PatchOperation) -> Dict[str, Any]:
    """Update domain name."""
    config["name"] = patch.new_value
    return config


def update_domain_description(config: Dict[str, Any], patch: PatchOperation) -> Dict[str, Any]:
    """Update domain description."""
    config["description"] = patch.new_value
    return config


def update_domain_version(config: Dict[str, Any], patch: PatchOperation) -> Dict[str, Any]:
    """Update domain version."""
    config["version"] = patch.new_value
    return config


# ============================================================================
# ENTITY OPERATIONS
# ============================================================================

def add_entity(config: Dict[str, Any], patch: PatchOperation) -> Dict[str, Any]:
    """Add new entity with guardrails."""
    if "entities" not in config:
        config["entities"] = []
    
    # Check if entity already exists
    if any(e["name"] == patch.payload["name"] for e in config["entities"]):
        raise ValueError(f"Entity '{patch.payload['name']}' already exists")
    
    # Ensure required fields
    entity = {
        "name": patch.payload["name"],
        "type": patch.payload.get("type", ""),
        "description": patch.payload.get("description", ""),
        "attributes": patch.payload.get("attributes", []),
        "synonyms": patch.payload.get("synonyms", [])
    }
    
    config["entities"].append(entity)
    return config


def update_entity_name(config: Dict[str, Any], patch: PatchOperation) -> Dict[str, Any]:
    """Update entity name with cascade to relationships."""
    for entity in config.get("entities", []):
        if entity["name"] == patch.target_name:
            # Check if new name conflicts
            if any(e["name"] == patch.new_value for e in config["entities"] if e["name"] != patch.target_name):
                raise ValueError(f"Entity '{patch.new_value}' already exists")
            
            old_name = entity["name"]
            entity["name"] = patch.new_value
            
            # Update references in relationships
            for rel in config.get("relationships", []):
                if rel.get("from") == old_name:
                    rel["from"] = patch.new_value
                if rel.get("to") == old_name:
                    rel["to"] = patch.new_value
            
            return config
    
    raise ValueError(f"Entity '{patch.target_name}' not found")


def update_entity_type(config: Dict[str, Any], patch: PatchOperation) -> Dict[str, Any]:
    """Update entity type."""
    for entity in config.get("entities", []):
        if entity["name"] == patch.target_name:
            entity["type"] = patch.new_value
            return config
    raise ValueError(f"Entity '{patch.target_name}' not found")


def update_entity_description(config: Dict[str, Any], patch: PatchOperation) -> Dict[str, Any]:
    """Update entity description."""
    for entity in config.get("entities", []):
        if entity["name"] == patch.target_name:
            entity["description"] = patch.new_value
            return config
    raise ValueError(f"Entity '{patch.target_name}' not found")


def delete_entity(config: Dict[str, Any], patch: PatchOperation) -> Dict[str, Any]:
    """Delete entity and check for relationship references."""
    # Check if entity is referenced in relationships
    for rel in config.get("relationships", []):
        if rel.get("from") == patch.target_name or rel.get("to") == patch.target_name:
            raise ValueError(
                f"Cannot delete entity '{patch.target_name}': "
                f"referenced in relationship '{rel['name']}'"
            )
    
    config["entities"] = [e for e in config.get("entities", []) if e["name"] != patch.target_name]
    return config


# ============================================================================
# ENTITY ATTRIBUTE OPERATIONS
# ============================================================================

def add_entity_attribute(config: Dict[str, Any], patch: PatchOperation) -> Dict[str, Any]:
    """Add attribute to entity."""
    for entity in config.get("entities", []):
        if entity["name"] == patch.parent_name:
            # Check for duplicate
            if any(a["name"] == patch.payload["name"] for a in entity.get("attributes", [])):
                raise ValueError(
                    f"Attribute '{patch.payload['name']}' already exists in {patch.parent_name}"
                )
            
            if "attributes" not in entity:
                entity["attributes"] = []
            
            attribute = {
                "name": patch.payload["name"],
                "description": patch.payload.get("description", ""),
                "examples": patch.payload.get("examples", [])
            }
            entity["attributes"].append(attribute)
            return config
    
    raise ValueError(f"Entity '{patch.parent_name}' not found")


def update_entity_attribute_name(config: Dict[str, Any], patch: PatchOperation) -> Dict[str, Any]:
    """Update entity attribute name."""
    for entity in config.get("entities", []):
        if entity["name"] == patch.parent_name:
            for attr in entity.get("attributes", []):
                if attr["name"] == patch.attribute_name:
                    attr["name"] = patch.new_value
                    return config
            raise ValueError(f"Attribute '{patch.attribute_name}' not found in {patch.parent_name}")
    raise ValueError(f"Entity '{patch.parent_name}' not found")


def update_entity_attribute_description(config: Dict[str, Any], patch: PatchOperation) -> Dict[str, Any]:
    """Update entity attribute description."""
    for entity in config.get("entities", []):
        if entity["name"] == patch.parent_name:
            for attr in entity.get("attributes", []):
                if attr["name"] == patch.attribute_name:
                    attr["description"] = patch.new_value
                    return config
            raise ValueError(f"Attribute '{patch.attribute_name}' not found in {patch.parent_name}")
    raise ValueError(f"Entity '{patch.parent_name}' not found")


def delete_entity_attribute(config: Dict[str, Any], patch: PatchOperation) -> Dict[str, Any]:
    """Delete entity attribute."""
    for entity in config.get("entities", []):
        if entity["name"] == patch.parent_name:
            entity["attributes"] = [
                a for a in entity.get("attributes", []) 
                if a["name"] != patch.attribute_name
            ]
            return config
    raise ValueError(f"Entity '{patch.parent_name}' not found")


# ============================================================================
# ENTITY ATTRIBUTE EXAMPLES (ARRAY OPERATIONS)
# ============================================================================

def add_entity_attribute_example(config: Dict[str, Any], patch: PatchOperation) -> Dict[str, Any]:
    """Add example to entity attribute's examples array."""
    for entity in config.get("entities", []):
        if entity["name"] == patch.parent_name:
            for attr in entity.get("attributes", []):
                if attr["name"] == patch.attribute_name:
                    if "examples" not in attr:
                        attr["examples"] = []
                    attr["examples"].append(patch.new_value)
                    return config
            raise ValueError(f"Attribute '{patch.attribute_name}' not found in {patch.parent_name}")
    raise ValueError(f"Entity '{patch.parent_name}' not found")


def update_entity_attribute_example(config: Dict[str, Any], patch: PatchOperation) -> Dict[str, Any]:
    """Update specific example in entity attribute."""
    for entity in config.get("entities", []):
        if entity["name"] == patch.parent_name:
            for attr in entity.get("attributes", []):
                if attr["name"] == patch.attribute_name:
                    examples = attr.get("examples", [])
                    if patch.old_value in examples:
                        idx = examples.index(patch.old_value)
                        examples[idx] = patch.new_value
                        return config
                    raise ValueError(f"Example '{patch.old_value}' not found")
            raise ValueError(f"Attribute '{patch.attribute_name}' not found")
    raise ValueError(f"Entity '{patch.parent_name}' not found")


def delete_entity_attribute_example(config: Dict[str, Any], patch: PatchOperation) -> Dict[str, Any]:
    """Delete example from entity attribute."""
    for entity in config.get("entities", []):
        if entity["name"] == patch.parent_name:
            for attr in entity.get("attributes", []):
                if attr["name"] == patch.attribute_name:
                    attr["examples"] = [
                        ex for ex in attr.get("examples", []) 
                        if ex != patch.old_value
                    ]
                    return config
            raise ValueError(f"Attribute '{patch.attribute_name}' not found")
    raise ValueError(f"Entity '{patch.parent_name}' not found")


# ============================================================================
# ENTITY SYNONYMS (ARRAY OPERATIONS)
# ============================================================================

def add_entity_synonym(config: Dict[str, Any], patch: PatchOperation) -> Dict[str, Any]:
    """Add synonym to entity."""
    for entity in config.get("entities", []):
        if entity["name"] == patch.parent_name:
            if "synonyms" not in entity:
                entity["synonyms"] = []
            if patch.new_value in entity["synonyms"]:
                raise ValueError(f"Synonym '{patch.new_value}' already exists")
            entity["synonyms"].append(patch.new_value)
            return config
    raise ValueError(f"Entity '{patch.parent_name}' not found")


def update_entity_synonym(config: Dict[str, Any], patch: PatchOperation) -> Dict[str, Any]:
    """Update entity synonym."""
    for entity in config.get("entities", []):
        if entity["name"] == patch.parent_name:
            synonyms = entity.get("synonyms", [])
            if patch.old_value in synonyms:
                idx = synonyms.index(patch.old_value)
                synonyms[idx] = patch.new_value
                return config
            raise ValueError(f"Synonym '{patch.old_value}' not found")
    raise ValueError(f"Entity '{patch.parent_name}' not found")


def delete_entity_synonym(config: Dict[str, Any], patch: PatchOperation) -> Dict[str, Any]:
    """Delete synonym from entity."""
    for entity in config.get("entities", []):
        if entity["name"] == patch.parent_name:
            entity["synonyms"] = [
                s for s in entity.get("synonyms", []) 
                if s != patch.old_value
            ]
            return config
    raise ValueError(f"Entity '{patch.parent_name}' not found")


# ============================================================================
# RELATIONSHIP OPERATIONS
# ============================================================================

def add_relationship(config: Dict[str, Any], patch: PatchOperation) -> Dict[str, Any]:
    """Add new relationship with validation."""
    if "relationships" not in config:
        config["relationships"] = []
    
    # Check if relationship already exists
    if any(r["name"] == patch.payload["name"] for r in config["relationships"]):
        raise ValueError(f"Relationship '{patch.payload['name']}' already exists")
    
    # Validate entity references
    entity_names = {e["name"] for e in config.get("entities", [])}
    if patch.payload["from"] not in entity_names:
        raise ValueError(f"Source entity '{patch.payload['from']}' does not exist")
    if patch.payload["to"] not in entity_names:
        raise ValueError(f"Target entity '{patch.payload['to']}' does not exist")
    
    relationship = {
        "name": patch.payload["name"],
        "from": patch.payload["from"],
        "to": patch.payload["to"],
        "description": patch.payload.get("description", ""),
        "attributes": patch.payload.get("attributes", [])
    }
    
    config["relationships"].append(relationship)
    return config


def update_relationship_name(config: Dict[str, Any], patch: PatchOperation) -> Dict[str, Any]:
    """Update relationship name."""
    for rel in config.get("relationships", []):
        if rel["name"] == patch.target_name:
            rel["name"] = patch.new_value
            return config
    raise ValueError(f"Relationship '{patch.target_name}' not found")


def update_relationship_from(config: Dict[str, Any], patch: PatchOperation) -> Dict[str, Any]:
    """Update relationship source entity."""
    entity_names = {e["name"] for e in config.get("entities", [])}
    if patch.new_value not in entity_names:
        raise ValueError(f"Entity '{patch.new_value}' does not exist")
    
    for rel in config.get("relationships", []):
        if rel["name"] == patch.target_name:
            rel["from"] = patch.new_value
            return config
    raise ValueError(f"Relationship '{patch.target_name}' not found")


def update_relationship_to(config: Dict[str, Any], patch: PatchOperation) -> Dict[str, Any]:
    """Update relationship target entity."""
    entity_names = {e["name"] for e in config.get("entities", [])}
    if patch.new_value not in entity_names:
        raise ValueError(f"Entity '{patch.new_value}' does not exist")
    
    for rel in config.get("relationships", []):
        if rel["name"] == patch.target_name:
            rel["to"] = patch.new_value
            return config
    raise ValueError(f"Relationship '{patch.target_name}' not found")


def update_relationship_description(config: Dict[str, Any], patch: PatchOperation) -> Dict[str, Any]:
    """Update relationship description."""
    for rel in config.get("relationships", []):
        if rel["name"] == patch.target_name:
            rel["description"] = patch.new_value
            return config
    raise ValueError(f"Relationship '{patch.target_name}' not found")


def delete_relationship(config: Dict[str, Any], patch: PatchOperation) -> Dict[str, Any]:
    """Delete relationship."""
    config["relationships"] = [
        r for r in config.get("relationships", []) 
        if r["name"] != patch.target_name
    ]
    return config


# ============================================================================
# RELATIONSHIP ATTRIBUTE OPERATIONS
# ============================================================================

def add_relationship_attribute(config: Dict[str, Any], patch: PatchOperation) -> Dict[str, Any]:
    """Add attribute to relationship."""
    for rel in config.get("relationships", []):
        if rel["name"] == patch.parent_name:
            if "attributes" not in rel:
                rel["attributes"] = []
            
            if any(a["name"] == patch.payload["name"] for a in rel["attributes"]):
                raise ValueError(
                    f"Attribute '{patch.payload['name']}' already exists in {patch.parent_name}"
                )
            
            attribute = {
                "name": patch.payload["name"],
                "description": patch.payload.get("description", ""),
                "examples": patch.payload.get("examples", [])
            }
            rel["attributes"].append(attribute)
            return config
    raise ValueError(f"Relationship '{patch.parent_name}' not found")


def update_relationship_attribute_name(config: Dict[str, Any], patch: PatchOperation) -> Dict[str, Any]:
    """Update relationship attribute name."""
    for rel in config.get("relationships", []):
        if rel["name"] == patch.parent_name:
            for attr in rel.get("attributes", []):
                if attr["name"] == patch.attribute_name:
                    attr["name"] = patch.new_value
                    return config
            raise ValueError(f"Attribute '{patch.attribute_name}' not found in {patch.parent_name}")
    raise ValueError(f"Relationship '{patch.parent_name}' not found")


def update_relationship_attribute_description(config: Dict[str, Any], patch: PatchOperation) -> Dict[str, Any]:
    """Update relationship attribute description."""
    for rel in config.get("relationships", []):
        if rel["name"] == patch.parent_name:
            for attr in rel.get("attributes", []):
                if attr["name"] == patch.attribute_name:
                    attr["description"] = patch.new_value
                    return config
            raise ValueError(f"Attribute '{patch.attribute_name}' not found in {patch.parent_name}")
    raise ValueError(f"Relationship '{patch.parent_name}' not found")


def delete_relationship_attribute(config: Dict[str, Any], patch: PatchOperation) -> Dict[str, Any]:
    """Delete relationship attribute."""
    for rel in config.get("relationships", []):
        if rel["name"] == patch.parent_name:
            rel["attributes"] = [
                a for a in rel.get("attributes", []) 
                if a["name"] != patch.attribute_name
            ]
            return config
    raise ValueError(f"Relationship '{patch.parent_name}' not found")


# ============================================================================
# RELATIONSHIP ATTRIBUTE EXAMPLES (ARRAY OPERATIONS)
# ============================================================================

def add_relationship_attribute_example(config: Dict[str, Any], patch: PatchOperation) -> Dict[str, Any]:
    """Add example to relationship attribute's examples array."""
    for rel in config.get("relationships", []):
        if rel["name"] == patch.parent_name:
            for attr in rel.get("attributes", []):
                if attr["name"] == patch.attribute_name:
                    if "examples" not in attr:
                        attr["examples"] = []
                    attr["examples"].append(patch.new_value)
                    return config
            raise ValueError(f"Attribute '{patch.attribute_name}' not found in {patch.parent_name}")
    raise ValueError(f"Relationship '{patch.parent_name}' not found")


def update_relationship_attribute_example(config: Dict[str, Any], patch: PatchOperation) -> Dict[str, Any]:
    """Update specific example in relationship attribute."""
    for rel in config.get("relationships", []):
        if rel["name"] == patch.parent_name:
            for attr in rel.get("attributes", []):
                if attr["name"] == patch.attribute_name:
                    examples = attr.get("examples", [])
                    if patch.old_value in examples:
                        idx = examples.index(patch.old_value)
                        examples[idx] = patch.new_value
                        return config
                    raise ValueError(f"Example '{patch.old_value}' not found")
            raise ValueError(f"Attribute '{patch.attribute_name}' not found")
    raise ValueError(f"Relationship '{patch.parent_name}' not found")


def delete_relationship_attribute_example(config: Dict[str, Any], patch: PatchOperation) -> Dict[str, Any]:
    """Delete example from relationship attribute."""
    for rel in config.get("relationships", []):
        if rel["name"] == patch.parent_name:
            for attr in rel.get("attributes", []):
                if attr["name"] == patch.attribute_name:
                    attr["examples"] = [
                        ex for ex in attr.get("examples", []) 
                        if ex != patch.old_value
                    ]
                    return config
            raise ValueError(f"Attribute '{patch.attribute_name}' not found")
    raise ValueError(f"Relationship '{patch.parent_name}' not found")


# ============================================================================
# EXTRACTION PATTERN OPERATIONS
# ============================================================================

def add_extraction_pattern(config: Dict[str, Any], patch: PatchOperation) -> Dict[str, Any]:
    """Add extraction pattern."""
    if "extraction_patterns" not in config:
        config["extraction_patterns"] = []
    
    pattern = {
        "pattern": patch.payload["pattern"],
        "entity_type": patch.payload["entity_type"],
        "attribute": patch.payload["attribute"],
        "extract_full_match": patch.payload.get("extract_full_match", True),
        "confidence": patch.payload.get("confidence", 0.9)
    }
    
    config["extraction_patterns"].append(pattern)
    return config


def update_extraction_pattern_pattern(config: Dict[str, Any], patch: PatchOperation) -> Dict[str, Any]:
    """Update extraction pattern regex."""
    # Find by index or unique identifier (using pattern as identifier for now)
    for i, pattern in enumerate(config.get("extraction_patterns", [])):
        if i == int(patch.target_name) if patch.target_name.isdigit() else False:
            pattern["pattern"] = patch.new_value
            return config
    raise ValueError(f"Extraction pattern '{patch.target_name}' not found")


def update_extraction_pattern_entity_type(config: Dict[str, Any], patch: PatchOperation) -> Dict[str, Any]:
    """Update extraction pattern entity type."""
    for i, pattern in enumerate(config.get("extraction_patterns", [])):
        if i == int(patch.target_name) if patch.target_name.isdigit() else False:
            pattern["entity_type"] = patch.new_value
            return config
    raise ValueError(f"Extraction pattern '{patch.target_name}' not found")


def update_extraction_pattern_attribute(config: Dict[str, Any], patch: PatchOperation) -> Dict[str, Any]:
    """Update extraction pattern attribute."""
    for i, pattern in enumerate(config.get("extraction_patterns", [])):
        if i == int(patch.target_name) if patch.target_name.isdigit() else False:
            pattern["attribute"] = patch.new_value
            return config
    raise ValueError(f"Extraction pattern '{patch.target_name}' not found")


def update_extraction_pattern_extract_full_match(config: Dict[str, Any], patch: PatchOperation) -> Dict[str, Any]:
    """Update extraction pattern extract_full_match flag."""
    for i, pattern in enumerate(config.get("extraction_patterns", [])):
        if i == int(patch.target_name) if patch.target_name.isdigit() else False:
            pattern["extract_full_match"] = patch.new_value
            return config
    raise ValueError(f"Extraction pattern '{patch.target_name}' not found")


def update_extraction_pattern_confidence(config: Dict[str, Any], patch: PatchOperation) -> Dict[str, Any]:
    """Update extraction pattern confidence."""
    for i, pattern in enumerate(config.get("extraction_patterns", [])):
        if i == int(patch.target_name) if patch.target_name.isdigit() else False:
            pattern["confidence"] = patch.new_value
            return config
    raise ValueError(f"Extraction pattern '{patch.target_name}' not found")


def delete_extraction_pattern(config: Dict[str, Any], patch: PatchOperation) -> Dict[str, Any]:
    """Delete extraction pattern."""
    idx = int(patch.target_name) if patch.target_name.isdigit() else -1
    if 0 <= idx < len(config.get("extraction_patterns", [])):
        config["extraction_patterns"].pop(idx)
        return config
    raise ValueError(f"Extraction pattern '{patch.target_name}' not found")


# ============================================================================
# KEY TERMS OPERATIONS
# ============================================================================

def add_key_term(config: Dict[str, Any], patch: PatchOperation) -> Dict[str, Any]:
    """Add key term. Ignores if already exists (idempotent for bulk)."""
    if "key_terms" not in config:
        config["key_terms"] = []
    
    if patch.new_value is None or str(patch.new_value).strip() == "":
        return config # Skip null/empty terms
        
    if patch.new_value in config["key_terms"]:
        # Instead of raising, we just return for bulk operation success
        return config
    
    config["key_terms"].append(patch.new_value)
    return config


def update_key_term(config: Dict[str, Any], patch: PatchOperation) -> Dict[str, Any]:
    """Update key term."""
    if patch.old_value is None or patch.new_value is None:
        return config
        
    key_terms = config.get("key_terms", [])
    if patch.old_value in key_terms:
        idx = key_terms.index(patch.old_value)
        key_terms[idx] = patch.new_value
        return config
    raise ValueError(f"Key term '{patch.old_value}' not found")


def delete_key_term(config: Dict[str, Any], patch: PatchOperation) -> Dict[str, Any]:
    """Delete key term."""
    if patch.old_value is None:
        return config
        
    config["key_terms"] = [
        t for t in config.get("key_terms", []) 
        if t != patch.old_value
    ]
    return config
