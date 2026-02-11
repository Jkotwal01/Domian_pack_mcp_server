"""Main LangGraph definition for domain configuration chatbot."""
from langgraph.graph import StateGraph, END
from app.langgraph.state import DomainGraphState
from app.langgraph.nodes import (
    intent_detection_node,
    patch_generation_node,
    validation_node,
    confirmation_node,
    apply_patch_node,
    response_generation_node
)


def should_generate_patch(state: DomainGraphState) -> str:
    """Determine if patch generation is needed."""
    intent = state.get("intent", "")
    if intent in ["general_query", "confirmation_yes", "confirmation_no"]:
        return "skip_patch"
    return "generate_patch"


def should_apply_patch(state: DomainGraphState) -> str:
    """Determine if patch should be applied."""
    if state["intent"] == "confirmation_yes" and state.get("proposed_patch"):
        return "apply"
    return "skip"


def create_domain_graph() -> StateGraph:
    """
    Create the LangGraph for domain configuration chatbot.
    
    Flow:
    1. Intent Detection
    2. Patch Generation (if needed)
    3. Validation (if patch generated)
    4. Confirmation (if patch valid)
    5. Apply Patch (if confirmed)
    6. Response Generation
    
    Returns:
        Compiled StateGraph
    """
    # Create graph
    workflow = StateGraph(DomainGraphState)
    
    # Add nodes
    workflow.add_node("intent_detection", intent_detection_node)
    workflow.add_node("patch_generation", patch_generation_node)
    workflow.add_node("validation", validation_node)
    workflow.add_node("confirmation", confirmation_node)
    workflow.add_node("apply_patch", apply_patch_node)
    workflow.add_node("response_generation", response_generation_node)
    
    # Set entry point
    workflow.set_entry_point("intent_detection")
    
    # Add edges
    workflow.add_conditional_edges(
        "intent_detection",
        should_generate_patch,
        {
            "generate_patch": "patch_generation",
            "skip_patch": "response_generation"
        }
    )
    
    workflow.add_edge("patch_generation", "validation")
    workflow.add_edge("validation", "confirmation")
    
    workflow.add_conditional_edges(
        "confirmation",
        should_apply_patch,
        {
            "apply": "apply_patch",
            "skip": "response_generation"
        }
    )
    
    workflow.add_edge("apply_patch", "response_generation")
    workflow.add_edge("response_generation", END)
    
    # Compile graph
    return workflow.compile()


# Create singleton graph instance
domain_graph = create_domain_graph()
