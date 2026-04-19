"""Extract coordinates from latlng-based place_ids."""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal
from app.models.business import Business
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    db = SessionLocal()
    try:
        # Get businesses without coordinates but with latlng place_ids
        businesses = db.query(Business).filter(
            (Business.latitude == None) | (Business.longitude == None),
            Business.place_id.like('latlng_%')
        ).all()
        
        logger.info(f"Found {len(businesses)} businesses with latlng place_ids")
        
        updated = 0
        failed = 0
        
        for business in businesses:
            try:
                # Extract coordinates from place_id
                # Format: latlng_LAT_LNG_NAME
                parts = business.place_id.split('_')
                if len(parts) >= 3 and parts[0] == 'latlng':
                    lat = float(parts[1])
                    lng = float(parts[2])
                    
                    business.latitude = lat
                    business.longitude = lng
                    db.commit()
                    updated += 1
                    logger.info(f"  ✓ Updated: {business.name} ({lat}, {lng})")
                else:
                    failed += 1
                    logger.warning(f"  ✗ Invalid place_id format: {business.place_id}")
                    
            except Exception as e:
                failed += 1
                logger.error(f"  ✗ Error updating {business.name}: {str(e)}")
                db.rollback()
        
        logger.info(f"\nComplete! Updated: {updated}, Failed: {failed}")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
