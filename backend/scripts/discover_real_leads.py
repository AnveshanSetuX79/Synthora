"""Discover real leads using Google Places API."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.google_places import GooglePlacesService

def discover_real_restaurants():
    """Discover real restaurants in Bangalore."""
    service = GooglePlacesService()
    
    print("=" * 80)
    print("DISCOVERING REAL RESTAURANTS IN BANGALORE")
    print("=" * 80)
    print()
    
    try:
        # Search for restaurants in Bangalore
        results = service.search_businesses(
            category='restaurant',
            location='Bangalore',
            limit=5
        )
        
        print(f"Found {len(results)} real restaurants:\n")
        
        for i, business in enumerate(results, 1):
            print(f"{i}. {business['name']}")
            print(f"   Place ID: {business['place_id']}")
            print(f"   Address: {business['address']}")
            print(f"   Rating: {business.get('rating', 'N/A')}")
            print(f"   Reviews: {business.get('user_ratings_total', 0)}")
            print()
        
        print("=" * 80)
        print("✅ These are REAL businesses from Google Places API")
        print("   Use the 'Discover Leads' feature with category + city to import them")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure GOOGLE_PLACES_API_KEY is set in your .env file")

if __name__ == "__main__":
    discover_real_restaurants()
