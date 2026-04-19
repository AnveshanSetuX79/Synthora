"""Health check and system status endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timezone
import os

# Try to import psutil, but make it optional
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from ..database import get_db
from ..scheduler import get_scheduler

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("/")
async def health_check(db: Session = Depends(get_db)):
    """Basic health check endpoint.
    
    Fast health check without expensive operations.
    Returns:
        Health status and timestamp
    """
    try:
        # Quick database ping (no complex queries)
        db.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": "LocalAI Leads Platform"
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy: {str(e)}"
        )


@router.get("/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check with component status.
    
    WARNING: This endpoint performs multiple checks and queries.
    Use /api/health for fast health checks during load testing.
    
    Returns:
        Detailed health information for all components
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "components": {}
    }
    
    # Check database
    try:
        db.execute(text("SELECT 1"))
        health_status["components"]["database"] = {
            "status": "up",
            "message": "Database connection successful"
        }
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["components"]["database"] = {
            "status": "down",
            "message": f"Database error: {str(e)}"
        }
    
    # Check scheduler
    try:
        scheduler = get_scheduler()
        if scheduler and scheduler.running:
            jobs = scheduler.get_jobs()
            health_status["components"]["scheduler"] = {
                "status": "up",
                "message": f"Scheduler running with {len(jobs)} jobs",
                "jobs": [
                    {
                        "id": job.id,
                        "name": job.name,
                        "next_run": job.next_run_time.isoformat() if job.next_run_time else None
                    }
                    for job in jobs
                ]
            }
        else:
            health_status["status"] = "degraded"
            health_status["components"]["scheduler"] = {
                "status": "down",
                "message": "Scheduler not running"
            }
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["components"]["scheduler"] = {
            "status": "error",
            "message": f"Scheduler error: {str(e)}"
        }
    
    # Check system resources
    try:
        if PSUTIL_AVAILABLE:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            health_status["components"]["system"] = {
                "status": "up",
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_mb": memory.available / (1024 * 1024),
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / (1024 * 1024 * 1024)
            }
            
            # Warn if resources are low
            if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
                health_status["status"] = "degraded"
                health_status["components"]["system"]["warning"] = "High resource usage"
        else:
            health_status["components"]["system"] = {
                "status": "unknown",
                "message": "psutil not installed - install with: pip install psutil"
            }
    except Exception as e:
        health_status["components"]["system"] = {
            "status": "error",
            "message": f"System check error: {str(e)}"
        }
    
    # Check environment
    health_status["components"]["environment"] = {
        "status": "up",
        "python_version": os.sys.version.split()[0],
        "environment": os.getenv("ENVIRONMENT", "development")
    }
    
    return health_status


@router.get("/readiness")
async def readiness_check(db: Session = Depends(get_db)):
    """Readiness check for load balancers.
    
    Returns 200 if service is ready to accept traffic.
    Returns 503 if service is not ready.
    """
    try:
        # Check critical components
        db.execute(text("SELECT 1"))
        
        return {
            "ready": True,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service not ready: {str(e)}"
        )


@router.get("/liveness")
async def liveness_check():
    """Liveness check for container orchestration.
    
    Returns 200 if service is alive.
    Should only fail if service needs to be restarted.
    """
    return {
        "alive": True,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/metrics")
async def get_metrics(db: Session = Depends(get_db)):
    """Get basic system metrics.
    
    Returns:
        System metrics for monitoring
    """
    try:
        metrics = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "system": {},
            "application": {}
        }
        
        # System metrics (if psutil available)
        if PSUTIL_AVAILABLE:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            metrics["system"] = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used_mb": memory.used / (1024 * 1024),
                "memory_available_mb": memory.available / (1024 * 1024),
                "disk_percent": disk.percent,
                "disk_used_gb": disk.used / (1024 * 1024 * 1024),
                "disk_free_gb": disk.free / (1024 * 1024 * 1024)
            }
        else:
            metrics["system"] = {
                "message": "psutil not installed - system metrics unavailable"
            }
        
        # Database metrics
        from ..models.user import User
        from ..models.deal import Deal
        from ..models.failure_log import FailureLog
        
        total_users = db.query(User).count()
        total_deals = db.query(Deal).count()
        pending_failures = db.query(FailureLog).filter(
            FailureLog.status.in_(['pending', 'retrying'])
        ).count()
        
        metrics["application"] = {
            "total_users": total_users,
            "total_deals": total_deals,
            "pending_failures": pending_failures
        }
        
        return metrics
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get metrics: {str(e)}"
        )
