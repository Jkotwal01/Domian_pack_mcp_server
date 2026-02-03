"""
Export Endpoint - Domain Pack Export
Handles exporting domain packs in YAML or JSON format.
"""

from fastapi import APIRouter, HTTPException, status, Query
from fastapi.responses import Response
import logging

from app.models.api_models import ExportResponse
from app.core import db
from app.logic import utils

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
    Download domain pack as a file with dynamic filename.
    Filename format: DomainName_version.extension (e.g., Legal_1.0.5.yaml)
    """
    try:
        # Validate format
        format = utils.validate_file_type(format)
        
        # Get latest version
        version_data = db.get_latest_version(session_id)
        content = version_data["content"]
        
        # Extract domain name and version for filename
        domain_name = content.get("name", "domain_pack")
        version = content.get("version", "1.0.0")
        
        # Clean domain name for filename (replace spaces with underscores, remove special chars)
        clean_domain_name = domain_name.replace(" ", "_").replace("-", "_")
        # Remove any characters that aren't alphanumeric or underscore
        clean_domain_name = ''.join(c for c in clean_domain_name if c.isalnum() or c == '_')
        
        # Serialize content
        serialized = utils.serialize_content(content, format)
        
        # Generate dynamic filename: DomainName_version.extension
        filename = f"{clean_domain_name}_{version}.{format}"
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

