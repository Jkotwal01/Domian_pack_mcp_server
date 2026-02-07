"""
LangGraph State Definition
Defines the state schema for the domain pack authoring workflow
"""
from typing import TypedDict, Annotated, Optional, List, Dict, Any
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages


class DomainPackState(TypedDict):
    """
    State for domain pack authoring workflow.
    This schema defines the 'single source of truth' that flows through the LangGraph cycle.
    """
    
    # --- User Input (Initialization) ---
    user_message: str  # The primary text input from the user for the current turn
    user_id: str       # Internal ID of the requesting user (for auditing/permissions)
    session_id: str    # ID of the contemporary chat session
    domain_pack_id: str # ID of the specific domain pack being edited
    
    # --- Context (Knowledge & Environment) ---
    current_snapshot: Optional[Dict[str, Any]]  # The current YAML/JSON state of the domain pack
    base_template: Optional[Dict[str, Any]]     # The base template used for new packs
    schema: Optional[Dict[str, Any]]            # The domain-specific validation schema
    relevant_memories: Optional[List[Dict[str, Any]]] # Past user preferences or relevant context from RAG
    search_results: Optional[List[Dict[str, Any]]]    # Results from external tools or knowledge base search
    
    # --- Intent & Reasoning ---
    detected_intent: Optional[str]              # The high-level action identified (e.g., 'add_entity')
    extracted_entities: Optional[Dict[str, Any]] # Key parameters extracted (e.g., entity name: 'Patient')
    
    # --- Proposal (AI Generated Plan) ---
    proposal: Optional[Dict[str, Any]]          # Human-readable summary of the proposed changes
    operations: Optional[List[Dict[str, Any]]]  # Low-level technical instructions for the MCP server
    confidence: Optional[float]                  # AI's confidence in the proposal (0.0 to 1.0)
    questions: Optional[List[Dict[str, Any]]]   # Clarification questions for the user if intent is unclear
    
    # --- HITL (Human-in-the-Loop) ---
    requires_confirmation: bool                 # true if the workflow must pause for user approval
    user_response: Optional[str]                # Input gathered during an HITL pause
    confirmed: Optional[bool]                   # Final 'green light' from the user to apply changes
    
    # --- MCP & Commit Result ---
    mcp_response: Optional[Dict[str, Any]]      # Output from the pure transformation engine (updated YAML/diff)
    new_version_id: Optional[str]              # The ID of the committed version in the database
    error: Optional[str]                        # Blocking error message if any node fails
    
    # --- Conversation History ---
    messages: Annotated[List[BaseMessage], add_messages] # Persistent chat history with message auto-merging
