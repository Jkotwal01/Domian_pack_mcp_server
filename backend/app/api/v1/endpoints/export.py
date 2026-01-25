"""
Export Endpoint - Domain Pack Export

Handles exporting domain packs in YAML or JSON format.
"""

from fastapi import APIRouter, HTTPException, status, Query
from fastapi.responses import Response
import logging

from app.models.api_models import ExportResponse
from app.core import db, utils

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/{session_id}", response_model=ExportResponse)
async def export_domain_pack(
    session_id: str,
    format: str = Query("yaml", description="Export format: 'yaml' or 'json'")
):
    """
    Export domain pack in YAML or JSON format.
    Returns the latest version by default.
    """
    try:
        # Validate format
        format = utils.validate_file_type(format)
        
        # Get latest version
        version_data = db.get_latest_version(session_id)
        content = version_data["content"]
        version_num = version_data["version"]
        
        # Serialize content
        serialized = utils.serialize_content(content, format)
        
        return ExportResponse(
            session_id=session_id,
            version=version_num,
            file_type=format,
            content=serialized
        )
        
    except db.SessionNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Export failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{session_id}/download")
async def download_domain_pack(
    session_id: str,
    format: str = Query("yaml", description="Export format: 'yaml' or 'json'")
):
    """
    Download domain pack as a file.
    """
    try:
        # Validate format
        format = utils.validate_file_type(format)
        
        # Get latest version
        version_data = db.get_latest_version(session_id)
        content = version_data["content"]
        
        # Serialize content
        serialized = utils.serialize_content(content, format)
        
        # Determine filename and media type
        filename = f"domain_pack.{format}"
        media_type = "application/x-yaml" if format == "yaml" else "application/json"
        
        return Response(
            content=serialized,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except db.SessionNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Download failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
