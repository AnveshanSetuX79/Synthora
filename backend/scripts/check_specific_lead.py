"""Check if a specific business has AI data."""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

try:
    # Check for Vaijanath Amruttulya
    result = db.execute(text("""
        SELECT 
            b.name,
            b.category,
            bi.ai_description,
            bi.ai_digital_maturity,
            bi.created_at,
            bi.ai_enriched_at
        FROM business_insights bi
        JOIN businesses b ON bi.business_id = b.id
        WHERE b.name LIKE '%Vaijanath%'
    """))
    
    row = result.fetchone()
    
    if row:
        name, category, ai_desc, ai_maturity, created, enriched = row
        print(f"✅ Found: {name}")
        print(f"   Category: {category}")
        print(f"   Created: {created}")
        print(f"   AI Enriched: {enriched}")
        
        if ai_desc:
            print(f"   ✅ HAS AI DATA")
            print(f"   Description: {ai_desc[:100]}...")
        else:
            print(f"   ❌ NO AI DATA")
            print(f"\n   This lead was discovered before AI enrichment was added.")
            print(f"   Run the backfill script to add AI data to old leads.")
    else:
        print("❌ Business not found in database")
        
finally:
    db.close()
