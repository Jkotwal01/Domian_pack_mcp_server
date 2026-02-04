"""
Version Manager Service
Handles version creation, retrieval, diff generation, and rollback
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy import select, and_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from deepdiff import DeepDiff

from app.db.models import Version, DomainPack, AuditLog, EventType
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class VersionManager:
    """Manages domain pack versions and history"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_version(
        self,
        domain_pack_id: UUID,
        snapshot: Dict[str, Any],
        committed_by: UUID,
        proposal_id: Optional[UUID] = None,
        commit_message: Optional[str] = None,
        is_rollback: bool = False,
        rollback_of_version_id: Optional[UUID] = None
    ) -> Version:
        """
        Create a new version with automatic version numbering and diff generation
        """
        # Get the latest version number
        result = await self.db.execute(
            select(func.max(Version.version_number))
            .where(Version.domain_pack_id == domain_pack_id)
        )
        max_version = result.scalar()
        version_number = (max_version or 0) + 1
        
        # Get previous version for diff
        previous_version = await self.get_latest_version(domain_pack_id)
        diff_from_previous = None
        
        if previous_version:
            diff_from_previous = self.generate_diff(
                previous_version.snapshot,
                snapshot
            )
        
        # Create new version
        version = Version(
            domain_pack_id=domain_pack_id,
            version_number=version_number,
            snapshot=snapshot,
            diff_from_previous=diff_from_previous,
            proposal_id=proposal_id,
            committed_by=committed_by,
            commit_message=commit_message,
            is_rollback=is_rollback,
            rollback_of_version_id=rollback_of_version_id
        )
        
        self.db.add(version)
        await self.db.flush()
        
        # Update domain pack current version
        domain_pack = await self.db.get(DomainPack, domain_pack_id)
        if domain_pack:
            domain_pack.current_version_id = version.id
            domain_pack.updated_at = datetime.utcnow()
        
        # Log audit event
        await self._log_audit(
            EventType.COMMIT_SUCCESS if not is_rollback else EventType.ROLLBACK_CREATED,
            user_id=committed_by,
            version_id=version.id,
            details={
                "domain_pack_id": str(domain_pack_id),
                "version_number": version_number,
                "proposal_id": str(proposal_id) if proposal_id else None,
                "is_rollback": is_rollback,
                "commit_message": commit_message
            }
        )
        
        logger.info(f"Created version {version_number} for domain pack {domain_pack_id}")
        return version
    
    async def get_version(self, version_id: UUID) -> Optional[Version]:
        """Get version by ID"""
        return await self.db.get(Version, version_id)
    
    async def get_latest_version(self, domain_pack_id: UUID) -> Optional[Version]:
        """Get the latest version for a domain pack"""
        result = await self.db.execute(
            select(Version)
            .where(Version.domain_pack_id == domain_pack_id)
            .order_by(desc(Version.version_number))
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def list_versions(
        self,
        domain_pack_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> List[Version]:
        """List all versions for a domain pack"""
        result = await self.db.execute(
            select(Version)
            .where(Version.domain_pack_id == domain_pack_id)
            .order_by(desc(Version.version_number))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_version_count(self, domain_pack_id: UUID) -> int:
        """Get total version count for a domain pack"""
        result = await self.db.execute(
            select(func.count(Version.id))
            .where(Version.domain_pack_id == domain_pack_id)
        )
        return result.scalar() or 0
    
    async def create_rollback_version(
        self,
        domain_pack_id: UUID,
        target_version_id: UUID,
        committed_by: UUID,
        reason: Optional[str] = None
    ) -> Version:
        """
        Create a rollback version (new version with old snapshot)
        """
        target_version = await self.get_version(target_version_id)
        if not target_version:
            raise ValueError(f"Target version {target_version_id} not found")
        
        if target_version.domain_pack_id != domain_pack_id:
            raise ValueError("Target version does not belong to this domain pack")
        
        commit_message = f"Rollback to version {target_version.version_number}"
        if reason:
            commit_message += f": {reason}"
        
        # Create new version with old snapshot
        rollback_version = await self.create_version(
            domain_pack_id=domain_pack_id,
            snapshot=target_version.snapshot,
            committed_by=committed_by,
            commit_message=commit_message,
            is_rollback=True,
            rollback_of_version_id=target_version_id
        )
        
        logger.info(
            f"Created rollback version {rollback_version.version_number} "
            f"to version {target_version.version_number}"
        )
        return rollback_version
    
    def generate_diff(
        self,
        old_snapshot: Dict[str, Any],
        new_snapshot: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate structured diff between two snapshots
        """
        diff = DeepDiff(
            old_snapshot,
            new_snapshot,
            ignore_order=False,
            report_repetition=True,
            verbose_level=2
        )
        
        # Convert to serializable format
        return {
            "added": diff.get("dictionary_item_added", []),
            "removed": diff.get("dictionary_item_removed", []),
            "changed": diff.get("values_changed", {}),
            "type_changes": diff.get("type_changes", {}),
            "iterable_changes": {
                "added": diff.get("iterable_item_added", {}),
                "removed": diff.get("iterable_item_removed", {})
            }
        }
    
    async def get_diff_between_versions(
        self,
        from_version_id: UUID,
        to_version_id: UUID
    ) -> Dict[str, Any]:
        """
        Generate diff between two specific versions
        """
        from_version = await self.get_version(from_version_id)
        to_version = await self.get_version(to_version_id)
        
        if not from_version or not to_version:
            raise ValueError("One or both versions not found")
        
        return self.generate_diff(from_version.snapshot, to_version.snapshot)
    
    async def _log_audit(
        self,
        event_type: EventType,
        user_id: UUID,
        version_id: UUID,
        details: dict
    ):
        """Log audit event"""
        audit_log = AuditLog(
            event_type=event_type,
            user_id=user_id,
            version_id=version_id,
            details=details
        )
        self.db.add(audit_log)
