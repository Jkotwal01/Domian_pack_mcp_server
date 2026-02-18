"""LangGraph nodes for domain configuration chatbot workflow."""
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from app.dp_chatbot_module.state import AgentState
from app.dp_chatbot_module.prompts import (
    INTENT_CLASSIFICATION_PROMPT,
    PATCH_GENERATION_PROMPT,
    ERROR_EXPLANATION_PROMPT
)
from app.schemas.patch import PatchOperation
from app.utils.patch_applier import apply_patch
from app.services.validation_service import ValidationService
import json


def classify_intent_node(state: AgentState) -> AgentState:
    """
    Classify user intent using small LLM.
    
    Uses GPT-3.5-turbo with minimal context (just entity/relationship names).
    Includes retry logic for LLM failures.
    """
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    
    # Minimal context: just entity/relationship names
    entity_names = [e["name"] for e in state["current_config"].get("entities", [])]
    rel_names = [r["name"] for r in state["current_config"].get("relationships", [])]
    
    context = f"Entities: {', '.join(entity_names)}\nRelationships: {', '.join(rel_names)}"
    
    prompt = INTENT_CLASSIFICATION_PROMPT.format(
        context=context,
        user_message=state["user_message"]
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
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    structured_llm = llm.with_structured_output(PatchOperation)
    
    # Get relevant context slice
    relevant_context = get_relevant_context(state)
    
    prompt = PATCH_GENERATION_PROMPT.format(
        intent=state["intent"],
        context=relevant_context,
        user_message=state["user_message"]
    )
    
    # Retry logic
    max_retries = 3
    for attempt in range(max_retries):
        try:
            patch = structured_llm.invoke(prompt)
            return {**state, "proposed_patch": patch.dict()}
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
    if state.get("error_message"):
        return state
    
    try:
        patch = PatchOperation(**state["proposed_patch"])
        updated_config = apply_patch(
            config=state["current_config"],
            patch=patch
        )
        return {**state, "updated_config": updated_config}
    except ValueError as e:
        return {**state, "error_message": str(e)}
    except Exception as e:
        return {**state, "error_message": f"Unexpected error applying patch: {str(e)}"}


def validate_patch_node(state: AgentState) -> AgentState:
    """
    Validate updated config using Pydantic schemas.
    """
    if state.get("error_message"):
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
    Generate diff preview for user confirmation.
    """
    if state.get("error_message"):
        return state
    
    try:
        diff = generate_diff(
            old_config=state["current_config"],
            new_config=state["updated_config"],
            patch=state["proposed_patch"]
        )
        
        return {
            **state,
            "needs_confirmation": True,
            "diff_preview": diff
        }
    except Exception as e:
        return {**state, "error_message": f"Failed to generate diff: {str(e)}"}


def generate_response_node(state: AgentState) -> AgentState:
    """
    Generate final assistant response.
    """
    if state.get("error_message"):
        # Use LLM to explain error in friendly way
        try:
            llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
            prompt = ERROR_EXPLANATION_PROMPT.format(
                error_message=state["error_message"],
                user_message=state["user_message"]
            )
            response = llm.invoke(prompt)
            friendly_error = response.content.strip()
            return {**state, "assistant_response": f"❌ {friendly_error}"}
        except:
            # Fallback to raw error
            return {**state, "assistant_response": f"❌ {state['error_message']}\n\nPlease refine your request."}
    
    if state["needs_confirmation"]:
        response = f"{state['diff_preview']}\n\nDo you want to apply these changes? (yes/no)"
        return {**state, "assistant_response": response}
    
    # Should not reach here in normal flow
    response = "✅ Changes applied successfully!"
    return {**state, "assistant_response": response}


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
    user_message = state["user_message"]
    
    # Try to extract target name from user message
    target_name = extract_target_from_message(user_message, config)
    
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


def generate_diff(old_config: Dict[str, Any], new_config: Dict[str, Any], patch: Dict[str, Any]) -> str:
    """
    Create human-readable diff preview.
    """
    operation = patch.get("type") or patch.get("operation")
    
    # Domain-level operations
    if operation == "update_domain_name":
        return f"~ Change domain name to '{patch['new_value']}'"
    elif operation == "update_domain_description":
        return f"~ Update domain description to '{patch['new_value']}'"
    elif operation == "update_domain_version":
        return f"~ Update version to '{patch['new_value']}'"
    
    # Entity operations
    elif operation == "add_entity":
        return f"+ Add entity '{patch['payload']['name']}'"
    elif operation == "update_entity_name":
        return f"~ Rename entity '{patch['target_name']}' to '{patch['new_value']}'"
    elif operation == "update_entity_type":
        return f"~ Change type of '{patch['target_name']}' to '{patch['new_value']}'"
    elif operation == "update_entity_description":
        return f"~ Update description of '{patch['target_name']}'"
    elif operation == "delete_entity":
        return f"- Delete entity '{patch['target_name']}'"
    
    # Entity attribute operations
    elif operation == "add_entity_attribute":
        return f"+ Add attribute '{patch['payload']['name']}' to {patch['parent_name']}"
    elif operation == "update_entity_attribute_name":
        return f"~ Rename attribute '{patch['attribute_name']}' to '{patch['new_value']}' in {patch['parent_name']}"
    elif operation == "update_entity_attribute_description":
        return f"~ Update description of {patch['parent_name']}.{patch['attribute_name']}"
    elif operation == "delete_entity_attribute":
        return f"- Remove attribute '{patch['attribute_name']}' from {patch['parent_name']}"
    
    # Entity attribute examples
    elif operation == "add_entity_attribute_example":
        return f"+ Add example '{patch['new_value']}' to {patch['parent_name']}.{patch['attribute_name']}"
    elif operation == "update_entity_attribute_example":
        return f"~ Change example '{patch['old_value']}' to '{patch['new_value']}' in {patch['parent_name']}.{patch['attribute_name']}"
    elif operation == "delete_entity_attribute_example":
        return f"- Remove example '{patch['old_value']}' from {patch['parent_name']}.{patch['attribute_name']}"
    
    # Entity synonyms
    elif operation == "add_entity_synonym":
        return f"+ Add synonym '{patch['new_value']}' to {patch['parent_name']}"
    elif operation == "update_entity_synonym":
        return f"~ Change synonym '{patch['old_value']}' to '{patch['new_value']}' in {patch['parent_name']}"
    elif operation == "delete_entity_synonym":
        return f"- Remove synonym '{patch['old_value']}' from {patch['parent_name']}"
    
    # Relationship operations
    elif operation == "add_relationship":
        return f"+ Add relationship '{patch['payload']['name']}' from {patch['payload']['from']} to {patch['payload']['to']}"
    elif operation == "update_relationship_name":
        return f"~ Rename relationship '{patch['target_name']}' to '{patch['new_value']}'"
    elif operation == "update_relationship_from":
        return f"~ Change source of '{patch['target_name']}' to '{patch['new_value']}'"
    elif operation == "update_relationship_to":
        return f"~ Change target of '{patch['target_name']}' to '{patch['new_value']}'"
    elif operation == "update_relationship_description":
        return f"~ Update description of relationship '{patch['target_name']}'"
    elif operation == "delete_relationship":
        return f"- Delete relationship '{patch['target_name']}'"
    
    # Relationship attributes (similar to entity attributes)
    elif operation == "add_relationship_attribute":
        return f"+ Add attribute '{patch['payload']['name']}' to relationship {patch['parent_name']}"
    elif operation == "update_relationship_attribute_name":
        return f"~ Rename attribute '{patch['attribute_name']}' to '{patch['new_value']}' in relationship {patch['parent_name']}"
    elif operation == "update_relationship_attribute_description":
        return f"~ Update description of {patch['parent_name']}.{patch['attribute_name']}"
    elif operation == "delete_relationship_attribute":
        return f"- Remove attribute '{patch['attribute_name']}' from relationship {patch['parent_name']}"
    
    # Relationship attribute examples
    elif operation == "add_relationship_attribute_example":
        return f"+ Add example '{patch['new_value']}' to {patch['parent_name']}.{patch['attribute_name']}"
    elif operation == "update_relationship_attribute_example":
        return f"~ Change example '{patch['old_value']}' to '{patch['new_value']}' in {patch['parent_name']}.{patch['attribute_name']}"
    elif operation == "delete_relationship_attribute_example":
        return f"- Remove example '{patch['old_value']}' from {patch['parent_name']}.{patch['attribute_name']}"
    
    # Extraction patterns
    elif operation == "add_extraction_pattern":
        return f"+ Add extraction pattern for {patch['payload']['entity_type']}.{patch['payload']['attribute']}"
    elif operation.startswith("update_extraction_pattern"):
        field = operation.replace("update_extraction_pattern_", "")
        return f"~ Update extraction pattern {field} to '{patch['new_value']}'"
    elif operation == "delete_extraction_pattern":
        return f"- Delete extraction pattern #{patch['target_name']}"
    
    # Key terms
    elif operation == "add_key_term":
        return f"+ Add key term '{patch['new_value']}'"
    elif operation == "update_key_term":
        return f"~ Change key term '{patch['old_value']}' to '{patch['new_value']}'"
    elif operation == "delete_key_term":
        return f"- Remove key term '{patch['old_value']}'"
    
    # Fallback
    return f"~ Apply {operation}"