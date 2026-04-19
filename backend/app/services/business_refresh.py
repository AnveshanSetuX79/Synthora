"""Business data refresh service.

Handles periodic refresh of business data from Google Places API.
Requirement 2.1: 7-day refresh cycle for existing records.
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..database import SessionLocal
from ..models.business import Business, BusinessInsight
from ..services.google_places import GooglePlacesService, GooglePlacesAPIError, RateLimitError
from ..services.lead_scoring import LeadScoringService
from ..config import settings

logger = logging.getLogger(__name__)


class BusinessRefreshService:
    """Service for refreshing business data from Google Places API."""
    
    REFRESH_INTERVAL_DAYS = 7
    BATCH_SIZE = 50  # Process in batches to avoid rate limits
    
    def __init__(self, db: Session):
        """Initialize refresh service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.places_service = GooglePlacesService(settings.google_places_api_key)
        self.scoring_service = LeadScoringService()
    
    def get_businesses_needing_refresh(self) -> List[Business]:
        """Get businesses that need data refresh (>7 days old).
        
        Returns:
            List of businesses needing refresh
        """
        cutoff_date = datetime.utcnow() - timedelta(days=self.REFRESH_INTERVAL_DAYS)
        
        businesses = (
            self.db.query(Business)
            .join(BusinessInsight)
            .filter(
                and_(
                    Business.is_active == True,
                    BusinessInsight.last_verified < cutoff_date
                )
            )
            .limit(self.BATCH_SIZE)
            .all()
        )
        
        logger.info(f"Found {len(businesses)} businesses needing refresh")
        return businesses
    
    def refresh_business(self, business: Business) -> Dict[str, Any]:
        """Refresh data for a single business.
        
        Args:
            business: Business to refresh
            
        Returns:
            Dict with refresh status and updated fields
        """
        try:
            # Fetch fresh data from Google Places
            business_data = self.places_service.refresh_business_data(business.place_id)
            
            if not business_data:
                logger.warning(f"No data returned for business {business.id} (place_id: {business.place_id})")
                return {
                    "success": False,
                    "business_id": business.id,
                    "error": "No data returned from API"
                }
            
            # Update business fields
            updated_fields = []
            
            if business.name != business_data.name:
                business.name = business_data.name
                updated_fields.append("name")
            
            if business.address != business_data.address:
                business.address = business_data.address
                updated_fields.append("address")
            
            if business.phone != business_data.phone:
                business.phone = business_data.phone
                updated_fields.append("phone")
            
            if business.city != business_data.city:
                business.city = business_data.city
                updated_fields.append("city")
            
            business.updated_at = datetime.utcnow()
            
            # Update business insights
            insight = business.insights
            if insight:
                if insight.rating != business_data.rating:
                    insight.rating = business_data.rating
                    updated_fields.append("rating")
                
                if insight.review_count != business_data.review_count:
                    insight.review_count = business_data.review_count
                    updated_fields.append("review_count")
                
                if insight.has_website != business_data.has_website:
                    insight.has_website = business_data.has_website
                    updated_fields.append("has_website")
                
                if insight.website_url != business_data.website_url:
                    insight.website_url = business_data.website_url
                    updated_fields.append("website_url")
                
                # Recalculate digital score
                old_score = insight.digital_score
                score_result = self.scoring_service.calculate_digital_score(business_data)
                insight.digital_score = score_result["score"]
                insight.digital_score_breakdown = score_result["breakdown"]
                
                if old_score != insight.digital_score:
                    updated_fields.append("digital_score")
                
                # Update last verified timestamp
                insight.last_verified = datetime.utcnow()
                insight.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"Refreshed business {business.id}: {len(updated_fields)} fields updated")
            return {
                "success": True,
                "business_id": business.id,
                "business_name": business.name,
                "updated_fields": updated_fields,
                "field_count": len(updated_fields)
            }
            
        except RateLimitError as e:
            logger.error(f"Rate limit exceeded while refreshing business {business.id}: {str(e)}")
            self.db.rollback()
            return {
                "success": False,
                "business_id": business.id,
                "error": "rate_limit",
                "message": str(e)
            }
        
        except GooglePlacesAPIError as e:
            logger.error(f"API error while refreshing business {business.id}: {str(e)}")
            self.db.rollback()
            return {
                "success": False,
                "business_id": business.id,
                "error": "api_error",
                "message": str(e)
            }
        
        except Exception as e:
            logger.error(f"Unexpected error refreshing business {business.id}: {str(e)}")
            self.db.rollback()
            return {
                "success": False,
                "business_id": business.id,
                "error": "unexpected",
                "message": str(e)
            }
    
    def refresh_batch(self) -> Dict[str, Any]:
        """Refresh a batch of businesses needing update.
        
        Returns:
            Summary of refresh operation
        """
        businesses = self.get_businesses_needing_refresh()
        
        if not businesses:
            logger.info("No businesses need refresh at this time")
            return {
                "total": 0,
                "success": 0,
                "failed": 0,
                "results": []
            }
        
        results = []
        success_count = 0
        failed_count = 0
        
        for business in businesses:
            result = self.refresh_business(business)
            results.append(result)
            
            if result["success"]:
                success_count += 1
            else:
                failed_count += 1
                
                # Stop if rate limit exceeded
                if result.get("error") == "rate_limit":
                    logger.warning("Rate limit exceeded, stopping batch refresh")
                    break
        
        summary = {
            "total": len(results),
            "success": success_count,
            "failed": failed_count,
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Batch refresh complete: {success_count} success, {failed_count} failed")
        return summary


def run_scheduled_refresh():
    """Run scheduled refresh job (called by scheduler).
    
    This function is called by APScheduler to refresh business data.
    """
    logger.info("Starting scheduled business data refresh")
    
    db = SessionLocal()
    try:
        service = BusinessRefreshService(db)
        result = service.refresh_batch()
        
        logger.info(f"Scheduled refresh completed: {result['success']} businesses updated")
        return result
    
    except Exception as e:
        logger.error(f"Scheduled refresh failed: {str(e)}")
        raise
    
    finally:
        db.close()
