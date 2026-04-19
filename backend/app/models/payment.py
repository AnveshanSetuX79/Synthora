"""Payment and transaction models."""
from sqlalchemy import Column, String, DateTime, Integer, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ..database import Base


class PaymentStatus(str, enum.Enum):
    """Payment status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class TransactionType(str, enum.Enum):
    """Transaction type."""
    DEPOSIT = "deposit"
    RELEASE = "release"
    REFUND = "refund"
    COMMISSION = "commission"


class Payment(Base):
    """Payment records for deals and milestones."""
    __tablename__ = "payments"

    id = Column(String(36), primary_key=True)
    deal_id = Column(String(36), ForeignKey("deals.id", ondelete="CASCADE"), nullable=False, index=True)
    milestone_id = Column(String(36), ForeignKey("milestones.id", ondelete="SET NULL"), nullable=True, index=True)
    
    amount = Column(Integer, nullable=False)  # In paise
    commission = Column(Integer, default=0, nullable=False)  # In paise
    status = Column(String(50), default="pending", nullable=False, index=True)  # Use String instead of Enum
    
    # Payment provider details
    razorpay_order_id = Column(String(255), unique=True, nullable=True, index=True)
    razorpay_payment_id = Column(String(255), unique=True, nullable=True, index=True)
    razorpay_signature = Column(String(500), nullable=True)
    
    # Metadata
    payment_method = Column(String(50), nullable=True)  # card, upi, netbanking
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    deal = relationship("Deal", back_populates="payments")
    milestone = relationship("Milestone", back_populates="payments")
    transactions = relationship("Transaction", back_populates="payment", cascade="all, delete-orphan")


class Transaction(Base):
    """Transaction records for audit trail."""
    __tablename__ = "transactions"

    id = Column(String(36), primary_key=True)
    payment_id = Column(String(36), ForeignKey("payments.id", ondelete="CASCADE"), nullable=False, index=True)
    deal_id = Column(String(36), ForeignKey("deals.id", ondelete="CASCADE"), nullable=False, index=True)
    milestone_id = Column(String(36), ForeignKey("milestones.id", ondelete="SET NULL"), nullable=True, index=True)
    
    type = Column(String(50), nullable=False, index=True)  # Use String instead of Enum
    amount = Column(Integer, nullable=False)  # In paise
    commission = Column(Integer, default=0, nullable=False)  # In paise
    status = Column(String(50), default="pending", nullable=False, index=True)  # Use String instead of Enum
    
    # Payment provider details
    payment_provider_id = Column(String(255), nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    payment = relationship("Payment", back_populates="transactions")
    deal = relationship("Deal")
    milestone = relationship("Milestone")
