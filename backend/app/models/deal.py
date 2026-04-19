"""Deal and milestone models."""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Enum, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ..database import Base


class PaymentFlow(str, enum.Enum):
    """Payment flow type."""
    SIMPLIFIED = "simplified"  # 2 milestones: 50% advance, 50% delivery
    FULL = "full"  # 3 milestones: 30% design, 40% development, 30% final


class DealStatus(str, enum.Enum):
    """Deal status."""
    PENDING = "pending"
    ACTIVE = "active"
    IN_PROGRESS = "inprogress"
    COMPLETED = "completed"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"


class MilestoneStatus(str, enum.Enum):
    """Milestone status."""
    PENDING = "pending"
    IN_PROGRESS = "inprogress"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"


class Deal(Base):
    """Deal/project between freelancer and business."""
    __tablename__ = "deals"

    id = Column(String(36), primary_key=True)
    freelancer_id = Column(String(36), ForeignKey("freelancers.id", ondelete="CASCADE"), nullable=False, index=True)
    business_id = Column(String(36), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True)
    business_owner_id = Column(String(36), ForeignKey("business_owners.id", ondelete="CASCADE"), nullable=True, index=True)
    
    amount = Column(Integer, nullable=False)  # In paise (₹1 = 100 paise)
    payment_flow = Column(String(50), default="Simplified", nullable=False)  # Use String instead of Enum
    status = Column(String(50), default="Pending", nullable=False, index=True)  # Use String instead of Enum
    
    # Metadata
    package_type = Column(String(100), nullable=True)  # Starter, Standard, Premium
    description = Column(Text, nullable=True)
    
    # Soft delete
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    freelancer = relationship("Freelancer", back_populates="deals")
    business = relationship("Business", back_populates="deals")
    business_owner = relationship("BusinessOwner", back_populates="deals")
    milestones = relationship("Milestone", back_populates="deal", cascade="all, delete-orphan", order_by="Milestone.sequence")
    payments = relationship("Payment", back_populates="deal", cascade="all, delete-orphan")
    dispute = relationship("Dispute", back_populates="deal", uselist=False, cascade="all, delete-orphan")
    review = relationship("Review", back_populates="deal", uselist=False, cascade="all, delete-orphan")


class Milestone(Base):
    """Project milestone for payment tracking."""
    __tablename__ = "milestones"

    id = Column(String(36), primary_key=True)
    deal_id = Column(String(36), ForeignKey("deals.id", ondelete="CASCADE"), nullable=False, index=True)
    sequence = Column(Integer, nullable=False)  # 1, 2, 3
    name = Column(String(255), nullable=False)  # Design, Development, Final Delivery
    percentage = Column(Integer, nullable=False)  # 30, 40, 30 or 50, 50
    amount = Column(Integer, nullable=False)  # In paise
    status = Column(String(50), default="Pending", nullable=False, index=True)  # Use String instead of Enum
    
    # Deliverables and feedback
    deliverables = Column(JSON, nullable=True)  # JSON array of deliverable URLs/descriptions
    feedback = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Timestamps
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejected_at = Column(DateTime(timezone=True), nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True, index=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    deal = relationship("Deal", back_populates="milestones")
    payments = relationship("Payment", back_populates="milestone")
