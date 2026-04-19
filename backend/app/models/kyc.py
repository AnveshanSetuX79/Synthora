"""KYC (Know Your Customer) verification models."""
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ..database import Base


class KYCDocumentType(str, enum.Enum):
    """KYC document type."""
    AADHAAR = "aadhaar"
    PAN = "pan"
    DRIVING_LICENSE = "drivinglicense"
    PASSPORT = "passport"
    BANK_ACCOUNT = "bankaccount"


class KYCVerificationStatus(str, enum.Enum):
    """KYC verification status."""
    PENDING = "pending"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "underreview"
    APPROVED = "approved"
    REJECTED = "rejected"


class KYCDocument(Base):
    """KYC document submission for freelancers."""
    __tablename__ = "kyc_documents"

    id = Column(String(36), primary_key=True)
    freelancer_id = Column(String(36), ForeignKey("freelancers.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Document details
    document_type = Column(String(50), nullable=False)  # Use String instead of Enum
    document_number = Column(String(100), nullable=False)
    document_url = Column(String(500), nullable=True)  # S3/storage URL
    
    # Bank details (for payouts)
    bank_account_number = Column(String(50), nullable=True)
    bank_ifsc_code = Column(String(20), nullable=True)
    bank_account_holder_name = Column(String(255), nullable=True)
    
    # Verification
    status = Column(String(50), default="pending", nullable=False, index=True)  # Use String instead of Enum
    rejection_reason = Column(Text, nullable=True)
    verified_by = Column(String(36), nullable=True)  # Admin user ID
    
    # Razorpay linked account (for Route/escrow)
    razorpay_account_id = Column(String(255), unique=True, nullable=True, index=True)
    razorpay_account_status = Column(String(50), nullable=True)
    
    # Additional data
    additional_data = Column(JSON, nullable=True)  # Additional verification data
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    freelancer = relationship("Freelancer", back_populates="kyc_documents")
