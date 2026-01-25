
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.db.session import get_db
from app.services.domain_service import DomainService
from app.schemas.api_requests import VersionResponse, VersionSummary
from app.core.exceptions import SessionNotFoundError, VersionNotFoundError

router = APIRouter()

def get_service(db: Session = Depends(get_db)) -> DomainService:
    return DomainService(db)

@router.get("/{session_id}/versions", response_model=List[VersionSummary]) # Using Summary for list
def list_versions(
    session_id: uuid.UUID,
    limit: int = 50,
    service: DomainService = Depends(get_service)
):
    try:
        versions = service.list_versions(session_id, limit)
        # Convert to summary (simplified view without full content/diff if heavy)
        # Note: In Pydantic v2 we can use from_attributes=True.
        # Assuming Pydantic v2/v1 compat
        return [
            VersionSummary(
                version=v.version,
                reason=v.reason,
                created_at=v.created_at,
                change_keys=list(v.diff["changed"].keys()) if v.diff and "changed" in v.diff else []
            ) for v in versions
        ]
    except SessionNotFoundError as e:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/{session_id}/versions/{version_id}", response_model=VersionResponse)
def get_version(
    session_id: uuid.UUID,
    version_id: int,
    service: DomainService = Depends(get_service)
):
    try:
        return service.get_version(session_id, version_id)
    except VersionNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
