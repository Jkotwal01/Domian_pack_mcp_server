"""
LangGraph Workflow Assembly
Builds the complete workflow graph with nodes and edges
"""
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.langgraph.state import DomainPackState
from app.langgraph.nodes import (
    intent_detection_node,
    context_assembly_node,
    proposal_generation_node,
    human_checkpoint_node,
    mcp_router_node,
    commit_handler_node
)
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


def should_confirm(state: DomainPackState) -> str:
    """Determine if human confirmation is required"""
    # If no operations were generated (e.g., a greeting), go to END
    if not state.get("operations"):
        return END
        
    if state.get("requires_confirmation", True):
        return "human_checkpoint"
    return "mcp_router"  # Auto-approve (rare)


def confirmation_result(state: DomainPackState) -> str:
    """Route based on user confirmation"""
    if state.get("confirmed"):
        # If no operations (though unlikely if confirmed), skip to END
        if not state.get("operations"):
            return END
        return "mcp_router"
    elif state.get("questions"):
        # Need clarification - could loop back to proposal generation
        return "proposal_generation"
    else:
        return END  # Rejected


def mcp_result(state: DomainPackState) -> str:
    """Route based on MCP operation result"""
    if state.get("error"):
        return END  # Failed
    return "commit_handler"


async def build_workflow() -> StateGraph:
    """
    Build the complete LangGraph workflow
    
    Workflow:
    START → Intent Detection → Context Assembly → Proposal Generation 
         → [Confirmation Required?]
              → Yes → Human Checkpoint → [Confirmed?]
                   → Yes → MCP Router → Commit Handler → END
                   → No/Clarify → Proposal Generation (loop)
              → No → MCP Router → Commit Handler → END
    """
    logger.info("Building LangGraph workflow")
    
    # Create graph
    workflow = StateGraph(DomainPackState)
    
    # Add nodes
    workflow.add_node("intent_detection", intent_detection_node)
    workflow.add_node("context_assembly", context_assembly_node)
    workflow.add_node("proposal_generation", proposal_generation_node)
    workflow.add_node("human_checkpoint", human_checkpoint_node)
    workflow.add_node("mcp_router", mcp_router_node)
    workflow.add_node("commit_handler", commit_handler_node)
    
    # Set entry point
    workflow.set_entry_point("intent_detection")
    
    # Add edges
    workflow.add_edge("intent_detection", "context_assembly")
    workflow.add_edge("context_assembly", "proposal_generation")
    
    # Conditional edge: check if confirmation required
    workflow.add_conditional_edges(
        "proposal_generation",
        should_confirm,
        {
            "human_checkpoint": "human_checkpoint",
            "mcp_router": "mcp_router",
            END: END
        }
    )
    
    # Conditional edge: handle confirmation result
    workflow.add_conditional_edges(
        "human_checkpoint",
        confirmation_result,
        {
            "mcp_router": "mcp_router",
            "proposal_generation": "proposal_generation",
            END: END
        }
    )
    
    # Conditional edge: handle MCP result
    workflow.add_conditional_edges(
        "mcp_router",
        mcp_result,
        {
            "commit_handler": "commit_handler",
            END: END
        }
    )
    
    # Final edge
    workflow.add_edge("commit_handler", END)
    
    logger.info("Workflow built successfully")
    return workflow


# Global workflow resources
_workflow_app = None
_checkpointer_cm = None  # Context manager
_checkpointer = None     # Actual saver instance


async def init_workflow():
    """
    Initialize workflow and its checkpointer
    Should be called during application startup
    """
    global _workflow_app, _checkpointer, _checkpointer_cm
    
    if _workflow_app is not None:
        return _workflow_app
        
    logger.info("Initializing LangGraph workflow and checkpointer")
    
    # Build the graph
    workflow = await build_workflow()
    
    # Create PostgreSQL checkpointer
    conn_string = settings.ASYNC_SQLALCHEMY_DATABASE_URI.replace("postgresql+asyncpg://", "postgresql://")
    
    # We manually manage the context manager
    _checkpointer_cm = AsyncPostgresSaver.from_conn_string(conn_string)
    # Enter the context to get the actual saver instance
    _checkpointer = await _checkpointer_cm.__aenter__()
    
    # Ensure tables are created
    logger.info("Setting up LangGraph checkpointer tables")
    await _checkpointer.setup()
    
    # Compile with checkpointer
    _workflow_app = workflow.compile(checkpointer=_checkpointer)
    
    logger.info("Workflow initialized successfully")
    return _workflow_app


async def close_workflow():
    """
    Close workflow resources
    Should be called during application shutdown
    """
    global _workflow_app, _checkpointer, _checkpointer_cm
    
    if _checkpointer_cm:
        logger.info("Closing LangGraph checkpointer")
        await _checkpointer_cm.__aexit__(None, None, None)
        _checkpointer_cm = None
        _checkpointer = None
        _workflow_app = None


# Global workflow instance
_workflow_app = None


async def get_workflow():
    """Get workflow instance, initializing if necessary"""
    global _workflow_app
    if _workflow_app is None:
        await init_workflow()
    return _workflow_app
