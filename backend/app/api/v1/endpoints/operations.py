"""
Operations Endpoints - Direct Operation Application

Handles direct operation application (bypassing LLM).
"""

from fastapi import APIRouter, HTTPException, status
import logging

from app.models.api_models import (
    OperationRequest,
    OperationResponse,
    BatchOperationRequest,
    ToolsResponse
)
from app.core import db, version_manager
from app.logic import utils, schema
from app.logic import operations

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/apply", response_model=OperationResponse)
async def apply_operation_endpoint(request: OperationRequest):
    """
    Apply an operation directly (bypass LLM).
    Follows the deterministic pipeline: load → validate → apply → bump → validate → diff → store
    """
    try:
        # Load latest version
        version_data = db.get_latest_version(request.session_id)
        content = version_data["content"]
        
        # Validate pre-operation
        schema.validate_domain_pack(content)
        
        # Apply operation
        operation_dict = request.operation.model_dump(exclude_none=True)
        new_content = operations.apply_operation(content, operation_dict)
        
        # Bump version
        version_manager.bump_version(new_content, "patch")
        
        # Validate post-operation
        schema.validate_domain_pack(new_content)
        
        # Calculate diff
        diff = utils.calculate_diff(content, new_content)
        
        # Store new version
        new_version = db.insert_version(
            session_id=request.session_id,
            content=new_content,
            diff=diff,
            reason=request.reason
        )
        
        return OperationResponse(
            version=new_version,
            diff=diff,
            message="Operation applied successfully"
        )
        
    except db.SessionNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    except operations.CRUDError as e:
        logger.error(f"Operation failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Operation application failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/batch", response_model=OperationResponse)
async def apply_batch_operations(request: BatchOperationRequest):
    """
    Apply multiple operations atomically.
    If any operation fails, all changes are rolled back.
    """
    try:
        # Load latest version
        version_data = db.get_latest_version(request.session_id)
        content = version_data["content"]
        
        # Validate pre-operation
        schema.validate_domain_pack(content)
        
        # Apply batch operations
        operations_list = [op.model_dump(exclude_none=True) for op in request.operations]
        new_content = operations.apply_batch(content, operations_list)
        
        # Bump version
        version_manager.bump_version(new_content, "patch")
        
        # Validate post-operation
        schema.validate_domain_pack(new_content)
        
        # Calculate diff
        diff = utils.calculate_diff(content, new_content)
        
        # Store new version
        new_version = db.insert_version(
            session_id=request.session_id,
            content=new_content,
            diff=diff,
            reason=request.reason
        )
        
        return OperationResponse(
            version=new_version,
            diff=diff,
            message=f"Batch of {len(request.operations)} operations applied successfully"
        )
        
    except db.SessionNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    except operations.CRUDError as e:
        logger.error(f"Batch operation failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Batch operation failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/tools", response_model=ToolsResponse)
async def get_available_tools():
    """
    Get list of available CRUD operation tools.
    Returns the 4 primitive operations: CREATE, READ, UPDATE, DELETE
    """
    return ToolsResponse(
        tools=["CREATE", "READ", "UPDATE", "DELETE"]
    )
