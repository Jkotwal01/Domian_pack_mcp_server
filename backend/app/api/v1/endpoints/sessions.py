
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any, List
import uuid

from app.db.session import get_db
from app.services.domain_service import DomainService
from app.schemas.api_requests import CreateSessionRequest, SessionResponse
from app.core.exceptions import SessionNotFoundError

router = APIRouter()

def get_service(db: Session = Depends(get_db)) -> DomainService:
    return DomainService(db)

@router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(
    request: CreateSessionRequest,
    service: DomainService = Depends(get_service)
):
    try:
        session = service.create_session(request)
        return session
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
         # In a real app, log error
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{session_id}", response_model=SessionResponse)
def get_session(
    session_id: uuid.UUID,
    service: DomainService = Depends(get_service)
):
    try:
        return service.get_session(session_id)
    except SessionNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: uuid.UUID,
    service: DomainService = Depends(get_service)
):
    try:
        service.delete_session(session_id)
    except SessionNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
