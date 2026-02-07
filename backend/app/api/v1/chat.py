"""
Chat/Conversation API Endpoints
Handles chat messages and LangGraph workflow invocation
"""
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from app.db.session import get_db
from app.api.v1.auth import get_current_user
from app.services.session_manager import SessionManager
from app.langgraph.workflow import get_workflow
from app.langgraph.state import DomainPackState
from app.schemas import (
    SessionCreate, SessionResponse, ChatRequest, ChatResponse
)
from langchain_core.messages import HumanMessage
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new conversation session"""
    session_manager = SessionManager(db)
    session = await session_manager.create_session(current_user.id, session_data)
    await db.commit()
    return session


@router.get("/sessions", response_model=List[SessionResponse])
async def list_sessions(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all active sessions for current user"""
    session_manager = SessionManager(db)
    sessions = await session_manager.get_active_sessions(current_user.id)
    return sessions


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get session details"""
    session_manager = SessionManager(db)
    session = await session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this session"
        )
    
    return session


@router.post("/sessions/{session_id}/messages", response_model=ChatResponse)
async def send_message(
    session_id: UUID,
    chat_request: ChatRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Send a message and invoke LangGraph workflow
    """
    # Verify session
    session_manager = SessionManager(db)
    session = await session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this session"
        )
    
    # Update session activity
    await session_manager.update_session_activity(session_id)
    await db.commit()
    
    # Get workflow
    workflow = await get_workflow()
    
    # Prepare initial state
    initial_state: DomainPackState = {
        "user_message": chat_request.message,
        "user_id": str(current_user.id),
        "session_id": str(session_id),
        "domain_pack_id": str(chat_request.domain_pack_id),
        "current_snapshot": None,
        "base_template": None,
        "schema": None,
        "relevant_memories": None,
        "search_results": None,
        "detected_intent": None,
        "extracted_entities": None,
        "proposal": None,
        "operations": None,
        "confidence": None,
        "questions": None,
        "requires_confirmation": False,
        "user_response": None,
        "confirmed": None,
        "mcp_response": None,
        "new_version_id": None,
        "error": None,
        "messages": [HumanMessage(content=chat_request.message)]
    }
    
    # Invoke workflow
    config = {
        "configurable": {
            "thread_id": str(session.thread_id)
        }
    }
    
    try:
        # Run workflow until human checkpoint or completion
        result = await workflow.ainvoke(initial_state, config)
        
        # Extract response
        last_message = result["messages"][-1].content if result.get("messages") else "Processing..."
        
        # Check if proposal was successfully created in DB (will have an id)
        proposal = result.get("proposal")
        if proposal and "id" not in proposal:
            proposal = None
            
        requires_confirmation = result.get("requires_confirmation", False)
        
        return ChatResponse(
            message=last_message,
            proposal=proposal,
            requires_confirmation=requires_confirmation
        )
    
    except Exception as e:
        logger.error(f"Error invoking workflow: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}"
        )


@router.websocket("/sessions/{session_id}/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: UUID
):
    """
    WebSocket endpoint for real-time chat updates
    """
    await websocket.accept()
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process message (simplified - would need auth via WS)
            response = {
                "type": "message",
                "content": f"Echo: {message_data.get('message')}"
            }
            
            await websocket.send_json(response)
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
