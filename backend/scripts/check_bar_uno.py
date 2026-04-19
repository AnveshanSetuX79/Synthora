"""Check if Bar Uno is real or mock data."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal
from sqlalchemy import text

def check_bar_uno():
    """Check Bar Uno data."""
    db = SessionLocal()
    try:
        result = db.execute(text("""
            SELECT 
                b.name, 
                b.category, 
                b.place_id, 
                b.address,
                b.city,
                bi.digital_score, 
                bi.has_website, 
                bi.rating, 
                bi.review_count,
                b.created_at
            FROM businesses b 
            JOIN business_insights bi ON b.id = bi.business_id 
            WHERE b.name = 'Bar Uno' 
            LIMIT 1
        """)).first()
        
        if result:
            print("=" * 80)
            print("BAR UNO - DATA VERIFICATION")
            print("=" * 80)
            print(f"Name: {result[0]}")
            print(f"Category: {result[1]}")
            print(f"Place ID: {result[2]}")
            print(f"Address: {result[3]}")
            print(f"City: {result[4]}")
            print(f"Digital Score: {result[5]}")
            print(f"Has Website: {result[6]}")
            print(f"Rating: {result[7]}")
            print(f"Reviews: {result[8]}")
            print(f"Created At: {result[9]}")
            print()
            
            # Check if it's from Google Places
            if result[2] and result[2].startswith('ChIJ'):
                print("✅ REAL DATA - This is a valid Google Places ID")
                print(f"   Google Places ID: {result[2]}")
                print("   This business was discovered via Google Places API")
            else:
                print("⚠️ MOCK/MANUAL DATA - Not from Google Places API")
            
            print("=" * 80)
        else:
            print("❌ Bar Uno not found in database")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_bar_uno()
