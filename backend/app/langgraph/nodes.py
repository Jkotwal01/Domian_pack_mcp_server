"""
LangGraph Nodes Implementation
Individual nodes for the domain pack authoring workflow
"""
from typing import Dict, Any, List, Optional, Sequence
from uuid import UUID
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
import yaml

from app.langgraph.state import DomainPackState
from app.services.version_manager import VersionManager
from app.services.memory_store import MemoryStore
from app.services.proposal_manager import ProposalManager
from app.services.mcp_client import get_mcp_client
from app.schemas import Operation, ProposalCreate, MCPOperationResponse
from app.core.config import settings
from app.db.session import AsyncSessionLocal
import logging

logger = logging.getLogger(__name__)


# Structured output schemas for LLM
class IntentDetection(BaseModel):
    """Detected intent from user message"""
    intent: str = Field(description="Primary intent: add_field, remove_field, rename_field, add_entity, etc.")
    entities: Dict[str, Any] = Field(description="Extracted entities and parameters")
    confidence: float = Field(description="Confidence score 0-1")


class ProposalGeneration(BaseModel):
    """Generated proposal from LLM"""
    intent_summary: str = Field(description="Human-readable summary of the intent")
    operations: List[Dict[str, Any]] = Field(description="List of structured operations")
    affected_paths: List[str] = Field(description="Paths that will be affected")
    diff_preview: str = Field(description="Preview of changes")
    questions: List[Dict[str, Any]] = Field(default_factory=list, description="Clarification questions if needed")
    confidence: float = Field(description="Confidence score 0-1")
    requires_confirmation: bool = Field(description="Whether human confirmation is required")


def get_llm(temperature: float = 0.1):
    """Get initialized LLM based on settings"""
    return ChatOpenAI(
        model=settings.get_llm_model,
        api_key=settings.get_llm_api_key,
        base_url=settings.get_llm_base_url,
        temperature=temperature
    )


async def intent_detection_node(state: DomainPackState) -> Dict[str, Any]:
    """
    Detect user intent from message
    """
    logger.info("Running intent detection node")
    
    # Initialize LLM
    llm = get_llm(temperature=0.1)
    
    # Create structured output LLM
    # Specify function_calling for better compatibility with Groq/Llama
    structured_llm = llm.with_structured_output(IntentDetection, method="function_calling")
    
    # Build prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert at analyzing user requests for domain pack modifications.
        
Analyze the user's message and detect their intent. 

MODIFICATION INTENTS (return high confidence only if clear actions are requested):
- add_field: Adding a new field to an entity
- remove_field: Removing a field from an entity
- rename_field: Renaming a field
- change_type: Changing field type
- add_entity: Adding a new entity
- remove_entity: Removing an entity
- add_enum: Adding enum values
- add_relationship: Adding relationships between entities

NON-MODIFICATION INTENTS:
- greeting: Simple greeting like "hello", "hi"
- general_query: Questions about what you can do, "how can you help?", or general info
- clarification: User providing more info on a previous request

Extract relevant entities if it's a modification intent.
Provide a confidence score based on clarity of the request.
If the request is a simple question or greeting, use the non-modification intents.
"""),
        ("human", "{user_message}")
    ])
    
    # Invoke LLM
    chain = prompt | structured_llm
    result = await chain.ainvoke({"user_message": state["user_message"]})
    
    logger.info(f"Detected intent: {result.intent} (confidence: {result.confidence})")
    
    return {
        "detected_intent": result.intent,
        "extracted_entities": result.entities,
        "confidence": result.confidence,
        "messages": [AIMessage(content=f"Understood: {result.intent}")]
    }


async def context_assembly_node(state: DomainPackState) -> Dict[str, Any]:
    """
    Assemble context for proposal generation
    """
    logger.info("Running context assembly node")
    
    async with AsyncSessionLocal() as db:
        # Get current version snapshot
        version_manager = VersionManager(db)
        current_version = await version_manager.get_latest_version(UUID(state["domain_pack_id"]))
        
        current_snapshot = current_version.snapshot if current_version else {}
        
        # Get relevant memories
        memory_store = MemoryStore(db)
        memories = await memory_store.get_relevant_memories(
            user_id=UUID(state["user_id"]),
            context=state["user_message"],
            limit=5
        )
        
        relevant_memories = [
            {
                "summary": mem.summary,
                "details": mem.details,
                "type": mem.type.value
            }
            for mem in memories
        ]
        
        logger.info(f"Assembled context: snapshot keys={list(current_snapshot.keys())}, memories={len(relevant_memories)}")
        
        return {
            "current_snapshot": current_snapshot,
            "relevant_memories": relevant_memories
        }


async def proposal_generation_node(state: DomainPackState) -> Dict[str, Any]:
    """
    Generate structured proposal using LLM
    """
    logger.info("Running proposal generation node")
    
    # Initialize LLM
    llm = get_llm(temperature=0.2)
    
    # Specify function_calling for better compatibility with Groq/Llama
    structured_llm = llm.with_structured_output(ProposalGeneration, method="function_calling")
    
    # Build context
    context_parts = []
    
    if state.get("current_snapshot"):
        context_parts.append(f"Current domain pack structure:\n{state['current_snapshot']}")
    
    if state.get("relevant_memories"):
        memories_text = "\n".join([f"- {m['summary']}" for m in state["relevant_memories"]])
        context_parts.append(f"Relevant user preferences:\n{memories_text}")
    
    context = "\n\n".join(context_parts)
    
    # Build prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert domain pack architect. Generate a structured proposal for modifying the domain pack.

Your proposal must include:
1. intent_summary: Clear summary of what will be changed
2. operations: List of structured operations with:
   - op_type: Operation type (add_field, remove_field, etc.)
   - target_path: Dot-notation path (e.g., "entities.Patient.fields")
   - payload: Operation-specific data
3. affected_paths: List of all paths that will be modified
4. diff_preview: Human-readable preview of changes
5. questions: Any clarification questions needed
6. confidence: Your confidence in this proposal (0-1)
7. requires_confirmation: Whether human approval is needed

IMPORTANT RULES:
- For destructive operations (remove, delete), ALWAYS set requires_confirmation=true
- For bulk operations (>5 fields), ALWAYS set requires_confirmation=true
- If confidence < 0.7, ALWAYS set requires_confirmation=true
- If you need clarification, add questions and set requires_confirmation=true

Context:
{context}"""),
        ("human", "User request: {user_message}\nDetected intent: {intent}")
    ])
    
    # Invoke LLM
    chain = prompt | structured_llm
    result = await chain.ainvoke({
        "user_message": state["user_message"],
        "intent": state.get("detected_intent", "unknown"),
        "context": context
    })
    
    logger.info(f"Generated proposal: {result.intent_summary} (confidence: {result.confidence})")
    
    return {
        "proposal": result.model_dump(),
        "operations": result.operations,
        "confidence": result.confidence,
        "questions": result.questions,
        "requires_confirmation": result.requires_confirmation,
        "messages": [AIMessage(content=f"Proposal: {result.intent_summary}")]
    }


async def human_checkpoint_node(state: DomainPackState) -> Dict[str, Any]:
    """
    Pause for human confirmation (HITL)
    This node creates a proposal in the database and waits
    """
    logger.info("Running human checkpoint node - creating proposal")
    
    async with AsyncSessionLocal() as db:
        # Get current version
        version_manager = VersionManager(db)
        current_version = await version_manager.get_latest_version(UUID(state["domain_pack_id"]))
        
        if not current_version:
            return {"error": "No current version found"}
        
        # Create proposal
        proposal_manager = ProposalManager(db)
        
        operations = [
            Operation(**op) for op in state.get("operations", [])
        ]
        
        proposal_data = ProposalCreate(
            intent_summary=state["proposal"]["intent_summary"],
            operations=operations,
            affected_paths=state["proposal"]["affected_paths"],
            diff_preview=state["proposal"].get("diff_preview"),
            questions=state.get("questions"),
            confidence_score=state.get("confidence"),
            suggested_by=f"LangGraph-{settings.get_llm_model}"
        )
        
        proposal = await proposal_manager.create_proposal(
            session_id=UUID(state["session_id"]),
            base_version_id=current_version.id,
            proposal_data=proposal_data,
            user_id=UUID(state["user_id"])
        )
        
        await db.commit()
        
        logger.info(f"Created proposal {proposal.id} - waiting for confirmation")
        
        # This is where LangGraph would interrupt and wait
        # The actual confirmation happens via API endpoint
        return {
            "proposal": {
                **state["proposal"],
                "id": str(proposal.id)
            },
            "messages": [AIMessage(content="Proposal created. Awaiting your confirmation.")]
        }


async def mcp_router_node(state: DomainPackState) -> Dict[str, Any]:
    """
    Route operations to MCP server
    """
    logger.info("Running MCP router node")
    
    # Get MCP client
    mcp_client = await get_mcp_client()
    
    # Prepare operations
    operations = [Operation(**op) for op in state.get("operations", [])]
    
    if not operations:
        logger.info("No operations to apply. Skipping MCP router.")
        return {
            "mcp_response": MCPOperationResponse(
                success=True,
                updated_yaml=state.get("current_snapshot"),
                diff=None
            ).model_dump(),
            "messages": [AIMessage(content="No changes needed.")]
        }
    
    # Call MCP
    mcp_response = await mcp_client.apply_operations(
        current_yaml=state.get("current_snapshot", {}),
        operations=operations
    )
    
    # Handle if mcp_response returns a string for updated_yaml (yaml.dump output)
    if isinstance(mcp_response.updated_yaml, str):
        try:
            mcp_response.updated_yaml = yaml.safe_load(mcp_response.updated_yaml)
        except Exception:
            pass
    
    if not mcp_response.success:
        logger.error(f"MCP operation failed: {mcp_response.errors}")
        return {
            "error": f"MCP operation failed: {', '.join(mcp_response.errors)}",
            "mcp_response": mcp_response.model_dump()
        }
    
    logger.info("MCP operation successful")
    
    return {
        "mcp_response": mcp_response.model_dump(),
        "messages": [AIMessage(content="Changes applied successfully via MCP")]
    }


async def commit_handler_node(state: DomainPackState) -> Dict[str, Any]:
    """
    Commit changes to version store
    """
    logger.info("Running commit handler node")
    
    mcp_response = state.get("mcp_response")
    if not mcp_response or not mcp_response.get("updated_yaml"):
        return {"error": "No updated YAML from MCP"}
    
    async with AsyncSessionLocal() as db:
        # Create new version
        version_manager = VersionManager(db)
        
        proposal_id = state["proposal"].get("id")
        
        new_version = await version_manager.create_version(
            domain_pack_id=UUID(state["domain_pack_id"]),
            snapshot=mcp_response["updated_yaml"],
            committed_by=UUID(state["user_id"]),
            proposal_id=UUID(proposal_id) if proposal_id else None,
            commit_message=state["proposal"]["intent_summary"]
        )
        
        # Mark proposal as committed
        if proposal_id:
            proposal_manager = ProposalManager(db)
            await proposal_manager.mark_committed(
                proposal_id=UUID(proposal_id),
                version_id=new_version.id
            )
        
        await db.commit()
        
        logger.info(f"Created version {new_version.version_number}")
        
        return {
            "new_version_id": str(new_version.id),
            "messages": [AIMessage(content=f"Changes committed as version {new_version.version_number}")]
        }
