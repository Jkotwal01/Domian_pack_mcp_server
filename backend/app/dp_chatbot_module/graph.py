"""LangGraph workflow for domain configuration chatbot."""
from langgraph.graph import StateGraph, END
from app.dp_chatbot_module.state import AgentState
from app.dp_chatbot_module.nodes import (
    classify_intent_node,
    generate_patch_node,
    apply_patch_node,
    validate_patch_node,
    prepare_confirmation_node,
    generate_response_node
)


def route_after_validation(state: AgentState) -> str:
    """
    Conditional routing after validation.
    
    If there's an error, go directly to response generation.
    Otherwise, prepare confirmation.
    """
    if state.get("error_message"):
        return "generate_response"
    return "prepare_confirmation"


# Build the workflow graph
workflow = StateGraph(AgentState)

# Add all nodes
workflow.add_node("classify_intent", classify_intent_node)
workflow.add_node("generate_patch", generate_patch_node)
workflow.add_node("apply_patch", apply_patch_node)
workflow.add_node("validate", validate_patch_node)
workflow.add_node("prepare_confirmation", prepare_confirmation_node)
workflow.add_node("generate_response", generate_response_node)

# Define the flow
workflow.set_entry_point("classify_intent")
workflow.add_edge("classify_intent", "generate_patch")
workflow.add_edge("generate_patch", "apply_patch")
workflow.add_edge("apply_patch", "validate")

# Conditional routing after validation
workflow.add_conditional_edges(
    "validate",
    route_after_validation,
    {
        "generate_response": "generate_response",
        "prepare_confirmation": "prepare_confirmation"
    }
)

workflow.add_edge("prepare_confirmation", "generate_response")
workflow.add_edge("generate_response", END)

# Compile the graph
domain_graph = workflow.compile()
