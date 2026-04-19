"""Demo generation API endpoints.

This module provides endpoints for:
- Generating demo websites for businesses
- Retrieving demo URLs
- Tracking demo analytics
- Serving public demo pages with SEO-friendly URLs

Requirements: 5.1, 5.2, 5.3, 5.6, 5.8, 7.1, 7.4
"""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

from ..database import get_db
from ..models.business import Business
from ..models.demo import DemoWebsite
from ..models.analytics import AnalyticsEvent
from ..services.demo_generator import DemoGeneratorService, DemoGeneratorError
from ..middleware.auth import get_current_user
from ..models.user import User
from ..utils.slug import generate_demo_slug

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/demos", tags=["demos"])


# Request/Response schemas
class GenerateDemoRequest(BaseModel):
    """Request schema for demo generation."""
    business_id: str = Field(..., description="Business ID")
    template_type: str = Field(default="auto", description="Template type (auto, restaurant, school)")


class DemoResponse(BaseModel):
    """Response schema for demo details."""
    demo_id: str
    business_id: str
    demo_url: str
    template_type: str
    view_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class DemoAnalyticsResponse(BaseModel):
    """Response schema for demo analytics."""
    demo_id: str
    view_count: int
    claim_clicks: int
    last_viewed_at: Optional[datetime]
    created_at: datetime


@router.post("/generate", response_model=DemoResponse, status_code=status.HTTP_201_CREATED)
async def generate_demo(
    request: GenerateDemoRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a demo website for a business.
    
    Args:
        request: Demo generation request
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Demo details with URL
        
    Raises:
        HTTPException: If business not found or generation fails
    """
    try:
        # Get business details
        business = db.query(Business).filter(Business.id == request.business_id).first()
        if not business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business not found"
            )
        
        # Check if demo already exists
        existing_demo = db.query(DemoWebsite).filter(
            DemoWebsite.business_id == request.business_id
        ).first()
        
        if existing_demo:
            logger.info(f"Demo already exists for business {request.business_id}")
            return DemoResponse(
                demo_id=str(existing_demo.id),
                business_id=str(existing_demo.business_id),
                demo_url=f"/demos/{existing_demo.id}",
                template_type=existing_demo.template_type,
                view_count=existing_demo.view_count,
                created_at=existing_demo.created_at
            )
        
        # Determine template type
        template_type = request.template_type
        if template_type == "auto":
            template_type = business.category.lower() if business.category else "restaurant"
        
        # Get rating and review count from insights
        rating = None
        review_count = 0
        if business.insights:
            rating = business.insights.rating
            review_count = business.insights.review_count or 0
        
        # Generate demo HTML
        demo_service = DemoGeneratorService()
        html_content = demo_service.generate_demo(
            business_name=business.name,
            category=business.category or "restaurant",
            address=business.address,
            city=business.city,
            phone=business.phone,
            rating=rating,
            review_count=review_count,
            description=None  # Will use default
        )
        
        # Generate SEO-friendly slug
        slug = generate_demo_slug(business.name, business.city, business.category or "restaurant")
        
        # Ensure IDs are strings - handle both dict and object types
        business_id_str = str(business.id) if business.id else None
        
        # current_user might be a dict or User object
        if isinstance(current_user, dict):
            user_id_str = str(current_user.get('id')) if current_user.get('id') else None
        else:
            user_id_str = str(current_user.id) if current_user.id else None
        
        # Create demo record
        demo = DemoWebsite(
            id=str(uuid.uuid4()),
            business_id=business_id_str,
            template_type=template_type,
            html_content=html_content,
            slug=slug,
            view_count=0,
            claim_clicks=0,
            created_by=user_id_str
        )
        
        db.add(demo)
        db.commit()
        db.refresh(demo)
        
        # Track analytics event
        event = AnalyticsEvent(
            id=uuid.uuid4(),
            event_type="demo_generated",
            user_id=user_id_str,
            metadata={
                "demo_id": str(demo.id),
                "business_id": str(business.id),
                "template_type": template_type
            }
        )
        db.add(event)
        db.commit()
        
        logger.info(f"Generated demo {demo.id} for business {business.id}")
        
        return DemoResponse(
            demo_id=str(demo.id),
            business_id=str(demo.business_id),
            demo_url=f"/demos/{demo.id}",
            template_type=demo.template_type,
            view_count=demo.view_count,
            created_at=demo.created_at
        )
        
    except DemoGeneratorError as e:
        logger.error(f"Demo generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate demo: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error generating demo: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate demo"
        )


@router.get("/{business_id}", response_model=DemoResponse)
async def get_demo(
    business_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get demo details for a business.
    
    Args:
        business_id: Business ID
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Demo details
        
    Raises:
        HTTPException: If demo not found
    """
    demo = db.query(DemoWebsite).filter(
        DemoWebsite.business_id == business_id
    ).first()
    
    if not demo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demo not found for this business"
        )
    
    return DemoResponse(
        demo_id=str(demo.id),
        business_id=str(demo.business_id),
        demo_url=f"/demos/{demo.id}",
        template_type=demo.template_type,
        view_count=demo.view_count,
        created_at=demo.created_at
    )


@router.get("/{business_id}/analytics", response_model=DemoAnalyticsResponse)
async def get_demo_analytics(
    business_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get analytics for a demo.
    
    Args:
        business_id: Business ID
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Demo analytics
        
    Raises:
        HTTPException: If demo not found
    """
    demo = db.query(DemoWebsite).filter(
        DemoWebsite.business_id == business_id
    ).first()
    
    if not demo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demo not found for this business"
        )
    
    return DemoAnalyticsResponse(
        demo_id=str(demo.id),
        view_count=demo.view_count,
        claim_clicks=demo.claim_clicks,
        last_viewed_at=demo.last_viewed_at,
        created_at=demo.created_at
    )


# Public endpoint - no authentication required
@router.get("/public/{demo_id}", response_class=HTMLResponse)
async def serve_demo(
    demo_id: str,
    db: Session = Depends(get_db)
):
    """Serve demo HTML (public endpoint).
    
    Args:
        demo_id: Demo ID
        db: Database session
        
    Returns:
        HTML content
        
    Raises:
        HTTPException: If demo not found
    """
    demo = db.query(DemoWebsite).filter(DemoWebsite.id == demo_id).first()
    
    if not demo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demo not found"
        )
    
    # Increment view count
    demo.view_count += 1
    demo.last_viewed_at = datetime.utcnow()
    db.commit()
    
    # Track analytics event
    event = AnalyticsEvent(
        id=uuid.uuid4(),
        event_type="demo_viewed",
        user_id=None,  # Public view
        metadata={
            "demo_id": str(demo.id),
            "business_id": str(demo.business_id)
        }
    )
    db.add(event)
    db.commit()
    
    logger.info(f"Demo {demo_id} viewed (total views: {demo.view_count})")
    
    return HTMLResponse(content=demo.html_content)



# SEO-friendly public endpoint - no authentication required
@router.get("/view/{city}/{category}/{slug}", response_class=HTMLResponse)
async def serve_demo_seo(
    city: str,
    category: str,
    slug: str,
    db: Session = Depends(get_db),
    request: Request = None
):
    """Serve demo HTML with SEO-friendly URL (public endpoint).
    
    URL format: /api/demos/view/{city}/{category}/{business-name}
    Example: /api/demos/view/bangalore/restaurant/bo-tai
    
    Args:
        city: City slug
        category: Category slug
        slug: Business name slug
        db: Database session
        request: FastAPI request object for tracking
        
    Returns:
        HTML content
        
    Raises:
        HTTPException: If demo not found
    """
    # Reconstruct full slug
    full_slug = f"{city}-{category}-{slug}"
    
    # Find demo by slug
    demo = db.query(DemoWebsite).filter(DemoWebsite.slug == full_slug).first()
    
    if not demo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demo not found"
        )
    
    # Increment view count
    demo.view_count += 1
    demo.last_viewed_at = datetime.utcnow()
    db.commit()
    
    # Extract traffic source information
    referrer = request.headers.get("referer", "") if request else ""
    user_agent = request.headers.get("user-agent", "") if request else ""
    
    # Extract UTM parameters from query string
    utm_source = request.query_params.get("utm_source", "") if request else ""
    utm_medium = request.query_params.get("utm_medium", "") if request else ""
    utm_campaign = request.query_params.get("utm_campaign", "") if request else ""
    
    # Determine traffic source
    traffic_source = "direct"
    if utm_source:
        traffic_source = utm_source
    elif referrer:
        if "google" in referrer.lower():
            traffic_source = "google"
        elif "facebook" in referrer.lower():
            traffic_source = "facebook"
        elif "twitter" in referrer.lower():
            traffic_source = "twitter"
        elif "linkedin" in referrer.lower():
            traffic_source = "linkedin"
        else:
            traffic_source = "referral"
    
    # Track analytics event with traffic source
    event = AnalyticsEvent(
        id=uuid.uuid4(),
        event_type="demo_viewed",
        user_id=None,  # Public view
        metadata={
            "demo_id": str(demo.id),
            "business_id": str(demo.business_id),
            "slug": full_slug,
            "traffic_source": traffic_source,
            "referrer": referrer[:200] if referrer else "",
            "utm_source": utm_source,
            "utm_medium": utm_medium,
            "utm_campaign": utm_campaign,
            "user_agent": user_agent[:200] if user_agent else ""
        }
    )
    db.add(event)
    db.commit()
    
    logger.info(f"Demo {full_slug} viewed from {traffic_source} (total views: {demo.view_count})")
    
    return HTMLResponse(content=demo.html_content)


@router.post("/claim/{demo_id}")
async def track_claim_click(
    demo_id: str,
    db: Session = Depends(get_db)
):
    """Track claim button click on demo.
    
    Args:
        demo_id: Demo ID
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If demo not found
    """
    demo = db.query(DemoWebsite).filter(DemoWebsite.id == demo_id).first()
    
    if not demo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demo not found"
        )
    
    # Increment claim clicks
    demo.claim_clicks += 1
    db.commit()
    
    # Track analytics event
    event = AnalyticsEvent(
        id=uuid.uuid4(),
        event_type="demo_claim_clicked",
        user_id=None,
        metadata={
            "demo_id": str(demo.id),
            "business_id": str(demo.business_id)
        }
    )
    db.add(event)
    db.commit()
    
    logger.info(f"Claim button clicked for demo {demo_id} (total clicks: {demo.claim_clicks})")
    
    return {"success": True, "message": "Claim click tracked"}
