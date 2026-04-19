"""Review and rating routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from ..database import get_db
from ..middleware.auth import get_current_user
from ..services.review_service import ReviewService, ReviewError

router = APIRouter(prefix="/api/reviews", tags=["reviews"])


# Schemas
class CreateReviewRequest(BaseModel):
    deal_id: str
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    review_text: str = Field(..., min_length=20, description="Review text (minimum 20 characters)")


class RespondToReviewRequest(BaseModel):
    response_text: str = Field(..., min_length=10, description="Response text (minimum 10 characters)")


@router.post("")
async def create_review(
    request: CreateReviewRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit a review for a completed deal.
    
    Requirement 9.2: Rating Process
    - Trigger: Project completion (all milestones approved)
    - Scale: 5 stars
    - Review: Minimum 20 characters
    - Deadline: Within 30 days of completion
    """
    try:
        # Only business owners can submit reviews
        if current_user.get("role") != "businessowner":
            raise HTTPException(status_code=403, detail="Only business owners can submit reviews")
        
        # Get business owner ID from user
        from ..models.user import BusinessOwner
        business_owner = db.query(BusinessOwner).filter(
            BusinessOwner.user_id == current_user["user_id"]
        ).first()
        
        if not business_owner:
            raise HTTPException(status_code=404, detail="Business owner profile not found")
        
        review = ReviewService.create_review(
            db=db,
            deal_id=request.deal_id,
            business_owner_id=business_owner.id,
            rating=request.rating,
            review_text=request.review_text
        )
        
        return {
            "message": "Review submitted successfully",
            "review_id": review.id,
            "rating": review.rating,
            "created_at": review.created_at.isoformat()
        }
    except ReviewError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create review: {str(e)}")


@router.get("/freelancer/{freelancer_id}")
async def get_freelancer_reviews(
    freelancer_id: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get all reviews for a freelancer.
    
    Requirement 9.2: Display
    - All reviews visible
    - Date and project type shown
    """
    try:
        reviews = ReviewService.get_freelancer_reviews(
            db=db,
            freelancer_id=freelancer_id,
            skip=skip,
            limit=limit
        )
        
        # Get freelancer info
        from ..models.user import Freelancer
        freelancer = db.query(Freelancer).filter(Freelancer.id == freelancer_id).first()
        
        return {
            "freelancer_id": freelancer_id,
            "freelancer_name": freelancer.name if freelancer else "Unknown",
            "average_rating": freelancer.average_rating if freelancer else 0.0,
            "review_count": freelancer.review_count if freelancer else 0,
            "reviews": reviews
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get reviews: {str(e)}")


@router.post("/{review_id}/respond")
async def respond_to_review(
    review_id: str,
    request: RespondToReviewRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add freelancer response to a review.
    
    Requirement 9.2: Display
    - Freelancer can respond
    """
    try:
        # Only freelancers can respond
        if current_user.get("role") != "freelancer":
            raise HTTPException(status_code=403, detail="Only freelancers can respond to reviews")
        
        # Get freelancer ID from user
        from ..models.user import Freelancer
        freelancer = db.query(Freelancer).filter(
            Freelancer.user_id == current_user["user_id"]
        ).first()
        
        if not freelancer:
            raise HTTPException(status_code=404, detail="Freelancer profile not found")
        
        review = ReviewService.respond_to_review(
            db=db,
            review_id=review_id,
            freelancer_id=freelancer.id,
            response_text=request.response_text
        )
        
        return {
            "message": "Response submitted successfully",
            "review_id": review.id,
            "responded_at": review.responded_at.isoformat()
        }
    except ReviewError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to respond to review: {str(e)}")


@router.get("/deal/{deal_id}/eligibility")
async def check_review_eligibility(
    deal_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if a deal is eligible for review."""
    try:
        # Get business owner ID
        from ..models.user import BusinessOwner
        business_owner = db.query(BusinessOwner).filter(
            BusinessOwner.user_id == current_user["user_id"]
        ).first()
        
        if not business_owner:
            raise HTTPException(status_code=404, detail="Business owner profile not found")
        
        eligibility = ReviewService.check_review_eligibility(
            db=db,
            deal_id=deal_id,
            business_owner_id=business_owner.id
        )
        
        return eligibility
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check eligibility: {str(e)}")


@router.get("/pending")
async def get_pending_reviews(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get deals pending review for the current business owner."""
    try:
        # Only business owners can see pending reviews
        if current_user.get("role") != "businessowner":
            raise HTTPException(status_code=403, detail="Only business owners can view pending reviews")
        
        # Get business owner ID
        from ..models.user import BusinessOwner
        business_owner = db.query(BusinessOwner).filter(
            BusinessOwner.user_id == current_user["user_id"]
        ).first()
        
        if not business_owner:
            raise HTTPException(status_code=404, detail="Business owner profile not found")
        
        pending = ReviewService.get_pending_reviews(
            db=db,
            business_owner_id=business_owner.id
        )
        
        return {
            "total": len(pending),
            "pending_reviews": pending
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get pending reviews: {str(e)}")
