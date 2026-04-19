"""Force update coordinates for all businesses without lat/lng."""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal
from app.models.business import Business
from app.services.google_places import GooglePlacesService
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    db = SessionLocal()
    try:
        # Get businesses without coordinates
        businesses = db.query(Business).filter(
            (Business.latitude == None) | (Business.longitude == None)
        ).limit(20).all()
        
        logger.info(f"Found {len(businesses)} businesses without coordinates")
        
        if not businesses:
            logger.info("All businesses have coordinates!")
            return
        
        # Initialize Google Places service
        google_service = GooglePlacesService(settings.google_places_api_key)
        
        updated = 0
        failed = 0
        
        for business in businesses:
            try:
                logger.info(f"Updating {business.name}...")
                
                # Get fresh data from Google Places
                business_data = google_service.get_business_details(business.place_id)
                
                if business_data and business_data.latitude and business_data.longitude:
                    business.latitude = business_data.latitude
                    business.longitude = business_data.longitude
                    db.commit()
                    updated += 1
                    logger.info(f"  ✓ Updated: {business.name} ({business_data.latitude}, {business_data.longitude})")
                else:
                    failed += 1
                    logger.warning(f"  ✗ No coordinates found for {business.name}")
                    
            except Exception as e:
                failed += 1
                logger.error(f"  ✗ Error updating {business.name}: {str(e)}")
                db.rollback()
        
        logger.info(f"\nComplete! Updated: {updated}, Failed: {failed}")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
