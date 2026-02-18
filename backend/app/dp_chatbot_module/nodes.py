"""LangGraph nodes for domain configuration chatbot workflow."""
from typing import Dict, Any
from app.dp_chatbot_module.state import AgentState
from app.utils.llm_factory import get_llm
from app.dp_chatbot_module.prompts import (
    INTENT_CLASSIFICATION_PROMPT,
    PATCH_GENERATION_PROMPT,
    ERROR_EXPLANATION_PROMPT,
    INFO_QUERY_PROMPT,
    GENERAL_KNOWLEDGE_PROMPT
)
from app.schemas.patch import PatchOperation, PatchList
from app.utils.patch_applier import apply_patch
from app.services.validation_service import ValidationService
import json


def classify_intent_node(state: AgentState) -> AgentState:
    """
    Classify user intent using small LLM.
    
    Uses GPT-4o-mini with minimal context (just entity/relationship names).
    Includes retry logic for LLM failures.
    """
    if state.get("error_message"):
        return state
        
    llm = get_llm(temperature=0)
    
    # Extract the user's latest message
    user_msg = state["messages"][-1].content
    
    # Limit context size for classification
    entities = state["current_config"].get("entities", [])
    relationships = state["current_config"].get("relationships", [])
    
    if len(entities) > 20:
        entity_context = f"{len(entities)} entities (including: {', '.join([e['name'] for e in entities[:5]])}...)"
    else:
        entity_context = f"Entities: {', '.join([e['name'] for e in entities])}"
        
    if len(relationships) > 20:
        rel_context = f"{len(relationships)} relationships (including: {', '.join([r['name'] for r in relationships[:5]])}...)"
    else:
        rel_context = f"Relationships: {', '.join([r['name'] for r in relationships])}"
    
    context = f"{entity_context}\n{rel_context}"
    
    prompt = INTENT_CLASSIFICATION_PROMPT.format(
        context=context,
        user_message=user_msg
    )
    
    # Retry logic
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = llm.invoke(prompt)
            intent = response.content.strip()
            return {**state, "intent": intent}
        except Exception as e:
            if attempt == max_retries - 1:
                return {**state, "error_message": f"Failed to classify intent after {max_retries} attempts: {str(e)}"}
            # Wait briefly before retry
            import time
            time.sleep(0.5 * (attempt + 1))
    
    return {**state, "error_message": "Failed to classify intent"}


def generate_patch_node(state: AgentState) -> AgentState:
    """
    Generate structured patch using LLM with structured output.
    
    Uses GPT-4o-mini with context slicing to reduce token usage.
    Includes retry logic for LLM failures.
    """
    if state.get("error_message"):
        return state
    
    intent = state.get("intent")
    if intent == "info_query":
        # Skip patch generation for queries
        return state
        
    llm = get_llm(temperature=0)
    structured_llm = llm.with_structured_output(PatchList)
    
    # Get relevant context slice
    relevant_context = get_relevant_context(state)
    
    # Implement recent 5 messages logic for CoT/Generation
    # LangGraph standard: messages[-1] is current HumanMessage
    # messages[-5:] gives the most recent window
    recent_messages = state["messages"][-5:]
    messages_str = "\n".join([f"{msg.type}: {msg.content}" for msg in recent_messages])
    
    prompt = PATCH_GENERATION_PROMPT.format(
        intent=state["intent"],
        context=relevant_context,
        user_message=messages_str # Use the contextual window for CoT
    )
    
    # Retry logic
    max_retries = 3
    for attempt in range(max_retries):
        try:
            patch_list = structured_llm.invoke(prompt)
            # Store in state
            return {
                **state, 
                "proposed_patch": patch_list.dict(),
                "reasoning": patch_list.reasoning
            }
        except Exception as e:
            if attempt == max_retries - 1:
                return {**state, "error_message": f"Failed to generate patch after {max_retries} attempts: {str(e)}"}
            # Wait briefly before retry
            import time
            time.sleep(0.5 * (attempt + 1))
    
    return {**state, "error_message": "Failed to generate patch"}


def apply_patch_node(state: AgentState) -> AgentState:
    """
    Apply patch to config using pure Python (no LLM).
    """
    if state.get("error_message") or state.get("intent") == "info_query":
        return state
    
    try:
        patch_list_data = state["proposed_patch"]
        patch_list = PatchList(**patch_list_data)
        
        current_config = state["current_config"]
        # Apply each patch sequentially
        for patch in patch_list.patches:
            current_config = apply_patch(
                config=current_config,
                patch=patch
            )
            
        return {**state, "updated_config": current_config}
    except ValueError as e:
        return {**state, "error_message": str(e)}
    except Exception as e:
        return {**state, "error_message": f"Unexpected error applying patch: {str(e)}"}


def validate_patch_node(state: AgentState) -> AgentState:
    """
    Validate updated config using Pydantic schemas.
    """
    if state.get("error_message") or state.get("intent") == "info_query":
        return state
    
    try:
        validation_result = ValidationService.validate_domain_config(state["updated_config"])
        
        if not validation_result["valid"]:
            error_msg = "Validation failed:\n" + "\n".join(validation_result["errors"])
            return {
                **state,
                "error_message": error_msg,
                "validation_result": validation_result
            }
        
        return {**state, "validation_result": validation_result}
    except Exception as e:
        return {**state, "error_message": f"Validation error: {str(e)}"}


def prepare_confirmation_node(state: AgentState) -> AgentState:
    """
    Check if patches were generated and set confirmation flag.
    """
    if state.get("error_message") or state.get("intent") == "info_query":
        return state
    
    try:
        patch_list_data = state["proposed_patch"]
        has_patches = patch_list_data and patch_list_data.get("patches")
        
        return {
            **state,
            "needs_confirmation": True if has_patches else False,
            "assistant_response": "Everything is already up to date!" if not has_patches else state.get("assistant_response", "")
        }
    except Exception as e:
        return {**state, "error_message": f"Failed to prepare confirmation: {str(e)}"}


def generate_response_node(state: AgentState) -> AgentState:
    """
    Generate final assistant response.
    """
    user_msg = state["messages"][-1].content
    
    if state.get("error_message"):
        # Use LLM to explain error in friendly way
        try:
            llm = get_llm(temperature=0)
            prompt = ERROR_EXPLANATION_PROMPT.format(
                error_message=state["error_message"],
                user_message=user_msg
            )
            response = llm.invoke(prompt)
            friendly_error = response.content.strip()
            return {**state, "assistant_response": f"❌ {friendly_error}"}
        except:
            # Fallback to raw error
            return {**state, "assistant_response": f"❌ {state['error_message']}\n\nPlease refine your request."}
    
    # Handle info_query
    if state.get("intent") == "info_query":
        try:
            llm = get_llm(temperature=0)
            
            # Use context slicer to get minimal relevant info
            context_str = get_relevant_context(state)
            
            # Use recent window for context
            recent_messages = state["messages"][-5:]
            messages_str = "\n".join([f"{msg.type}: {msg.content}" for msg in recent_messages])
                
            prompt = INFO_QUERY_PROMPT.format(
                context=context_str,
                user_message=messages_str
            )
            response = llm.invoke(prompt)
            return {**state, "assistant_response": response.content.strip()}
        except Exception as e:
            return {**state, "assistant_response": f"❌ Failed to answer query: {str(e)}"}
    
    if state["needs_confirmation"]:
        response = "I've analyzed your request and prepared the following changes. Please review the detailed patch payload below."
        return {**state, "assistant_response": response}
    
    # Check if there was a patch that was automatically applied
    if state.get("proposed_patch") and state.get("updated_config"):
        response = "✅ Changes applied successfully! You can see the details below."
        return {**state, "assistant_response": response}
    
    # Should not reach here in normal flow
    response = "✅ Operation completed successfully!"
    return {**state, "assistant_response": response}


def general_knowledge_node(state: AgentState) -> AgentState:
    """
    Handle general queries using system knowledge base.
    """
    try:
        import os
        kb_path = os.path.join(os.path.dirname(__file__), "knowledge_base.md")
        kb_content = ""
        if os.path.exists(kb_path):
            with open(kb_path, "r", encoding="utf-8") as f:
                kb_content = f.read()
        
        user_msg = state["messages"][-1].content
        llm = get_llm(temperature=0)
        prompt = GENERAL_KNOWLEDGE_PROMPT.format(
            context=kb_content or "No additional documentation available.",
            user_message=user_msg
        )
        response = llm.invoke(prompt)
        return {**state, "assistant_response": response.content.strip()}
    except Exception as e:
        return {**state, "assistant_response": f"❌ Failed to answer general query: {str(e)}"}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_relevant_context(state: AgentState) -> str:
    """
    Extract minimal relevant context based on intent.
    
    This reduces token usage by 85-96% compared to sending full config.
    """
    from app.utils.context_slicer import format_minimal_context, extract_target_from_message
    
    intent = state["intent"]
    config = state["current_config"]
    
    # Extract the user's latest message
    user_msg = state["messages"][-1].content
    
    # Try to extract target name from user message
    target_name = extract_target_from_message(user_msg, config)
    
    # Use context slicer to get minimal context
    return format_minimal_context(config, intent, target_name)


def extract_target_name(user_message: str, config: Dict[str, Any]) -> str:
    """
    Extract target entity/relationship name from user message.
    
    Simple heuristic: look for entity/relationship names in the message.
    """
    user_message_lower = user_message.lower()
    
    # Check entities
    for entity in config.get("entities", []):
        if entity["name"].lower() in user_message_lower:
            return entity["name"]
    
    # Check relationships
    for rel in config.get("relationships", []):
        if rel["name"].lower() in user_message_lower:
            return rel["name"]
    
    return ""
