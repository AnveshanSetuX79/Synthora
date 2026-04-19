"""Create a test business owner account."""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal
from app.models.user import User, BusinessOwner
from app.models.business import Business
from app.utils.auth import hash_password
import uuid
from datetime import datetime, timezone

def create_business_owner():
    db = SessionLocal()
    
    try:
        # Check if business owner already exists
        existing_user = db.query(User).filter(User.email == "owner@restaurant.com").first()
        if existing_user:
            print("Business owner already exists!")
            print(f"Email: owner@restaurant.com")
            print(f"Role: {existing_user.role}")
            return
        
        # Get first business or create one
        business = db.query(Business).first()
        if not business:
            print("No businesses found in database. Creating a test business...")
            business = Business(
                id=str(uuid.uuid4()),
                place_id="test_place_123",
                name="Test Restaurant",
                category="restaurant",
                address="123 Main St, Pune, India",
                city="Pune",
                phone="+919876543210",
                is_active=True,
                created_at=datetime.now(timezone.utc)
            )
            db.add(business)
            db.commit()
            db.refresh(business)
        
        # Create user
        user = User(
            id=str(uuid.uuid4()),
            email="owner@restaurant.com",
            password_hash=hash_password("Owner@123"),
            role="businessowner",
            phone="+919876543210",
            phone_verified=True,
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
        db.add(user)
        db.flush()
        
        # Create business owner profile
        owner = BusinessOwner(
            id=str(uuid.uuid4()),
            user_id=user.id,
            owner_name="Restaurant Owner",
            business_id=business.id
        )
        db.add(owner)
        
        db.commit()
        
        print("✅ Business owner created successfully!")
        print(f"Email: owner@restaurant.com")
        print(f"Password: Owner@123")
        print(f"Role: businessowner")
        print(f"Business: {business.name}")
        print(f"Business ID: {business.id}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating business owner: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    create_business_owner()
