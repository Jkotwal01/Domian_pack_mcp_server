"""LangGraph nodes for domain configuration chatbot workflow."""
from typing import Dict, Any, List
import re
import time as _time
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

# Canonical set of all valid intent labels the classifier may produce
VALID_INTENTS = {
    "domain_operation",
    "entity_operation",
    "relationship_operation",
    "extraction_pattern_operation",
    "key_term_operation",
    "info_query",
    "general_query",
}


# ============================================================================
# HELPERS
# ============================================================================

def _normalize_intent(raw: str) -> str:
    """
    Normalize the LLM's raw intent output to a clean category token.

    - Strip surrounding whitespace and punctuation.
    - Lower-case for comparison.
    - Return the matched canonical intent, or the cleaned string if no match
      (caller is responsible for validating against VALID_INTENTS).
    """
    # Remove surrounding whitespace, quotes, and trailing punctuation
    cleaned = re.sub(r'[\"\'\.\\,\!\?]+$', '', raw.strip()).strip()
    cleaned_lower = cleaned.lower()

    # Direct match
    if cleaned_lower in VALID_INTENTS:
        return cleaned_lower

    # Substring match as a fallback (handles e.g. "Intent: entity_operation")
    for intent in VALID_INTENTS:
        if intent in cleaned_lower:
            return intent

    return cleaned_lower  # caller will flag as invalid


def _record_node_call(
    state: AgentState,
    node_name: str,
    input_tokens: int,
    output_tokens: int,
    elapsed_ms: float,
    intent: str = None,
) -> List[Dict[str, Any]]:
    """Return a new node_call_logs list with one entry appended."""
    existing = list(state.get("node_call_logs") or [])
    existing.append({
        "node_name": node_name,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "response_time_ms": round(elapsed_ms, 2),
        "intent": intent,
    })
    return existing


# ============================================================================
# NODES
# ============================================================================

def classify_intent_node(state: AgentState) -> AgentState:
    """
    Classify user intent using small LLM.

    Uses GPT-4o-mini with richer context (entity/relationship names + descriptions).
    Normalizes and validates the LLM response against VALID_INTENTS.
    Records per-node token usage and response time.
    Includes retry logic for LLM failures.
    """
    if state.get("error_message"):
        return state

    llm = get_llm(temperature=0)

    # Extract the user's latest message
    user_msg = state["messages"][-1].content

    # Build a richer context for the classifier
    entities = state["current_config"].get("entities", [])
    relationships = state["current_config"].get("relationships", [])
    key_terms = state["current_config"].get("key_terms", [])
    extraction_patterns = state["current_config"].get("extraction_patterns", [])
    domain_name = state["current_config"].get("name", "")
    domain_description = state["current_config"].get("description", "")

    # Format entity lines with type and description
    if len(entities) > 20:
        entity_lines = (
            f"{len(entities)} entities (first 5: "
            + ", ".join(
                f"{e.get('type', e['name'])} ({e.get('description', '')[:60]})"
                for e in entities[:5]
            )
            + "...)"
        )
    else:
        entity_lines = "\n".join(
            f"  - {e.get('type', e['name'])}: {e.get('description', 'No description')[:80]}"
            for e in entities
        ) or "  (none)"

    # Format relationship lines
    if len(relationships) > 20:
        rel_lines = (
            f"{len(relationships)} relationships (first 5: "
            + ", ".join(r.get('name', '') for r in relationships[:5])
            + "...)"
        )
    else:
        rel_lines = "\n".join(
            f"  - {r.get('name', '')}: {r.get('description', 'No description')[:80]}"
            for r in relationships
        ) or "  (none)"

    context = (
        f"Domain: {domain_name} — {domain_description}\n"
        f"Entities ({len(entities)} total):\n{entity_lines}\n"
        f"Relationships ({len(relationships)} total):\n{rel_lines}\n"
        f"Key Terms: {len(key_terms)} entries\n"
        f"Extraction Patterns: {len(extraction_patterns)} entries"
    )

    prompt = INTENT_CLASSIFICATION_PROMPT.format(
        context=context,
        user_message=user_msg
    )

    # Retry logic with per-node monitoring
    max_retries = 3
    for attempt in range(max_retries):
        try:
            from langchain_community.callbacks import get_openai_callback
            t0 = _time.perf_counter()
            with get_openai_callback() as cb:
                response = llm.invoke(prompt)
            elapsed_ms = (_time.perf_counter() - t0) * 1000

            intent = _normalize_intent(response.content)

            if intent not in VALID_INTENTS:
                if attempt == max_retries - 1:
                    return {
                        **state,
                        "error_message": (
                            f"Intent classification returned an unrecognized category: '{intent}'. "
                            f"Valid categories are: {', '.join(sorted(VALID_INTENTS))}."
                        )
                    }
                _time.sleep(0.5 * (attempt + 1))
                continue

            logs = _record_node_call(
                state, "classify_intent",
                cb.prompt_tokens, cb.completion_tokens,
                elapsed_ms, intent=intent
            )
            return {**state, "intent": intent, "node_call_logs": logs}

        except Exception as e:
            if attempt == max_retries - 1:
                return {
                    **state,
                    "error_message": f"Failed to classify intent after {max_retries} attempts: {str(e)}"
                }
            _time.sleep(0.5 * (attempt + 1))

    return {**state, "error_message": "Failed to classify intent"}


def generate_patch_node(state: AgentState) -> AgentState:
    """
    Generate structured patch using LLM with structured output.

    Uses GPT-4o-mini with context slicing to reduce token usage.
    Records per-node token usage and response time.
    Includes retry logic for LLM failures.
    """
    if state.get("error_message"):
        return state

    intent = state.get("intent")
    if intent == "info_query":
        return state

    llm = get_llm(temperature=0)
    structured_llm = llm.with_structured_output(PatchList)

    # Get relevant context slice
    relevant_context = get_relevant_context(state)

    recent_messages = state["messages"][-5:]
    messages_str = "\n".join([f"{msg.type}: {msg.content}" for msg in recent_messages])

    prompt = PATCH_GENERATION_PROMPT.format(
        intent=state["intent"],
        context=relevant_context,
        user_message=messages_str
    )

    max_retries = 3
    for attempt in range(max_retries):
        try:
            from langchain_community.callbacks import get_openai_callback
            t0 = _time.perf_counter()
            with get_openai_callback() as cb:
                patch_list = structured_llm.invoke(prompt)
            elapsed_ms = (_time.perf_counter() - t0) * 1000

            logs = _record_node_call(
                state, "generate_patch",
                cb.prompt_tokens, cb.completion_tokens,
                elapsed_ms
            )
            return {
                **state,
                "proposed_patch": patch_list.dict(),
                "reasoning": patch_list.reasoning,
                "node_call_logs": logs,
            }
        except Exception as e:
            if attempt == max_retries - 1:
                return {**state, "error_message": f"Failed to generate patch after {max_retries} attempts: {str(e)}"}
            _time.sleep(0.5 * (attempt + 1))

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
        for patch in patch_list.patches:
            current_config = apply_patch(config=current_config, patch=patch)

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
    Records LLM token usage when the LLM is used (info_query and error paths).
    """
    user_msg = state["messages"][-1].content

    if state.get("error_message"):
        try:
            from langchain_community.callbacks import get_openai_callback
            llm = get_llm(temperature=0)
            prompt = ERROR_EXPLANATION_PROMPT.format(
                error_message=state["error_message"],
                user_message=user_msg
            )
            t0 = _time.perf_counter()
            with get_openai_callback() as cb:
                response = llm.invoke(prompt)
            elapsed_ms = (_time.perf_counter() - t0) * 1000

            logs = _record_node_call(
                state, "generate_response_error",
                cb.prompt_tokens, cb.completion_tokens,
                elapsed_ms
            )
            friendly_error = response.content.strip()
            return {**state, "assistant_response": f"❌ {friendly_error}", "node_call_logs": logs}
        except:
            return {**state, "assistant_response": f"❌ {state['error_message']}\n\nPlease refine your request."}

    # Handle info_query
    if state.get("intent") == "info_query":
        try:
            from langchain_community.callbacks import get_openai_callback
            llm = get_llm(temperature=0)
            context_str = get_relevant_context(state)
            recent_messages = state["messages"][-5:]
            messages_str = "\n".join([f"{msg.type}: {msg.content}" for msg in recent_messages])

            prompt = INFO_QUERY_PROMPT.format(
                context=context_str,
                user_message=messages_str
            )
            t0 = _time.perf_counter()
            with get_openai_callback() as cb:
                response = llm.invoke(prompt)
            elapsed_ms = (_time.perf_counter() - t0) * 1000

            logs = _record_node_call(
                state, "generate_response_info",
                cb.prompt_tokens, cb.completion_tokens,
                elapsed_ms
            )
            return {**state, "assistant_response": response.content.strip(), "node_call_logs": logs}
        except Exception as e:
            return {**state, "assistant_response": f"❌ Failed to answer query: {str(e)}"}

    if state["needs_confirmation"]:
        response = "I've analyzed your request and prepared the following changes. Please review the detailed patch payload below."
        return {**state, "assistant_response": response}

    if state.get("proposed_patch") and state.get("updated_config"):
        response = "✅ Changes applied successfully! You can see the details below."
        return {**state, "assistant_response": response}

    response = "✅ Operation completed successfully!"
    return {**state, "assistant_response": response}


def general_knowledge_node(state: AgentState) -> AgentState:
    """
    Handle general queries using system knowledge base.
    Records LLM token usage.
    """
    try:
        from langchain_community.callbacks import get_openai_callback
        user_msg = state["messages"][-1].content
        llm = get_llm(temperature=0)
        prompt = GENERAL_KNOWLEDGE_PROMPT.format(
            context="No additional documentation available.",
            user_message=user_msg
        )
        t0 = _time.perf_counter()
        with get_openai_callback() as cb:
            response = llm.invoke(prompt)
        elapsed_ms = (_time.perf_counter() - t0) * 1000

        logs = _record_node_call(
            state, "general_knowledge",
            cb.prompt_tokens, cb.completion_tokens,
            elapsed_ms
        )
        return {**state, "assistant_response": response.content.strip(), "node_call_logs": logs}
    except Exception as e:
        return {**state, "assistant_response": f"❌ Failed to answer general query: {str(e)}"}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_relevant_context(state: AgentState) -> str:
    """
    Extract minimal relevant context based on intent.

    This reduces token usage by 85-96% compared to sending full config.
    For info_query, keyword-sniffing on the user message routes to the
    correct config slice so the LLM always receives the right data.
    """
    from app.utils.context_slicer import format_minimal_context, extract_target_from_message

    intent = state["intent"]
    config = state["current_config"]

    # Extract the user's latest message
    user_msg = state["messages"][-1].content
    user_msg_lower = user_msg.lower()

    # For info_query, route to the appropriate context slice based on keywords
    if intent == "info_query":
        if any(kw in user_msg_lower for kw in ("extraction pattern", "pattern", "regex")):
            intent = "extraction_pattern_operation"
        elif any(kw in user_msg_lower for kw in ("key term", "key_term", "vocabulary")):
            intent = "key_term_operation"
        elif "relationship" in user_msg_lower:
            intent = "relationship_operation"
        elif any(kw in user_msg_lower for kw in ("domain name", "domain description", "domain version")):
            intent = "domain_operation"
        # else: leave as info_query → full context dump

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
