"""Test that BusinessInsightResponse.from_orm works correctly with AI fields."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal
from app.models.business import BusinessInsight
from app.schemas.leads import BusinessInsightResponse
from sqlalchemy import text

def test_schema_mapping():
    """Test that from_orm correctly maps database columns to schema fields."""
    db = SessionLocal()
    try:
        # Find a business insight with AI data
        result = db.execute(text("""
            SELECT * FROM business_insights 
            WHERE ai_description IS NOT NULL 
            LIMIT 1
        """)).first()
        
        if not result:
            print("❌ No AI-enriched insights found in database")
            return False
            
        # Convert to dict
        data = dict(result._mapping)
        print(f"✅ Found insight with AI data: {data.get('ai_description', '')[:50]}...")
        
        # Create a mock object with the data
        class MockInsight:
            def __init__(self, data):
                for key, value in data.items():
                    setattr(self, key, value)
        
        mock_obj = MockInsight(data)
        
        # Test from_orm
        try:
            response = BusinessInsightResponse.from_orm(mock_obj)
            print("✅ from_orm() succeeded!")
            print(f"   priority_score: {response.priority_score}")
            print(f"   freshness: {response.freshness}")
            print(f"   ai_description: {response.ai_description[:50] if response.ai_description else 'None'}...")
            print(f"   ai_digital_maturity: {response.ai_digital_maturity}")
            print(f"   ai_growth_potential: {response.ai_growth_potential}")
            return True
        except Exception as e:
            print(f"❌ from_orm() failed: {e}")
            return False
            
    finally:
        db.close()

if __name__ == "__main__":
    success = test_schema_mapping()
    sys.exit(0 if success else 1)
