
from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid

# --- Shared Models ---
class OperationItem(BaseModel):
    action: str
    path: List[str] = []
    value: Optional[Any] = None
    updates: Optional[Dict[str, Any]] = None
    strategy: Optional[str] = "append" # for merge
    equals: Optional[Any] = None # for assert
    exists: Optional[bool] = None # for assert

# --- Request Models ---
class CreateSessionRequest(BaseModel):
    file_type: str = "yaml" # yaml or json
    initial_content: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None

class ApplyOperationsRequest(BaseModel):
    operations: List[OperationItem]

# --- Response Models ---
class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    session_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    current_version: int
    file_type: str
    # metadata is reserved in SQLAlchemy, so we use metadata_ in the model.
    # We map 'metadata' in JSON to 'metadata_' attribute in ORM object.
    metadata: Optional[Dict[str, Any]] = Field(default=None, validation_alias="metadata_")

class VersionResponse(BaseModel):
    version: int
    content: Dict[str, Any]
    diff: Optional[Dict[str, Any]]
    reason: Optional[str]
    created_at: datetime

class VersionSummary(BaseModel):
    version: int
    reason: Optional[str]
    created_at: datetime
    change_keys: Optional[List[str]] = None

class ErrorResponse(BaseModel):
    detail: str
