"""Chat API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.database import get_db
from app.schemas.chat import (
    ChatSessionCreate,
    ChatSessionResponse,
    ChatMessageResponse,
    ChatRequest,
    ChatResponse
)
from app.services.chat_service import ChatService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: ChatSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create or get active chat session for a domain.
    
    Args:
        session_data: Session creation data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Chat session
    """
    session = ChatService.create_or_get_session(
        db,
        session_data.domain_config_id,
        current_user
    )
    return session


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a chat session by ID.
    
    Args:
        session_id: Session UUID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Chat session
    """
    session = ChatService.get_session(db, session_id, current_user)
    return session


@router.post("/sessions/{session_id}/message", response_model=ChatResponse)
async def send_message(
    session_id: UUID,
    message_data: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a message to the chatbot.
    
    Args:
        session_id: Session UUID
        message_data: User message
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Chat response from assistant
    """
    response = ChatService.send_message(db, session_id, message_data, current_user)
    return response


@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
async def get_messages(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50
):
    """
    Get messages for a session.
    
    Args:
        session_id: Session UUID
        current_user: Current authenticated user
        db: Database session
        limit: Maximum number of messages
        
    Returns:
        List of chat messages
    """
    messages = ChatService.get_messages(db, session_id, current_user, limit)
    return messages


@router.post("/sessions/{session_id}/close")
async def close_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Close a chat session.
    
    Args:
        session_id: Session UUID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success message
    """
    ChatService.close_session(db, session_id, current_user)
    return {"message": "Session closed successfully"}
