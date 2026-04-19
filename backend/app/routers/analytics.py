"""Analytics API endpoints for event tracking and metrics."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import logging

from ..database import get_db
from ..middleware.auth import get_current_user
from ..services.analytics import AnalyticsService, AnalyticsError
from ..models.user import Freelancer, User, BusinessOwner
from ..models.business import Business
from ..models.lead import Lead, LeadContact
from ..models.deal import Deal
from ..models.payment import Payment

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/analytics", tags=["analytics"])


# Request/Response Schemas

class TrackEventRequest(BaseModel):
    """Request schema for tracking an event."""
    event_type: str = Field(..., description="Event type: lead_viewed, demo_generated, demo_viewed, message_sent, deal_created, payment_completed")
    metadata: Optional[dict] = None


class TrackEventResponse(BaseModel):
    """Response schema for tracking an event."""
    success: bool
    event_id: str
    message: str


class ConversionFunnelResponse(BaseModel):
    """Response schema for conversion funnel."""
    success: bool
    funnel: dict


class FreelancerROIResponse(BaseModel):
    """Response schema for freelancer ROI."""
    success: bool
    roi_metrics: dict


class EventHistoryResponse(BaseModel):
    """Response schema for event history."""
    success: bool
    total: int
    events: list


class CategoryInsightsResponse(BaseModel):
    """Response schema for category insights."""
    success: bool
    insights: dict


# API Endpoints

@router.post("/track", response_model=TrackEventResponse)
async def track_event(
    request: TrackEventRequest = Body(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Track an analytics event.
    
    This endpoint tracks user actions for analytics and funnel analysis.
    
    **Requirements**: 10.1, 10.2
    
    Args:
        request: Event details (event_type, metadata)
        current_user: Authenticated user from JWT
        
    Returns:
        Event tracking confirmation
        
    Raises:
        400: Invalid event type
    """
    try:
        user_id = current_user.get("user_id")
        
        analytics_service = AnalyticsService()
        event = analytics_service.track_event(
            db=db,
            event_type=request.event_type,
            user_id=user_id,
            metadata=request.metadata
        )
        
        return TrackEventResponse(
            success=True,
            event_id=event.id,
            message="Event tracked successfully"
        )
        
    except AnalyticsError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "ANALYTICS_ERROR",
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Error tracking event: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": str(e)
            }
        )


@router.get("/funnel", response_model=ConversionFunnelResponse)
async def get_conversion_funnel(
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    category: Optional[str] = Query(None, description="Business category filter"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get conversion funnel analytics.
    
    Returns conversion rates for each stage:
    - Leads discovered → Leads contacted
    - Leads contacted → Demos viewed
    - Demos viewed → Deals created
    - Deals created → Payments completed
    
    **Requirements**: 10.3, 10.4, 39.1
    
    Args:
        start_date: Optional start date filter
        end_date: Optional end date filter
        category: Optional category filter
        current_user: Authenticated user from JWT
        
    Returns:
        Conversion funnel metrics
    """
    try:
        # Parse dates if provided
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        # For freelancers, filter by their ID
        freelancer_id = None
        if current_user.get("role") == "freelancer":
            user_id = current_user.get("user_id")
            freelancer = db.query(Freelancer).filter(Freelancer.user_id == user_id).first()
            if freelancer:
                freelancer_id = freelancer.id
        
        analytics_service = AnalyticsService()
        funnel = analytics_service.get_conversion_funnel(
            db=db,
            start_date=start_dt,
            end_date=end_dt,
            category=category,
            freelancer_id=freelancer_id
        )
        
        return ConversionFunnelResponse(
            success=True,
            funnel=funnel
        )
        
    except AnalyticsError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "ANALYTICS_ERROR",
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Error getting conversion funnel: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": str(e)
            }
        )


@router.get("/freelancer-roi", response_model=FreelancerROIResponse)
async def get_freelancer_roi(
    period: str = Query("Month", description="Period: Week, Month, Quarter, AllTime"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get ROI metrics for current freelancer.
    
    Returns metrics including:
    - Total earnings
    - Leads used
    - Cost per acquisition
    - Win rate
    - Average time to close
    - Expected close probability
    
    **Requirements**: 42.1, 42.2, 42.3, 42.4
    
    Args:
        period: Period for calculation (Week, Month, Quarter, AllTime)
        current_user: Authenticated user from JWT
        
    Returns:
        Freelancer ROI metrics
        
    Raises:
        403: User is not a freelancer
        404: Freelancer profile not found
    """
    try:
        # Verify user is a freelancer
        if current_user.get("role") != "freelancer":
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "FORBIDDEN",
                    "message": "Only freelancers can access ROI metrics"
                }
            )
        
        # Get freelancer
        user_id = current_user.get("user_id")
        freelancer = db.query(Freelancer).filter(Freelancer.user_id == user_id).first()
        
        if not freelancer:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "NOT_FOUND",
                    "message": "Freelancer profile not found"
                }
            )
        
        # Calculate ROI
        analytics_service = AnalyticsService()
        roi_metrics = analytics_service.calculate_freelancer_roi(
            db=db,
            freelancer_id=freelancer.id,
            period=period
        )
        
        return FreelancerROIResponse(
            success=True,
            roi_metrics=roi_metrics
        )
        
    except AnalyticsError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "ANALYTICS_ERROR",
                "message": str(e)
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting freelancer ROI: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": str(e)
            }
        )


@router.get("/events", response_model=EventHistoryResponse)
async def get_event_history(
    event_type: Optional[str] = Query(None, description="Event type filter"),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of events"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get event history with filters.
    
    **Requirements**: 10.1
    
    Args:
        event_type: Optional event type filter
        start_date: Optional start date filter
        end_date: Optional end date filter
        limit: Maximum number of events to return
        current_user: Authenticated user from JWT
        
    Returns:
        List of events
    """
    try:
        # Parse dates if provided
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        # For freelancers, filter by their user ID
        user_id = None
        if current_user.get("role") == "freelancer":
            user_id = current_user.get("user_id")
        
        analytics_service = AnalyticsService()
        events = analytics_service.get_event_history(
            db=db,
            event_type=event_type,
            user_id=user_id,
            start_date=start_dt,
            end_date=end_dt,
            limit=limit
        )
        
        return EventHistoryResponse(
            success=True,
            total=len(events),
            events=events
        )
        
    except AnalyticsError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "ANALYTICS_ERROR",
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Error getting event history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": str(e)
            }
        )


@router.get("/category-insights/{category}", response_model=CategoryInsightsResponse)
async def get_category_insights(
    category: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get conversion insights for a specific category.
    
    Returns insights like:
    - "Restaurants convert at 18% with avg deal value of ₹15,000"
    
    **Requirements**: 43.1, 43.2
    
    Args:
        category: Business category
        current_user: Authenticated user from JWT
        
    Returns:
        Category insights
    """
    try:
        analytics_service = AnalyticsService()
        insights = analytics_service.get_category_insights(db, category)
        
        return CategoryInsightsResponse(
            success=True,
            insights=insights
        )
        
    except AnalyticsError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "ANALYTICS_ERROR",
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Error getting category insights: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": str(e)
            }
        )


@router.get("/admin/dashboard")
async def get_admin_dashboard(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get admin dashboard metrics (optimized).
    
    Requirements: 24.1-24.11, 39.1, 39.2, 39.3, 39.4, 39.5
    """
    try:
        # Check if user is admin or founder
        role = current_user.get("role")
        if role not in ["admin", "founder"]:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Basic counts (fast queries)
        total_users = db.query(func.count(User.id)).scalar() or 0
        total_freelancers = db.query(func.count(Freelancer.id)).scalar() or 0
        total_business_owners = db.query(func.count(BusinessOwner.id)).scalar() or 0
        
        # Deal metrics
        total_deals = db.query(func.count(Deal.id)).scalar() or 0
        active_deals = db.query(func.count(Deal.id)).filter(
            Deal.status.in_(["active", "inprogress"])
        ).scalar() or 0
        completed_deals = db.query(func.count(Deal.id)).filter(
            Deal.status == "completed"
        ).scalar() or 0
        
        # Revenue metrics (simplified)
        total_revenue = db.query(func.sum(Deal.amount)).filter(
            Deal.status == "completed"
        ).scalar() or 0
        
        avg_deal_value = db.query(func.avg(Deal.amount)).filter(
            Deal.status == "completed"
        ).scalar() or 0
        
        # Simple time-based revenue (using deal completion)
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = now - timedelta(days=7)
        month_start = now - timedelta(days=30)
        
        revenue_today = db.query(func.sum(Deal.amount)).filter(
            and_(
                Deal.status == "completed",
                Deal.completed_at >= today_start
            )
        ).scalar() or 0
        
        revenue_this_week = db.query(func.sum(Deal.amount)).filter(
            and_(
                Deal.status == "completed",
                Deal.completed_at >= week_start
            )
        ).scalar() or 0
        
        revenue_this_month = db.query(func.sum(Deal.amount)).filter(
            and_(
                Deal.status == "completed",
                Deal.completed_at >= month_start
            )
        ).scalar() or 0
        
        # Overall conversion rate (simplified)
        total_leads = db.query(func.count(Lead.id)).scalar() or 0
        overall_conversion = (completed_deals / total_leads * 100) if total_leads > 0 else 0
        
        return {
            "users": {
                "total": total_users,
                "freelancers": total_freelancers,
                "business_owners": total_business_owners
            },
            "deals": {
                "total": total_deals,
                "active": active_deals,
                "completed": completed_deals,
                "average_value": round(float(avg_deal_value) / 100, 2) if avg_deal_value else 0
            },
            "revenue": {
                "total": round(total_revenue / 100, 2),
                "today": round(revenue_today / 100, 2),
                "this_week": round(revenue_this_week / 100, 2),
                "this_month": round(revenue_this_month / 100, 2)
            },
            "conversion": {
                "overall_rate": round(overall_conversion, 2),
                "freelancer_avg": 0,
                "business_response": 0
            },
            "metrics": {
                "businesses": {
                    "total": db.query(func.count(Business.id)).scalar() or 0
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching admin dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/founder/dashboard")
async def get_founder_dashboard(
    days: int = Query(30, description="Time range in days (7, 30, or 90)"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get founder business viability dashboard.
    
    Requirements: 37.1-37.14 (Founder Analytics Dashboard)
    
    Returns critical business metrics:
    - Response rate %
    - Demo → signup conversion
    - Signup → deal conversion
    - Average deal value
    - Revenue/day
    - Runway calculation
    - Cohort analysis
    - Geographic performance
    """
    try:
        # Check if user is founder
        role = current_user.get("role")
        if role != "founder":
            raise HTTPException(status_code=403, detail="Founder access required")
        
        # Calculate date range
        now = datetime.utcnow()
        start_date = now - timedelta(days=days)
        
        # 1. Response Rate (outreach → response)
        total_contacted = db.query(func.count(LeadContact.id)).filter(
            LeadContact.first_contact_at >= start_date
        ).scalar() or 0
        
        total_responded = db.query(func.count(LeadContact.id)).filter(
            and_(
                LeadContact.first_contact_at >= start_date,
                LeadContact.status.in_(["interested", "negotiating", "closed"])
            )
        ).scalar() or 0
        
        response_rate = (total_responded / total_contacted * 100) if total_contacted > 0 else 0
        
        # 2. Demo → Signup Conversion
        # Assuming demos_viewed is tracked in analytics_events
        from ..models.analytics import AnalyticsEvent
        demos_viewed = db.query(func.count(AnalyticsEvent.id)).filter(
            and_(
                AnalyticsEvent.event_type == "demo_viewed",
                AnalyticsEvent.timestamp >= start_date
            )
        ).scalar() or 0
        
        signups = db.query(func.count(BusinessOwner.id)).filter(
            BusinessOwner.created_at >= start_date
        ).scalar() or 0
        
        demo_to_signup = (signups / demos_viewed * 100) if demos_viewed > 0 else 0
        
        # 3. Signup → Deal Conversion
        deals_created = db.query(func.count(Deal.id)).filter(
            Deal.created_at >= start_date
        ).scalar() or 0
        
        signup_to_deal = (deals_created / signups * 100) if signups > 0 else 0
        
        # 4. Average Deal Value
        avg_deal_value = db.query(func.avg(Deal.amount)).filter(
            and_(
                Deal.status == "completed",
                Deal.completed_at >= start_date
            )
        ).scalar() or 0
        avg_deal_value = round(float(avg_deal_value) / 100, 2) if avg_deal_value else 0
        
        # 5. Revenue/Day
        total_revenue = db.query(func.sum(Deal.amount)).filter(
            and_(
                Deal.status == "completed",
                Deal.completed_at >= start_date
            )
        ).scalar() or 0
        total_revenue = round(float(total_revenue) / 100, 2) if total_revenue else 0
        revenue_per_day = round(total_revenue / days, 2) if days > 0 else 0
        
        # 6. Runway Calculation
        # Assuming monthly burn rate (you should configure this)
        monthly_burn = 50000  # ₹50,000 per month (configure based on actual costs)
        monthly_revenue = revenue_per_day * 30
        runway_months = round((monthly_revenue / monthly_burn) * 12, 1) if monthly_burn > 0 else 0
        
        # 7. Cohort Analysis by Tier
        cohorts = []
        for tier in ['new', 'verified', 'top_rated']:
            freelancer_count = db.query(func.count(Freelancer.id)).filter(
                Freelancer.tier == tier
            ).scalar() or 0
            
            tier_deals = db.query(func.count(Deal.id)).join(Freelancer).filter(
                and_(
                    Freelancer.tier == tier,
                    Deal.created_at >= start_date
                )
            ).scalar() or 0
            
            tier_completed = db.query(func.count(Deal.id)).join(Freelancer).filter(
                and_(
                    Freelancer.tier == tier,
                    Deal.status == "completed",
                    Deal.completed_at >= start_date
                )
            ).scalar() or 0
            
            completion_rate = round((tier_completed / tier_deals * 100), 1) if tier_deals > 0 else 0
            
            tier_avg_value = db.query(func.avg(Deal.amount)).join(Freelancer).filter(
                and_(
                    Freelancer.tier == tier,
                    Deal.status == "completed",
                    Deal.completed_at >= start_date
                )
            ).scalar() or 0
            tier_avg_value = round(float(tier_avg_value) / 100, 2) if tier_avg_value else 0
            
            tier_revenue = db.query(func.sum(Deal.amount)).join(Freelancer).filter(
                and_(
                    Freelancer.tier == tier,
                    Deal.status == "completed",
                    Deal.completed_at >= start_date
                )
            ).scalar() or 0
            tier_revenue = round(float(tier_revenue) / 100, 2) if tier_revenue else 0
            
            cohorts.append({
                "tier": tier,
                "freelancer_count": freelancer_count,
                "total_deals": tier_deals,
                "completion_rate": completion_rate,
                "avg_deal_value": tier_avg_value,
                "total_revenue": tier_revenue
            })
        
        # 8. Geographic Performance
        geographic = []
        cities = db.query(Business.city, func.count(Business.id)).group_by(Business.city).all()
        
        for city, business_count in cities[:10]:  # Top 10 cities
            city_deals = db.query(func.count(Deal.id)).join(Business).filter(
                and_(
                    Business.city == city,
                    Deal.created_at >= start_date
                )
            ).scalar() or 0
            
            city_conversion = round((city_deals / business_count * 100), 1) if business_count > 0 else 0
            
            city_avg_value = db.query(func.avg(Deal.amount)).join(Business).filter(
                and_(
                    Business.city == city,
                    Deal.status == "completed",
                    Deal.completed_at >= start_date
                )
            ).scalar() or 0
            city_avg_value = round(float(city_avg_value) / 100, 2) if city_avg_value else 0
            
            city_revenue = db.query(func.sum(Deal.amount)).join(Business).filter(
                and_(
                    Business.city == city,
                    Deal.status == "completed",
                    Deal.completed_at >= start_date
                )
            ).scalar() or 0
            city_revenue = round(float(city_revenue) / 100, 2) if city_revenue else 0
            
            geographic.append({
                "city": city,
                "total_businesses": business_count,
                "total_deals": city_deals,
                "conversion_rate": city_conversion,
                "avg_deal_value": city_avg_value,
                "total_revenue": city_revenue
            })
        
        # Sort by revenue
        geographic.sort(key=lambda x: x["total_revenue"], reverse=True)
        
        # Generate alerts for critical thresholds
        alerts = []
        if response_rate < 15:
            alerts.append(f"⚠️ Response rate ({response_rate:.1f}%) is below viable threshold (15%)")
        if demo_to_signup < 10:
            alerts.append(f"⚠️ Demo-to-signup conversion ({demo_to_signup:.1f}%) is below viable threshold (10%)")
        if signup_to_deal < 20:
            alerts.append(f"⚠️ Signup-to-deal conversion ({signup_to_deal:.1f}%) is below viable threshold (20%)")
        if runway_months < 6:
            alerts.append(f"⚠️ Runway ({runway_months} months) is below safe threshold (6 months)")
        
        return {
            "viability": {
                "response_rate": round(response_rate, 1),
                "demo_to_signup": round(demo_to_signup, 1),
                "signup_to_deal": round(signup_to_deal, 1),
                "total_contacted": total_contacted,
                "total_responded": total_responded,
                "demos_viewed": demos_viewed,
                "signups": signups,
                "deals_created": deals_created
            },
            "financial": {
                "avg_deal_value": avg_deal_value,
                "revenue_per_day": revenue_per_day,
                "monthly_burn": monthly_burn,
                "runway_months": runway_months,
                "total_revenue": total_revenue
            },
            "cohorts": cohorts,
            "geographic": geographic,
            "alerts": alerts,
            "time_range": {
                "days": days,
                "start_date": start_date.isoformat(),
                "end_date": now.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching founder dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
