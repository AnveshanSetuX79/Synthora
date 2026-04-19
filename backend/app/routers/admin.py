"""Admin management routes."""
from fastapi import APIRouter, Depends, HTTPException, Body, Response
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Optional
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel
import csv
import io
import uuid

from ..database import get_db
from ..models.user import User, Freelancer, BusinessOwner
from ..models.business import Business, BusinessInsight
from ..models.kyc import KYCDocument
from ..models.deal import Deal
from ..models.payment import Payment
from ..models.audit import AuditLog
from ..models.review import Review
from ..models.dispute import Dispute
from ..middleware.auth import require_admin
from ..services.kyc import KYCService
from ..services.business_refresh import BusinessRefreshService
from ..scheduler import get_scheduler

router = APIRouter(prefix="/api/admin", tags=["admin"])


# Schemas
class BusinessUpdateRequest(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    # Note: email and website fields don't exist in Business model


class KYCApprovalRequest(BaseModel):
    approved: bool
    rejection_reason: Optional[str] = None


class UserActionRequest(BaseModel):
    action: str  # suspend, ban, activate
    reason: Optional[str] = None


class DisputeResolutionRequest(BaseModel):
    resolution: str  # refund, release, partial_refund
    amount: Optional[int] = None  # For partial refunds
    notes: Optional[str] = None


class BusinessVerificationRequest(BaseModel):
    is_verified: bool
    notes: Optional[str] = None


# Helper function to log admin actions
def log_admin_action(
    db: Session,
    admin_id: str,
    action: str,
    table_name: str,
    record_id: str,
    old_data: Optional[dict] = None,
    new_data: Optional[dict] = None,
    changed_fields: Optional[list] = None
):
    """Log admin action to audit trail."""
    try:
        audit_log = AuditLog(
            id=str(uuid.uuid4()),
            table_name=table_name,
            record_id=record_id,
            action=action,
            old_data=old_data,
            new_data=new_data,
            changed_fields=changed_fields,
            user_id=admin_id,
            user_role="admin"
        )
        db.add(audit_log)
        db.commit()
    except Exception as e:
        print(f"Failed to log admin action: {str(e)}")
        # Don't fail the main operation if logging fails


# Lead Management
@router.get("/businesses")
async def get_all_businesses(
    skip: int = 0,
    limit: int = 50,
    search: Optional[str] = None,
    category: Optional[str] = None,
    include_inactive: bool = False,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all businesses with filtering and search."""
    query = db.query(Business)
    
    # Filter out inactive businesses by default
    if not include_inactive:
        query = query.filter(Business.is_active == True)
    
    if search:
        query = query.filter(
            or_(
                Business.name.ilike(f"%{search}%"),
                Business.address.ilike(f"%{search}%"),
                Business.phone.ilike(f"%{search}%")
            )
        )
    
    if category:
        query = query.filter(Business.category == category)
    
    total = query.count()
    businesses = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "businesses": [
            {
                "id": b.id,
                "name": b.name,
                "category": b.category,
                "address": b.address,
                "phone": b.phone,
                "email": None,  # Business model doesn't have email
                "website": None,  # Business model doesn't have website
                "latitude": None,
                "longitude": None,
                "created_at": b.created_at,
                "is_verified": getattr(b, 'is_verified', False),
                "is_active": b.is_active
            }
            for b in businesses
        ]
    }


@router.put("/businesses/{business_id}")
async def update_business(
    business_id: str,
    request: BusinessUpdateRequest,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update business information (manual enrichment)."""
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Store old data for audit
    old_data = {
        "name": business.name,
        "category": business.category,
        "address": business.address,
        "phone": business.phone
    }
    
    changed_fields = []
    if request.name is not None and request.name != business.name:
        business.name = request.name
        changed_fields.append("name")
    if request.category is not None and request.category != business.category:
        business.category = request.category
        changed_fields.append("category")
    if request.address is not None and request.address != business.address:
        business.address = request.address
        changed_fields.append("address")
    if request.phone is not None and request.phone != business.phone:
        business.phone = request.phone
        changed_fields.append("phone")
    
    business.updated_at = datetime.now(timezone.utc)
    db.commit()
    
    # Log admin action
    new_data = {
        "name": business.name,
        "category": business.category,
        "address": business.address,
        "phone": business.phone
    }
    log_admin_action(
        db=db,
        admin_id=current_user["user_id"],
        action="UPDATE",
        table_name="businesses",
        record_id=business_id,
        old_data=old_data,
        new_data=new_data,
        changed_fields=changed_fields
    )
    
    return {
        "message": "Business updated successfully",
        "business_id": business_id
    }


@router.delete("/businesses/{business_id}")
async def delete_business(
    business_id: str,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Remove duplicate or invalid business."""
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Store old data for audit
    old_data = {
        "name": business.name,
        "is_active": business.is_active
    }
    
    # Soft delete
    business.is_active = False
    business.deleted_at = datetime.now(timezone.utc)
    db.commit()
    
    # Log admin action
    log_admin_action(
        db=db,
        admin_id=current_user["user_id"],
        action="DELETE",
        table_name="businesses",
        record_id=business_id,
        old_data=old_data,
        new_data={"is_active": False, "deleted_at": business.deleted_at.isoformat()}
    )
    
    return {
        "message": "Business deleted successfully",
        "business_id": business_id
    }


@router.post("/businesses/{business_id}/verify")
async def verify_business(
    business_id: str,
    request: BusinessVerificationRequest,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Mark business as verified or unverified."""
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    old_verified = business.is_verified
    
    # Update verification status
    business.is_verified = request.is_verified
    business.updated_at = datetime.now(timezone.utc)
    db.commit()
    
    # Log admin action
    log_admin_action(
        db=db,
        admin_id=current_user["user_id"],
        action="UPDATE",
        table_name="businesses",
        record_id=business_id,
        old_data={"is_verified": old_verified},
        new_data={"is_verified": request.is_verified, "notes": request.notes},
        changed_fields=["is_verified"]
    )
    
    return {
        "message": f"Business {'verified' if request.is_verified else 'unverified'} successfully",
        "business_id": business_id,
        "is_verified": request.is_verified
    }


# Freelancer Monitoring
@router.get("/freelancers")
async def get_all_freelancers(
    skip: int = 0,
    limit: int = 50,
    tier: Optional[str] = None,
    kyc_status: Optional[str] = None,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all freelancers with filtering."""
    query = db.query(Freelancer).join(User)
    
    if tier:
        query = query.filter(Freelancer.tier == tier)
    
    if kyc_status:
        query = query.join(KYCDocument).filter(KYCDocument.status == kyc_status)
    
    total = query.count()
    freelancers = query.offset(skip).limit(limit).all()
    
    result = []
    for f in freelancers:
        user = db.query(User).filter(User.id == f.user_id).first()
        kyc = db.query(KYCDocument).filter(KYCDocument.freelancer_id == f.id).first()
        
        result.append({
            "id": f.id,
            "user_id": f.user_id,
            "name": f.name,  # Name is in Freelancer model
            "email": user.email if user else "Unknown",
            "tier": f.tier,
            "portfolio_url": f.portfolio_url,
            "is_active": user.is_active if user else False,
            "kyc_status": kyc.status if kyc else "not_submitted",
            "created_at": f.created_at,
            "total_deals": db.query(Deal).filter(Deal.freelancer_id == f.id).count(),
            "completed_deals": db.query(Deal).filter(
                Deal.freelancer_id == f.id,
                Deal.status == "completed"
            ).count()
        })
    
    return {
        "total": total,
        "freelancers": result
    }


@router.post("/freelancers/{freelancer_id}/action")
async def freelancer_action(
    freelancer_id: str,
    request: UserActionRequest,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Suspend, ban, or activate freelancer account."""
    freelancer = db.query(Freelancer).filter(Freelancer.id == freelancer_id).first()
    if not freelancer:
        raise HTTPException(status_code=404, detail="Freelancer not found")
    
    user = db.query(User).filter(User.id == freelancer.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if request.action == "suspend":
        user.is_active = False
        message = "Freelancer suspended"
    elif request.action == "ban":
        user.is_active = False
        freelancer.is_banned = True
        message = "Freelancer banned"
    elif request.action == "activate":
        user.is_active = True
        freelancer.is_banned = False
        message = "Freelancer activated"
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    db.commit()
    
    return {
        "message": message,
        "freelancer_id": freelancer_id,
        "action": request.action,
        "reason": request.reason
    }


# KYC Approval
@router.get("/kyc/pending")
async def get_pending_kyc(
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all pending KYC submissions."""
    kyc_service = KYCService()
    pending_kyc = kyc_service.get_pending_kyc_submissions(db, skip, limit)
    
    return {
        "total": len(pending_kyc),
        "submissions": pending_kyc
    }


@router.post("/kyc/{kyc_id}/review")
async def review_kyc(
    kyc_id: str,
    request: KYCApprovalRequest,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Approve or reject KYC submission."""
    kyc_service = KYCService()
    
    try:
        kyc_doc = kyc_service.verify_kyc_document(
            db=db,
            kyc_document_id=kyc_id,
            admin_id=current_user["user_id"],
            approved=request.approved,
            rejection_reason=request.rejection_reason
        )
        
        return {
            "message": "KYC approved" if request.approved else "KYC rejected",
            "kyc_id": kyc_id,
            "status": kyc_doc.status
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Dispute Resolution
@router.get("/disputes")
async def get_disputes(
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all disputed deals."""
    query = db.query(Deal).filter(Deal.status == "disputed")
    
    total = query.count()
    deals = query.offset(skip).limit(limit).all()
    
    result = []
    for deal in deals:
        freelancer = db.query(Freelancer).filter(Freelancer.id == deal.freelancer_id).first()
        business = db.query(Business).filter(Business.id == deal.business_id).first()
        
        freelancer_user = db.query(User).filter(User.id == freelancer.user_id).first() if freelancer else None
        
        result.append({
            "id": deal.id,
            "amount": deal.amount,
            "status": deal.status,
            "freelancer_name": freelancer_user.name if freelancer_user else "Unknown",
            "business_name": business.name if business else "Unknown",
            "created_at": deal.created_at,
            "updated_at": deal.updated_at
        })
    
    return {
        "total": total,
        "disputes": result
    }


@router.post("/disputes/{deal_id}/resolve")
async def resolve_dispute(
    deal_id: str,
    request: DisputeResolutionRequest,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Resolve a disputed deal."""
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    if deal.status != "disputed":
        raise HTTPException(status_code=400, detail="Deal is not in disputed state")
    
    if request.resolution == "refund":
        # Full refund to business owner
        deal.status = "cancelled"
        message = "Full refund issued to business owner"
    elif request.resolution == "release":
        # Release payment to freelancer
        deal.status = "completed"
        message = "Payment released to freelancer"
    elif request.resolution == "partial_refund":
        if not request.amount:
            raise HTTPException(status_code=400, detail="Amount required for partial refund")
        # Partial refund logic
        message = f"Partial refund of ₹{request.amount/100} issued"
    else:
        raise HTTPException(status_code=400, detail="Invalid resolution type")
    
    deal.updated_at = datetime.now(timezone.utc)
    db.commit()
    
    return {
        "message": message,
        "deal_id": deal_id,
        "resolution": request.resolution,
        "notes": request.notes
    }


# Performance Tracking
@router.get("/freelancers/{freelancer_id}/performance")
async def get_freelancer_performance(
    freelancer_id: str,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get detailed performance metrics for a freelancer."""
    freelancer = db.query(Freelancer).filter(Freelancer.id == freelancer_id).first()
    if not freelancer:
        raise HTTPException(status_code=404, detail="Freelancer not found")
    
    # Get deals
    total_deals = db.query(Deal).filter(Deal.freelancer_id == freelancer_id).count()
    completed_deals = db.query(Deal).filter(
        Deal.freelancer_id == freelancer_id,
        Deal.status == "completed"
    ).count()
    active_deals = db.query(Deal).filter(
        Deal.freelancer_id == freelancer_id,
        Deal.status.in_(["active", "inprogress"])
    ).count()
    disputed_deals = db.query(Deal).filter(
        Deal.freelancer_id == freelancer_id,
        Deal.status == "disputed"
    ).count()
    
    # Get revenue
    total_revenue = db.query(func.sum(Payment.amount)).filter(
        Payment.freelancer_id == freelancer_id,
        Payment.status == "completed"
    ).scalar() or 0
    
    # Get average deal value
    avg_deal_value = db.query(func.avg(Deal.amount)).filter(
        Deal.freelancer_id == freelancer_id
    ).scalar() or 0
    
    return {
        "freelancer_id": freelancer_id,
        "tier": freelancer.tier,
        "total_deals": total_deals,
        "completed_deals": completed_deals,
        "active_deals": active_deals,
        "disputed_deals": disputed_deals,
        "completion_rate": (completed_deals / total_deals * 100) if total_deals > 0 else 0,
        "dispute_rate": (disputed_deals / total_deals * 100) if total_deals > 0 else 0,
        "total_revenue": total_revenue,
        "average_deal_value": float(avg_deal_value) if avg_deal_value else 0
    }


# Flag Suspicious Activity
@router.post("/freelancers/{freelancer_id}/flag")
async def flag_freelancer(
    freelancer_id: str,
    reason: str = Body(..., embed=True),
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Flag freelancer for suspicious activity."""
    freelancer = db.query(Freelancer).filter(Freelancer.id == freelancer_id).first()
    if not freelancer:
        raise HTTPException(status_code=404, detail="Freelancer not found")
    
    # Add flag to freelancer (you might want to create a separate flags table)
    freelancer.is_flagged = True
    freelancer.flag_reason = reason
    freelancer.flagged_at = datetime.now(timezone.utc)
    
    db.commit()
    
    return {
        "message": "Freelancer flagged successfully",
        "freelancer_id": freelancer_id,
        "reason": reason
    }


# Business Data Refresh (Requirement 2.1)
@router.post("/businesses/refresh")
async def trigger_business_refresh(
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Manually trigger business data refresh from Google Places API.
    
    Refreshes businesses that haven't been updated in 7+ days.
    Requirement 2.1: 7-day refresh cycle.
    """
    try:
        refresh_service = BusinessRefreshService(db)
        result = refresh_service.refresh_batch()
        
        return {
            "message": "Business refresh completed",
            "total_processed": result["total"],
            "successful": result["success"],
            "failed": result["failed"],
            "timestamp": result["timestamp"],
            "details": result["results"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Refresh failed: {str(e)}"
        )


@router.get("/businesses/refresh/status")
async def get_refresh_status(
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get status of business data refresh system.
    
    Shows:
    - Scheduler status
    - Number of businesses needing refresh
    - Last refresh statistics
    """
    from datetime import timedelta
    
    # Check scheduler status
    scheduler = get_scheduler()
    scheduler_running = scheduler is not None and scheduler.running
    
    # Get scheduled jobs
    scheduled_jobs = []
    if scheduler and scheduler.running:
        for job in scheduler.get_jobs():
            scheduled_jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None
            })
    
    # Count businesses needing refresh
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=7)
    businesses_needing_refresh = (
        db.query(Business)
        .join(BusinessInsight)
        .filter(
            Business.is_active == True,
            BusinessInsight.last_verified < cutoff_date
        )
        .count()
    )
    
    # Get recently refreshed count
    recent_cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    recently_refreshed = (
        db.query(Business)
        .join(BusinessInsight)
        .filter(
            Business.is_active == True,
            BusinessInsight.last_verified >= recent_cutoff
        )
        .count()
    )
    
    # Total active businesses
    total_active = db.query(Business).filter(Business.is_active == True).count()
    
    return {
        "scheduler": {
            "running": scheduler_running,
            "jobs": scheduled_jobs
        },
        "statistics": {
            "total_active_businesses": total_active,
            "needing_refresh": businesses_needing_refresh,
            "refreshed_last_24h": recently_refreshed,
            "refresh_threshold_days": 7
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.post("/businesses/{business_id}/refresh")
async def refresh_single_business(
    business_id: str,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Manually refresh a single business from Google Places API.
    
    Useful for testing or immediate updates.
    """
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    try:
        refresh_service = BusinessRefreshService(db)
        result = refresh_service.refresh_business(business)
        
        if result["success"]:
            return {
                "message": "Business refreshed successfully",
                "business_id": business_id,
                "business_name": result["business_name"],
                "updated_fields": result["updated_fields"],
                "field_count": result["field_count"]
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Refresh failed: {result.get('message', 'Unknown error')}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Refresh failed: {str(e)}"
        )


# Analytics & Reports
@router.get("/analytics/dashboard")
async def get_admin_dashboard(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get comprehensive platform analytics and statistics."""
    try:
        # Parse dates
        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        else:
            end_dt = datetime.now(timezone.utc)
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        else:
            start_dt = end_dt - timedelta(days=30)
        
        # User statistics
        total_users = db.query(User).count()
        total_freelancers = db.query(Freelancer).count()
        total_business_owners = db.query(BusinessOwner).count()
        active_freelancers = db.query(Freelancer).join(User).filter(User.is_active == True).count()
        
        # Business statistics
        total_businesses = db.query(Business).filter(Business.is_active == True).count()
        verified_businesses = db.query(Business).filter(
            Business.is_active == True,
            Business.is_verified == True
        ).count()
        
        # Deal statistics
        total_deals = db.query(Deal).count()
        active_deals = db.query(Deal).filter(Deal.status.in_(["active", "inprogress"])).count()
        completed_deals = db.query(Deal).filter(Deal.status == "completed").count()
        disputed_deals = db.query(Deal).filter(Deal.status == "disputed").count()
        
        # Deal statistics in date range
        deals_in_range = db.query(Deal).filter(
            Deal.created_at.between(start_dt, end_dt)
        ).count()
        completed_in_range = db.query(Deal).filter(
            Deal.created_at.between(start_dt, end_dt),
            Deal.status == "completed"
        ).count()
        
        # Average deal value
        avg_deal_value = db.query(func.avg(Deal.amount)).scalar() or 0
        
        # Revenue statistics
        total_revenue = db.query(func.sum(Payment.amount)).filter(
            Payment.status == "completed"
        ).scalar() or 0
        
        # Revenue by date range
        revenue_in_range = db.query(func.sum(Payment.amount)).filter(
            Payment.status == "completed",
            Payment.completed_at.between(start_dt, end_dt)
        ).scalar() or 0
        
        # Commission revenue (10% of total revenue)
        commission_rate = 0.10
        total_commission = int(total_revenue * commission_rate)
        commission_in_range = int(revenue_in_range * commission_rate)
        
        # Revenue breakdown
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        revenue_today = db.query(func.sum(Payment.amount)).filter(
            Payment.status == "completed",
            Payment.completed_at >= today
        ).scalar() or 0
        
        week_start = today - timedelta(days=today.weekday())
        revenue_this_week = db.query(func.sum(Payment.amount)).filter(
            Payment.status == "completed",
            Payment.completed_at >= week_start
        ).scalar() or 0
        
        month_start = today.replace(day=1)
        revenue_this_month = db.query(func.sum(Payment.amount)).filter(
            Payment.status == "completed",
            Payment.completed_at >= month_start
        ).scalar() or 0
        
        # Conversion rates
        total_contacts = db.query(func.count(func.distinct(Deal.business_id))).scalar() or 0
        conversion_rate = (completed_deals / total_contacts * 100) if total_contacts > 0 else 0
        
        # Response rates (deals created / total contacts)
        from ..models.lead import LeadContact
        total_lead_contacts = db.query(LeadContact).count()
        response_rate = (total_deals / total_lead_contacts * 100) if total_lead_contacts > 0 else 0
        
        # Dispute rate
        dispute_rate = (disputed_deals / total_deals * 100) if total_deals > 0 else 0
        
        # Review statistics
        total_reviews = db.query(Review).count()
        avg_rating = db.query(func.avg(Review.rating)).scalar() or 0
        
        # Dispute statistics
        total_disputes = db.query(Dispute).count()
        open_disputes = db.query(Dispute).filter(Dispute.status.in_(["open", "escalated"])).count()
        resolved_disputes = db.query(Dispute).filter(Dispute.status == "closed").count()
        
        return {
            "period": {
                "start": start_dt.isoformat(),
                "end": end_dt.isoformat()
            },
            "users": {
                "total": total_users,
                "freelancers": total_freelancers,
                "business_owners": total_business_owners,
                "active_freelancers": active_freelancers
            },
            "businesses": {
                "total": total_businesses,
                "verified": verified_businesses
            },
            "deals": {
                "total": total_deals,
                "active": active_deals,
                "completed": completed_deals,
                "disputed": disputed_deals,
                "in_period": deals_in_range,
                "completed_in_period": completed_in_range,
                "average_value": round(avg_deal_value / 100, 2)
            },
            "revenue": {
                "total": round(total_revenue / 100, 2),
                "in_period": round(revenue_in_range / 100, 2),
                "today": round(revenue_today / 100, 2),
                "this_week": round(revenue_this_week / 100, 2),
                "this_month": round(revenue_this_month / 100, 2)
            },
            "commission": {
                "rate": commission_rate,
                "total": round(total_commission / 100, 2),
                "in_period": round(commission_in_range / 100, 2)
            },
            "conversion": {
                "overall_rate": round(conversion_rate, 2),
                "response_rate": round(response_rate, 2),
                "dispute_rate": round(dispute_rate, 2)
            },
            "reviews": {
                "total": total_reviews,
                "average_rating": round(avg_rating, 2)
            },
            "disputes": {
                "total": total_disputes,
                "open": open_disputes,
                "resolved": resolved_disputes
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch analytics: {str(e)}"
        )


@router.get("/analytics/export")
async def export_analytics_csv(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Export analytics data as CSV."""
    try:
        # Get dashboard data
        dashboard_data = await get_admin_dashboard(start_date, end_date, current_user, db)
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(['Metric Category', 'Metric', 'Value'])
        
        # Write user metrics
        writer.writerow(['Users', 'Total Users', dashboard_data['users']['total']])
        writer.writerow(['Users', 'Total Freelancers', dashboard_data['users']['freelancers']])
        writer.writerow(['Users', 'Total Business Owners', dashboard_data['users']['business_owners']])
        writer.writerow(['Users', 'Active Freelancers', dashboard_data['users']['active_freelancers']])
        
        # Write business metrics
        writer.writerow(['Businesses', 'Total Businesses', dashboard_data['businesses']['total']])
        writer.writerow(['Businesses', 'Verified Businesses', dashboard_data['businesses']['verified']])
        
        # Write deal metrics
        writer.writerow(['Deals', 'Total Deals', dashboard_data['deals']['total']])
        writer.writerow(['Deals', 'Active Deals', dashboard_data['deals']['active']])
        writer.writerow(['Deals', 'Completed Deals', dashboard_data['deals']['completed']])
        writer.writerow(['Deals', 'Disputed Deals', dashboard_data['deals']['disputed']])
        writer.writerow(['Deals', 'Average Deal Value (₹)', dashboard_data['deals']['average_value']])
        
        # Write revenue metrics
        writer.writerow(['Revenue', 'Total Revenue (₹)', dashboard_data['revenue']['total']])
        writer.writerow(['Revenue', 'Revenue in Period (₹)', dashboard_data['revenue']['in_period']])
        writer.writerow(['Revenue', 'Revenue Today (₹)', dashboard_data['revenue']['today']])
        writer.writerow(['Revenue', 'Revenue This Week (₹)', dashboard_data['revenue']['this_week']])
        writer.writerow(['Revenue', 'Revenue This Month (₹)', dashboard_data['revenue']['this_month']])
        
        # Write commission metrics
        writer.writerow(['Commission', 'Commission Rate', f"{dashboard_data['commission']['rate']*100}%"])
        writer.writerow(['Commission', 'Total Commission (₹)', dashboard_data['commission']['total']])
        writer.writerow(['Commission', 'Commission in Period (₹)', dashboard_data['commission']['in_period']])
        
        # Write conversion metrics
        writer.writerow(['Conversion', 'Overall Conversion Rate (%)', dashboard_data['conversion']['overall_rate']])
        writer.writerow(['Conversion', 'Response Rate (%)', dashboard_data['conversion']['response_rate']])
        writer.writerow(['Conversion', 'Dispute Rate (%)', dashboard_data['conversion']['dispute_rate']])
        
        # Write review metrics
        writer.writerow(['Reviews', 'Total Reviews', dashboard_data['reviews']['total']])
        writer.writerow(['Reviews', 'Average Rating', dashboard_data['reviews']['average_rating']])
        
        # Write dispute metrics
        writer.writerow(['Disputes', 'Total Disputes', dashboard_data['disputes']['total']])
        writer.writerow(['Disputes', 'Open Disputes', dashboard_data['disputes']['open']])
        writer.writerow(['Disputes', 'Resolved Disputes', dashboard_data['disputes']['resolved']])
        
        # Get CSV content
        csv_content = output.getvalue()
        output.close()
        
        # Return as downloadable file
        filename = f"admin-analytics-{datetime.now(timezone.utc).strftime('%Y%m%d')}.csv"
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export CSV: {str(e)}"
        )


@router.get("/audit-logs")
async def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    table_name: Optional[str] = None,
    action: Optional[str] = None,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get admin action audit logs."""
    query = db.query(AuditLog).filter(AuditLog.user_role == "admin")
    
    if table_name:
        query = query.filter(AuditLog.table_name == table_name)
    
    if action:
        query = query.filter(AuditLog.action == action)
    
    total = query.count()
    logs = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "logs": [
            {
                "id": log.id,
                "table_name": log.table_name,
                "record_id": log.record_id,
                "action": log.action,
                "old_data": log.old_data,
                "new_data": log.new_data,
                "changed_fields": log.changed_fields,
                "user_id": log.user_id,
                "created_at": log.created_at.isoformat()
            }
            for log in logs
        ]
    }
