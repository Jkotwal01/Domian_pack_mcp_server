"""
Version API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from app.db.session import get_db
from app.api.v1.auth import get_current_user
from app.services.version_manager import VersionManager
from app.schemas import (
    VersionResponse, VersionListResponse, RollbackRequest,
    PaginationParams
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/versions", tags=["Versions"])


@router.get("/domain-packs/{domain_pack_id}/versions", response_model=List[VersionListResponse])
async def list_versions(
    domain_pack_id: UUID,
    pagination: PaginationParams = Depends(),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all versions for a domain pack"""
    version_manager = VersionManager(db)
    versions = await version_manager.list_versions(
        domain_pack_id=domain_pack_id,
        skip=pagination.skip,
        limit=pagination.limit
    )
    return versions


@router.get("/{version_id}", response_model=VersionResponse)
async def get_version(
    version_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific version details"""
    version_manager = VersionManager(db)
    version = await version_manager.get_version(version_id)
    
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found"
        )
    
    return version


@router.get("/{version_id}/diff")
async def get_version_diff(
    version_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get diff from previous version"""
    version_manager = VersionManager(db)
    version = await version_manager.get_version(version_id)
    
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found"
        )
    
    return {
        "version_id": str(version_id),
        "version_number": version.version_number,
        "diff": version.diff_from_previous
    }


@router.post("/domain-packs/{domain_pack_id}/rollback", response_model=VersionResponse)
async def create_rollback(
    domain_pack_id: UUID,
    rollback_data: RollbackRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a rollback version"""
    version_manager = VersionManager(db)
    
    try:
        rollback_version = await version_manager.create_rollback_version(
            domain_pack_id=domain_pack_id,
            target_version_id=rollback_data.target_version_id,
            committed_by=current_user.id,
            reason=rollback_data.reason
        )
        
        await db.commit()
        return rollback_version
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
