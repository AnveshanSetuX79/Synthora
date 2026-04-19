"""Notification models for in-app and email notifications.

Requirement 16: Notification System
"""
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from ..database import Base


class Notification(Base):
    """In-app notification model."""
    
    __tablename__ = "notifications"
    
    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign keys
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # Notification details
    type = Column(String(50), nullable=False, index=True)  # 'message', 'milestone', 'dispute', 'payment'
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    link = Column(String(500), nullable=True)  # Link to relevant page
    
    # Status
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    
    # Indexes
    __table_args__ = (
        Index('ix_notifications_user_unread', 'user_id', 'is_read'),
        Index('ix_notifications_user_created', 'user_id', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, type={self.type}, is_read={self.is_read})>"


class NotificationPreference(Base):
    """User notification preferences."""
    
    __tablename__ = "notification_preferences"
    
    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign keys
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, unique=True, index=True)
    
    # Email notification preferences
    email_new_message = Column(Boolean, default=True, nullable=False)
    email_milestone_submitted = Column(Boolean, default=True, nullable=False)
    email_milestone_approved = Column(Boolean, default=True, nullable=False)
    email_milestone_rejected = Column(Boolean, default=True, nullable=False)
    email_dispute_raised = Column(Boolean, default=True, nullable=False)
    email_payment_processed = Column(Boolean, default=True, nullable=False)
    
    # In-app notification preferences (always enabled for now)
    inapp_new_message = Column(Boolean, default=True, nullable=False)
    inapp_milestone_submitted = Column(Boolean, default=True, nullable=False)
    inapp_milestone_approved = Column(Boolean, default=True, nullable=False)
    inapp_milestone_rejected = Column(Boolean, default=True, nullable=False)
    inapp_dispute_raised = Column(Boolean, default=True, nullable=False)
    inapp_payment_processed = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="notification_preferences")
    
    def __repr__(self):
        return f"<NotificationPreference(id={self.id}, user_id={self.user_id})>"
