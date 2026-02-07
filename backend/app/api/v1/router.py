"""
API v1 Router
Combines all API endpoints
"""
from fastapi import APIRouter

from app.api.v1 import auth, chat, proposals, versions

api_router = APIRouter()

# Include all routers
api_router.include_router(auth.router)
api_router.include_router(chat.router)
api_router.include_router(proposals.router)
api_router.include_router(versions.router)


