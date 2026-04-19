"""FastAPI application entry point."""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
import logging
import time

from .routers import auth, leads, deals, outreach, payments, demos, analytics, business_owners, admin, disputes, reviews, health, notifications
from .scheduler import start_scheduler, stop_scheduler
from .middleware.performance import PerformanceMiddleware
from .middleware.security import (
    SecurityHeadersMiddleware,
    XSSProtectionMiddleware,
    CSRFProtectionMiddleware
)
from .middleware.rate_limit import RateLimitMiddleware

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.WARNING,  # Changed from INFO to WARNING
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Silence noisy loggers
logging.getLogger('apscheduler').setLevel(logging.WARNING)
logging.getLogger('app.services.retry_service').setLevel(logging.WARNING)

# Create FastAPI app
app = FastAPI(
    title="LocalAI Leads Platform API",
    description="AI-assisted marketplace connecting freelance web developers with local businesses",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add performance monitoring middleware
app.add_middleware(PerformanceMiddleware)

# Add security middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(XSSProtectionMiddleware)
app.add_middleware(CSRFProtectionMiddleware)
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=60,
    requests_per_hour=1000
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(leads.router)
app.include_router(deals.router)
app.include_router(outreach.router)
app.include_router(payments.router)
app.include_router(demos.router)
app.include_router(analytics.router)
app.include_router(business_owners.router)
app.include_router(admin.router)
app.include_router(disputes.router)
app.include_router(reviews.router)
app.include_router(notifications.router)

# Import and include failures router
from .routers import failures
app.include_router(failures.router)

# Include health check router
app.include_router(health.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "LocalAI Leads Platform API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/api/health"
    }


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("Application starting up")
    start_scheduler()
    logger.info("Startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Application shutting down")
    stop_scheduler()
    logger.info("Shutdown complete")
