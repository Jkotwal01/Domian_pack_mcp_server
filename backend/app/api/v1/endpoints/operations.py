"""
Operations Endpoints - Direct Operation Application

Handles direct operation application (bypassing LLM).
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
import logging

from app.models.api_models import (
    OperationRequest,
    OperationResponse,
    BatchOperationRequest,
    ToolsResponse
)
from app.services.streaming import streaming_service
from app.core import db, utils, schema, operations, version_manager

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/apply", response_model=OperationResponse)
async def apply_operation_endpoint(request: OperationRequest):
    """
    Apply an operation directly (bypass LLM).
    Follows the deterministic pipeline: load → validate → apply → bump → validate → diff → store
    """
    try:
        stream_id = f"{request.session_id}_op"
        
        await streaming_service.emit_status(stream_id, "Loading version...", 10)
        
        # Load latest version
        version_data = db.get_latest_version(request.session_id)
        content = version_data["content"]
        
        await streaming_service.emit_status(stream_id, "Parsing content...", 20)
        
        # Content is already parsed (stored as dict in DB)
        
        await streaming_service.emit_validation(stream_id, "Pre-operation validation...", 30)
        
        # Validate pre-operation
        schema.validate_domain_pack(content)
        
        await streaming_service.emit_status(stream_id, "Applying operation...", 50)
        
        # Apply operation
        operation_dict = request.operation.model_dump(exclude_none=True)
        new_content = operations.apply_operation(content, operation_dict)
        
        await streaming_service.emit_status(stream_id, "Bumping version...", 60)
        
        # Bump version
        version_manager.bump_version(new_content, "patch")
        
        await streaming_service.emit_validation(stream_id, "Post-operation validation...", 70)
        
        # Validate post-operation
        schema.validate_domain_pack(new_content)
        
        await streaming_service.emit_status(stream_id, "Calculating diff...", 85)
        
        # Calculate diff
        diff = utils.calculate_diff(content, new_content)
        
        await streaming_service.emit_diff(stream_id, "Diff calculated", diff, 90)
        
        await streaming_service.emit_status(stream_id, "Storing version...", 95)
        
        # Store new version
        new_version = db.insert_version(
            session_id=request.session_id,
            content=new_content,
            diff=diff,
            reason=request.reason
        )
        
        await streaming_service.emit_complete(
            stream_id,
            "Operation applied successfully",
            {"version": new_version}
        )
        
        return OperationResponse(
            version=new_version,
            diff=diff,
            message="Operation applied successfully"
        )
        
    except db.SessionNotFoundError:
        await streaming_service.emit_error(stream_id, "Session not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    except operations.OperationError as e:
        logger.error(f"Operation failed: {str(e)}")
        await streaming_service.emit_error(stream_id, str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Operation application failed: {str(e)}")
        await streaming_service.emit_error(stream_id, str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/stream/{operation_id}")
async def stream_operation_progress(operation_id: str):
    """
    SSE endpoint for streaming operation progress.
    """
    async def event_generator() -> AsyncGenerator[str, None]:
        async for event in streaming_service.stream_events(operation_id):
            yield event
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/batch", response_model=OperationResponse)
async def apply_batch_operations(request: BatchOperationRequest):
    """
    Apply multiple operations atomically.
    If any operation fails, all changes are rolled back.
    """
    try:
        stream_id = f"{request.session_id}_batch"
        
        await streaming_service.emit_status(stream_id, "Loading version...", 10)
        
        # Load latest version
        version_data = db.get_latest_version(request.session_id)
        content = version_data["content"]
        
        await streaming_service.emit_validation(stream_id, "Pre-operation validation...", 20)
        
        # Validate pre-operation
        schema.validate_domain_pack(content)
        
        await streaming_service.emit_status(stream_id, f"Applying {len(request.operations)} operations...", 40)
        
        # Apply batch operations
        operations_list = [op.model_dump(exclude_none=True) for op in request.operations]
        new_content = operations.apply_batch(content, operations_list)
        
        await streaming_service.emit_status(stream_id, "Bumping version...", 60)
        
        # Bump version
        version_manager.bump_version(new_content, "patch")
        
        await streaming_service.emit_validation(stream_id, "Post-operation validation...", 70)
        
        # Validate post-operation
        schema.validate_domain_pack(new_content)
        
        await streaming_service.emit_status(stream_id, "Calculating diff...", 85)
        
        # Calculate diff
        diff = utils.calculate_diff(content, new_content)
        
        await streaming_service.emit_status(stream_id, "Storing version...", 95)
        
        # Store new version
        new_version = db.insert_version(
            session_id=request.session_id,
            content=new_content,
            diff=diff,
            reason=request.reason
        )
        
        await streaming_service.emit_complete(
            stream_id,
            f"Batch of {len(request.operations)} operations applied successfully",
            {"version": new_version}
        )
        
        return OperationResponse(
            version=new_version,
            diff=diff,
            message=f"Batch of {len(request.operations)} operations applied successfully"
        )
        
    except db.SessionNotFoundError:
        await streaming_service.emit_error(stream_id, "Session not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    except operations.OperationError as e:
        logger.error(f"Batch operation failed: {str(e)}")
        await streaming_service.emit_error(stream_id, str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Batch operation failed: {str(e)}")
        await streaming_service.emit_error(stream_id, str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/tools", response_model=ToolsResponse)
async def get_available_tools():
    """
    Get list of available operation tools.
    """
    return ToolsResponse(
        tools=list(operations.OPERATIONS.keys())
    )
