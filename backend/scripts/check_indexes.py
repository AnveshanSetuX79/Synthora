"""Check database indexes."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    result = db.execute(text("""
        SELECT tablename, indexname 
        FROM pg_indexes 
        WHERE schemaname = 'public' 
        ORDER BY tablename, indexname
    """)).fetchall()
    
    print("Current Database Indexes:")
    print("=" * 80)
    current_table = None
    for table, index in result:
        if table != current_table:
            print(f"\n{table}:")
            current_table = table
        print(f"  - {index}")
    
finally:
    db.close()
