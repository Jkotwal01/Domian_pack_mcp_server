"""
API v1 Router

Aggregates all v1 endpoints.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import sessions, chat, operations, versions, rollback, export

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(operations.router, prefix="/operations", tags=["operations"])
api_router.include_router(versions.router, prefix="/versions", tags=["versions"])
api_router.include_router(rollback.router, prefix="/rollback", tags=["rollback"])
api_router.include_router(export.router, prefix="/export", tags=["export"])
