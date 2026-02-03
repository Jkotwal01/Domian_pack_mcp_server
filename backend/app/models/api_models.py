"""
API Models (Pydantic DTOs) for Domain Pack Backend

All request/response models for the FastAPI endpoints.
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Dict, Any, List, Optional
from datetime import datetime


# ============================================================================
# Session Models
# ============================================================================

class SessionCreateRequest(BaseModel):
    """Request to create a new session"""
    content: str = Field(..., description="Domain pack content (YAML or JSON string)")
    file_type: str = Field(..., description="File type: 'yaml' or 'json'")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")


class SessionResponse(BaseModel):
    """Response with session information"""
    session_id: str = Field(..., description="Session UUID")
    version: int = Field(..., description="Current version number")
    file_type: str = Field(..., description="File type: 'yaml' or 'json'")
    created_at: datetime = Field(..., description="Session creation timestamp")
    tools: List[str] = Field(..., description="Available operation tools")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "version": 1,
                "file_type": "yaml",
                "created_at": "2024-01-25T10:30:00Z",
                "tools": ["add", "replace", "delete", "update", "merge", "add_unique", "batch", "assert"]
            }
        }


# ============================================================================
# Chat/Intent Models
# ============================================================================

class ChatIntentRequest(BaseModel):
    """Request to extract intent from natural language"""
    session_id: str = Field(..., description="Session UUID")
    message: str = Field(..., description="Natural language message from user")


class OperationSpec(BaseModel):
    """Structured operation specification for CRUD operations"""
    # Support both 'op' (new CRUD format) and 'action' (legacy) - at least one required
    op: Optional[str] = Field(None, description="CRUD operation: CREATE, READ, UPDATE, or DELETE")
    action: Optional[str] = Field(None, description="Legacy operation action (deprecated, use 'op')")
    
    path: List[str] = Field(..., description="Path in domain pack structure as list of strings")
    value: Optional[Any] = Field(None, description="Value for CREATE and UPDATE operations")
    
    # Legacy fields (kept for backward compatibility)
    updates: Optional[Dict[str, Any]] = Field(None, description="Legacy: not used in CRUD operations")
    strategy: Optional[str] = Field(None, description="Legacy: not used in CRUD operations")
    equals: Optional[Any] = Field(None, description="Legacy: not used in CRUD operations")
    exists: Optional[bool] = Field(None, description="Legacy: not used in CRUD operations")
    
    @model_validator(mode='after')
    def validate_op_or_action(self):
        """Ensure at least one of 'op' or 'action' is provided"""
        if not self.op and not self.action:
            raise ValueError("Either 'op' or 'action' field must be provided")
        
        # If action is provided but not op, copy action to op
        if self.action and not self.op:
            self.op = self.action
        
        # If op is provided but not action, copy op to action for backward compatibility
        if self.op and not self.action:
            self.action = self.op
        
        return self


class ChatIntentResponse(BaseModel):
    """Response with extracted intent (not yet applied) or suggestion"""
    type: str = Field(..., description="'suggestion' or 'operation'")
    message: str = Field(..., description="LLM response message or intent summary")
    operations: Optional[List[OperationSpec]] = Field(None, description="List of structured operations to be applied if type is 'operation'")
    intent_id: Optional[str] = Field(None, description="Intent ID for confirmation (if type is 'operation')")


class ChatConfirmRequest(BaseModel):
    """Request to confirm and apply an intent"""
    session_id: str = Field(..., description="Session UUID")
    intent_id: str = Field(..., description="Intent ID to confirm")
    approved: bool = Field(..., description="Whether to approve and apply the operation")


class ChatConfirmResponse(BaseModel):
    """Response after confirming operation"""
    approved: bool = Field(..., description="Whether operation was approved")
    version: Optional[int] = Field(None, description="New version number (if approved)")
    diff: Optional[Dict[str, Any]] = Field(None, description="Diff from previous version")
    message: str = Field(..., description="Result message")


# ============================================================================
# Operation Models
# ============================================================================

class OperationRequest(BaseModel):
    """Request to apply an operation directly"""
    session_id: str = Field(..., description="Session UUID")
    operation: OperationSpec = Field(..., description="Operation to apply")
    reason: Optional[str] = Field("Direct operation", description="Reason for the change")


class OperationResponse(BaseModel):
    """Response after applying operation"""
    version: int = Field(..., description="New version number")
    diff: Dict[str, Any] = Field(..., description="Diff from previous version")
    message: str = Field(..., description="Success message")


class BatchOperationRequest(BaseModel):
    """Request to apply multiple operations atomically"""
    session_id: str = Field(..., description="Session UUID")
    operations: List[OperationSpec] = Field(..., description="List of operations to apply")
    reason: Optional[str] = Field("Batch operation", description="Reason for the changes")


class ToolsResponse(BaseModel):
    """Response with available operation tools"""
    tools: List[str] = Field(..., description="List of available operation types")
    
    class Config:
        json_schema_extra = {
            "example": {
                "tools": ["add", "replace", "delete", "update", "merge", "add_unique", "batch", "assert"]
            }
        }


# ============================================================================
# Version Models
# ============================================================================

class VersionResponse(BaseModel):
    """Response with version information"""
    version: int = Field(..., description="Version number")
    content: Dict[str, Any] = Field(..., description="Domain pack content at this version")
    diff: Optional[Dict[str, Any]] = Field(None, description="Diff from previous version")
    reason: str = Field(..., description="Reason for this version")
    created_at: datetime = Field(..., description="Version creation timestamp")


class VersionListItem(BaseModel):
    """Version metadata (without full content)"""
    version: int = Field(..., description="Version number")
    reason: str = Field(..., description="Reason for this version")
    created_at: datetime = Field(..., description="Version creation timestamp")
    has_diff: bool = Field(..., description="Whether diff is available")


class VersionListResponse(BaseModel):
    """Response with list of versions"""
    session_id: str = Field(..., description="Session UUID")
    versions: List[VersionListItem] = Field(..., description="List of version metadata")
    total: int = Field(..., description="Total number of versions")


# ============================================================================
# Rollback Models
# ============================================================================

class RollbackRequest(BaseModel):
    """Request to rollback to a previous version"""
    session_id: str = Field(..., description="Session UUID")
    target_version: int = Field(..., description="Version number to rollback to")


class RollbackResponse(BaseModel):
    """Response after rollback"""
    new_version: int = Field(..., description="New version number (rollback creates new version)")
    rolled_back_to: int = Field(..., description="Version that was rolled back to")
    diff: Dict[str, Any] = Field(..., description="Diff showing rollback changes")
    message: str = Field(..., description="Success message")


# ============================================================================
# Export Models
# ============================================================================

class ExportResponse(BaseModel):
    """Response with exported content"""
    session_id: str = Field(..., description="Session UUID")
    version: int = Field(..., description="Version number")
    file_type: str = Field(..., description="Export format: 'yaml' or 'json'")
    content: str = Field(..., description="Serialized domain pack content")


# ============================================================================
# Error Models
# ============================================================================

class ErrorResponse(BaseModel):
    """Error response"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
