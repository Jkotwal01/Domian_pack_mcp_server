"""LangGraph state schema for domain configuration chatbot."""
from typing import TypedDict, List, Dict, Any, Optional


class DomainGraphState(TypedDict):
    """
    State maintained throughout the conversation.
    This state is rebuilt on each request from database data.
    """
    # Context
    domain_config: Dict[str, Any]  # Current domain configuration
    entity_index: Dict[str, Dict[str, Any]]  # Quick entity lookup by type
    relationship_index: Dict[str, List[Dict[str, Any]]]  # Relationships by type
    
    # Conversation
    messages: List[Dict[str, str]]  # Chat history (last N messages)
    user_message: str  # Current user input
    
    # Intent & Action
    intent: str  # Detected intent (add_entity, edit_relationship, etc.)
    target_entity: Optional[str]  # Entity being modified
    target_relationship: Optional[str]  # Relationship being modified
    proposed_patch: Optional[List[Dict[str, Any]]]  # JSONPatch operations
    
    # Reasoning (runtime only, not persisted)
    reasoning_steps: List[str]  # Chain of thought
    
    # Confirmation
    needs_confirmation: bool  # Whether user confirmation is required
    confirmation_message: Optional[str]  # Message to show user
    awaiting_confirmation: bool  # Waiting for yes/no response
    
    # Output
    assistant_response: str  # Response to send to user
    updated_config: Optional[Dict[str, Any]]  # Updated config if changes applied
    error: Optional[str]  # Error message if any


def create_initial_state(
    domain_config: Dict[str, Any],
    user_message: str,
    chat_history: List[Dict[str, str]]
) -> DomainGraphState:
    """
    Create initial state for graph execution.
    
    Args:
        domain_config: Current domain configuration
        user_message: User's message
        chat_history: Recent chat messages
        
    Returns:
        Initial graph state
    """
    # Build entity index
    entity_index = {}
    for entity in domain_config.get("entities", []):
        entity_index[entity["type"]] = entity
    
    # Build relationship index
    relationship_index = {}
    for rel in domain_config.get("relationships", []):
        rel_type = rel["name"]
        if rel_type not in relationship_index:
            relationship_index[rel_type] = []
        relationship_index[rel_type].append(rel)
    
    return DomainGraphState(
        domain_config=domain_config,
        entity_index=entity_index,
        relationship_index=relationship_index,
        messages=chat_history,
        user_message=user_message,
        intent="",
        target_entity=None,
        target_relationship=None,
        proposed_patch=None,
        reasoning_steps=[],
        needs_confirmation=False,
        confirmation_message=None,
        awaiting_confirmation=False,
        assistant_response="",
        updated_config=None,
        error=None
    )
