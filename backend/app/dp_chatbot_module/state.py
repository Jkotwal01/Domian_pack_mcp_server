"""LangGraph state schema for domain configuration chatbot."""
from typing import TypedDict, Optional, Dict, Any, List, Annotated
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """State that flows through all LangGraph nodes."""
    
    # Input (Refactored to unified messages list)
    messages: Annotated[List[BaseMessage], add_messages]
    current_config: Dict[str, Any]  # Current domain config JSON
    
    # Processing
    intent: Optional[str]  # Detected operation intent
    target_entity: Optional[str]  # Target entity/relationship name
    proposed_patch: Optional[Dict[str, Any]]  # Generated patch operation
    node_call_logs: Optional[List[Dict[str, Any]]]  # Per-node LLM call metrics
    
    # Validation
    validation_result: Optional[Dict[str, Any]]  # Validation outcome
    updated_config: Optional[Dict[str, Any]]  # Config after patch
    
    # Output
    reasoning: Optional[str]  # Lightweight reasoning/plan
    needs_confirmation: bool  # Whether user confirmation needed
    assistant_response: str  # Message to user
    error_message: Optional[str]  # Error details if any


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
    # Convert dict history to Message objects
    messages = []
    for msg in chat_history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))
            
    # Add the current user message
    messages.append(HumanMessage(content=user_message))
    
    return {
        "messages": messages,
        "current_config": domain_config,
        "intent": None,
        "target_entity": None,
        "proposed_patch": None,
        "node_call_logs": [],
        "validation_result": None,
        "updated_config": None,
        "needs_confirmation": False,
        "assistant_response": "",
        "reasoning": None,
        "error_message": None
    }
