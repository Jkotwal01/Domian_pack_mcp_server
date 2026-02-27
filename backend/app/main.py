"""Main FastAPI application."""
from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.utils.llm_monitor import llm_monitor

# Create FastAPI app
app = FastAPI(
    title="Domain Pack Generator API",
    description="FastAPI + LangGraph backend for conversational domain pack configuration",
    version="1.0.0",
    debug=settings.DEBUG,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Print startup banner."""
    print("\n" + "="*60)
    print("🚀 Domain Pack Generator API Started")
    print("="*60)
    print("="*60 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    """Print shutdown info."""
    print("\n" + "="*60)
    print("🛑 Shutting Down")
    print("="*60)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "Domain Pack Generator API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check for monitoring."""
    return {"status": "healthy"}


# Import and include routers
from app.api import auth, domains, chat
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(domains.router, prefix="/domains", tags=["domains"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
