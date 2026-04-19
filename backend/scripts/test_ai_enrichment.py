"""Test if AI enrichment is working."""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

try:
    # Check if any business insights have AI data
    result = db.execute(text("""
        SELECT 
            b.name,
            b.category,
            bi.ai_description,
            bi.ai_digital_maturity,
            bi.ai_growth_potential,
            bi.ai_urgency_score
        FROM business_insights bi
        JOIN businesses b ON bi.business_id = b.id
        WHERE bi.ai_description IS NOT NULL
        ORDER BY bi.created_at DESC
        LIMIT 5
    """))
    
    rows = result.fetchall()
    
    if rows:
        print("✅ AI enrichment data found!")
        print("\nSample businesses with AI data:")
        for name, category, desc, maturity, growth, urgency in rows:
            print(f"\n📍 {name} ({category})")
            print(f"   Description: {desc[:100]}...")
            print(f"   Digital Maturity: {maturity}")
            print(f"   Growth Potential: {growth}")
            print(f"   Urgency Score: {urgency}")
    else:
        print("❌ No AI enrichment data found in database!")
        print("\nThis means:")
        print("1. The AI enrichment code isn't running during lead discovery")
        print("2. OR there's an error preventing the data from being saved")
        print("\nCheck backend logs for errors.")
        
finally:
    db.close()
