"""Test script for business data refresh functionality.

Run this to test the refresh service manually.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal
from app.services.business_refresh import BusinessRefreshService
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Test the business refresh service."""
    logger.info("Starting business refresh test")
    
    db = SessionLocal()
    try:
        service = BusinessRefreshService(db)
        
        # Get businesses needing refresh
        businesses = service.get_businesses_needing_refresh()
        logger.info(f"Found {len(businesses)} businesses needing refresh")
        
        if businesses:
            logger.info("\nBusinesses needing refresh:")
            for b in businesses[:5]:  # Show first 5
                logger.info(f"  - {b.name} (ID: {b.id}, Place ID: {b.place_id})")
            
            # Ask for confirmation
            response = input(f"\nRefresh {len(businesses)} businesses? (y/n): ")
            if response.lower() == 'y':
                result = service.refresh_batch()
                
                logger.info("\n=== Refresh Results ===")
                logger.info(f"Total processed: {result['total']}")
                logger.info(f"Successful: {result['success']}")
                logger.info(f"Failed: {result['failed']}")
                
                if result['results']:
                    logger.info("\nDetailed results:")
                    for r in result['results']:
                        if r['success']:
                            logger.info(f"  ✓ {r['business_name']}: {r['field_count']} fields updated")
                        else:
                            logger.info(f"  ✗ {r['business_id']}: {r.get('error', 'Unknown error')}")
            else:
                logger.info("Refresh cancelled")
        else:
            logger.info("No businesses need refresh at this time")
    
    except Exception as e:
        logger.error(f"Error during refresh test: {str(e)}")
        raise
    
    finally:
        db.close()
        logger.info("Test complete")


if __name__ == "__main__":
    main()
