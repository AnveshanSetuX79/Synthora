"""Script to set a user as founder."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.user import User

def set_founder_role(email: str):
    """Set user role to founder."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"❌ User with email '{email}' not found")
            return
        
        old_role = user.role
        user.role = "founder"
        db.commit()
        
        print(f"✅ Successfully updated user role")
        print(f"   Email: {email}")
        print(f"   Old Role: {old_role}")
        print(f"   New Role: founder")
        print(f"\n🚀 You can now access the Founder Dashboard at /founder/dashboard")
        print(f"\n⚠️  IMPORTANT: Logout and login again for changes to take effect!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Change this to your admin email
    email = "admin@localai.com"
    
    if len(sys.argv) > 1:
        email = sys.argv[1]
    
    print(f"Setting founder role for: {email}")
    set_founder_role(email)
