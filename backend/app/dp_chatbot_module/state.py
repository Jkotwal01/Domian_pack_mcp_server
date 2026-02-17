"""LangGraph state schema for domain configuration chatbot."""
from typing import TypedDict, Optional, Dict, Any, List


class AgentState(TypedDict):
    """State that flows through all LangGraph nodes."""
    
    # Input
    current_config: Dict[str, Any]  # Current domain config JSON
    user_message: str  # User's natural language request
    chat_history: List[Dict[str, str]]  # Recent conversation context
    
    # Processing
    intent: Optional[str]  # Detected operation intent
    target_entity: Optional[str]  # Target entity/relationship name
    proposed_patch: Optional[Dict[str, Any]]  # Generated patch operation
    
    # Validation
    validation_result: Optional[Dict[str, Any]]  # Validation outcome
    updated_config: Optional[Dict[str, Any]]  # Config after patch
    
    # Output
    needs_confirmation: bool  # Whether user confirmation needed
    assistant_response: str  # Message to user
    error_message: Optional[str]  # Error details if any
    diff_preview: Optional[str]  # Human-readable change preview


def create_initial_state(
    domain_config: Dict[str, Any],
    user_message: str,
    chat_history: List[Dict[str, str]]
) -> AgentState:
    """
    Initialize state for graph execution.
    
    Args:
        domain_config: Current domain configuration JSON
        user_message: User's natural language request
        chat_history: Recent conversation messages
        
    Returns:
        Initial AgentState with all fields set
    """
    return {
        "current_config": domain_config,
        "user_message": user_message,
        "chat_history": chat_history,
        "intent": None,
        "target_entity": None,
        "proposed_patch": None,
        "validation_result": None,
        "updated_config": None,
        "needs_confirmation": False,
        "assistant_response": "",
        "error_message": None,
        "diff_preview": None
    }
