"""Test what the API is returning for a lead with AI data."""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.database import SessionLocal
from sqlalchemy import text
from app.schemas.leads import BusinessInsightResponse
from pydantic import ValidationError

db = SessionLocal()

try:
    # Get a business insight with AI data
    result = db.execute(text("""
        SELECT 
            bi.*
        FROM business_insights bi
        WHERE bi.ai_description IS NOT NULL
        LIMIT 1
    """))
    
    row = result.fetchone()
    
    if row:
        print("✅ Found business insight with AI data")
        print(f"\nDatabase columns returned: {result.keys()}")
        
        # Try to create a Pydantic model from it
        try:
            # Convert row to dict
            data = dict(zip(result.keys(), row))
            print(f"\nData dict keys: {list(data.keys())}")
            
            # Check if AI fields are present
            ai_fields = [k for k in data.keys() if k.startswith('ai_')]
            print(f"\nAI fields in data: {ai_fields}")
            
            if data.get('ai_description'):
                print(f"\n✅ ai_description exists: {data['ai_description'][:100]}...")
            else:
                print("\n❌ ai_description is None or missing")
                
            # Try to create the response model
            response = BusinessInsightResponse(**data)
            print("\n✅ BusinessInsightResponse model created successfully!")
            print(f"   Has ai_description: {response.ai_description is not None}")
            print(f"   Has ai_specialties: {response.ai_specialties is not None}")
            
        except ValidationError as e:
            print(f"\n❌ Pydantic validation error:")
            print(e)
        except Exception as e:
            print(f"\n❌ Error creating response model: {str(e)}")
    else:
        print("❌ No business insights with AI data found")
        
finally:
    db.close()
