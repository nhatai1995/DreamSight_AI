"""
Dream Interpretation API - Main Application Entry Point
Production-hardened with rate limiting, CORS, and error handling.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from config import get_settings
from routers import dreams, admin
from utils.db_loader import initialize_database

settings = get_settings()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown."""
    # Startup
    initialize_database()
    yield
    # Shutdown (cleanup if needed)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered dream interpretation using LangChain and ChromaDB",
    lifespan=lifespan,
)

# Attach limiter to app state
app.state.limiter = limiter

# Register rate limit exceeded handler
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS Configuration (from environment variable)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler for graceful 503 responses
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch unhandled exceptions and return graceful 503."""
    # Log the error (in production, use proper logging)
    print(f"⚠️ Unhandled exception: {type(exc).__name__}: {exc}")
    
    # Return graceful error response
    return JSONResponse(
        status_code=503,
        content={
            "detail": "The Oracle is meditating (Service busy). Please try again.",
            "error_type": type(exc).__name__,
        }
    )


# Include routers
app.include_router(dreams.router, prefix="/api/dreams", tags=["Dreams"])
app.include_router(admin.router, prefix="/api", tags=["Admin"])


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
