
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import yaml
import uuid
from typing import Dict, Any, List

from app.db.session import get_db
from app.services.domain_service import DomainService
from app.logic.schema import validate_domain_pack

router = APIRouter()

@router.get("/")
async def list_domain_packs(db: Session = Depends(get_db)):
    service = DomainService(db)
    packs = service.list_domain_packs()
    return [{"id": p.id, "name": p.name, "description": p.description, "version": p.version} for p in packs]

@router.get("/{domain_id}/export")
async def export_domain_pack(domain_id: uuid.UUID, db: Session = Depends(get_db)):
    service = DomainService(db)
    try:
        data = service.get_full_domain_pack(domain_id)
        # Convert to YAML for the editor
        yaml_content = yaml.dump(data, sort_keys=False, allow_unicode=True)
        return {"yaml": yaml_content, "json": data}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{domain_id}/sync")
async def sync_domain_pack(domain_id: uuid.UUID, request: Dict[str, Any], db: Session = Depends(get_db)):
    """
    Sync domain pack from provided JSON or YAML-parsed content.
    Expects {"content": {...}} or {"yaml": "..."}
    """
    service = DomainService(db)
    content = request.get("content")
    
    if "yaml" in request:
        try:
            content = yaml.safe_load(request["yaml"])
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid YAML: {str(e)}")
            
    if not content:
        raise HTTPException(status_code=400, detail="No content provided for sync")

    try:
        service.sync_domain_from_content(domain_id, content)
        return {"status": "success", "message": "Domain pack synchronized and version history updated"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")

@router.post("/")
async def create_domain_pack(request: Dict[str, Any], db: Session = Depends(get_db)):
    service = DomainService(db)
    name = request.get("name")
    description = request.get("description", "")
    if not name:
        raise HTTPException(status_code=400, detail="Name is required")
        
    domain = service.create_domain_pack(name, description)
    return {"id": domain.id, "name": domain.name}
