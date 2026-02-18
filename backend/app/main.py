"""
C-DIT Backend — FastAPI Main Entry Point
AI-Powered Agricultural Advisory System
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routers import analyze, chat, feedback
from app.services.vector_index import initialize_vector_index

# ─── Logging ─────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("c-dit")


# ─── Lifespan (startup / shutdown) ──────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup."""
    logger.info("🌾 Starting C-DIT Backend...")
    await initialize_vector_index()
    logger.info("Vector index initialized successfully")
    logger.info(f"🌾 C-DIT Backend ready on http://localhost:{settings.port}")
    logger.info("Available endpoints:")
    logger.info("  POST /analyze/image   — Image disease classification")
    logger.info("  POST /analyze/voice   — Voice-to-text analysis")
    logger.info("  POST /analyze/text    — Text description analysis")
    logger.info("  POST /chat/followup   — Follow-up questions")
    logger.info("  POST /feedback        — Farmer feedback")
    logger.info("  GET  /health          — Health check")
    yield
    logger.info("Shutting down C-DIT Backend...")


# ─── App ─────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="C-DIT Agricultural Advisory Backend",
    description="AI-Powered Crop Disease Advisory System",
    version="2.0.0",
    lifespan=lifespan,
)

# ─── CORS ────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origin],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

# ─── Routers ─────────────────────────────────────────────────────────────────

app.include_router(analyze.router)
app.include_router(chat.router)
app.include_router(feedback.router)


# ─── Health Check ────────────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "C-DIT Agricultural Advisory Backend",
    }


# ─── Sessions endpoint (for frontend history page) ──────────────────────────

@app.get("/sessions")
async def get_sessions():
    from app.services.supabase_client import get_sessions
    sessions = get_sessions(limit=20)
    return {"success": True, "data": sessions}


# ─── Global Error Handling ───────────────────────────────────────────────────

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"success": False, "error": {"message": str(exc)}},
    )


@app.exception_handler(Exception)
async def general_error_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": {"message": "Internal Server Error"}},
    )


# ─── Run with uvicorn ────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.port, reload=True)
