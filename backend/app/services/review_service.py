"""Review service for managing ratings and reviews.

This service handles:
- Review submission after deal completion
- Freelancer responses to reviews
- Average rating calculation
- Review eligibility checking

Requirements: 9.2
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func
import uuid

from ..models.review import Review
from ..models.deal import Deal, DealStatus
from ..models.user import Freelancer, BusinessOwner, User

logger = logging.getLogger(__name__)


class ReviewError(Exception):
    """Base exception for review errors."""
    pass


class ReviewService:
    """Service for managing reviews and ratings."""
    
    REVIEW_DEADLINE_DAYS = 30
    MIN_REVIEW_LENGTH = 20
    
    @classmethod
    def create_review(
        cls,
        db: Session,
        deal_id: str,
        business_owner_id: str,
        rating: int,
        review_text: str
    ) -> Review:
        """Create a review for a completed deal.
        
        Args:
            db: Database session
            deal_id: Deal ID
            business_owner_id: Business owner ID submitting review
            rating: Rating (1-5 stars)
            review_text: Review text (minimum 20 characters)
            
        Returns:
            Created Review object
            
        Raises:
            ReviewError: If review creation fails
        """
        try:
            # Validate rating
            if rating < 1 or rating > 5:
                raise ReviewError("Rating must be between 1 and 5 stars")
            
            # Validate review text length
            if len(review_text.strip()) < cls.MIN_REVIEW_LENGTH:
                raise ReviewError(f"Review must be at least {cls.MIN_REVIEW_LENGTH} characters")
            
            # Check if deal exists and is completed
            deal = db.query(Deal).filter(Deal.id == deal_id).first()
            if not deal:
                raise ReviewError(f"Deal {deal_id} not found")
            
            if deal.status != DealStatus.COMPLETED.value:
                raise ReviewError("Can only review completed deals")
            
            # Check if business owner owns this deal
            if deal.business_owner_id != business_owner_id:
                raise ReviewError("You can only review your own deals")
            
            # Check if review already exists
            existing_review = db.query(Review).filter(Review.deal_id == deal_id).first()
            if existing_review:
                raise ReviewError("Review already exists for this deal")
            
            # Check review deadline (30 days after completion)
            if deal.completed_at:
                deadline = deal.completed_at + timedelta(days=cls.REVIEW_DEADLINE_DAYS)
                if datetime.now(timezone.utc) > deadline:
                    raise ReviewError(f"Review deadline ({cls.REVIEW_DEADLINE_DAYS} days) has passed")
            
            # Create review
            review = Review(
                id=str(uuid.uuid4()),
                deal_id=deal_id,
                freelancer_id=deal.freelancer_id,
                business_owner_id=business_owner_id,
                rating=rating,
                review_text=review_text.strip()
            )
            
            db.add(review)
            db.commit()
            db.refresh(review)
            
            # Update freelancer's average rating
            cls.update_freelancer_rating(db, deal.freelancer_id)
            
            logger.info(f"Review created for deal {deal_id} by business owner {business_owner_id}")
            
            return review
            
        except ReviewError:
            raise
        except Exception as e:
            logger.error(f"Error creating review: {str(e)}")
            db.rollback()
            raise ReviewError(f"Failed to create review: {str(e)}")
    
    @classmethod
    def respond_to_review(
        cls,
        db: Session,
        review_id: str,
        freelancer_id: str,
        response_text: str
    ) -> Review:
        """Add freelancer response to a review.
        
        Args:
            db: Database session
            review_id: Review ID
            freelancer_id: Freelancer ID responding
            response_text: Response text
            
        Returns:
            Updated Review object
            
        Raises:
            ReviewError: If response fails
        """
        try:
            # Get review
            review = db.query(Review).filter(Review.id == review_id).first()
            if not review:
                raise ReviewError(f"Review {review_id} not found")
            
            # Check if freelancer owns this review
            if review.freelancer_id != freelancer_id:
                raise ReviewError("You can only respond to your own reviews")
            
            # Check if already responded
            if review.response_text:
                raise ReviewError("You have already responded to this review")
            
            # Validate response text
            if len(response_text.strip()) < 10:
                raise ReviewError("Response must be at least 10 characters")
            
            # Add response
            review.response_text = response_text.strip()
            review.responded_at = datetime.now(timezone.utc)
            
            db.commit()
            db.refresh(review)
            
            logger.info(f"Freelancer {freelancer_id} responded to review {review_id}")
            
            return review
            
        except ReviewError:
            raise
        except Exception as e:
            logger.error(f"Error responding to review: {str(e)}")
            db.rollback()
            raise ReviewError(f"Failed to respond to review: {str(e)}")
    
    @classmethod
    def get_freelancer_reviews(
        cls,
        db: Session,
        freelancer_id: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[Dict]:
        """Get all reviews for a freelancer.
        
        Args:
            db: Database session
            freelancer_id: Freelancer ID
            skip: Number of reviews to skip
            limit: Maximum number of reviews to return
            
        Returns:
            List of review dictionaries
        """
        reviews = db.query(Review).filter(
            Review.freelancer_id == freelancer_id
        ).order_by(
            Review.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        result = []
        for review in reviews:
            # Get business owner info
            business_owner = db.query(BusinessOwner).filter(
                BusinessOwner.id == review.business_owner_id
            ).first()
            
            # Get deal info
            deal = db.query(Deal).filter(Deal.id == review.deal_id).first()
            
            result.append({
                "id": review.id,
                "deal_id": review.deal_id,
                "rating": review.rating,
                "review_text": review.review_text,
                "response_text": review.response_text,
                "responded_at": review.responded_at.isoformat() if review.responded_at else None,
                "created_at": review.created_at.isoformat(),
                "business_owner_name": business_owner.owner_name if business_owner else "Unknown",
                "package_type": deal.package_type if deal else None,
                "deal_amount": deal.amount if deal else None
            })
        
        return result
    
    @classmethod
    def update_freelancer_rating(
        cls,
        db: Session,
        freelancer_id: str
    ) -> None:
        """Update freelancer's average rating and review count.
        
        Args:
            db: Database session
            freelancer_id: Freelancer ID
        """
        try:
            freelancer = db.query(Freelancer).filter(
                Freelancer.id == freelancer_id
            ).first()
            
            if not freelancer:
                return
            
            # Calculate average rating
            result = db.query(
                func.avg(Review.rating).label('avg_rating'),
                func.count(Review.id).label('review_count')
            ).filter(
                Review.freelancer_id == freelancer_id
            ).first()
            
            freelancer.average_rating = float(result.avg_rating) if result.avg_rating else 0.0
            freelancer.review_count = result.review_count or 0
            
            db.commit()
            
            logger.info(
                f"Updated freelancer {freelancer_id} rating: "
                f"{freelancer.average_rating:.2f} ({freelancer.review_count} reviews)"
            )
            
        except Exception as e:
            logger.error(f"Error updating freelancer rating: {str(e)}")
            db.rollback()
    
    @classmethod
    def check_review_eligibility(
        cls,
        db: Session,
        deal_id: str,
        business_owner_id: str
    ) -> Dict:
        """Check if a deal is eligible for review.
        
        Args:
            db: Database session
            deal_id: Deal ID
            business_owner_id: Business owner ID
            
        Returns:
            Dict with eligibility status and message
        """
        deal = db.query(Deal).filter(Deal.id == deal_id).first()
        
        if not deal:
            return {"eligible": False, "message": "Deal not found"}
        
        if deal.business_owner_id != business_owner_id:
            return {"eligible": False, "message": "Not your deal"}
        
        if deal.status != DealStatus.COMPLETED.value:
            return {"eligible": False, "message": "Deal not completed"}
        
        # Check if review already exists
        existing_review = db.query(Review).filter(Review.deal_id == deal_id).first()
        if existing_review:
            return {"eligible": False, "message": "Review already submitted"}
        
        # Check deadline
        if deal.completed_at:
            deadline = deal.completed_at + timedelta(days=cls.REVIEW_DEADLINE_DAYS)
            if datetime.now(timezone.utc) > deadline:
                return {
                    "eligible": False,
                    "message": f"Review deadline ({cls.REVIEW_DEADLINE_DAYS} days) has passed"
                }
            
            days_remaining = (deadline - datetime.now(timezone.utc)).days
            return {
                "eligible": True,
                "message": f"You have {days_remaining} days to submit a review",
                "deadline": deadline.isoformat()
            }
        
        return {"eligible": True, "message": "Deal is eligible for review"}
    
    @classmethod
    def get_pending_reviews(
        cls,
        db: Session,
        business_owner_id: str
    ) -> List[Dict]:
        """Get deals pending review for a business owner.
        
        Args:
            db: Database session
            business_owner_id: Business owner ID
            
        Returns:
            List of deals pending review
        """
        # Get completed deals without reviews
        deals = db.query(Deal).filter(
            Deal.business_owner_id == business_owner_id,
            Deal.status == DealStatus.COMPLETED.value
        ).all()
        
        pending = []
        for deal in deals:
            # Check if review exists
            review = db.query(Review).filter(Review.deal_id == deal.id).first()
            if review:
                continue
            
            # Check deadline
            if deal.completed_at:
                deadline = deal.completed_at + timedelta(days=cls.REVIEW_DEADLINE_DAYS)
                if datetime.now(timezone.utc) > deadline:
                    continue
                
                days_remaining = (deadline - datetime.now(timezone.utc)).days
                
                # Get freelancer info
                freelancer = db.query(Freelancer).filter(
                    Freelancer.id == deal.freelancer_id
                ).first()
                
                pending.append({
                    "deal_id": deal.id,
                    "freelancer_id": deal.freelancer_id,
                    "freelancer_name": freelancer.name if freelancer else "Unknown",
                    "package_type": deal.package_type,
                    "amount": deal.amount,
                    "completed_at": deal.completed_at.isoformat(),
                    "days_remaining": days_remaining,
                    "deadline": deadline.isoformat()
                })
        
        return pending
