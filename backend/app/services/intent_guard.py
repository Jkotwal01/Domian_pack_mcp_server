"""
Intent Guard Service
Manages pending intents for confirmation flow.
Stores intents temporarily before user confirmation.
"""

import uuid
from typing import Dict, Optional
from datetime import datetime, timezone
from app.models.api_models import OperationSpec
import asyncio
import logging

logger = logging.getLogger(__name__)


class PendingIntent:
    """Represents a pending intent awaiting confirmation"""
    
    def __init__(self, session_id: str, operations: list[OperationSpec], intent_summary: str):
        self.intent_id = str(uuid.uuid4())
        self.session_id = session_id
        self.operations = operations
        self.intent_summary = intent_summary
        self.created_at = datetime.now(timezone.utc)    
        
    def is_expired(self, timeout_seconds: int = 500) -> bool:
        """Check if intent has expired"""
        age = datetime.now(timezone.utc) - self.created_at
        return age.total_seconds() > timeout_seconds


class IntentGuard:
    """
    Guards and manages pending intents.
    Provides confirmation flow for LLM-generated operations.
    """
    
    def __init__(self, timeout_seconds: int = 300):
        self.pending_intents: Dict[str, PendingIntent] = {}
        self.timeout_seconds = timeout_seconds
        self._lock = asyncio.Lock()
    
    async def store_intent(
        self,
        session_id: str,
        operations: list[OperationSpec],
        intent_summary: str
    ) -> str:
        """
        Store a pending intent.
        
        Args:
            session_id: Session UUID
            operation: Structured operation
            intent_summary: Human-readable summary
            
        Returns:
            Intent ID for confirmation
        """
        intent = PendingIntent(session_id, operations, intent_summary)
        
        async with self._lock:
            self.pending_intents[intent.intent_id] = intent
            logger.debug(f"Stored intent {intent.intent_id} for session {session_id}")
        
        return intent.intent_id
    
    async def get_intent(self, intent_id: str) -> Optional[PendingIntent]:
        """
        Retrieve a pending intent.
        
        Args:
            intent_id: Intent ID
            
        Returns:
            PendingIntent if found and not expired, None otherwise
        """
        async with self._lock:
            intent = self.pending_intents.get(intent_id)
            
            if intent is None:
                return None
            
            if intent.is_expired(self.timeout_seconds):
                # Remove expired intent
                del self.pending_intents[intent_id]
                return None
            
            return intent
    
    async def confirm_intent(self, intent_id: str, session_id: str) -> Optional[PendingIntent]:
        """
        Confirm and remove a pending intent.
        
        Args:
            intent_id: Intent ID
            session_id: Session ID (must match stored intent)
            
        Returns:
            PendingIntent if found and confirmed, None otherwise
        """
        async with self._lock:
            intent = self.pending_intents.get(intent_id)
            
            if intent is None:
                return None
            
            if intent.is_expired(self.timeout_seconds):
                del self.pending_intents[intent_id]
                return None
            
            # Verify session ID matches
            if intent.session_id != session_id:
                logger.warning(f"Session ID mismatch for intent {intent_id}: expected {intent.session_id}, got {session_id}")
                return None
            
            # Remove from pending
            del self.pending_intents[intent_id]
            return intent
    
    async def reject_intent(self, intent_id: str) -> bool:
        """
        Reject and remove a pending intent.
        
        Args:
            intent_id: Intent ID
            
        Returns:
            True if intent was found and rejected, False otherwise
        """
        async with self._lock:
            if intent_id in self.pending_intents:
                del self.pending_intents[intent_id]
                return True
            return False
    
    async def cleanup_expired(self) -> int:
        """
        Remove all expired intents.
        
        Returns:
            Number of intents removed
        """
        async with self._lock:
            expired_ids = [
                intent_id
                for intent_id, intent in self.pending_intents.items()
                if intent.is_expired(self.timeout_seconds)
            ]
            
            for intent_id in expired_ids:
                del self.pending_intents[intent_id]
            
            return len(expired_ids)
    
    async def get_session_intents(self, session_id: str) -> list[PendingIntent]:
        """
        Get all pending intents for a session.
        
        Args:
            session_id: Session UUID
            
        Returns:
            List of pending intents for the session
        """
        async with self._lock:
            return [
                intent
                for intent in self.pending_intents.values()
                if intent.session_id == session_id and not intent.is_expired(self.timeout_seconds)
            ]


# Global intent guard instance
intent_guard = IntentGuard()
