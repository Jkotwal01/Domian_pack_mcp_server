"""
Versions Endpoints - Version Management

Handles version listing and retrieval.
"""

from fastapi import APIRouter, HTTPException, status, Query
import logging

from app.models.api_models import VersionResponse, VersionListResponse, VersionListItem
from app.core import db

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/{session_id}", response_model=VersionListResponse)
async def list_versions(
    session_id: str,
    limit: int = Query(50, description="Maximum number of versions to return")
):
    """
    List all versions for a session.
    Returns version metadata without full content.
    """
    try:
        versions = db.list_versions(session_id, limit=limit)
        
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
        
    except db.SessionNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    except Exception as e:
        logger.error(f"List versions failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{session_id}/{version}", response_model=VersionResponse)
async def get_version(session_id: str, version: int):
    """
    Get a specific version with full content.
    """
    try:
        version_data = db.get_version(session_id, version)
        
        return VersionResponse(
            version=version_data["version"],
            content=version_data["content"],
            diff=version_data.get("diff"),
            reason=version_data["reason"],
            created_at=version_data["created_at"]
        )
        
    except db.SessionNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    except db.VersionNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Version {version} not found")
    except Exception as e:
        logger.error(f"Get version failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
