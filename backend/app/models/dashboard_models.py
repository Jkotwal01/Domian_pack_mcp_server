"""
API Models for Dashboard Endpoints
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# ============================================================================
# Dashboard Models
# ============================================================================

class SessionSummary(BaseModel):
    """Summary of a session with metadata"""
    session_id: str = Field(..., description="Session UUID")
    domain_name: str = Field(..., description="Domain name extracted from content")
    current_version: int = Field(..., description="Latest version number")
    total_versions: int = Field(..., description="Total number of versions")
    file_type: str = Field(..., description="File type: 'yaml' or 'json'")
    created_at: datetime = Field(..., description="Session creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class AllSessionsResponse(BaseModel):
    """Response with all sessions summary"""
    sessions: List[SessionSummary] = Field(..., description="List of session summaries")
    total: int = Field(..., description="Total number of sessions")


class VersionSummary(BaseModel):
    """Summary of a version with domain info"""
    session_id: str = Field(..., description="Session UUID")
    domain_name: str = Field(..., description="Domain name")
    version: int = Field(..., description="Version number")
    semantic_version: str = Field(..., description="Semantic version from content (e.g., 1.0.0)")
    file_type: str = Field(..., description="File type")
    created_at: datetime = Field(..., description="Version creation timestamp")
    reason: str = Field(..., description="Reason for this version")


class AllVersionsResponse(BaseModel):
    """Response with all final versions across sessions"""
    versions: List[VersionSummary] = Field(..., description="List of all latest versions")
    total: int = Field(..., description="Total number of versions")


class VersionYAMLResponse(BaseModel):
    """Response with version content as YAML"""
    session_id: str = Field(..., description="Session UUID")
    version: int = Field(..., description="Version number")
    domain_name: str = Field(..., description="Domain name")
    yaml_content: str = Field(..., description="YAML formatted content")
    created_at: datetime = Field(..., description="Version creation timestamp")


class CompareVersionsRequest(BaseModel):
    """Request to compare two versions"""
    session_id_1: str = Field(..., description="First session UUID")
    version_1: int = Field(..., description="First version number")
    session_id_2: str = Field(..., description="Second session UUID")
    version_2: int = Field(..., description="Second version number")


class VersionDiff(BaseModel):
    """Diff information for a field"""
    field: str = Field(..., description="Field path")
    old_value: Optional[Any] = Field(None, description="Old value")
    new_value: Optional[Any] = Field(None, description="New value")
    change_type: str = Field(..., description="Type of change: 'added', 'removed', 'modified'")


class CompareVersionsResponse(BaseModel):
    """Response with version comparison"""
    session_1: str = Field(..., description="First session UUID")
    version_1: int = Field(..., description="First version number")
    domain_1: str = Field(..., description="First domain name")
    session_2: str = Field(..., description="Second session UUID")
    version_2: int = Field(..., description="Second version number")
    domain_2: str = Field(..., description="Second domain name")
    differences: List[VersionDiff] = Field(..., description="List of differences")
    yaml_diff: str = Field(..., description="YAML formatted diff")
    total_changes: int = Field(..., description="Total number of changes")
