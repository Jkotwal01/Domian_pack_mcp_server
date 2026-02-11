"""Domain configuration API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.database import get_db
from app.schemas.domain import (
    DomainConfigCreate,
    DomainConfigUpdate,
    DomainConfigResponse,
    DomainConfigList
)
from app.services.domain_service import DomainService
from app.services.validation_service import ValidationService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("", response_model=List[DomainConfigList])
async def list_domains(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all domains owned by the current user.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of domain configurations (without full config_json)
    """
    domains = DomainService.get_user_domains(db, current_user)
    return domains


@router.post("", response_model=DomainConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_domain(
    domain_data: DomainConfigCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new domain configuration with base template.
    
    Args:
        domain_data: Domain creation data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Created domain configuration
    """
    domain = DomainService.create_domain(db, domain_data, current_user)
    return domain


@router.get("/{domain_id}", response_model=DomainConfigResponse)
async def get_domain(
    domain_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a domain configuration by ID.
    
    Args:
        domain_id: Domain UUID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Domain configuration with full config_json
    """
    domain = DomainService.get_domain_by_id(db, domain_id, current_user)
    return domain


@router.put("/{domain_id}", response_model=DomainConfigResponse)
async def update_domain(
    domain_id: UUID,
    domain_data: DomainConfigUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a domain configuration.
    
    Args:
        domain_id: Domain UUID
        domain_data: Update data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated domain configuration
    """
    # Validate config_json if provided
    if domain_data.config_json is not None:
        ValidationService.validate_config(domain_data.config_json)
    
    domain = DomainService.update_domain(db, domain_id, domain_data, current_user)
    return domain


@router.delete("/{domain_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_domain(
    domain_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a domain configuration.
    
    Args:
        domain_id: Domain UUID
        current_user: Current authenticated user
        db: Database session
    """
    DomainService.delete_domain(db, domain_id, current_user)
    return None
