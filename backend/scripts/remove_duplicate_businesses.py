"""Remove duplicate businesses from database.

This script:
1. Finds businesses with duplicate place_ids
2. Keeps the oldest record (first created)
3. Deletes newer duplicates
4. Updates any foreign key references
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.database import SessionLocal, engine
from sqlalchemy import text, func
from datetime import datetime


def remove_duplicates():
    """Remove duplicate businesses keeping the oldest record."""
    db = SessionLocal()
    
    try:
        print("🔍 Finding duplicate businesses...")
        
        # Use raw SQL to avoid model import issues
        # Find duplicate place_ids
        result = db.execute(text("""
            SELECT place_id, COUNT(*) as count
            FROM businesses
            GROUP BY place_id
            HAVING COUNT(*) > 1
        """))
        
        duplicates = result.fetchall()
        
        if not duplicates:
            print("✅ No duplicate businesses found!")
            return
        
        print(f"Found {len(duplicates)} duplicate place_ids")
        
        total_removed = 0
        
        for place_id, count in duplicates:
            # Get all businesses with this place_id
            businesses = db.execute(text("""
                SELECT id, name, created_at
                FROM businesses
                WHERE place_id = :place_id
                ORDER BY created_at ASC
            """), {"place_id": place_id}).fetchall()
            
            # Keep the first (oldest) one
            keep_id = businesses[0][0]
            keep_name = businesses[0][1]
            keep_created = businesses[0][2]
            
            print(f"\n📍 {keep_name} (place_id: {place_id})")
            print(f"   Keeping: {keep_id} (created {keep_created})")
            print(f"   Removing {len(businesses) - 1} duplicates:")
            
            for business in businesses[1:]:
                dup_id = business[0]
                dup_created = business[2]
                print(f"   - {dup_id} (created {dup_created})")
                
                # Update foreign key references
                # 1. Update leads
                result = db.execute(text("""
                    UPDATE leads
                    SET business_id = :keep_id
                    WHERE business_id = :dup_id
                """), {"keep_id": keep_id, "dup_id": dup_id})
                print(f"     Updated {result.rowcount} leads")
                
                # 2. Handle business insights - delete duplicates for keep_id, move others
                # First check if keep already has insights
                has_insights = db.execute(text("""
                    SELECT COUNT(*) FROM business_insights
                    WHERE business_id = :keep_id
                """), {"keep_id": keep_id}).scalar()
                
                if has_insights:
                    # Delete duplicate insights
                    result = db.execute(text("""
                        DELETE FROM business_insights
                        WHERE business_id = :dup_id
                    """), {"dup_id": dup_id})
                    print(f"     Deleted {result.rowcount} duplicate insights")
                else:
                    # Move insights to keep
                    result = db.execute(text("""
                        UPDATE business_insights
                        SET business_id = :keep_id
                        WHERE business_id = :dup_id
                    """), {"keep_id": keep_id, "dup_id": dup_id})
                    print(f"     Moved {result.rowcount} insights")
                
                # 3. Update demo websites
                result = db.execute(text("""
                    UPDATE demo_websites
                    SET business_id = :keep_id
                    WHERE business_id = :dup_id
                """), {"keep_id": keep_id, "dup_id": dup_id})
                print(f"     Updated {result.rowcount} demos")
                
                # 4. Update business owners
                result = db.execute(text("""
                    UPDATE business_owners
                    SET business_id = :keep_id
                    WHERE business_id = :dup_id
                """), {"keep_id": keep_id, "dup_id": dup_id})
                print(f"     Updated {result.rowcount} business owners")
                
                # Delete the duplicate business
                db.execute(text("""
                    DELETE FROM businesses
                    WHERE id = :dup_id
                """), {"dup_id": dup_id})
                total_removed += 1
        
        # Commit all changes
        db.commit()
        
        print(f"\n✅ Successfully removed {total_removed} duplicate businesses!")
        
        # Verify
        remaining = db.execute(text("""
            SELECT COUNT(*) FROM (
                SELECT place_id
                FROM businesses
                GROUP BY place_id
                HAVING COUNT(*) > 1
            ) as dupes
        """)).scalar()
        
        if remaining == 0:
            print("✅ Verification passed: No duplicates remaining")
        else:
            print(f"⚠️ Warning: {remaining} duplicates still exist")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("REMOVE DUPLICATE BUSINESSES")
    print("=" * 60)
    
    remove_duplicates()
    
    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
