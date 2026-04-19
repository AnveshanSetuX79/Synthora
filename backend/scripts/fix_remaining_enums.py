"""Script to fix any remaining enum columns."""
import sys
sys.path.append('.')

from app.database import engine
from sqlalchemy import text

def fix_remaining_enums():
    """Fix remaining enum columns one by one with proper transaction handling."""
    
    tables_to_fix = [
        ("freelancer_roi", "period"),
        ("analytics_events", "event_type"),
        ("leads", "source"),
        ("leads", "status"),
        ("lead_contacts", "status"),
        ("lead_contacts", "consent_status"),
        ("outreach_messages", "channel"),
        ("outreach_messages", "delivery_status"),
        ("lead_activities", "activity_type"),
        ("messages", "channel"),
        ("messages", "status"),
        ("campaigns", "type"),
        ("campaigns", "status"),
        ("business_insights", "freshness"),
        ("kyc_documents", "document_type"),
        ("kyc_documents", "status"),
    ]
    
    for table, column in tables_to_fix:
        try:
            with engine.begin() as conn:
                print(f"Converting {table}.{column}...", end=" ")
                conn.execute(text(f"ALTER TABLE {table} ALTER COLUMN {column} TYPE VARCHAR(50)"))
                print("✅")
        except Exception as e:
            if "does not exist" in str(e):
                print("⏭️  (doesn't exist)")
            elif "already" in str(e).lower():
                print("✅ (already converted)")
            else:
                print(f"❌ {str(e)[:100]}")
    
    print("\n✅ All enum columns processed!")

if __name__ == "__main__":
    fix_remaining_enums()
