"""
Proposal API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from app.db.session import get_db
from app.api.v1.auth import get_current_user
from app.services.proposal_manager import ProposalManager
from app.schemas import (
    ProposalResponse, ProposalConfirmRequest, ProposalRejectRequest,
    PaginationParams
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/proposals", tags=["Proposals"])


@router.get("/{proposal_id}", response_model=ProposalResponse)
async def get_proposal(
    proposal_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get proposal details"""
    proposal_manager = ProposalManager(db)
    proposal = await proposal_manager.get_proposal(proposal_id)
    
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found"
        )
    
    return proposal


@router.get("/sessions/{session_id}/proposals", response_model=List[ProposalResponse])
async def list_session_proposals(
    session_id: UUID,
    pagination: PaginationParams = Depends(),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all proposals for a session"""
    proposal_manager = ProposalManager(db)
    proposals = await proposal_manager.list_pending_proposals(
        session_id=session_id,
        skip=pagination.skip,
        limit=pagination.limit
    )
    return proposals


@router.post("/{proposal_id}/confirm", response_model=ProposalResponse)
async def confirm_proposal(
    proposal_id: UUID,
    confirm_data: ProposalConfirmRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Confirm a proposal and trigger MCP commit
    """
    proposal_manager = ProposalManager(db)
    
    try:
        proposal = await proposal_manager.confirm_proposal(
            proposal_id=proposal_id,
            user_id=current_user.id,
            user_response=confirm_data.user_response
        )
        
        await db.commit()
        
        # TODO: Trigger workflow continuation to MCP and commit
        # This would resume the LangGraph workflow from the checkpoint
        
        return proposal
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{proposal_id}/reject", response_model=ProposalResponse)
async def reject_proposal(
    proposal_id: UUID,
    reject_data: ProposalRejectRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Reject a proposal"""
    proposal_manager = ProposalManager(db)
    
    try:
        proposal = await proposal_manager.reject_proposal(
            proposal_id=proposal_id,
            user_id=current_user.id,
            reason=reject_data.reason
        )
        
        await db.commit()
        return proposal
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
