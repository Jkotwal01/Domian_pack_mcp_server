"""
LangGraph State Definition
Defines the state schema for the domain pack authoring workflow
"""
from typing import TypedDict, Annotated, Optional, List, Dict, Any
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages


class DomainPackState(TypedDict):
    """State for domain pack authoring workflow"""
    
    # User input
    user_message: str
    user_id: str
    session_id: str
    domain_pack_id: str
    
    # Context
    current_snapshot: Optional[Dict[str, Any]]
    base_template: Optional[Dict[str, Any]]
    schema: Optional[Dict[str, Any]]
    relevant_memories: Optional[List[Dict[str, Any]]]
    search_results: Optional[List[Dict[str, Any]]]
    
    # Intent & Reasoning
    detected_intent: Optional[str]
    extracted_entities: Optional[Dict[str, Any]]
    
    # Proposal
    proposal: Optional[Dict[str, Any]]
    operations: Optional[List[Dict[str, Any]]]
    confidence: Optional[float]
    questions: Optional[List[Dict[str, Any]]]
    
    # HITL
    requires_confirmation: bool
    user_response: Optional[str]
    confirmed: Optional[bool]
    
    # MCP & Commit
    mcp_response: Optional[Dict[str, Any]]
    new_version_id: Optional[str]
    error: Optional[str]
    
    # Messages (conversation history)
    messages: Annotated[List[BaseMessage], add_messages]
