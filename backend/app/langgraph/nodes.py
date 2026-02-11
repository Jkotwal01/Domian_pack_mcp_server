"""LangGraph nodes for domain configuration chatbot."""
from typing import Dict, Any
import json
import jsonpatch
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from app.langgraph.state import DomainGraphState
from app.langgraph.prompts import (
    INTENT_DETECTION_PROMPT,
    PATCH_GENERATION_PROMPT,
    CONFIRMATION_PROMPT,
    RESPONSE_GENERATION_PROMPT,
    GENERAL_QUERY_PROMPT
)
from app.config import settings
from app.utils.llm_monitor import llm_monitor

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7,
    openai_api_key=settings.OPENAI_API_KEY
)


def intent_detection_node(state: DomainGraphState) -> DomainGraphState:
    """
    Detect user intent from message.
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with detected intent
    """
    state["reasoning_steps"].append("Analyzing user intent...")
    
    # Check if awaiting confirmation
    if state.get("awaiting_confirmation"):
        user_msg_lower = state["user_message"].lower().strip()
        if user_msg_lower in ["yes", "y", "confirm", "ok", "proceed", "sure"]:
            state["intent"] = "confirmation_yes"
            state["reasoning_steps"].append("User confirmed the change")
            return state
        elif user_msg_lower in ["no", "n", "cancel", "stop", "nope"]:
            state["intent"] = "confirmation_no"
            state["reasoning_steps"].append("User rejected the change")
            return state
    
    # Prepare context
    entity_list = ", ".join([e["name"] for e in state["domain_config"].get("entities", [])])
    relationship_list = ", ".join([r["name"] for r in state["domain_config"].get("relationships", [])])
    
    chat_history = "\n".join([
        f"{msg['role']}: {msg['message']}" 
        for msg in state["messages"][-5:]  # Last 5 messages
    ])
    
    # Create prompt
    prompt = INTENT_DETECTION_PROMPT.format(
        domain_name=state["domain_config"].get("name", "Unknown"),
        domain_description=state["domain_config"].get("description", ""),
        entity_list=entity_list or "None",
        relationship_list=relationship_list or "None",
        user_message=state["user_message"],
        chat_history=chat_history or "No previous conversation"
    )
    
    # Call LLM with monitoring
    messages = [SystemMessage(content=prompt)]
    with llm_monitor.track_call("intent_detection"):
        response = llm.invoke(messages)
    intent = response.content.strip().lower()
    
    state["intent"] = intent
    state["reasoning_steps"].append(f"Detected intent: {intent}")
    
    return state


def patch_generation_node(state: DomainGraphState) -> DomainGraphState:
    """
    Generate JSONPatch for the requested change.
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with proposed patch
    """
    intent = state["intent"]
    
    # Skip patch generation for queries and confirmations
    if intent in ["general_query", "confirmation_yes", "confirmation_no"]:
        return state
    
    state["reasoning_steps"].append("Generating patch for the change...")
    
    # Create prompt
    prompt = PATCH_GENERATION_PROMPT.format(
        intent=intent,
        user_message=state["user_message"],
        domain_config=json.dumps(state["domain_config"], indent=2)
    )
    
    # Call LLM with monitoring
    messages = [SystemMessage(content=prompt)]
    with llm_monitor.track_call("patch_generation"):
        response = llm.invoke(messages)
    
    try:
        # Parse JSONPatch
        patch_json = response.content.strip()
        # Remove markdown code blocks if present
        if patch_json.startswith("```"):
            patch_json = patch_json.split("```")[1]
            if patch_json.startswith("json"):
                patch_json = patch_json[4:]
        patch_json = patch_json.strip()
        
        proposed_patch = json.loads(patch_json)
        state["proposed_patch"] = proposed_patch
        state["reasoning_steps"].append(f"Generated patch: {len(proposed_patch)} operations")
    except json.JSONDecodeError as e:
        state["error"] = f"Failed to parse patch: {str(e)}"
        state["reasoning_steps"].append(f"Error parsing patch: {str(e)}")
    
    return state


def validation_node(state: DomainGraphState) -> DomainGraphState:
    """
    Validate the proposed patch.
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with validation results
    """
    if state.get("error") or not state.get("proposed_patch"):
        return state
    
    state["reasoning_steps"].append("Validating proposed changes...")
    
    try:
        # Apply patch to a copy
        config_copy = json.loads(json.dumps(state["domain_config"]))
        patch = jsonpatch.JsonPatch(state["proposed_patch"])
        updated_config = patch.apply(config_copy)
        
        # Basic validation (more comprehensive validation would go here)
        if "entities" not in updated_config:
            raise ValueError("Patch removed entities array")
        if "relationships" not in updated_config:
            raise ValueError("Patch removed relationships array")
        
        state["reasoning_steps"].append("Validation passed")
    except Exception as e:
        state["error"] = f"Validation failed: {str(e)}"
        state["reasoning_steps"].append(f"Validation error: {str(e)}")
    
    return state


def confirmation_node(state: DomainGraphState) -> DomainGraphState:
    """
    Generate confirmation message for user.
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with confirmation message
    """
    intent = state["intent"]
    
    # Skip confirmation for queries
    if intent in ["general_query", "confirmation_yes", "confirmation_no"]:
        return state
    
    if state.get("error"):
        return state
    
    state["reasoning_steps"].append("Generating confirmation message...")
    
    # Create prompt
    prompt = CONFIRMATION_PROMPT.format(
        intent=intent,
        proposed_patch=json.dumps(state.get("proposed_patch", []), indent=2)
    )
    
    # Call LLM with monitoring
    messages = [SystemMessage(content=prompt)]
    with llm_monitor.track_call("confirmation_generation"):
        response = llm.invoke(messages)
    
    state["confirmation_message"] = response.content.strip()
    state["needs_confirmation"] = True
    state["reasoning_steps"].append("Confirmation message generated")
    
    return state


def apply_patch_node(state: DomainGraphState) -> DomainGraphState:
    """
    Apply the patch to domain configuration.
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with applied changes
    """
    if state["intent"] != "confirmation_yes":
        return state
    
    if not state.get("proposed_patch"):
        state["error"] = "No patch to apply"
        return state
    
    state["reasoning_steps"].append("Applying changes to domain configuration...")
    
    try:
        # Apply patch
        config_copy = json.loads(json.dumps(state["domain_config"]))
        patch = jsonpatch.JsonPatch(state["proposed_patch"])
        updated_config = patch.apply(config_copy)
        
        state["updated_config"] = updated_config
        state["reasoning_steps"].append("Changes applied successfully")
    except Exception as e:
        state["error"] = f"Failed to apply patch: {str(e)}"
        state["reasoning_steps"].append(f"Error applying patch: {str(e)}")
    
    return state


def response_generation_node(state: DomainGraphState) -> DomainGraphState:
    """
    Generate final response to user.
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with assistant response
    """
    state["reasoning_steps"].append("Generating response...")
    
    intent = state["intent"]
    
    # Handle errors
    if state.get("error"):
        state["assistant_response"] = f"I encountered an error: {state['error']}. Please try rephrasing your request."
        return state
    
    # Handle confirmation needed
    if state.get("needs_confirmation") and intent not in ["confirmation_yes", "confirmation_no"]:
        state["assistant_response"] = state.get("confirmation_message", "")
        state["awaiting_confirmation"] = True
        return state
    
    # Handle confirmation responses
    if intent == "confirmation_yes":
        if state.get("updated_config"):
            state["assistant_response"] = "Great! I've applied the changes to your domain configuration."
        else:
            state["assistant_response"] = "Changes confirmed, but there was an issue applying them. Please try again."
        return state
    
    if intent == "confirmation_no":
        state["assistant_response"] = "No problem! The changes have been cancelled. What else would you like to do?"
        state["awaiting_confirmation"] = False
        return state
    
    # Handle general queries
    if intent == "general_query":
        entity_list = ", ".join([e["name"] for e in state["domain_config"].get("entities", [])])
        relationship_list = ", ".join([r["name"] for r in state["domain_config"].get("relationships", [])])
        
        prompt = GENERAL_QUERY_PROMPT.format(
            domain_name=state["domain_config"].get("name", "Unknown"),
            domain_description=state["domain_config"].get("description", ""),
            entity_list=entity_list or "None",
            relationship_list=relationship_list or "None",
            pattern_count=len(state["domain_config"].get("extraction_patterns", [])),
            term_count=len(state["domain_config"].get("key_terms", [])),
            user_message=state["user_message"]
        )
        
        messages = [SystemMessage(content=prompt)]
        with llm_monitor.track_call("general_query"):
            response = llm.invoke(messages)
        state["assistant_response"] = response.content.strip()
        return state
    
    # Default response
    context = f"Intent: {intent}\nReasoning: {', '.join(state['reasoning_steps'])}"
    prompt = RESPONSE_GENERATION_PROMPT.format(
        intent=intent,
        user_message=state["user_message"],
        context=context
    )
    
    messages = [SystemMessage(content=prompt)]
    with llm_monitor.track_call("response_generation"):
        response = llm.invoke(messages)
    state["assistant_response"] = response.content.strip()
    
    return state
