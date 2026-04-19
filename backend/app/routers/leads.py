"""Lead discovery and management API endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
import uuid
import logging
import os

from ..database import get_db
from ..config import settings
from ..services.google_places import (
    GooglePlacesService,
    GooglePlacesAPIError,
    RateLimitError
)
from ..services.latlng_api import (
    LatLngService,
    LatLngAPIError,
    RateLimitError as LatLngRateLimitError
)
from ..services.lead_scoring import LeadScoringService
from ..services.lead_allocation import (
    LeadAllocationService,
    ExclusivityViolationError,
    DailyLimitExceededError,
    AllocationError
)
from ..services.ai_enrichment import ai_enrichment_service
from ..models.business import Business, BusinessInsight, FreshnessScore
from ..models.lead import Lead, LeadSource, LeadStatus
from ..models.user import Freelancer
from ..middleware.auth import get_current_user
from ..schemas.leads import (
    LeadDiscoverRequest,
    LeadDiscoverResponse,
    LeadListResponse,
    LeadDetailResponse,
    LeadResponse,
    BusinessResponse,
    BusinessInsightResponse
)
from ..schemas.allocation import (
    ClaimLeadResponse,
    AvailableLeadsResponse,
    AvailableLeadItem,
    MyLeadsResponse,
    MyLeadItem
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/leads", tags=["leads"])


def get_places_service():
    """Dependency to get Places service instance (LatLng or Google)."""
    use_latlng = settings.use_latlng
    
    if use_latlng:
        api_key = settings.latlng_api_key
        logger.info("Using LatLng service for place discovery")
        return LatLngService(api_key)
    else:
        logger.info("Using Google Places service for place discovery")
        return GooglePlacesService(settings.google_places_api_key)


@router.post("/discover", response_model=LeadDiscoverResponse)
async def discover_leads(
    request: LeadDiscoverRequest = Body(...),
    service = Depends(get_places_service),
    db: Session = Depends(get_db)
):
    """Discover businesses using Places API (Google or LocationIQ) and store as leads.
    
    This endpoint:
    1. Searches for businesses by category and location
    2. Calculates digital scores for each business
    3. Stores businesses and insights in the database
    4. Creates lead records
    
    **Requirements**: 1.1, 2.1, 3.1, 32.1
    
    Args:
        request: Discovery request with category, location, and limit
        
    Returns:
        List of discovered and stored leads with scores
        
    Raises:
        429: Rate limit exceeded
        500: API error or service unavailable
    """
    try:
        # Discover businesses from Places API
        print(f"[DISCOVER] Location: {request.location}, Category: {request.category}, Limit: {request.limit}")
        logger.info(f"Discovering businesses: location={request.location}, category={request.category}, limit={request.limit}")
        businesses = service.search_businesses(
            location=request.location,
            category=request.category,
            limit=request.limit
        )
        print(f"[DISCOVER] Found {len(businesses)} businesses from API")
        logger.info(f"Found {len(businesses)} businesses from API")
        
        stored_leads = []
        seen_place_ids = set()  # Track place_ids to prevent duplicates
        
        for business_data in businesses:
            try:
                # Skip if we've already processed this place_id
                if business_data.place_id in seen_place_ids:
                    logger.info(f"Skipping duplicate place_id: {business_data.place_id}")
                    continue
                
                seen_place_ids.add(business_data.place_id)
                
                # Check if business already exists
                existing_business = db.query(Business).filter(
                    Business.place_id == business_data.place_id
                ).first()
                
                if existing_business:
                    # Update existing business
                    business = existing_business
                    business.name = business_data.name
                    business.address = business_data.address
                    business.city = business_data.city
                    business.phone = business_data.phone
                    business.category = business_data.category
                    business.latitude = business_data.latitude
                    business.longitude = business_data.longitude
                    business.updated_at = datetime.utcnow()
                else:
                    # Create new business
                    business = Business(
                        id=str(uuid.uuid4()),
                        place_id=business_data.place_id,
                        name=business_data.name,
                        category=business_data.category,
                        address=business_data.address,
                        city=business_data.city,
                        phone=business_data.phone,
                        latitude=business_data.latitude,
                        longitude=business_data.longitude,
                        is_active=True
                    )
                    db.add(business)
                
                # Calculate digital score
                scoring_result = LeadScoringService.calculate_digital_score(
                    rating=business_data.rating,
                    review_count=business_data.review_count,
                    has_website=business_data.has_website,
                    category=business_data.category
                )
                
                # Get AI enrichment data
                ai_enrichment = ai_enrichment_service.enrich_business_data(
                    business_name=business_data.name,
                    category=business_data.category,
                    address=business_data.address,
                    city=business_data.city,
                    rating=business_data.rating,
                    review_count=business_data.review_count,
                    has_website=business_data.has_website,
                    website_url=business_data.website_url,
                    phone=business_data.phone
                )
                
                # Get pitch suggestions
                pitch_suggestions = ai_enrichment_service.get_pitch_suggestions(ai_enrichment)
                
                # Check if insights already exist
                existing_insights = db.query(BusinessInsight).filter(
                    BusinessInsight.business_id == business.id
                ).first()
                
                if existing_insights:
                    # Update existing insights
                    insights = existing_insights
                    insights.digital_score = scoring_result["score"]
                    insights.digital_score_breakdown = scoring_result["breakdown"]
                    insights.priority_score = scoring_result["score"]  # For MVP, priority = digital score
                    insights.freshness = "high"  # Valid enum value: high, medium, low
                    insights.rating = business_data.rating
                    insights.review_count = business_data.review_count
                    insights.has_website = business_data.has_website
                    insights.website_url = business_data.website_url
                    insights.last_verified = datetime.utcnow()
                    insights.updated_at = datetime.utcnow()
                    
                    # Update AI enrichment fields
                    insights.ai_description = ai_enrichment.get("business_description")
                    insights.ai_specialties = ai_enrichment.get("specialties")
                    insights.ai_target_customers = ai_enrichment.get("target_customers")
                    insights.ai_pain_points = ai_enrichment.get("pain_points")
                    insights.ai_recommended_solutions = ai_enrichment.get("recommended_solutions")
                    insights.ai_competitive_advantages = ai_enrichment.get("competitive_advantages")
                    insights.ai_digital_maturity = ai_enrichment.get("digital_maturity")
                    insights.ai_growth_potential = ai_enrichment.get("growth_potential")
                    insights.ai_estimated_size = ai_enrichment.get("estimated_size")
                    insights.ai_online_presence_score = ai_enrichment.get("online_presence_score")
                    insights.ai_urgency_score = ai_enrichment.get("urgency_score")
                    insights.ai_enrichment_confidence = ai_enrichment.get("enrichment_confidence")
                    insights.ai_enriched_at = datetime.utcnow()
                    insights.ai_pitch_suggestions = pitch_suggestions
                else:
                    # Create new insights
                    insights = BusinessInsight(
                        id=str(uuid.uuid4()),
                        business_id=business.id,
                        digital_score=scoring_result["score"],
                        digital_score_breakdown=scoring_result["breakdown"],
                        priority_score=scoring_result["score"],  # For MVP, priority = digital score
                        opportunity_tag="medium",  # Valid enum value: high, medium, low
                        freshness="high",  # Valid enum value: high, medium, low
                        status="active",  # Valid enum value: active, contacted, cold, unavailable
                        rating=business_data.rating,
                        review_count=business_data.review_count,
                        has_website=business_data.has_website,
                        website_url=business_data.website_url,
                        contact_count=0,
                        last_verified=datetime.utcnow(),
                        
                        # AI enrichment fields
                        ai_description=ai_enrichment.get("business_description"),
                        ai_specialties=ai_enrichment.get("specialties"),
                        ai_target_customers=ai_enrichment.get("target_customers"),
                        ai_pain_points=ai_enrichment.get("pain_points"),
                        ai_recommended_solutions=ai_enrichment.get("recommended_solutions"),
                        ai_competitive_advantages=ai_enrichment.get("competitive_advantages"),
                        ai_digital_maturity=ai_enrichment.get("digital_maturity"),
                        ai_growth_potential=ai_enrichment.get("growth_potential"),
                        ai_estimated_size=ai_enrichment.get("estimated_size"),
                        ai_online_presence_score=ai_enrichment.get("online_presence_score"),
                        ai_urgency_score=ai_enrichment.get("urgency_score"),
                        ai_enrichment_confidence=ai_enrichment.get("enrichment_confidence"),
                        ai_enriched_at=datetime.utcnow(),
                        ai_pitch_suggestions=pitch_suggestions
                    )
                    db.add(insights)
                
                # Create lead record
                lead = Lead(
                    id=str(uuid.uuid4()),
                    business_id=business.id,
                    source=LeadSource.GOOGLE,
                    score=scoring_result["score"],
                    status=LeadStatus.NEW,
                    is_active=True
                )
                db.add(lead)
                
                # Commit after each business to avoid long transactions
                db.commit()
                
                # Build response
                stored_leads.append(
                    LeadResponse(
                        id=lead.id,
                        business_id=business.id,
                        source=lead.source if isinstance(lead.source, str) else lead.source.value,
                        score=lead.score,
                        status=lead.status if isinstance(lead.status, str) else lead.status.value,
                        created_at=lead.created_at,
                        business=BusinessResponse(
                            id=business.id,
                            place_id=business.place_id,
                            name=business.name,
                            category=business.category,
                            address=business.address,
                            city=business.city,
                            phone=business.phone,
                            latitude=business.latitude,
                            longitude=business.longitude,
                            created_at=business.created_at,
                            updated_at=business.updated_at
                        ),
                        insights=BusinessInsightResponse.from_orm(insights)
                    )
                )
            except Exception as e:
                # Log error but continue with next business
                logger.error(f"Error processing business {business_data.name}: {str(e)}")
                db.rollback()
                continue
        
        return LeadDiscoverResponse(
            success=True,
            discovered=len(businesses),
            stored=len(stored_leads),
            leads=stored_leads
        )
        
    except (RateLimitError, LatLngRateLimitError) as e:
        db.rollback()
        raise HTTPException(
            status_code=429,
            detail={
                "error": "RATE_LIMIT_EXCEEDED",
                "message": str(e),
                "retry_after": "24 hours"
            }
        )
    except (GooglePlacesAPIError, LatLngAPIError) as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "error": "API_ERROR",
                "message": str(e)
            }
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": str(e)
            }
        )


@router.get("", response_model=LeadListResponse)
async def list_leads(
    category: Optional[str] = Query(None, description="Filter by business category"),
    score_min: Optional[int] = Query(None, ge=0, le=100, description="Minimum digital score"),
    score_max: Optional[int] = Query(None, ge=0, le=100, description="Maximum digital score"),
    freshness: Optional[str] = Query(None, description="Filter by freshness (High, Medium, Low)"),
    status: Optional[str] = Query(None, description="Filter by lead status"),
    limit: int = Query(20, ge=1, le=100, description="Number of results per page"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: Session = Depends(get_db)
):
    """List leads with optional filters.
    
    This endpoint retrieves leads from the database with support for:
    - Category filtering
    - Digital score range filtering
    - Freshness filtering
    - Status filtering
    - Pagination
    
    **Requirements**: 1.1, 2.1, 3.1, 32.1
    
    Args:
        category: Business category filter
        score_min: Minimum digital score
        score_max: Maximum digital score
        freshness: Freshness level (High/Medium/Low)
        status: Lead status filter
        limit: Results per page
        offset: Pagination offset
        
    Returns:
        List of leads matching filters
    """
    try:
        # Build query
        query = db.query(Lead).join(Business).join(BusinessInsight)
        
        # Apply filters
        filters = []
        
        if category:
            filters.append(Business.category == category)
        
        if score_min is not None:
            filters.append(BusinessInsight.digital_score >= score_min)
        
        if score_max is not None:
            filters.append(BusinessInsight.digital_score <= score_max)
        
        if freshness:
            try:
                freshness_enum = FreshnessScore(freshness)
                filters.append(BusinessInsight.freshness == freshness_enum)
            except ValueError:
                pass  # Invalid freshness value, ignore
        
        if status:
            try:
                status_enum = LeadStatus(status.upper())
                filters.append(Lead.status == status_enum)
            except ValueError:
                pass  # Invalid status value, ignore
        
        # Apply all filters
        if filters:
            query = query.filter(and_(*filters))
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        leads = query.order_by(BusinessInsight.digital_score.desc()).offset(offset).limit(limit).all()
        
        # Build response
        lead_responses = []
        for lead in leads:
            business = lead.business
            insights = db.query(BusinessInsight).filter(
                BusinessInsight.business_id == business.id
            ).first()
            
            lead_responses.append(
                LeadResponse(
                    id=lead.id,
                    business_id=business.id,
                    source=lead.source if isinstance(lead.source, str) else lead.source.value,
                    score=lead.score,
                    status=lead.status if isinstance(lead.status, str) else lead.status.value,
                    created_at=lead.created_at,
                    business=BusinessResponse(
                        id=business.id,
                        place_id=business.place_id,
                        name=business.name,
                        category=business.category,
                        address=business.address,
                        city=business.city,
                        phone=business.phone,
                        latitude=business.latitude,
                        longitude=business.longitude,
                        created_at=business.created_at,
                        updated_at=business.updated_at
                    ),
                    insights=BusinessInsightResponse.from_orm(insights) if insights else None
                )
            )
        
        return LeadListResponse(
            success=True,
            total=total,
            leads=lead_responses
        )
        
    except Exception as e:
        logger.error(f"Error listing leads: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": str(e)
            }
        )


@router.get("/available", response_model=AvailableLeadsResponse)
async def get_available_leads(
    category: Optional[str] = Query(None, description="Filter by business category"),
    score_min: Optional[int] = Query(None, ge=0, le=100, description="Minimum digital score"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of leads to return"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available leads for current freelancer (respects tier limits).
    
    Available leads are those:
    - Not in active exclusivity window
    - Not already contacted by this freelancer
    - Match optional filters
    
    **Requirements**: 41.1, 41.2, 33.1
    
    Args:
        category: Optional category filter
        score_min: Optional minimum score filter
        limit: Maximum number of leads to return
        current_user: Authenticated user from JWT
        
    Returns:
        List of available leads with remaining allocation count
        
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
                    "message": "Only freelancers can access available leads"
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
        
        # Get available leads
        available_leads = LeadAllocationService.get_available_leads(
            db=db,
            freelancer_id=freelancer.id,
            category=category,
            score_min=score_min,
            limit=limit
        )
        
        # Convert to response format
        lead_items = [AvailableLeadItem(**lead) for lead in available_leads]
        
        return AvailableLeadsResponse(
            success=True,
            remaining_allocations=freelancer.remaining_contacts,
            daily_limit=freelancer.daily_limit,
            available_count=len(lead_items),
            leads=lead_items
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting available leads: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": str(e)
            }
        )


@router.get("/my-leads", response_model=MyLeadsResponse)
async def get_my_leads(
    status: Optional[str] = Query(None, description="Filter by contact status"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get leads allocated to current freelancer.
    
    **Requirements**: 41.1, 41.2
    
    Args:
        status: Optional status filter (Contacted, Interested, Negotiating, etc.)
        current_user: Authenticated user from JWT
        
    Returns:
        List of allocated leads with contact details
        
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
                    "message": "Only freelancers can access their leads"
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
        
        # Get my leads
        my_leads = LeadAllocationService.get_my_leads(
            db=db,
            freelancer_id=freelancer.id,
            status=status
        )
        
        # Convert to response format
        lead_items = [MyLeadItem(**lead) for lead in my_leads]
        
        return MyLeadsResponse(
            success=True,
            total=len(lead_items),
            leads=lead_items
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting my leads: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": str(e)
            }
        )


@router.get("/{lead_id}", response_model=LeadDetailResponse)
async def get_lead_details(
    lead_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed information for a specific lead.
    
    **Requirements**: 1.1, 2.1, 3.1
    
    Args:
        lead_id: Lead ID
        
    Returns:
        Detailed lead information including business and insights
        
    Raises:
        404: Lead not found
    """
    try:
        # Get lead with business
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        
        if not lead:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "NOT_FOUND",
                    "message": f"Lead with ID {lead_id} not found"
                }
            )
        
        business = lead.business
        insights = db.query(BusinessInsight).filter(
            BusinessInsight.business_id == business.id
        ).first()
        
        lead_response = LeadResponse(
            id=lead.id,
            business_id=business.id,
            source=lead.source if isinstance(lead.source, str) else lead.source.value,
            score=lead.score,
            status=lead.status if isinstance(lead.status, str) else lead.status.value,
            created_at=lead.created_at,
            business=BusinessResponse(
                id=business.id,
                place_id=business.place_id,
                name=business.name,
                category=business.category,
                address=business.address,
                city=business.city,
                phone=business.phone,
                latitude=business.latitude,
                longitude=business.longitude,
                created_at=business.created_at,
                updated_at=business.updated_at
            ),
            insights=BusinessInsightResponse.from_orm(insights) if insights else None
        )
        
        return LeadDetailResponse(
            success=True,
            lead=lead_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting lead details: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": str(e)
            }
        )


@router.get("/business/{place_id}")
async def get_business_details(
    place_id: str,
    service = Depends(get_places_service),
    db: Session = Depends(get_db)
):
    """Get detailed information for a specific business.
    
    **Requirements**: 2.1, 2.2, 2.3
    
    Args:
        place_id: Google Places place_id
        
    Returns:
        Detailed business information
        
    Raises:
        404: Business not found
        429: Rate limit exceeded
        500: API error
    """
    try:
        business = service.get_business_details(place_id)
        
        if not business:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "NOT_FOUND",
                    "message": f"Business with place_id {place_id} not found"
                }
            )
        
        return {
            "success": True,
            "business": {
                "place_id": business.place_id,
                "name": business.name,
                "address": business.address,
                "city": business.city,
                "phone": business.phone,
                "rating": business.rating,
                "review_count": business.review_count,
                "category": business.category,
                "has_website": business.has_website,
                "website_url": business.website_url
            }
        }
        
    except RateLimitError as e:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "RATE_LIMIT_EXCEEDED",
                "message": str(e)
            }
        )
    except GooglePlacesAPIError as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "API_ERROR",
                "message": str(e)
            }
        )



# Lead Allocation Endpoints

@router.post("/{lead_id}/claim", response_model=ClaimLeadResponse)
async def claim_lead(
    lead_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Claim a lead with 6-hour exclusivity window.
    
    This endpoint:
    1. Checks if lead is available (not in active exclusivity window)
    2. Checks freelancer's daily limit
    3. Creates lead contact with 6-hour exclusivity window
    4. Updates freelancer's remaining contacts
    
    **Requirements**: 41.1, 41.2, 41.3, 33.1
    
    Args:
        lead_id: Lead ID to claim
        current_user: Authenticated user from JWT
        
    Returns:
        Claim confirmation with exclusivity window details
        
    Raises:
        400: Lead already in exclusivity window or daily limit exceeded
        403: User is not a freelancer
        404: Lead not found
    """
    try:
        # Verify user is a freelancer
        if current_user.get("role") != "freelancer":
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "FORBIDDEN",
                    "message": "Only freelancers can claim leads"
                }
            )
        
        # Get freelancer ID
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
        
        # Allocate lead
        lead_contact = LeadAllocationService.allocate_lead(
            db=db,
            lead_id=lead_id,
            freelancer_id=freelancer.id
        )
        
        return ClaimLeadResponse(
            success=True,
            contact_id=lead_contact.id,
            lead_id=lead_contact.lead_id,
            freelancer_id=lead_contact.freelancer_id,
            exclusivity_expires_at=lead_contact.exclusivity_expires_at,
            message=f"Lead claimed successfully. Exclusivity expires at {lead_contact.exclusivity_expires_at.isoformat()}"
        )
        
    except ExclusivityViolationError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "EXCLUSIVITY_VIOLATION",
                "message": str(e)
            }
        )
    except DailyLimitExceededError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "DAILY_LIMIT_EXCEEDED",
                "message": str(e)
            }
        )
    except AllocationError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "ALLOCATION_ERROR",
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Error claiming lead: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": str(e)
            }
        )



@router.post("/copilot/{lead_id}")
async def get_ai_copilot_intelligence(
    lead_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get AI-powered sales intelligence for a specific lead.
    Limited to 3 uses per lead per freelancer.
    """
    from ..services.ai_copilot import AICopilot
    from ..models.lead import LeadContact
    
    try:
        # Extract user_id from token payload
        user_id = current_user.get("user_id")
        
        # Get freelancer
        freelancer = db.query(Freelancer).filter(Freelancer.user_id == user_id).first()
        if not freelancer:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "NOT_FOUND",
                    "message": "Freelancer profile not found"
                }
            )
        
        # Get lead
        lead = db.query(Lead).filter(Lead.id == lead_id, Lead.is_active == True).first()
        if not lead:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "NOT_FOUND",
                    "message": "Lead not found"
                }
            )
        
        # Check if freelancer has claimed this lead
        lead_contact = db.query(LeadContact).filter(
            LeadContact.lead_id == lead_id,
            LeadContact.freelancer_id == freelancer.id
        ).first()
        
        if not lead_contact:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "NOT_CLAIMED",
                    "message": "You must claim this lead before using AI Copilot"
                }
            )
        
        # Check usage limit (handle None case)
        copilot_uses = lead_contact.copilot_uses or 0
        if copilot_uses >= AICopilot.MAX_USES_PER_LEAD:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "LIMIT_EXCEEDED",
                    "message": f"AI Copilot limit reached ({AICopilot.MAX_USES_PER_LEAD} uses per lead)",
                    "remaining_uses": 0
                }
            )
        
        # Get business and insights
        business = lead.business
        insights = business.insights
        
        if not business or not insights:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "DATA_NOT_FOUND",
                    "message": "Business data not available"
                }
            )
        
        # Prepare data for AI Copilot
        business_data = {
            'name': business.name,
            'category': business.category,
            'address': business.address,
            'city': business.city,
            'phone': business.phone,
            'latitude': business.latitude,
            'longitude': business.longitude
        }
        
        insights_data = {
            'digital_score': insights.digital_score,
            'has_website': insights.has_website,
            'website_url': insights.website_url,
            'rating': insights.rating,
            'review_count': insights.review_count,
            'ai_description': insights.ai_description,
            'ai_specialties': insights.ai_specialties,
            'ai_target_customers': insights.ai_target_customers,
            'ai_pain_points': insights.ai_pain_points,
            'ai_recommended_solutions': insights.ai_recommended_solutions,
            'ai_competitive_advantages': insights.ai_competitive_advantages,
            'ai_digital_maturity': insights.ai_digital_maturity,
            'ai_growth_potential': insights.ai_growth_potential,
            'ai_estimated_size': insights.ai_estimated_size,
            'ai_online_presence_score': insights.ai_online_presence_score,
            'ai_urgency_score': insights.ai_urgency_score,
            'ai_enrichment_confidence': insights.ai_enrichment_confidence,
            'ai_pitch_suggestions': insights.ai_pitch_suggestions
        }
        
        # Generate intelligence
        copilot = AICopilot()
        intelligence = copilot.generate_sales_intelligence(
            business_data=business_data,
            insights_data=insights_data,
            remaining_uses=AICopilot.MAX_USES_PER_LEAD - copilot_uses
        )
        
        # Update usage tracking (handle None case)
        if lead_contact.copilot_uses is None:
            lead_contact.copilot_uses = 0
        lead_contact.copilot_uses += 1
        lead_contact.last_copilot_use = datetime.utcnow()
        db.commit()
        
        return {
            'success': True,
            'intelligence': intelligence
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating AI copilot intelligence: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": str(e)
            }
        )


@router.get("/api/leads/{lead_id}/ai-insights")
async def get_ai_business_insights(
    lead_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI-generated business intelligence report for a lead.
    
    This endpoint generates a comprehensive business intelligence report
    including opportunity analysis, pricing recommendations, sales strategies,
    and personalized outreach messages.
    
    **IMPORTANT**: This enhances REAL business data with AI insights.
    All AI-generated content is clearly marked in the response.
    
    **Modes** (priority order):
    1. Ollama Mode (FREE, local AI) - if USE_OLLAMA=true in .env
    2. ChatGPT Mode (Paid) - if OPENAI_API_KEY is set
    3. Template Mode (FREE) - fallback, always works
    """
    from ..services.ai_business_copilot import AIBusinessCopilot
    
    # Get the lead
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Get the business
    business = db.query(Business).filter(Business.id == lead.business_id).first()
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Initialize AI Copilot
    # Priority: Ollama (FREE) > OpenAI (Paid) > Template (FREE)
    use_ollama = os.getenv("USE_OLLAMA", "false").lower() == "true"
    api_key = os.getenv("OPENAI_API_KEY") if not use_ollama else None
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    
    copilot = AIBusinessCopilot(
        api_key=api_key,
        use_ollama=use_ollama,
        ollama_url=ollama_url
    )
    
    # Generate business intelligence report
    report = copilot.generate_business_intelligence(
        name=business.name,
        category=business.category,
        city=business.city,
        digital_score=business.digital_score or 0,
        has_website=business.has_website,
        rating=business.rating,
        review_count=business.review_count,
        data_source="Google Places API",
        phone=business.phone,
        address=business.address,
        place_id=business.place_id
    )
    
    return report
