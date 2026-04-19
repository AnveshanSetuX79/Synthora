"""Check current database state."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import create_engine, inspect, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in environment variables")
    sys.exit(1)

print(f"Connecting to database...")
print(f"URL: {DATABASE_URL[:50]}...")

try:
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    
    print("\n=== DATABASE CONNECTION SUCCESSFUL ===\n")
    
    # Get all tables
    tables = inspector.get_table_names()
    print(f"📊 Total tables: {len(tables)}\n")
    
    if tables:
        print("📋 Existing tables:")
        for table in sorted(tables):
            print(f"  ✓ {table}")
    else:
        print("⚠️  No tables found in database")
    
    # Check for enum types
    print("\n🔤 Checking enum types...")
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT typname 
            FROM pg_type 
            WHERE typtype = 'e'
            ORDER BY typname
        """))
        enums = [row[0] for row in result]
        
        if enums:
            print(f"Found {len(enums)} enum types:")
            for enum in enums:
                print(f"  ✓ {enum}")
        else:
            print("  No enum types found")
    
    # Check alembic version
    print("\n📌 Checking migration status...")
    if 'alembic_version' in tables:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version_num FROM alembic_version"))
            version = result.scalar()
            if version:
                print(f"  Current migration: {version}")
            else:
                print("  No migrations applied yet")
    else:
        print("  Alembic version table not found - no migrations applied")
    
    print("\n✅ Database check complete!")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    sys.exit(1)
