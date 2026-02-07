from fastapi import APIRouter
from app.api.v1.endpoints import domain_packs

api_router = APIRouter()

api_router.include_router(domain_packs.router, prefix="/domain-packs", tags=["domain-packs"])
