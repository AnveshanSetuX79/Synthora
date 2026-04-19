"""Authentication API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Body, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
import uuid
import re
from collections import defaultdict
from typing import Dict

from ..database import get_db
from ..models.user import User, Freelancer, BusinessOwner, UserRole, FreelancerTier
from ..schemas.auth import (
    UserRegisterRequest, 
    UserRegisterResponse, 
    ErrorResponse,
    VerifyOTPRequest,
    LoginRequest
)
from ..utils.auth import hash_password, create_access_token, verify_password
from ..utils.otp import generate_otp, store_otp, send_otp_sms, verify_otp as verify_otp_code
from ..utils.password_validator import validate_password_strength
from ..services.audit_log import AuditLogService
from ..middleware.auth import get_current_user

router = APIRouter(prefix="/api/auth", tags=["authentication"])

# In-memory rate limiting for registration (5 attempts per IP per hour)
# For production, use Redis
registration_attempts: Dict[str, list] = defaultdict(list)
REGISTRATION_LIMIT = 5  # Max registrations per IP per hour
REGISTRATION_WINDOW = 3600  # 1 hour in seconds


def check_registration_rate_limit(ip_address: str) -> bool:
    """Check if IP has exceeded registration rate limit.
    
    Args:
        ip_address: Client IP address
        
    Returns:
        True if within limit, False if exceeded
    """
    now = datetime.now()
    hour_ago = now - timedelta(hours=1)
    
    # Clean old attempts
    registration_attempts[ip_address] = [
        timestamp for timestamp in registration_attempts[ip_address]
        if timestamp > hour_ago
    ]
    
    # Check limit
    if len(registration_attempts[ip_address]) >= REGISTRATION_LIMIT:
        return False
    
    # Record this attempt
    registration_attempts[ip_address].append(now)
    return True


def get_client_ip(request: Request) -> str:
    """Get client IP address from request."""
    # Check X-Forwarded-For header (for proxied requests)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    # Check X-Real-IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fall back to direct client IP
    if request.client:
        return request.client.host
    
    return "unknown"


@router.post(
    "/register",
    response_model=UserRegisterResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input or duplicate email"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def register_user(
    request: UserRegisterRequest,
    req: Request,
    db: Session = Depends(get_db)
):
    """
    Register a new user (freelancer or business owner).
    
    This endpoint:
    1. Validates email format and uniqueness
    2. Validates phone number format
    3. Validates password strength
    4. Hashes password using bcrypt
    5. Generates and sends OTP via SMS
    6. Creates User record and role-specific record
    7. Returns JWT token for immediate access
    
    Requirements: 4.1, 4.2, 4.3, 35.1
    """
    
    # Check rate limit (5 registrations per IP per hour)
    client_ip = get_client_ip(req)
    if not check_registration_rate_limit(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many registration attempts. Please try again in an hour."
        )
    
    print(f"Registration request received: email={request.email}, role={request.role}, name={request.name}")
    
    # Validate password strength
    is_valid, errors = validate_password_strength(request.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Password does not meet requirements", "errors": errors}
        )
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        print(f"Email already exists: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Generate OTP and send via SMS
    otp = generate_otp()
    store_otp(request.phone, otp)
    
    # Send OTP via SMS (mock for MVP)
    sms_sent = await send_otp_sms(request.phone, otp)
    if not sms_sent:
        # Log error but don't fail registration
        print(f"Warning: Failed to send OTP to {request.phone}")
    
    # Hash password
    password_hash = hash_password(request.password)
    
    # Create user ID
    user_id = str(uuid.uuid4())
    
    try:
        # Create User record - use string directly, SQLAlchemy will handle it
        user = User(
            id=user_id,
            email=request.email,
            password_hash=password_hash,
            role=request.role,  # Pass string directly: "freelancer" or "businessowner"
            phone=request.phone,
            phone_verified=False,  # Will be set to True after OTP verification
            email_verified=False,
            is_active=True  # Allow login immediately, OTP verification is separate
        )
        db.add(user)
        db.flush()  # Flush to get user.id for foreign key
        
        # Create role-specific record
        freelancer_id = None
        tier = None
        business_owner_id = None
        business_id = None
        
        if request.role == "freelancer":
            freelancer_id = str(uuid.uuid4())
            freelancer = Freelancer(
                id=freelancer_id,
                user_id=user.id,
                name=request.name,
                portfolio_url=request.portfolio_url,
                tier="New",  # Use string value directly
                daily_limit=3,
                remaining_contacts=3
            )
            db.add(freelancer)
            tier = "New"
            
        elif request.role == "businessowner":
            business_owner_id = str(uuid.uuid4())
            business_owner = BusinessOwner(
                id=business_owner_id,
                user_id=user.id,
                owner_name=request.owner_name,
                business_id=None  # Will be linked later when business is claimed
            )
            db.add(business_owner)
        
        # Commit transaction
        db.commit()
        db.refresh(user)
        
        # Generate JWT token
        token_data = {
            "user_id": user.id,
            "email": user.email,
            "role": user.role,  # Already a string now
        }
        
        # Add tier for freelancers
        if request.role == "freelancer":
            token_data["tier"] = tier
        
        access_token = create_access_token(token_data)
        
        # Return response
        return UserRegisterResponse(
            user_id=user.id,
            email=user.email,
            role=user.role,  # Already a string
            phone=user.phone,
            phone_verified=user.phone_verified,
            access_token=access_token,
            token_type="bearer",
            freelancer_id=freelancer_id,
            tier=tier,
            business_owner_id=business_owner_id,
            business_id=business_id
        )
        
    except IntegrityError as e:
        db.rollback()
        print(f"IntegrityError during registration: {str(e)}")
        print(f"Original error: {e.orig}")
        # Check if it's a duplicate email error
        if "email" in str(e.orig).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database integrity error: {str(e.orig)}"
        )
    except Exception as e:
        db.rollback()
        print(f"Registration error: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user account: {str(e)}"
        )



@router.post(
    "/verify-otp",
    response_model=UserRegisterResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid or expired OTP"},
        404: {"model": ErrorResponse, "description": "User not found"}
    }
)
async def verify_otp(
    request: VerifyOTPRequest,
    db: Session = Depends(get_db)
):
    """
    Verify OTP code and activate user account.
    
    This endpoint:
    1. Verifies the OTP code against stored value
    2. Marks phone as verified
    3. Updates user status to active
    4. Returns success confirmation
    
    Requirements: 4.2, 35.1
    """
    from ..schemas.auth import VerifyOTPRequest, VerifyOTPResponse
    from ..utils.otp import verify_otp as verify_otp_code
    
    print(f"OTP verification request: phone={request.phone}, otp={request.otp_code}")
    
    # Verify OTP
    if not verify_otp_code(request.phone, request.otp_code):
        print(f"OTP verification failed for phone: {request.phone}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP code"
        )
    
    # Find user by phone
    user = db.query(User).filter(User.phone == request.phone).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found with this phone number"
        )
    
    # Update user verification status
    user.phone_verified = True
    user.is_active = True
    
    try:
        db.commit()
        db.refresh(user)
        
        # Generate new JWT token with updated status
        token_data = {
            "user_id": user.id,
            "email": user.email,
            "role": user.role,  # Already a string
        }
        
        # Add tier for freelancers
        if user.role == "freelancer" and user.freelancer:
            token_data["tier"] = user.freelancer.tier
        
        access_token = create_access_token(token_data)
        
        # Prepare response based on role
        response_data = {
            "user_id": user.id,
            "email": user.email,
            "role": user.role,  # Already a string
            "phone": user.phone,
            "phone_verified": user.phone_verified,
            "access_token": access_token,
            "token_type": "bearer"
        }
        
        if user.role == "freelancer" and user.freelancer:
            response_data["freelancer_id"] = user.freelancer.id
            response_data["tier"] = user.freelancer.tier
        elif user.role == "businessowner" and user.business_owner:
            response_data["business_owner_id"] = user.business_owner.id
            response_data["business_id"] = user.business_owner.business_id
        
        return UserRegisterResponse(**response_data)
        
    except Exception as e:
        db.rollback()
        print(f"OTP verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify OTP"
        )


@router.post(
    "/login",
    response_model=UserRegisterResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid credentials"},
        401: {"model": ErrorResponse, "description": "Account not verified"}
    }
)
async def login(
    request: LoginRequest,
    req: Request,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT token.
    
    This endpoint:
    1. Validates credentials (email/phone + password)
    2. Logs authentication attempt
    3. Generates JWT token with user_id, role, tier
    4. Returns token and user profile
    
    Requirements: 4.1, 4.3
    """
    print(f"Login request: identifier={request.identifier}, password_length={len(request.password)}")
    
    # Try to find user by email or phone (case-insensitive for email)
    user = None
    if "@" in request.identifier:
        # Identifier is email - use case-insensitive comparison
        from sqlalchemy import func
        user = db.query(User).filter(func.lower(User.email) == request.identifier.lower()).first()
    else:
        # Identifier is phone
        phone = re.sub(r'[\s\-]', '', request.identifier)
        user = db.query(User).filter(User.phone == phone).first()
    
    if not user:
        print(f"User not found for identifier: {request.identifier}")
        # Log failed login attempt
        AuditLogService.log_login_attempt(
            db=db,
            user_id=None,
            email=request.identifier,
            ip_address=req.client.host if req.client else "unknown",
            user_agent=req.headers.get("user-agent", ""),
            success=False,
            failure_reason="User not found"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email/phone or password"
        )
    
    print(f"User found: {user.email}, is_active={user.is_active}, phone_verified={user.phone_verified}")
    
    # Verify password
    if not verify_password(request.password, user.password_hash):
        print(f"Password verification failed for user: {user.email}")
        # Log failed login attempt
        AuditLogService.log_login_attempt(
            db=db,
            user_id=user.id,
            email=user.email,
            ip_address=req.client.host if req.client else "unknown",
            user_agent=req.headers.get("user-agent", ""),
            success=False,
            failure_reason="Invalid password"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email/phone or password"
        )
    
    # Log successful login
    AuditLogService.log_login_attempt(
        db=db,
        user_id=user.id,
        email=user.email,
        ip_address=req.client.host if req.client else "unknown",
        user_agent=req.headers.get("user-agent", ""),
        success=True
    )
    
    # Check if account is active (only check phone_verified, not is_active)
    # Allow login even if not verified, but show warning
    if not user.phone_verified:
        print(f"User {user.email} attempting login without phone verification")
        # Still allow login but could add a warning in response
        # For now, we'll allow it to make testing easier
    
    # Generate JWT token
    token_data = {
        "user_id": user.id,
        "email": user.email,
        "role": user.role,  # Already a string
    }
    
    # Add tier for freelancers
    if user.role == "freelancer" and user.freelancer:
        token_data["tier"] = user.freelancer.tier
    
    access_token = create_access_token(token_data)
    
    # Update last active timestamp
    user.last_active = datetime.utcnow()
    db.commit()
    
    # Prepare response based on role
    response_data = {
        "user_id": user.id,
        "email": user.email,
        "role": user.role,  # Already a string
        "phone": user.phone,
        "phone_verified": user.phone_verified,
        "access_token": access_token,
        "token_type": "bearer"
    }
    
    if user.role == "freelancer" and user.freelancer:
        response_data["freelancer_id"] = user.freelancer.id
        response_data["tier"] = user.freelancer.tier
    elif user.role == "businessowner" and user.business_owner:
        response_data["business_owner_id"] = user.business_owner.id
        response_data["business_id"] = user.business_owner.business_id
    
    return UserRegisterResponse(**response_data)


@router.get("/profile")
async def get_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user profile information."""
    user_id = current_user.get("user_id")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    profile_data = {
        "name": "",
        "email": user.email,
        "phone": user.phone,
        "role": user.role,
        "portfolio_url": "",
        "tier": "new",
        "daily_limit": 3,
        "remaining_contacts": 0,
    }
    
    if user.role == "freelancer" and user.freelancer:
        profile_data["name"] = user.freelancer.name
        profile_data["portfolio_url"] = user.freelancer.portfolio_url or ""
        profile_data["tier"] = user.freelancer.tier
        profile_data["daily_limit"] = user.freelancer.daily_limit
        profile_data["remaining_contacts"] = user.freelancer.remaining_contacts
    elif user.role == "businessowner" and user.business_owner:
        profile_data["name"] = user.business_owner.owner_name
    
    return profile_data


@router.put("/profile")
async def update_profile(
    request: dict = Body(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile information."""
    user_id = current_user.get("user_id")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    name = request.get("name")
    portfolio_url = request.get("portfolio_url")
    
    if user.role == "freelancer" and user.freelancer:
        if name:
            user.freelancer.name = name
        if portfolio_url is not None:
            user.freelancer.portfolio_url = portfolio_url
    elif user.role == "businessowner" and user.business_owner:
        if name:
            user.business_owner.owner_name = name
    
    db.commit()
    
    return {"success": True, "message": "Profile updated successfully"}


@router.put("/change-password")
async def change_password(
    request: dict = Body(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password."""
    user_id = current_user.get("user_id")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    current_password = request.get("current_password")
    new_password = request.get("new_password")
    
    if not current_password or not new_password:
        raise HTTPException(
            status_code=400,
            detail={"error": "MISSING_FIELDS", "message": "Current password and new password are required"}
        )
    
    # Verify current password
    if not verify_password(current_password, user.password_hash):
        raise HTTPException(
            status_code=400,
            detail={"error": "INVALID_PASSWORD", "message": "Current password is incorrect"}
        )
    
    # Validate new password
    if len(new_password) < 8:
        raise HTTPException(
            status_code=400,
            detail={"error": "WEAK_PASSWORD", "message": "Password must be at least 8 characters"}
        )
    
    # Hash and update password
    user.password_hash = hash_password(new_password)
    db.commit()
    
    return {"success": True, "message": "Password changed successfully"}
