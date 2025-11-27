"""
AI Healthcare Application - FastAPI Backend
Main application entry point with health checks and middleware configuration.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from src.api.config import settings
from src.api.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Handle application lifespan events."""
    # Startup
    logger.info("🚀 Starting AI Healthcare Application")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"API Version: {settings.API_VERSION}")

    # TODO: Initialize database connection pool
    # TODO: Initialize Redis connection
    # TODO: Initialize FHIR client

    yield

    # Shutdown
    logger.info("👋 Shutting down AI Healthcare Application")
    # TODO: Close database connections
    # TODO: Close Redis connections


# Create FastAPI application
app = FastAPI(
    title="AI Healthcare Application API",
    description="AI-powered healthcare platform with CarePrep and ContextAI features",
    version=settings.API_VERSION,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware for production
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,
    )


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header to responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.

    Returns:
        dict: Health status and system information
    """
    return {
        "status": "healthy",
        "service": "AI Healthcare API",
        "version": settings.API_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": time.time(),
    }


# Detailed health check with dependencies
@app.get("/health/detailed", tags=["Health"])
async def detailed_health_check():
    """
    Detailed health check including dependencies.

    Returns:
        dict: Detailed health status of all services
    """
    health_status = {
        "status": "healthy",
        "service": "AI Healthcare API",
        "version": settings.API_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": time.time(),
        "dependencies": {
            "database": "unknown",  # TODO: Check database connection
            "redis": "unknown",  # TODO: Check Redis connection
            "fhir_server": "unknown",  # TODO: Check FHIR server
        },
        "features": {
            "careprep": settings.ENABLE_PREVISIT,
            "contextai": settings.ENABLE_APPOINT_READY,
            "transcription": settings.ENABLE_TRANSCRIPTION,
            "fhir_integration": settings.ENABLE_FHIR,
        },
    }

    return health_status


# Application info endpoint
@app.get("/info", tags=["Info"])
async def app_info():
    """
    Application information endpoint.

    Returns:
        dict: Application metadata
    """
    return {
        "name": "AI Healthcare Application",
        "version": settings.API_VERSION,
        "environment": settings.ENVIRONMENT,
        "features": {
            "careprep": {
                "enabled": settings.ENABLE_PREVISIT,
                "description": "Patient symptom checking and appointment preparation",
            },
            "contextai": {
                "enabled": settings.ENABLE_APPOINT_READY,
                "description": "Provider-facing appointment context and care gap detection",
            },
            "transcription": {
                "enabled": settings.ENABLE_TRANSCRIPTION,
                "description": "Real-time audio transcription with Azure Speech Services",
            },
            "fhir_integration": {
                "enabled": settings.ENABLE_FHIR,
                "description": "HL7 FHIR R4 integration for healthcare data interoperability",
            },
        },
        "documentation": {
            "swagger_ui": "/docs" if settings.ENVIRONMENT != "production" else None,
            "redoc": "/redoc" if settings.ENVIRONMENT != "production" else None,
        },
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information.

    Returns:
        dict: Welcome message and quick links
    """
    return {
        "message": "Welcome to AI Healthcare Application API",
        "version": settings.API_VERSION,
        "docs": "/docs" if settings.ENVIRONMENT != "production" else "Documentation disabled in production",
        "health": "/health",
        "info": "/info",
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors.

    Args:
        request: The request that caused the error
        exc: The exception that was raised

    Returns:
        JSONResponse: Error response
    """
    logger.error(
        f"Unhandled exception: {exc}",
        exc_info=True,
        extra={
            "path": request.url.path,
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc) if settings.ENVIRONMENT != "production" else "An unexpected error occurred",
            "path": request.url.path,
        },
    )


# Import and include routers
from src.api.routers import (
    auth, patients, visits, clinical, appointments, templates,
    ai_assistant, tasks, tenants,
    # CarePrep + ContextAI routers
    careprep_unified, contextai, careprep_forms
)

# Core routers
app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(visits.router)
app.include_router(clinical.router)
app.include_router(appointments.router)
app.include_router(templates.router)
app.include_router(ai_assistant.router)
app.include_router(tasks.router)
app.include_router(tenants.router)

# CarePrep/ContextAI routers
app.include_router(careprep_unified.router)  # /api/careprep/* (AI symptom analysis)
app.include_router(contextai.router)          # /api/contextai/* (provider context)
app.include_router(careprep_forms.router)     # /api/careprep/forms/* (appointment forms)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "local" else False,
        log_level=settings.LOG_LEVEL.lower(),
    )
