"""
Unified Sessions & Versions Endpoints

Consolidates session and version management into a single, organized endpoint file.
Uses OOP base classes for consistent error handling.
"""

from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form, Query
from typing import Optional
import logging
import jsonschema

from app.models.api_models import (
    SessionResponse,
    VersionListResponse,
    VersionListItem,
    VersionResponse
)
from app.api.base import SessionEndpoint, VersionEndpoint
from app.logic import utils, schema, operations

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize endpoint handlers
session_handler = SessionEndpoint()
version_handler = VersionEndpoint()


# ============================================================================
# Session Endpoints
# ============================================================================

@router.post("/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    file: Optional[UploadFile] = File(None),
    content: Optional[str] = Form(None),
    file_type: Optional[str] = Form(None)
):
    """
    Create a new domain pack session.
    Accepts either file upload or raw content.
    """
    @session_handler.handle_db_errors
    async def _create():
        # Get content from file or form
        if file:
            content_bytes = await file.read()
            content_str = content_bytes.decode('utf-8')
            detected_type = utils.detect_file_type(file.filename)
            
            if file_type and file_type.lower() not in ('string', 'none', ''):
                try:
                    final_file_type = utils.validate_file_type(file_type)
                except ValueError:
                    final_file_type = detected_type
            else:
                final_file_type = detected_type
        elif content:
            content_str = content
            if not file_type:
                raise ValueError("file_type required when providing raw content")
            final_file_type = utils.validate_file_type(file_type)
        else:
            raise ValueError("Either file or content must be provided")
        
        # Parse and validate content
        parsed_content = utils.parse_content(content_str, final_file_type)
        schema.validate_domain_pack(parsed_content)
        
        # Create session
        session_id = await session_handler.create_new_session(
            content=parsed_content,
            file_type=final_file_type,
            metadata=None
        )
        
        # Get session info
        session_info = await session_handler.get_session_info(session_id)
        
        return SessionResponse(
            session_id=session_id,
            version=session_info["current_version"],
            file_type=session_info["file_type"],
            created_at=session_info["created_at"],
            tools=list(operations.OPERATIONS.keys())
        )
    
    return await _create()


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """Get session information."""
    
    @session_handler.handle_db_errors
    async def _get():
        session_info = await session_handler.get_session_info(session_id)
        
        return SessionResponse(
            session_id=session_id,
            version=session_info["current_version"],
            file_type=session_info["file_type"],
            created_at=session_info["created_at"],
            tools=list(operations.OPERATIONS.keys())
        )
    
    return await _get()


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(session_id: str):
    """Delete a session and all its versions."""
    
    @session_handler.handle_db_errors
    async def _delete():
        await session_handler.remove_session(session_id)
    
    await _delete()


# ============================================================================
# Version Endpoints
# ============================================================================

@router.get("/sessions/{session_id}/versions", response_model=VersionListResponse)
async def list_versions(
    session_id: str,
    limit: int = Query(50, description="Maximum number of versions to return")
):
    """
    List all versions for a session.
    Returns version metadata without full content.
    """
    
    @version_handler.handle_db_errors
    async def _list():
        versions = await version_handler.get_version_list(session_id, limit=limit)
        
        version_items = [
            VersionListItem(
                version=v["version"],
                reason=v["reason"],
                created_at=v["created_at"],
                has_diff=v["diff"] is not None
            )
            for v in versions
        ]
        
        return VersionListResponse(
            session_id=session_id,
            versions=version_items,
            total=len(version_items)
        )
    
    return await _list()


@router.get("/sessions/{session_id}/versions/{version}", response_model=VersionResponse)
async def get_version(session_id: str, version: int):
    """Get a specific version with full content."""
    
    @version_handler.handle_db_errors
    async def _get():
        version_data = await version_handler.get_version_data(session_id, version)
        
        return VersionResponse(
            version=version_data["version"],
            content=version_data["content"],
            diff=version_data.get("diff"),
            reason=version_data["reason"],
            created_at=version_data["created_at"]
        )
    
    return await _get()


@router.get("/sessions/{session_id}/versions/latest", response_model=VersionResponse)
async def get_latest_version(session_id: str):
    """Get the latest version for a session."""
    
    @version_handler.handle_db_errors
    async def _get():
        version_data = await version_handler.get_latest_version(session_id)
        
        return VersionResponse(
            version=version_data["version"],
            content=version_data["content"],
            diff=version_data.get("diff"),
            reason=version_data["reason"],
            created_at=version_data["created_at"]
        )
    
    return await _get()


@router.delete("/sessions/{session_id}/versions/{version}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_version(session_id: str, version: int):
    """Delete a specific version."""
    
    @version_handler.handle_db_errors
    async def _delete():
        await version_handler.remove_version(session_id, version)
    
    await _delete()
