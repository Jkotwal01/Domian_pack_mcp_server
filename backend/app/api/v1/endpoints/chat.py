"""
Chat Endpoints - Natural Language Interface

Handles natural language intent extraction and confirmation.
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
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
from app.services.streaming import streaming_service
from app.core import db, utils, schema, operations, version_manager

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/intent", response_model=ChatIntentResponse)
async def extract_intent(request: ChatIntentRequest):
    """
    Extract structured operation from natural language.
    Returns proposed operation WITHOUT applying it.
    """
    try:
        # Load current schema from DB
        await streaming_service.emit_status(request.session_id, "Loading schema...", 10)
        
        version_data = db.get_latest_version(request.session_id)
        schema_content = version_data["content"]
        
        # Extract intent using LLM
        await streaming_service.emit_status(request.session_id, "Analyzing intent with LLM...", 30)
        
        # Define streaming callback
        async def llm_chunk_callback(chunk: str):
            await streaming_service.emit_llm_chunk(request.session_id, chunk, 50)
        
        intent_summary, operation = await llm_service.extract_intent(
            user_message=request.message,
            schema_definition=schema_content,
            stream_callback=llm_chunk_callback
        )
        
        # Validate operation structure
        await streaming_service.emit_status(request.session_id, "Validating operation...", 80)
        
        # Store pending intent
        intent_id = await intent_guard.store_intent(
            session_id=request.session_id,
            operation=operation,
            intent_summary=intent_summary
        )
        
        await streaming_service.emit_complete(
            request.session_id,
            "Intent extracted successfully",
            {"intent_id": intent_id, "intent_summary": intent_summary}
        )
        
        return ChatIntentResponse(
            intent_summary=intent_summary,
            operation=operation,
            intent_id=intent_id
        )
        
    except db.SessionNotFoundError:
        await streaming_service.emit_error(request.session_id, "Session not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    except Exception as e:
        logger.error(f"Intent extraction failed: {str(e)}")
        await streaming_service.emit_error(request.session_id, str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/intent/stream/{session_id}")
async def stream_intent_progress(session_id: str):
    """
    SSE endpoint for streaming intent extraction progress.
    Client should connect to this before calling POST /intent.
    """
    async def event_generator() -> AsyncGenerator[str, None]:
        async for event in streaming_service.stream_events(session_id):
            yield event
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


@router.post("/confirm", response_model=ChatConfirmResponse)
async def confirm_intent(request: ChatConfirmRequest):
    """
    Confirm and apply (or reject) a pending intent.
    """
    try:
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
        intent = await intent_guard.confirm_intent(request.intent_id)
        if not intent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Intent not found or expired"
            )
        
        # Apply operation (reuse operation application logic)
        await streaming_service.emit_status(request.session_id, "Loading version...", 10)
        
        # Load latest version
        version_data = db.get_latest_version(request.session_id)
        content = version_data["content"]
        file_type = db.get_session(request.session_id)["file_type"]
        
        await streaming_service.emit_validation(request.session_id, "Pre-operation validation...", 30)
        
        # Validate pre-operation
        schema.validate_domain_pack(content)
        
        await streaming_service.emit_status(request.session_id, "Applying operation...", 50)
        
        # Apply operation
        operation_dict = intent.operation.model_dump(exclude_none=True)
        new_content = operations.apply_operation(content, operation_dict)
        
        await streaming_service.emit_status(request.session_id, "Bumping version...", 60)
        
        # Bump version
        version_manager.bump_version(new_content, "patch")
        
        await streaming_service.emit_validation(request.session_id, "Post-operation validation...", 70)
        
        # Validate post-operation
        schema.validate_domain_pack(new_content)
        
        await streaming_service.emit_status(request.session_id, "Calculating diff...", 85)
        
        # Calculate diff
        diff = utils.calculate_diff(content, new_content)
        
        await streaming_service.emit_status(request.session_id, "Storing version...", 95)
        
        # Store new version
        new_version = db.insert_version(
            session_id=request.session_id,
            content=new_content,
            diff=diff,
            reason=intent.intent_summary
        )
        
        await streaming_service.emit_complete(
            request.session_id,
            "Operation applied successfully",
            {"version": new_version, "diff": diff}
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
