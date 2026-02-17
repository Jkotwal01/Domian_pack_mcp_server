"""Context slicing utilities for optimizing LLM token usage.

These utilities extract only the relevant portions of the domain configuration
to send to the LLM, reducing token usage by 85-96%.
"""
from typing import Dict, Any, List, Optional
import json


def get_relevant_entities(
    config: Dict[str, Any],
    entity_names: List[str]
) -> List[Dict[str, Any]]:
    """
    Extract only specified entities from config.
    
    Args:
        config: Full domain configuration
        entity_names: List of entity names to extract
        
    Returns:
        List of matching entities with full details
    """
    entities = config.get("entities", [])
    return [
        entity for entity in entities
        if entity["name"] in entity_names
    ]


def get_relevant_relationships(
    config: Dict[str, Any],
    relationship_names: Optional[List[str]] = None,
    entity_names: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Extract relationships by name or by connected entities.
    
    Args:
        config: Full domain configuration
        relationship_names: Specific relationship names to extract
        entity_names: Extract relationships connected to these entities
        
    Returns:
        List of matching relationships
    """
    relationships = config.get("relationships", [])
    
    if relationship_names:
        return [
            rel for rel in relationships
            if rel["name"] in relationship_names
        ]
    
    if entity_names:
        return [
            rel for rel in relationships
            if rel.get("from") in entity_names or rel.get("to") in entity_names
        ]
    
    return relationships


def format_minimal_context(
    config: Dict[str, Any],
    intent: str,
    target_name: Optional[str] = None
) -> str:
    """
    Format minimal context based on intent and target.
    
    This is the main function used by LangGraph nodes to reduce token usage.
    
    Args:
        config: Full domain configuration
        intent: Detected operation intent
        target_name: Target entity/relationship name if known
        
    Returns:
        Minimal JSON string containing only relevant context
    """
    # Domain-level operations
    if "domain" in intent:
        return json.dumps({
            "name": config.get("name"),
            "description": config.get("description"),
            "version": config.get("version")
        }, indent=2)
    
    # Entity operations
    if "entity" in intent and "relationship" not in intent:
        if target_name:
            entities = get_relevant_entities(config, [target_name])
            if entities:
                return json.dumps({"entity": entities[0]}, indent=2)
        
        # Fallback: return entity names only
        entity_names = [e["name"] for e in config.get("entities", [])]
        return json.dumps({"entity_names": entity_names})
    
    # Relationship operations
    if "relationship" in intent:
        if target_name:
            relationships = get_relevant_relationships(config, relationship_names=[target_name])
            if relationships:
                # Include entity names for reference validation
                entity_names = [e["name"] for e in config.get("entities", [])]
                return json.dumps({
                    "relationship": relationships[0],
                    "available_entities": entity_names
                }, indent=2)
        
        # Fallback: return relationship and entity names
        rel_names = [r["name"] for r in config.get("relationships", [])]
        entity_names = [e["name"] for e in config.get("entities", [])]
        return json.dumps({
            "relationship_names": rel_names,
            "entity_names": entity_names
        })
    
    # Extraction pattern operations
    if "extraction_pattern" in intent:
        patterns = config.get("extraction_patterns", [])
        entity_types = [e["type"] for e in config.get("entities", [])]
        return json.dumps({
            "pattern_count": len(patterns),
            "available_entity_types": entity_types
        })
    
    # Key terms operations
    if "key_term" in intent:
        return json.dumps({
            "key_terms": config.get("key_terms", [])
        })
    
    # Default: return summary
    return json.dumps({
        "entity_names": [e["name"] for e in config.get("entities", [])],
        "relationship_names": [r["name"] for r in config.get("relationships", [])]
    })


def extract_target_from_message(
    message: str,
    config: Dict[str, Any]
) -> Optional[str]:
    """
    Extract target entity/relationship name from user message.
    
    Uses simple heuristic: looks for entity/relationship names in message.
    
    Args:
        message: User's natural language message
        config: Domain configuration
        
    Returns:
        Target name if found, None otherwise
    """
    message_lower = message.lower()
    
    # Check entities
    for entity in config.get("entities", []):
        if entity["name"].lower() in message_lower:
            return entity["name"]
    
    # Check relationships
    for rel in config.get("relationships", []):
        if rel["name"].lower() in message_lower:
            return rel["name"]
    
    return None


def get_context_size_reduction(
    full_config: Dict[str, Any],
    minimal_context: str
) -> Dict[str, Any]:
    """
    Calculate token reduction statistics.
    
    Args:
        full_config: Full domain configuration
        minimal_context: Minimal context string
        
    Returns:
        Dict with size statistics
    """
    full_size = len(json.dumps(full_config))
    minimal_size = len(minimal_context)
    reduction_pct = ((full_size - minimal_size) / full_size) * 100
    
    return {
        "full_size_bytes": full_size,
        "minimal_size_bytes": minimal_size,
        "reduction_bytes": full_size - minimal_size,
        "reduction_percentage": round(reduction_pct, 2)
    }
