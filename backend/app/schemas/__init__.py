"""
Pydantic schemas for API requests and responses
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.db.models import (
    UserRole, ProposalStatus, MemoryType, MemoryScope, 
    MemorySource, EventType
)


# ============================================================================
# User Schemas
# ============================================================================

class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: UserRole = UserRole.EDITOR


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: UUID
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Authentication Schemas
# ============================================================================

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[UUID] = None
    email: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ============================================================================
# Session Schemas
# ============================================================================

class SessionCreate(BaseModel):
    domain_pack_id: Optional[UUID] = None
    metadata: Optional[Dict[str, Any]] = None


class SessionResponse(BaseModel):
    id: UUID
    user_id: UUID
    thread_id: UUID
    domain_pack_id: Optional[UUID] = None
    metadata: Optional[Dict[str, Any]] = Field(None, validation_alias="details")
    created_at: datetime
    last_activity: datetime
    ended_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Domain Pack Schemas
# ============================================================================

class DomainPackCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    base_template: Dict[str, Any]
    domain_schema: Dict[str, Any] = Field(..., alias="schema")


class DomainPackUpdate(BaseModel):
    description: Optional[str] = None


class DomainPackResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    current_version_id: Optional[UUID] = None
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class DomainPackDetail(DomainPackResponse):
    base_template: Dict[str, Any]
    domain_schema: Dict[str, Any] = Field(..., alias="schema")
    current_version: Optional["VersionResponse"] = None


# ============================================================================
# Version Schemas
# ============================================================================

class VersionResponse(BaseModel):
    id: UUID
    domain_pack_id: UUID
    version_number: int
    snapshot: Dict[str, Any]
    diff_from_previous: Optional[Dict[str, Any]] = None
    proposal_id: Optional[UUID] = None
    committed_by: UUID
    commit_message: Optional[str] = None
    is_rollback: bool
    rollback_of_version_id: Optional[UUID] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class VersionListResponse(BaseModel):
    id: UUID
    version_number: int
    committed_by: UUID
    commit_message: Optional[str] = None
    is_rollback: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class RollbackRequest(BaseModel):
    target_version_id: UUID
    reason: Optional[str] = None


# ============================================================================
# Proposal Schemas
# ============================================================================

class Operation(BaseModel):
    """Structured operation for domain pack changes"""
    op_type: str = Field(..., description="Operation type: add_field, remove_field, rename_field, etc.")
    target_path: str = Field(..., description="Dot-notation path to target")
    payload: Dict[str, Any] = Field(..., description="Operation-specific data")


class ProposalCreate(BaseModel):
    intent_summary: str
    operations: List[Operation]
    affected_paths: List[str]
    diff_preview: Optional[str] = None
    questions: Optional[List[Dict[str, Any]]] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    suggested_by: Optional[str] = None


class ProposalResponse(BaseModel):
    id: UUID
    session_id: UUID
    base_version_id: UUID
    intent_summary: str
    operations: List[Dict[str, Any]]
    affected_paths: List[str]
    diff_preview: Optional[str] = None
    questions: Optional[List[Dict[str, Any]]] = None
    confidence_score: Optional[float] = None
    suggested_by: Optional[str] = None
    status: ProposalStatus
    requires_confirmation: bool
    created_at: datetime
    expires_at: Optional[datetime] = None
    confirmed_by: Optional[UUID] = None
    confirmed_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class ProposalConfirmRequest(BaseModel):
    user_response: Optional[str] = None


class ProposalRejectRequest(BaseModel):
    reason: Optional[str] = None


class ProposalClarifyRequest(BaseModel):
    clarification: str
    

# ============================================================================
# Memory Schemas
# ============================================================================

class MemoryEntryCreate(BaseModel):
    type: MemoryType
    scope: MemoryScope
    summary: str
    details: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    source: MemorySource = MemorySource.USER_CONFIRMED


class MemoryEntryUpdate(BaseModel):
    summary: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    last_confirmed_at: Optional[datetime] = None


class MemoryEntryResponse(BaseModel):
    id: UUID
    user_id: UUID
    type: MemoryType
    scope: MemoryScope
    summary: str
    details: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = None
    last_confirmed_at: Optional[datetime] = None
    source: MemorySource
    created_at: datetime
    expires_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Audit Log Schemas
# ============================================================================

class AuditLogResponse(BaseModel):
    id: UUID
    event_type: EventType
    user_id: Optional[UUID] = None
    session_id: Optional[UUID] = None
    proposal_id: Optional[UUID] = None
    version_id: Optional[UUID] = None
    details: Dict[str, Any]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Chat/Message Schemas
# ============================================================================

class ChatMessage(BaseModel):
    role: str = Field(..., description="user or assistant")
    content: str


class ChatRequest(BaseModel):
    message: str
    domain_pack_id: UUID


class ChatResponse(BaseModel):
    message: str
    proposal: Optional[ProposalResponse] = None
    requires_confirmation: bool = False


# ============================================================================
# MCP Schemas
# ============================================================================

class MCPOperationRequest(BaseModel):
    current_yaml: Dict[str, Any]
    operations: List[Operation]


class MCPOperationResponse(BaseModel):
    success: bool
    updated_yaml: Optional[Dict[str, Any]] = None
    diff: Optional[Dict[str, Any]] = None
    errors: List[str] = []
    warnings: List[str] = []


# ============================================================================
# Pagination & Filters
# ============================================================================

class PaginationParams(BaseModel):
    skip: int = Field(0, ge=0)
    limit: int = Field(50, ge=1, le=100)


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    skip: int
    limit: int
    has_more: bool


# Forward references
DomainPackDetail.model_rebuild()
