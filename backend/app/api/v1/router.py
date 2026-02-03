"""
API v1 Router - Refactored

Consolidates routes using unified endpoints and removes redundancy.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import (
    sessions_versions,  # Unified sessions + versions
    chat,
    operations,
    rollback,
    export,
    dashboard
)

api_router = APIRouter()

# Unified sessions and versions (RESTful structure)
api_router.include_router(
    sessions_versions.router,
    tags=["sessions", "versions"]
)

# Other endpoints
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(operations.router, prefix="/operations", tags=["operations"])
api_router.include_router(rollback.router, prefix="/rollback", tags=["rollback"])
api_router.include_router(export.router, prefix="/export", tags=["export"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
