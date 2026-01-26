"""
Chat Endpoints - Natural Language Interface

Handles natural language intent extraction and confirmation.
"""

from fastapi import APIRouter, HTTPException, status
import logging

from app.models.api_models import (
    ChatIntentRequest,
    ChatIntentResponse,
    ChatConfirmRequest,
    ChatConfirmResponse,
    OperationSpec
)
from app.services.llm_intent import llm_service
from app.services.intent_guard import intent_guard
from app.core import db, utils, schema, operations, version_manager

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/intent", response_model=ChatIntentResponse)
async def extract_intent(request: ChatIntentRequest):
    """
    Extract structured operation from natural language.
    Returns proposed operation WITHOUT applying it.
    """
    # Sanitize inputs
    request.session_id = request.session_id.strip()
    request.message = request.message.strip()
    try:
        # Load current schema from DB
        version_data = db.get_latest_version(request.session_id)
        schema_content = version_data["content"]
        
        # Extract intent using LLM (without streaming callback)
        intent_info = await llm_service.extract_intent(
            user_message=request.message,
            schema_definition=schema_content
        )
        
        resp_type = intent_info["type"]
        message = intent_info["message"]
        operations_list = intent_info.get("operations")
        
        intent_id = None
        if resp_type == "operation" and operations_list:
            # Store pending intent only for operations
            intent_id = await intent_guard.store_intent(
                session_id=request.session_id,
                operations=operations_list,
                intent_summary=message
            )
        
        return ChatIntentResponse(
            type=resp_type,
            message=message,
            operations=operations_list,
            intent_id=intent_id
        )
        
    except db.SessionNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    except Exception as e:
        logger.error(f"Intent extraction failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/confirm", response_model=ChatConfirmResponse)
async def confirm_intent(request: ChatConfirmRequest):
    """
    Confirm and apply (or reject) a pending intent.
    """
    # Sanitize inputs
    request.session_id = request.session_id.strip()
    request.intent_id = request.intent_id.strip()
    
    try:
        logger.info(f"Confirming intent: '{request.intent_id}' for session: '{request.session_id}'")
        if not request.approved:
            # Reject intent
            rejected = await intent_guard.reject_intent(request.intent_id)
            if not rejected:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Intent not found or expired"
                )
            
            return ChatConfirmResponse(
                approved=False,
                message="Intent rejected"
            )
        
        # Retrieve and confirm intent
        intent = await intent_guard.confirm_intent(request.intent_id, request.session_id)
        if not intent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Intent not found or expired"
            )
        
        # Load latest version
        version_data = db.get_latest_version(request.session_id)
        content = version_data["content"]
        file_type = db.get_session(request.session_id)["file_type"]
        
        # Validate pre-operation
        schema.validate_domain_pack(content)
        
        # Ensure proper structure before applying operations
        content = utils.initialize_domain_pack(content)
        
        # Apply operations as a batch
        operations_list = [op.model_dump(exclude_none=True) for op in intent.operations]
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
            reason=intent.intent_summary
        )
        
        return ChatConfirmResponse(
            approved=True,
            version=new_version,
            diff=diff,
            message="Operation applied successfully"
        )
        
    except db.SessionNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    except operations.OperationError as e:
        logger.error(f"Operation failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Confirmation failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
