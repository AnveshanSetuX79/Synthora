"""Failure log model for retry logic."""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
import enum

from ..database import Base


class FailureStatus(str, enum.Enum):
    """Failure status enumeration."""
    PENDING = "pending"
    RETRYING = "retrying"
    FAILED = "failed"
    RESOLVED = "resolved"
    FALLBACK = "fallback"


class FailureLog(Base):
    """Failure log for tracking retry attempts."""
    __tablename__ = "failure_logs"

    id = Column(String(36), primary_key=True)
    service = Column(String(50), nullable=False, index=True)  # 'sms', 'email', 'payment'
    operation = Column(String(100), nullable=False)
    target = Column(String(255), nullable=False)  # phone/email/payment_id
    attempt_number = Column(Integer, nullable=False, default=0)
    max_attempts = Column(Integer, nullable=False, default=3)
    error_message = Column(Text, nullable=True)
    error_code = Column(String(50), nullable=True)
    failure_metadata = Column(JSON, nullable=True)  # Renamed from 'metadata' to avoid SQLAlchemy conflict
    status = Column(String(50), nullable=False, default="pending", index=True)
    next_retry_at = Column(DateTime(timezone=True), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by = Column(String(36), nullable=True)
    admin_notified = Column(Boolean, default=False, nullable=False)
    fallback_attempted = Column(Boolean, default=False, nullable=False)
