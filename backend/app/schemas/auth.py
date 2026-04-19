"""Authentication request/response schemas."""
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from typing import Optional
import re


class UserRegisterRequest(BaseModel):
    """User registration request schema."""
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=20)
    password: str = Field(..., min_length=8)
    role: str = Field(..., pattern="^(freelancer|business_owner)$")
    
    # Role-specific fields
    name: Optional[str] = None  # For freelancer
    portfolio_url: Optional[str] = None  # For freelancer
    business_name: Optional[str] = None  # For business_owner
    owner_name: Optional[str] = None  # For business_owner
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        """Validate phone number format."""
        # Remove spaces and dashes
        phone = re.sub(r'[\s\-]', '', v)
        # Check if it's a valid phone number (digits only)
        if not re.match(r'^\+?[0-9]{10,15}$', phone):
            raise ValueError('Invalid phone number format')
        return phone
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Validate password complexity."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        return v
    
    @model_validator(mode='after')
    def validate_role_specific_fields(self):
        """Validate role-specific required fields."""
        if self.role == 'freelancer' and not self.name:
            raise ValueError('Name is required for freelancer registration')
        if self.role == 'business_owner' and not self.owner_name:
            raise ValueError('Owner name is required for business owner registration')
        return self


class UserRegisterResponse(BaseModel):
    """User registration response schema."""
    user_id: str
    email: str
    role: str
    phone: str
    phone_verified: bool
    access_token: str
    token_type: str = "bearer"
    
    # Role-specific data
    freelancer_id: Optional[str] = None
    tier: Optional[str] = None
    business_owner_id: Optional[str] = None
    business_id: Optional[str] = None


class VerifyOTPRequest(BaseModel):
    """OTP verification request schema."""
    phone: str = Field(..., min_length=10, max_length=20)
    otp_code: str = Field(..., min_length=6, max_length=6)
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        """Validate phone number format."""
        phone = re.sub(r'[\s\-]', '', v)
        if not re.match(r'^\+?[0-9]{10,15}$', phone):
            raise ValueError('Invalid phone number format')
        return phone
    
    @field_validator('otp_code')
    @classmethod
    def validate_otp(cls, v):
        """Validate OTP format."""
        if not re.match(r'^[0-9]{6}$', v):
            raise ValueError('OTP must be 6 digits')
        return v


class VerifyOTPResponse(BaseModel):
    """OTP verification response schema."""
    success: bool
    message: str
    user_id: Optional[str] = None
    phone_verified: bool = False


class LoginRequest(BaseModel):
    """User login request schema."""
    identifier: str = Field(..., description="Email or phone number")
    password: str = Field(..., min_length=8)


class LoginResponse(BaseModel):
    """User login response schema."""
    access_token: str
    token_type: str = "bearer"
    user: dict


class ErrorResponse(BaseModel):
    """Error response schema."""
    detail: str
