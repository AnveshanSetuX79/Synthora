"""Lead scoring service for digital presence evaluation.

This service implements the rule-based scoring algorithm that evaluates
businesses based on their digital presence and assigns scores to help
freelancers prioritize leads.

Scoring Algorithm:
- Rating: 0-30 points (based on Google rating 0-5)
- Reviews: 0-25 points (based on review count)
- No website: 30 points (bonus for businesses without websites)
- Category priority: 0-15 points (based on business category)

Total: 0-100 digital presence score

Requirements: 3.1, 3.2, 3.3, 3.4
"""
import logging
from typing import Dict, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class OpportunityTag(str, Enum):
    """Lead opportunity classification."""
    HIGH = "High"      # 80-100 points
    MEDIUM = "Medium"  # 50-79 points
    LOW = "Low"        # 0-49 points


class CategoryPriority(str, Enum):
    """Business category priority levels."""
    RESTAURANT = "Restaurant"
    SCHOOL = "School"
    CAFE = "Cafe"
    GYM = "Gym"
    SALON = "Salon"
    OTHER = "Other"


# Category priority scores (0-15 points)
CATEGORY_SCORES = {
    CategoryPriority.RESTAURANT: 15,  # High priority for MVP
    CategoryPriority.CAFE: 12,
    CategoryPriority.SALON: 10,
    CategoryPriority.GYM: 10,
    CategoryPriority.SCHOOL: 8,
    CategoryPriority.OTHER: 5,
}


class LeadScoringService:
    """Service for calculating digital presence scores for businesses."""
    
    # Scoring thresholds
    MAX_RATING_SCORE = 30
    MAX_REVIEW_SCORE = 25
    NO_WEBSITE_BONUS = 30
    MAX_CATEGORY_SCORE = 15
    
    # Review count thresholds for scoring
    REVIEW_THRESHOLDS = [
        (0, 0),      # 0 reviews = 0 points
        (10, 5),     # 1-10 reviews = 5 points
        (25, 10),    # 11-25 reviews = 10 points
        (50, 15),    # 26-50 reviews = 15 points
        (100, 20),   # 51-100 reviews = 20 points
        (float('inf'), 25)  # 100+ reviews = 25 points
    ]
    
    @classmethod
    def calculate_digital_score(
        cls,
        rating: Optional[float],
        review_count: int,
        has_website: bool,
        category: str
    ) -> Dict[str, any]:
        """Calculate digital presence score for a business.
        
        Args:
            rating: Google rating (0-5), None if no rating
            review_count: Number of reviews
            has_website: Whether business has a website
            category: Business category
            
        Returns:
            Dictionary containing:
                - score: Total digital score (0-100)
                - breakdown: Score breakdown by component
                - opportunity_tag: High/Medium/Low classification
        """
        # Calculate component scores
        rating_score = cls._calculate_rating_score(rating)
        review_score = cls._calculate_review_score(review_count)
        website_score = cls._calculate_website_score(has_website)
        category_score = cls._calculate_category_score(category)
        
        # Total score
        total_score = rating_score + review_score + website_score + category_score
        
        # Ensure score is within bounds
        total_score = max(0, min(100, total_score))
        
        # Determine opportunity tag
        opportunity_tag = cls._classify_opportunity(total_score)
        
        # Build breakdown
        breakdown = {
            "rating": rating_score,
            "reviews": review_score,
            "no_website": website_score,
            "category_priority": category_score,
        }
        
        logger.info(
            f"Calculated digital score: {total_score} "
            f"(rating={rating_score}, reviews={review_score}, "
            f"website={website_score}, category={category_score})"
        )
        
        return {
            "score": total_score,
            "breakdown": breakdown,
            "opportunity_tag": opportunity_tag.value,
        }
    
    @classmethod
    def _calculate_rating_score(cls, rating: Optional[float]) -> int:
        """Calculate score based on Google rating (0-30 points).
        
        Args:
            rating: Google rating (0-5), None if no rating
            
        Returns:
            Score between 0 and 30
        """
        if rating is None or rating <= 0:
            return 0
        
        # Linear scale: 5-star rating = 30 points
        # Formula: (rating / 5) * 30
        score = (rating / 5.0) * cls.MAX_RATING_SCORE
        return int(round(score))
    
    @classmethod
    def _calculate_review_score(cls, review_count: int) -> int:
        """Calculate score based on review count (0-25 points).
        
        Uses tiered scoring:
        - 0 reviews: 0 points
        - 1-10 reviews: 5 points
        - 11-25 reviews: 10 points
        - 26-50 reviews: 15 points
        - 51-100 reviews: 20 points
        - 100+ reviews: 25 points
        
        Args:
            review_count: Number of reviews
            
        Returns:
            Score between 0 and 25
        """
        if review_count < 0:
            review_count = 0
        
        for threshold, score in cls.REVIEW_THRESHOLDS:
            if review_count <= threshold:
                return score
        
        return cls.MAX_REVIEW_SCORE
    
    @classmethod
    def _calculate_website_score(cls, has_website: bool) -> int:
        """Calculate score for website presence (0 or 30 points).
        
        Businesses WITHOUT websites get 30 bonus points as they are
        high-value leads for freelancers.
        
        Args:
            has_website: Whether business has a website
            
        Returns:
            30 if no website, 0 if has website
        """
        return 0 if has_website else cls.NO_WEBSITE_BONUS
    
    @classmethod
    def _calculate_category_score(cls, category: str) -> int:
        """Calculate score based on business category (0-15 points).
        
        Different categories have different priority levels based on
        conversion potential and MVP focus.
        
        Args:
            category: Business category
            
        Returns:
            Score between 0 and 15
        """
        # Normalize category string
        category_normalized = category.strip().title()
        
        # Try to match to known categories
        try:
            category_enum = CategoryPriority(category_normalized)
            return CATEGORY_SCORES.get(category_enum, CATEGORY_SCORES[CategoryPriority.OTHER])
        except ValueError:
            # Unknown category, use OTHER score
            return CATEGORY_SCORES[CategoryPriority.OTHER]
    
    @classmethod
    def _classify_opportunity(cls, score: int) -> OpportunityTag:
        """Classify lead opportunity based on digital score.
        
        Classification:
        - High: 80-100 points
        - Medium: 50-79 points
        - Low: 0-49 points
        
        Args:
            score: Digital presence score (0-100)
            
        Returns:
            OpportunityTag enum value
        """
        if score >= 80:
            return OpportunityTag.HIGH
        elif score >= 50:
            return OpportunityTag.MEDIUM
        else:
            return OpportunityTag.LOW
