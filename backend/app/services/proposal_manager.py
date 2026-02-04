"""
Proposal Manager Service
Handles proposal lifecycle: create, confirm, reject, commit
"""
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Proposal, ProposalStatus, Version, AuditLog, EventType
from app.schemas import ProposalCreate, ProposalResponse, Operation
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class ProposalManager:
    """Manages proposal lifecycle and operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_proposal(
        self,
        session_id: UUID,
        base_version_id: UUID,
        proposal_data: ProposalCreate,
        user_id: UUID
    ) -> Proposal:
        """
        Create a new proposal
        """
        # Calculate expiry
        expires_at = datetime.utcnow() + timedelta(hours=settings.PROPOSAL_EXPIRY_HOURS)
        
        # Determine if confirmation is required
        requires_confirmation = self._requires_confirmation(proposal_data)
        
        proposal = Proposal(
            session_id=session_id,
            base_version_id=base_version_id,
            intent_summary=proposal_data.intent_summary,
            operations=[op.model_dump() for op in proposal_data.operations],
            affected_paths=proposal_data.affected_paths,
            diff_preview=proposal_data.diff_preview,
            questions=proposal_data.questions,
            confidence_score=proposal_data.confidence_score,
            suggested_by=proposal_data.suggested_by,
            status=ProposalStatus.PENDING,
            requires_confirmation=requires_confirmation,
            expires_at=expires_at
        )
        
        self.db.add(proposal)
        await self.db.flush()
        
        # Log audit event
        await self._log_audit(
            EventType.PROPOSAL_CREATED,
            user_id=user_id,
            proposal_id=proposal.id,
            details={
                "intent": proposal_data.intent_summary,
                "operations_count": len(proposal_data.operations),
                "confidence": proposal_data.confidence_score
            }
        )
        
        logger.info(f"Created proposal {proposal.id} for session {session_id}")
        return proposal
    
    async def get_proposal(self, proposal_id: UUID) -> Optional[Proposal]:
        """Get proposal by ID"""
        result = await self.db.execute(
            select(Proposal).where(Proposal.id == proposal_id)
        )
        return result.scalar_one_or_none()
    
    async def list_pending_proposals(
        self,
        session_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> List[Proposal]:
        """List pending proposals for a session"""
        result = await self.db.execute(
            select(Proposal)
            .where(
                and_(
                    Proposal.session_id == session_id,
                    Proposal.status == ProposalStatus.PENDING
                )
            )
            .order_by(Proposal.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def confirm_proposal(
        self,
        proposal_id: UUID,
        user_id: UUID,
        user_response: Optional[str] = None
    ) -> Proposal:
        """
        Confirm a proposal (user approved)
        """
        proposal = await self.get_proposal(proposal_id)
        if not proposal:
            raise ValueError(f"Proposal {proposal_id} not found")
        
        if proposal.status != ProposalStatus.PENDING:
            raise ValueError(f"Proposal {proposal_id} is not pending")
        
        proposal.status = ProposalStatus.CONFIRMED
        proposal.confirmed_by = user_id
        proposal.confirmed_at = datetime.utcnow()
        
        # Log audit event
        await self._log_audit(
            EventType.PROPOSAL_CONFIRMED,
            user_id=user_id,
            proposal_id=proposal.id,
            details={
                "user_response": user_response,
                "confirmed_at": proposal.confirmed_at.isoformat()
            }
        )
        
        logger.info(f"Confirmed proposal {proposal_id} by user {user_id}")
        return proposal
    
    async def reject_proposal(
        self,
        proposal_id: UUID,
        user_id: UUID,
        reason: Optional[str] = None
    ) -> Proposal:
        """
        Reject a proposal (user declined)
        """
        proposal = await self.get_proposal(proposal_id)
        if not proposal:
            raise ValueError(f"Proposal {proposal_id} not found")
        
        if proposal.status != ProposalStatus.PENDING:
            raise ValueError(f"Proposal {proposal_id} is not pending")
        
        proposal.status = ProposalStatus.REJECTED
        proposal.rejection_reason = reason
        proposal.confirmed_by = user_id
        proposal.confirmed_at = datetime.utcnow()
        
        # Log audit event
        await self._log_audit(
            EventType.PROPOSAL_REJECTED,
            user_id=user_id,
            proposal_id=proposal.id,
            details={
                "reason": reason,
                "rejected_at": proposal.confirmed_at.isoformat()
            }
        )
        
        logger.info(f"Rejected proposal {proposal_id} by user {user_id}")
        return proposal
    
    async def mark_committed(
        self,
        proposal_id: UUID,
        version_id: UUID
    ) -> Proposal:
        """
        Mark proposal as committed after successful MCP operation
        """
        proposal = await self.get_proposal(proposal_id)
        if not proposal:
            raise ValueError(f"Proposal {proposal_id} not found")
        
        proposal.status = ProposalStatus.COMMITTED
        
        logger.info(f"Marked proposal {proposal_id} as committed with version {version_id}")
        return proposal
    
    async def abort_proposal(
        self,
        proposal_id: UUID,
        reason: str
    ) -> Proposal:
        """
        Abort a proposal due to error or conflict
        """
        proposal = await self.get_proposal(proposal_id)
        if not proposal:
            raise ValueError(f"Proposal {proposal_id} not found")
        
        proposal.status = ProposalStatus.ABORTED
        proposal.rejection_reason = reason
        
        logger.warning(f"Aborted proposal {proposal_id}: {reason}")
        return proposal
    
    async def cleanup_expired_proposals(self) -> int:
        """
        Cleanup expired pending proposals
        Returns number of proposals cleaned up
        """
        now = datetime.utcnow()
        result = await self.db.execute(
            select(Proposal).where(
                and_(
                    Proposal.status == ProposalStatus.PENDING,
                    Proposal.expires_at < now
                )
            )
        )
        expired_proposals = list(result.scalars().all())
        
        for proposal in expired_proposals:
            proposal.status = ProposalStatus.ABORTED
            proposal.rejection_reason = "Expired"
        
        logger.info(f"Cleaned up {len(expired_proposals)} expired proposals")
        return len(expired_proposals)
    
    def _requires_confirmation(self, proposal_data: ProposalCreate) -> bool:
        """
        Determine if proposal requires human confirmation based on heuristics
        """
        # Always require confirmation for destructive operations
        destructive_ops = ["remove_field", "remove_entity", "delete", "drop"]
        for op in proposal_data.operations:
            if op.op_type in destructive_ops:
                return True
        
        # Require confirmation for bulk operations
        if len(proposal_data.affected_paths) > settings.HIGH_RISK_FIELD_THRESHOLD:
            return True
        
        # Require confirmation for low confidence
        if proposal_data.confidence_score and proposal_data.confidence_score < settings.AUTO_APPROVE_CONFIDENCE_THRESHOLD:
            return True
        
        # Require confirmation if there are questions
        if proposal_data.questions:
            return True
        
        # Default: require confirmation
        return True
    
    async def _log_audit(
        self,
        event_type: EventType,
        user_id: UUID,
        proposal_id: UUID,
        details: dict
    ):
        """Log audit event"""
        audit_log = AuditLog(
            event_type=event_type,
            user_id=user_id,
            proposal_id=proposal_id,
            details=details
        )
        self.db.add(audit_log)
