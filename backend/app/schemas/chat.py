"""Chat schemas for chatbot interaction."""
from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.models.chat_session import SessionStatus
from app.models.chat_message import MessageRole


class ChatSessionCreate(BaseModel):
    """Schema for creating a chat session."""
    domain_config_id: UUID4


class ChatSessionResponse(BaseModel):
    """Schema for chat session response."""
    id: UUID4
    user_id: UUID4
    domain_config_id: UUID4
    status: SessionStatus
    created_at: datetime
    last_activity_at: datetime
    total_llm_calls: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    session_metadata: Dict[str, Any] = {}
    
    class Config:
        from_attributes = True


class ChatMessageCreate(BaseModel):
    """Schema for creating a chat message."""
    role: MessageRole
    message: str


class ChatMessageResponse(BaseModel):
    """Schema for chat message response."""
    id: UUID4
    session_id: UUID4
    role: MessageRole
    message: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    """Schema for chat message request."""
    message: str


class ChatResponse(BaseModel):
    """Schema for chat response."""
    message: str
    reasoning: Optional[str] = None
    needs_confirmation: bool = False
    proposed_changes: Optional[Dict[str, Any]] = None
    proposed_patch: Optional[Dict[str, Any]] = None # Align with state name
    diff_preview: Optional[str] = None
    updated_config: Optional[Dict[str, Any]] = None


class ChatSessionStats(BaseModel):
    """Schema for chat session LLM statistics."""
    total_llm_calls: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    
    class Config:
        from_attributes = True


class NodeCallLogResponse(BaseModel):
    """Schema for a single per-node LLM call log entry."""
    id: UUID4
    session_id: UUID4
    turn: int
    node_name: str
    input_tokens: int
    output_tokens: int
    response_time_ms: float
    intent: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
