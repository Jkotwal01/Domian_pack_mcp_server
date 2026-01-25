"""
Sessions Endpoints - Session Management
Handles session creation, retrieval, and deletion.
"""

from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from typing import Optional
import logging
import jsonschema

from app.models.api_models import SessionCreateRequest, SessionResponse
from app.core import db, utils, schema, operations

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    file: Optional[UploadFile] = File(None),
    content: Optional[str] = Form(None),
    file_type: Optional[str] = Form(None)
):
    """
    Create a new domain pack session.
    Accepts either file upload or raw content.
    """
    try:
        # Get content from file or form
        if file:
            content_bytes = await file.read()
            content_str = content_bytes.decode('utf-8')
            # Detect file type from filename
            detected_type = utils.detect_file_type(file.filename)
            # Only use provided file_type if it's valid, otherwise use detected
            if file_type and file_type.lower() not in ('string', 'none', ''):
                try:
                    file_type = utils.validate_file_type(file_type)
                except ValueError:
                    file_type = detected_type
            else:
                file_type = detected_type
        elif content:
            content_str = content
            if not file_type:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="file_type required when providing raw content"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either file or content must be provided"
            )
        
        # Validate file type
        file_type = utils.validate_file_type(file_type)
        
        # Parse content
        parsed_content = utils.parse_content(content_str, file_type)
        
        # Validate schema
        schema.validate_domain_pack(parsed_content)
        
        # Create session
        session_id = db.create_session(
            initial_content=parsed_content,
            file_type=file_type,
            metadata=None
        )
        
        # Get session info
        session_info = db.get_session(session_id)
        
        return SessionResponse(
            session_id=session_id,
            version=session_info["current_version"],
            file_type=session_info["file_type"],
            created_at=session_info["created_at"],
            tools=list(operations.OPERATIONS.keys())
        )
        
    except utils.ParseError as e:
        logger.error(f"Parse error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Parse error: {str(e)}")
    except jsonschema.ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Validation error: {str(e)}")
    except Exception as e:
        logger.error(f"Session creation failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """
    Get session information.
    """
    try:
        session_info = db.get_session(session_id)
        
        return SessionResponse(
            session_id=session_id,
            version=session_info["current_version"],
            file_type=session_info["file_type"],
            created_at=session_info["created_at"],
            tools=list(operations.OPERATIONS.keys())
        )
        
    except db.SessionNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    except Exception as e:
        logger.error(f"Get session failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(session_id: str):
    """
    Delete a session and all its versions.
    """
    try:
        db.delete_session(session_id)
    except db.SessionNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    except Exception as e:
        logger.error(f"Delete session failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
