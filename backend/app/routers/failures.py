"""Failure log management routes for admin."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel

from ..database import get_db
from ..models.failure_log import FailureLog
from ..middleware.auth import require_admin
from ..services.retry_service import RetryService

router = APIRouter(prefix="/api/admin/failures", tags=["admin", "failures"])


# Schemas
class FailureLogResponse(BaseModel):
    id: str
    service: str
    operation: str
    target: str
    attempt_number: int
    max_attempts: int
    error_message: Optional[str]
    error_code: Optional[str]
    status: str
    next_retry_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime]
    resolved_by: Optional[str]
    admin_notified: bool
    fallback_attempted: bool


class RetryRequest(BaseModel):
    failure_log_id: str


class ResolveRequest(BaseModel):
    failure_log_id: str


@router.get("/logs")
async def get_failure_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    service: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all failure logs with filtering.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        service: Filter by service (sms, email, payment)
        status: Filter by status (pending, retrying, failed, resolved, fallback)
        search: Search in target or error message
        
    Returns:
        List of failure logs with pagination info
    """
    try:
        query = db.query(FailureLog)
        
        # Apply filters
        if service:
            query = query.filter(FailureLog.service == service)
        
        if status:
            query = query.filter(FailureLog.status == status)
        
        if search:
            query = query.filter(
                or_(
                    FailureLog.target.ilike(f"%{search}%"),
                    FailureLog.error_message.ilike(f"%{search}%")
                )
            )
        
        # Get total count
        total = query.count()
        
        # Get paginated results
        logs = query.order_by(FailureLog.created_at.desc()).offset(skip).limit(limit).all()
        
        return {
            "total": total,
            "logs": [
                {
                    "id": log.id,
                    "service": log.service,
                    "operation": log.operation,
                    "target": log.target,
                    "attempt_number": log.attempt_number,
                    "max_attempts": log.max_attempts,
                    "error_message": log.error_message,
                    "error_code": log.error_code,
                    "status": log.status,
                    "next_retry_at": log.next_retry_at.isoformat() if log.next_retry_at else None,
                    "created_at": log.created_at.isoformat(),
                    "updated_at": log.updated_at.isoformat(),
                    "resolved_at": log.resolved_at.isoformat() if log.resolved_at else None,
                    "resolved_by": log.resolved_by,
                    "admin_notified": log.admin_notified,
                    "fallback_attempted": log.fallback_attempted,
                    "metadata": log.failure_metadata  # Renamed from 'metadata'
                }
                for log in logs
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch failure logs: {str(e)}")


@router.get("/stats")
async def get_failure_stats(
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get failure statistics.
    
    Returns:
        Statistics about failures by service and status
    """
    try:
        # Total failures
        total_failures = db.query(func.count(FailureLog.id)).scalar() or 0
        
        # By status
        pending = db.query(func.count(FailureLog.id)).filter(FailureLog.status == "pending").scalar() or 0
        retrying = db.query(func.count(FailureLog.id)).filter(FailureLog.status == "retrying").scalar() or 0
        failed = db.query(func.count(FailureLog.id)).filter(FailureLog.status == "failed").scalar() or 0
        resolved = db.query(func.count(FailureLog.id)).filter(FailureLog.status == "resolved").scalar() or 0
        fallback = db.query(func.count(FailureLog.id)).filter(FailureLog.status == "fallback").scalar() or 0
        
        # By service
        sms_failures = db.query(func.count(FailureLog.id)).filter(FailureLog.service == "sms").scalar() or 0
        email_failures = db.query(func.count(FailureLog.id)).filter(FailureLog.service == "email").scalar() or 0
        payment_failures = db.query(func.count(FailureLog.id)).filter(FailureLog.service == "payment").scalar() or 0
        
        # Requiring attention (pending or retrying)
        requiring_attention = pending + retrying
        
        # Admin notifications sent
        admin_notified = db.query(func.count(FailureLog.id)).filter(FailureLog.admin_notified == True).scalar() or 0
        
        return {
            "total_failures": total_failures,
            "by_status": {
                "pending": pending,
                "retrying": retrying,
                "failed": failed,
                "resolved": resolved,
                "fallback": fallback
            },
            "by_service": {
                "sms": sms_failures,
                "email": email_failures,
                "payment": payment_failures
            },
            "requiring_attention": requiring_attention,
            "admin_notified": admin_notified
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch failure stats: {str(e)}")


@router.post("/retry")
async def manual_retry(
    request: RetryRequest,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Manually retry a failed operation.
    
    Args:
        request: Retry request with failure_log_id
        
    Returns:
        Success message
    """
    try:
        retry_service = RetryService(db)
        success = retry_service.manual_retry(request.failure_log_id, current_user["user_id"])
        
        if success:
            return {
                "message": "Retry initiated successfully",
                "failure_log_id": request.failure_log_id
            }
        else:
            raise HTTPException(status_code=404, detail="Failure log not found")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retry: {str(e)}")


@router.post("/resolve")
async def resolve_failure(
    request: ResolveRequest,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Manually resolve a failure.
    
    Args:
        request: Resolve request with failure_log_id
        
    Returns:
        Success message
    """
    try:
        retry_service = RetryService(db)
        success = retry_service.resolve_failure(request.failure_log_id, current_user["user_id"])
        
        if success:
            return {
                "message": "Failure resolved successfully",
                "failure_log_id": request.failure_log_id
            }
        else:
            raise HTTPException(status_code=404, detail="Failure log not found")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resolve: {str(e)}")


@router.get("/logs/{failure_log_id}")
async def get_failure_log(
    failure_log_id: str,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific failure log.
    
    Args:
        failure_log_id: Failure log ID
        
    Returns:
        Detailed failure log information
    """
    try:
        log = db.query(FailureLog).filter(FailureLog.id == failure_log_id).first()
        
        if not log:
            raise HTTPException(status_code=404, detail="Failure log not found")
        
        return {
            "id": log.id,
            "service": log.service,
            "operation": log.operation,
            "target": log.target,
            "attempt_number": log.attempt_number,
            "max_attempts": log.max_attempts,
            "error_message": log.error_message,
            "error_code": log.error_code,
            "metadata": log.failure_metadata,  # Renamed from 'metadata'
            "status": log.status,
            "next_retry_at": log.next_retry_at.isoformat() if log.next_retry_at else None,
            "created_at": log.created_at.isoformat(),
            "updated_at": log.updated_at.isoformat(),
            "resolved_at": log.resolved_at.isoformat() if log.resolved_at else None,
            "resolved_by": log.resolved_by,
            "admin_notified": log.admin_notified,
            "fallback_attempted": log.fallback_attempted
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch failure log: {str(e)}")
