
from fastapi import APIRouter, HTTPException, status, UploadFile, File, Body
from typing import Dict, Any
from app.logic.schema import validate_domain_pack
from app.logic.utils import parse_yaml, ParseError
from pydantic import BaseModel
import jsonschema

router = APIRouter()

class ValidationResponse(BaseModel):
    valid: bool
    errors: list[str] = []

@router.post("/yaml", response_model=ValidationResponse)
async def validate_yaml(
    content: str = Body(..., media_type="text/plain")
):
    """
    Validate raw YAML content against the Domain Pack schema.
    Send raw YAML in the request body.
    """
    try:
        # Parse YAML
        data = parse_yaml(content)
        
        # Validate Schema
        validate_domain_pack(data)
        
        return ValidationResponse(valid=True)
        
    except ParseError as e:
        return ValidationResponse(valid=False, errors=[f"YAML Parse Error: {str(e)}"])
    except jsonschema.ValidationError as e:
        # Construct readable error path
        path = " -> ".join(str(p) for p in e.path) if e.path else "root"
        error_msg = f"Validation failed at {path}: {e.message}"
        return ValidationResponse(valid=False, errors=[error_msg])
    except ValueError as e:
        return ValidationResponse(valid=False, errors=[str(e)])
