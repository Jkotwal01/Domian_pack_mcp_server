"""
Rollback Endpoint - Version Rollback

Handles rollback to previous versions (creates new version, never deletes).
"""

from fastapi import APIRouter, HTTPException, status
import logging

from app.models.api_models import RollbackRequest, RollbackResponse
from app.core import db, utils, schema

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=RollbackResponse)
async def rollback_version(request: RollbackRequest):
    """
    Rollback to a previous version.
    Creates a NEW version with the content from the target version.
    Never deletes versions - maintains full audit trail.
    """
    try:
        # Get target version
        target_version_data = db.get_version(request.session_id, request.target_version)
        target_content = target_version_data["content"]
        
        # Get current version for diff
        current_version_data = db.get_latest_version(request.session_id)
        current_content = current_version_data["content"]
        
        # Validate target content (should already be valid, but double-check)
        schema.validate_domain_pack(target_content)
        
        # Calculate diff (showing what changed in the rollback)
        diff = utils.calculate_diff(current_content, target_content)
        
        # Create new version with rolled-back content
        new_version = db.insert_version(
            session_id=request.session_id,
            content=target_content,
            diff=diff,
            reason=f"Rollback to version {request.target_version}"
        )
        
        return RollbackResponse(
            new_version=new_version,
            rolled_back_to=request.target_version,
            diff=diff,
            message=f"Successfully rolled back to version {request.target_version}"
        )
        
    except db.SessionNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    except db.VersionNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Version {request.target_version} not found")
    except Exception as e:
        logger.error(f"Rollback failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
