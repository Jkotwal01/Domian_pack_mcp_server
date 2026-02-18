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
    """Print startup banner with LLM monitoring info and load stats."""
    print("\n" + "="*60)
    print("🚀 Domain Pack Generator API Started")
    print("="*60)
    
    # Load persistent stats
    try:
        from app.database import SessionLocal
        from app.models.llm_usage import LLMUsage
        db = SessionLocal()
        usage = db.query(LLMUsage).first()
        if usage:
            llm_monitor.total_calls = usage.total_calls
            llm_monitor.total_input_tokens = usage.total_input_tokens
            llm_monitor.total_output_tokens = usage.total_output_tokens
            print(f"📊 Loaded Persistent Stats: Calls={usage.total_calls}, Tokens={usage.total_input_tokens + usage.total_output_tokens}")
        db.close()
    except Exception as e:
        print(f"⚠️ Failed to load persistent LLM stats: {e}")

    print("📊 LLM API Monitoring: ENABLED")
    print("   - All LLM calls will be tracked")
    print("   - Response times will be measured")
    print("   - Stats available at /stats endpoint")
    print("="*60 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    """Print monitoring summary on shutdown."""
    print("\n" + "="*60)
    print("🛑 Shutting Down - LLM Monitoring Summary")
    print("="*60)
    llm_monitor.print_summary()


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


@app.get("/stats")
async def get_llm_stats():
    """Get LLM API call statistics."""
    return {
        "llm_monitoring": llm_monitor.get_stats(),
        "message": "Real-time LLM API statistics"
    }


# Import and include routers
from app.api import auth, domains, chat
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(domains.router, prefix="/domains", tags=["domains"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
