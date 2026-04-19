"""Dispute resolution models."""
from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ..database import Base


class DisputeStatus(str, enum.Enum):
    """Dispute status."""
    OPEN = "open"  # Newly created
    SELF_RESOLUTION = "self_resolution"  # 48-hour self-resolution period
    ADMIN_MEDIATION = "admin_mediation"  # Escalated to admin
    RESOLVED = "resolved"  # Resolved
    CLOSED = "closed"  # Closed


class DisputeResolution(str, enum.Enum):
    """Dispute resolution type."""
    FULL_PAYMENT_FREELANCER = "full_payment_freelancer"
    PARTIAL_PAYMENT = "partial_payment"
    FULL_REFUND_BUSINESS = "full_refund_business"
    CANCELLED = "cancelled"


class Dispute(Base):
    """Dispute between freelancer and business."""
    __tablename__ = "disputes"

    id = Column(String(36), primary_key=True)
    deal_id = Column(String(36), ForeignKey("deals.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # Parties
    raised_by = Column(String(36), nullable=False)  # User ID who raised the dispute
    raised_by_role = Column(String(50), nullable=False)  # freelancer or business_owner
    
    # Dispute details
    reason = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="open", nullable=False, index=True)
    
    # Resolution
    resolution_type = Column(String(50), nullable=True)
    resolution_amount = Column(Integer, nullable=True)  # In paise, for partial payments
    resolution_notes = Column(Text, nullable=True)
    resolved_by = Column(String(36), ForeignKey("users.id"), nullable=True)  # Admin user ID
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    self_resolution_deadline = Column(DateTime(timezone=True), nullable=False)  # 48 hours from creation
    escalated_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    deal = relationship("Deal", back_populates="dispute")
    messages = relationship("DisputeMessage", back_populates="dispute", cascade="all, delete-orphan", order_by="DisputeMessage.created_at")
    resolver = relationship("User", foreign_keys=[resolved_by])


class DisputeMessage(Base):
    """Messages in dispute chat."""
    __tablename__ = "dispute_messages"

    id = Column(String(36), primary_key=True)
    dispute_id = Column(String(36), ForeignKey("disputes.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Message details
    sender_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    sender_role = Column(String(50), nullable=False)  # freelancer, business_owner, admin
    message = Column(Text, nullable=False)
    
    # Metadata
    is_system_message = Column(String(10), default="false", nullable=False)  # System notifications
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    dispute = relationship("Dispute", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_id])
