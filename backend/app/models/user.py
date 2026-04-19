"""User models: Freelancer, BusinessOwner, Admin."""
from sqlalchemy import Column, String, Boolean, DateTime, Float, Integer, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from ..database import Base


class UserRole(str, enum.Enum):
    """User role enumeration."""
    FREELANCER = "freelancer"
    BUSINESS_OWNER = "businessowner"
    ADMIN = "admin"
    FOUNDER = "founder"


class FreelancerTier(str, enum.Enum):
    """Freelancer tier enumeration."""
    NEW = "new"
    VERIFIED = "verified"
    TOP_RATED = "toprated"


class KYCStatus(str, enum.Enum):
    """KYC verification status."""
    PENDING = "pending"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"


class User(Base):
    """Base user model for authentication."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, index=True)  # Use String instead of Enum for now
    phone = Column(String(20), nullable=False, index=True)
    phone_verified = Column(Boolean, default=False, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_active = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    freelancer = relationship("Freelancer", back_populates="user", uselist=False, cascade="all, delete-orphan")
    business_owner = relationship("BusinessOwner", back_populates="user", uselist=False, cascade="all, delete-orphan")
    admin = relationship("Admin", back_populates="user", uselist=False, cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    notification_preferences = relationship("NotificationPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")


class Freelancer(Base):
    """Freelancer-specific profile data."""
    __tablename__ = "freelancers"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    portfolio_url = Column(String(500), nullable=True)
    tier = Column(String(50), default="New", nullable=False, index=True)  # Use String instead of Enum
    daily_limit = Column(Integer, default=3, nullable=False)
    remaining_contacts = Column(Integer, default=3, nullable=False)
    kyc_status = Column(String(50), default="Pending", nullable=False, index=True)  # Use String instead of Enum
    kyc_documents = Column(String(1000), nullable=True)  # JSON array of document URLs
    average_rating = Column(Float, default=0.0, nullable=False)
    review_count = Column(Integer, default=0, nullable=False)
    conversion_rate = Column(Float, default=0.0, nullable=False)
    response_rate = Column(Float, default=0.0, nullable=False)
    total_earnings = Column(Integer, default=0, nullable=False)  # In paise (₹1 = 100 paise)
    deals_closed = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="freelancer")
    lead_contacts = relationship("LeadContact", back_populates="freelancer", cascade="all, delete-orphan")
    deals = relationship("Deal", back_populates="freelancer", cascade="all, delete-orphan")
    sent_messages = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender")
    kyc_documents = relationship("KYCDocument", back_populates="freelancer", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="freelancer", cascade="all, delete-orphan")


class BusinessOwner(Base):
    """Business owner profile data."""
    __tablename__ = "business_owners"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    business_id = Column(String(36), ForeignKey("businesses.id", ondelete="SET NULL"), nullable=True, index=True)
    owner_name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="business_owner")
    business = relationship("Business", back_populates="owner")
    deals = relationship("Deal", back_populates="business_owner", cascade="all, delete-orphan")
    received_messages = relationship("Message", foreign_keys="Message.recipient_id", back_populates="recipient")
    reviews = relationship("Review", back_populates="business_owner", cascade="all, delete-orphan")


class Admin(Base):
    """Admin/Founder profile data."""
    __tablename__ = "admins"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    permissions = Column(String(1000), nullable=True)  # JSON array of permissions
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="admin")
