"""
FastAPI Main Application
Domain Pack Authoring System Backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.session import init_db, close_db
from app.services.mcp_client import close_mcp_client
from app.langgraph.workflow import init_workflow, close_workflow
import logging

# Setup logging before app startup
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    logger.info("Starting Domain Pack Authoring API...")
    
    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
    
    # Setup LangSmith tracing if enabled
    if settings.LANGSMITH_TRACING and settings.LANGSMITH_API_KEY:
        import os
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = settings.LANGSMITH_API_KEY
        os.environ["LANGCHAIN_PROJECT"] = settings.LANGSMITH_PROJECT
        logger.info("LangSmith tracing enabled")
    
    # Initialize LangGraph workflow
    try:
        await init_workflow()
        logger.info("LangGraph workflow initialized")
    except Exception as e:
        logger.error(f"Failed to initialize LangGraph workflow: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    await close_workflow()
    await close_db()
    await close_mcp_client()
    logger.info("Shutdown complete")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    """Root endpoint"""
    logger.info("Root endpoint called")
    return {
        "message": "Welcome to Domain Pack Authoring API",
        "version": "1.0.0",
        "docs": f"{settings.API_V1_STR}/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "domain-pack-authoring-api"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )

