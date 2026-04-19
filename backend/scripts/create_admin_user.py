"""Script to create an admin user."""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database import engine, Base
from app.models.user import User, Admin
from app.utils.auth import hash_password
import uuid


def create_admin_user(
    email: str,
    password: str,
    name: str,
    phone: str = "+919999999999"
):
    """Create an admin user in the database."""
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Create session
    db = Session(bind=engine)
    
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"❌ User with email {email} already exists!")
            return None
        
        # Create user
        user_id = str(uuid.uuid4())
        admin_id = str(uuid.uuid4())
        
        user = User(
            id=user_id,
            email=email,
            password_hash=hash_password(password),
            role="admin",
            phone=phone,
            phone_verified=True,
            email_verified=True,
            is_active=True
        )
        
        # Create admin profile
        admin = Admin(
            id=admin_id,
            user_id=user_id,
            name=name,
            permissions='["all"]'
        )
        
        db.add(user)
        db.add(admin)
        db.commit()
        
        print("✅ Admin user created successfully!")
        print(f"\n📧 Email: {email}")
        print(f"🔑 Password: {password}")
        print(f"👤 Name: {name}")
        print(f"📱 Phone: {phone}")
        print(f"\n🔗 Login at: http://localhost:5173/login")
        
        return user
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating admin user: {e}")
        return None
    finally:
        db.close()


if __name__ == "__main__":
    # Create admin user with default credentials
    create_admin_user(
        email="admin@localai.com",
        password="Admin@123",
        name="Platform Admin",
        phone="+919999999999"
    )
