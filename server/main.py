"""
Main FastAPI application entry point for Stuchai Voice OS.

This module initializes the FastAPI app, sets up middleware, 
includes routers, and handles startup/shutdown events.
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from shared.config import settings
from server.models.database import init_db, close_db
from server.api import auth, clients, agents, voices, admin

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.
    
    Handles startup and shutdown events:
    - Initialize database connection
    - Set up voice services
    - Cleanup on shutdown
    """
    # Startup
    logger.info("Starting Stuchai Voice OS...")
    await init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Stuchai Voice OS...")
    await close_db()
    logger.info("Shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Voice Operating System for AI-driven property management + automation",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check() -> dict:
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns:
        dict: Status information
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": "1.0.0"
    }


# Include API routers
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Authentication"])
app.include_router(admin.router, prefix=f"{settings.API_V1_PREFIX}/admin", tags=["Admin"])
app.include_router(clients.router, prefix=f"{settings.API_V1_PREFIX}/client", tags=["Clients"])
app.include_router(agents.router, prefix=f"{settings.API_V1_PREFIX}/agent", tags=["Agents"])
app.include_router(voices.router, prefix=f"{settings.API_V1_PREFIX}/voice", tags=["Voices"])


# Root endpoint
@app.get("/")
async def root() -> dict:
    """
    Root endpoint providing API information.
    
    Returns:
        dict: API information
    """
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )

