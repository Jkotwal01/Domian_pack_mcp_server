"""
Memory Store Service
Handles short-term and long-term memory storage with semantic search
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy import select, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
import numpy as np

from app.db.models import MemoryEntry, MemoryType, MemoryScope, MemorySource, AuditLog, EventType
from app.schemas import MemoryEntryCreate, MemoryEntryUpdate
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class MemoryStore:
    """Manages user memory entries with semantic search capabilities"""
    
    def __init__(self, db: AsyncSession, embedding_client=None):
        self.db = db
        self.embedding_client = embedding_client
    
    async def store_memory(
        self,
        user_id: UUID,
        memory_data: MemoryEntryCreate,
        expires_in_days: Optional[int] = None
    ) -> MemoryEntry:
        """
        Store a new memory entry
        """
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        # Generate embedding if client available
        embedding = None
        if self.embedding_client:
            embedding = await self._generate_embedding(memory_data.summary)
        
        memory = MemoryEntry(
            user_id=user_id,
            type=memory_data.type,
            scope=memory_data.scope,
            summary=memory_data.summary,
            details=memory_data.details,
            confidence=memory_data.confidence,
            embedding=embedding,
            source=memory_data.source,
            last_confirmed_at=datetime.utcnow() if memory_data.source == MemorySource.USER_CONFIRMED else None,
            expires_at=expires_at
        )
        
        self.db.add(memory)
        await self.db.flush()
        
        # Log audit event
        await self._log_audit(
            EventType.MEMORY_CREATED,
            user_id=user_id,
            details={
                "memory_id": str(memory.id),
                "type": memory_data.type.value,
                "scope": memory_data.scope.value,
                "summary": memory_data.summary
            }
        )
        
        logger.info(f"Stored memory {memory.id} for user {user_id}")
        return memory
    
    async def get_memory(self, memory_id: UUID) -> Optional[MemoryEntry]:
        """Get memory by ID"""
        return await self.db.get(MemoryEntry, memory_id)
    
    async def update_memory(
        self,
        memory_id: UUID,
        memory_update: MemoryEntryUpdate,
        user_id: UUID
    ) -> MemoryEntry:
        """Update an existing memory"""
        memory = await self.get_memory(memory_id)
        if not memory:
            raise ValueError(f"Memory {memory_id} not found")
        
        if memory.user_id != user_id:
            raise ValueError("Cannot update memory of another user")
        
        # Update fields
        if memory_update.summary:
            memory.summary = memory_update.summary
            # Regenerate embedding if summary changed
            if self.embedding_client:
                memory.embedding = await self._generate_embedding(memory_update.summary)
        
        if memory_update.details is not None:
            memory.details = memory_update.details
        
        if memory_update.confidence is not None:
            memory.confidence = memory_update.confidence
        
        if memory_update.last_confirmed_at:
            memory.last_confirmed_at = memory_update.last_confirmed_at
        
        # Log audit event
        await self._log_audit(
            EventType.MEMORY_UPDATED,
            user_id=user_id,
            details={
                "memory_id": str(memory_id),
                "updated_fields": list(memory_update.model_dump(exclude_unset=True).keys())
            }
        )
        
        logger.info(f"Updated memory {memory_id}")
        return memory
    
    async def delete_memory(self, memory_id: UUID, user_id: UUID) -> bool:
        """Delete a memory entry"""
        memory = await self.get_memory(memory_id)
        if not memory:
            return False
        
        if memory.user_id != user_id:
            raise ValueError("Cannot delete memory of another user")
        
        await self.db.delete(memory)
        logger.info(f"Deleted memory {memory_id}")
        return True
    
    async def get_relevant_memories(
        self,
        user_id: UUID,
        context: str,
        scope: Optional[MemoryScope] = None,
        limit: int = 10
    ) -> List[MemoryEntry]:
        """
        Get relevant memories for a given context using semantic search
        """
        # Build base query
        conditions = [MemoryEntry.user_id == user_id]
        
        if scope:
            conditions.append(MemoryEntry.scope == scope)
        
        # Filter out expired memories
        conditions.append(
            or_(
                MemoryEntry.expires_at.is_(None),
                MemoryEntry.expires_at > datetime.utcnow()
            )
        )
        
        # If embedding client available, do semantic search
        if self.embedding_client:
            return await self._semantic_search(user_id, context, conditions, limit)
        
        # Fallback: return recent memories
        result = await self.db.execute(
            select(MemoryEntry)
            .where(and_(*conditions))
            .order_by(desc(MemoryEntry.last_confirmed_at), desc(MemoryEntry.created_at))
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_user_memories(
        self,
        user_id: UUID,
        type: Optional[MemoryType] = None,
        scope: Optional[MemoryScope] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[MemoryEntry]:
        """Get all memories for a user with optional filters"""
        conditions = [MemoryEntry.user_id == user_id]
        
        if type:
            conditions.append(MemoryEntry.type == type)
        
        if scope:
            conditions.append(MemoryEntry.scope == scope)
        
        result = await self.db.execute(
            select(MemoryEntry)
            .where(and_(*conditions))
            .order_by(desc(MemoryEntry.created_at))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def cleanup_expired_memories(self) -> int:
        """
        Cleanup expired memory entries
        Returns number of memories cleaned up
        """
        now = datetime.utcnow()
        result = await self.db.execute(
            select(MemoryEntry).where(
                and_(
                    MemoryEntry.expires_at.isnot(None),
                    MemoryEntry.expires_at < now
                )
            )
        )
        expired_memories = list(result.scalars().all())
        
        for memory in expired_memories:
            await self.db.delete(memory)
        
        logger.info(f"Cleaned up {len(expired_memories)} expired memories")
        return len(expired_memories)
    
    async def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding vector for text"""
        if not self.embedding_client:
            return None
        
        try:
            # This would use OpenAI embeddings or similar
            # For now, placeholder
            # response = await self.embedding_client.embeddings.create(
            #     input=text,
            #     model=settings.EMBEDDING_MODEL
            # )
            # return response.data[0].embedding
            return None
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None
    
    async def _semantic_search(
        self,
        user_id: UUID,
        query: str,
        conditions: List,
        limit: int
    ) -> List[MemoryEntry]:
        """
        Perform semantic search using embeddings
        """
        # Generate query embedding
        query_embedding = await self._generate_embedding(query)
        if not query_embedding:
            # Fallback to recent memories
            result = await self.db.execute(
                select(MemoryEntry)
                .where(and_(*conditions))
                .order_by(desc(MemoryEntry.created_at))
                .limit(limit)
            )
            return list(result.scalars().all())
        
        # Get all candidate memories
        result = await self.db.execute(
            select(MemoryEntry).where(and_(*conditions))
        )
        memories = list(result.scalars().all())
        
        # Calculate cosine similarity
        scored_memories = []
        for memory in memories:
            if memory.embedding:
                similarity = self._cosine_similarity(query_embedding, memory.embedding)
                scored_memories.append((memory, similarity))
        
        # Sort by similarity and return top results
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        return [memory for memory, score in scored_memories[:limit]]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            a = np.array(vec1)
            b = np.array(vec2)
            return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
        except:
            return 0.0
    
    async def _log_audit(
        self,
        event_type: EventType,
        user_id: UUID,
        details: dict
    ):
        """Log audit event"""
        audit_log = AuditLog(
            event_type=event_type,
            user_id=user_id,
            details=details
        )
        self.db.add(audit_log)
