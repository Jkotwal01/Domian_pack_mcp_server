"""
Session Manager Service
Handles user session creation and management
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Session, AuditLog, EventType
from app.schemas import SessionCreate, SessionResponse
import logging

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages user conversation sessions"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_session(
        self,
        user_id: UUID,
        session_data: SessionCreate
    ) -> Session:
        """
        Create a new conversation session
        """
        session = Session(
            user_id=user_id,
            thread_id=uuid4(),
            domain_pack_id=session_data.domain_pack_id,
            details=session_data.metadata or {}
        )
        
        self.db.add(session)
        await self.db.flush()
        
        # Log audit event
        await self._log_audit(
            EventType.SESSION_STARTED,
            user_id=user_id,
            session_id=session.id,
            details={
                "thread_id": str(session.thread_id),
                "domain_pack_id": str(session_data.domain_pack_id) if session_data.domain_pack_id else None
            }
        )
        
        logger.info(f"Created session {session.id} for user {user_id}")
        return session
    
    async def get_session(self, session_id: UUID) -> Optional[Session]:
        """Get session by ID"""
        return await self.db.get(Session, session_id)
    
    async def get_session_by_thread(self, thread_id: UUID) -> Optional[Session]:
        """Get session by thread ID"""
        result = await self.db.execute(
            select(Session).where(Session.thread_id == thread_id)
        )
        return result.scalar_one_or_none()
    
    async def update_session_activity(self, session_id: UUID) -> Session:
        """Update last activity timestamp"""
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        session.last_activity = datetime.utcnow()
        return session
    
    async def get_active_sessions(
        self,
        user_id: UUID,
        limit: int = 50
    ) -> List[Session]:
        """Get active (not ended) sessions for a user"""
        result = await self.db.execute(
            select(Session)
            .where(
                and_(
                    Session.user_id == user_id,
                    Session.ended_at.is_(None)
                )
            )
            .order_by(Session.last_activity.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_all_sessions(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> List[Session]:
        """Get all sessions for a user"""
        result = await self.db.execute(
            select(Session)
            .where(Session.user_id == user_id)
            .order_by(Session.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def end_session(
        self,
        session_id: UUID,
        user_id: UUID
    ) -> Session:
        """End a session"""
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        if session.user_id != user_id:
            raise ValueError("Cannot end session of another user")
        
        session.ended_at = datetime.utcnow()
        
        # Log audit event
        await self._log_audit(
            EventType.SESSION_ENDED,
            user_id=user_id,
            session_id=session.id,
            details={
                "ended_at": session.ended_at.isoformat(),
                "duration_seconds": (session.ended_at - session.created_at).total_seconds()
            }
        )
        
        logger.info(f"Ended session {session_id}")
        return session
    
    async def _log_audit(
        self,
        event_type: EventType,
        user_id: UUID,
        session_id: UUID,
        details: dict
    ):
        """Log audit event"""
        audit_log = AuditLog(
            event_type=event_type,
            user_id=user_id,
            session_id=session_id,
            details=details
        )
        self.db.add(audit_log)
