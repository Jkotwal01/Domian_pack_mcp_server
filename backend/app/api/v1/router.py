
from fastapi import APIRouter
from app.api.v1.endpoints import sessions, versions, operations, validation

api_router = APIRouter()

api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
# Versions are nested under sessions generally, but let's expose generic listing or keep it under sessions logic.
# In endpoints/versions.py I defined paths like /{session_id}/versions.
# So I should mount it at root level relative to API or merged with sessions.
# However, FastAPI allows including same router with different prefixes or just raw.
# My versions endpoint has /params so it expects to be at root of V1 or similar.
# Let's see: @router.get("/{session_id}/versions") -> if included at /sessions it becomes /sessions/{sid}/versions.
# Wait, sessions router handles /sessions/root.
# If I mount versions router at /sessions, it will work.
api_router.include_router(versions.router, prefix="/sessions", tags=["versions"]) 
api_router.include_router(operations.router, prefix="/sessions", tags=["operations"])
api_router.include_router(validation.router, prefix="/validate", tags=["validation"])
