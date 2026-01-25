
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid

from app.db.session import get_db
from app.services.domain_service import DomainService
from app.schemas.api_requests import ApplyOperationsRequest, VersionResponse
from app.core.exceptions import SessionNotFoundError
import jsonschema

router = APIRouter()

def get_service(db: Session = Depends(get_db)) -> DomainService:
    return DomainService(db)

@router.post("/{session_id}/operations", response_model=VersionResponse)
def apply_operations(
    session_id: uuid.UUID,
    request: ApplyOperationsRequest,
    service: DomainService = Depends(get_service)
):
    try:
        # Convert Pydantic models to dicts for the service
        ops_dicts = [op.dict(exclude_none=True) for op in request.operations]
        new_version = service.apply_operations(session_id, ops_dicts)
        return new_version
    except SessionNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (ValueError, jsonschema.ValidationError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
