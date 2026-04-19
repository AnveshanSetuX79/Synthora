"""Message and conversation models for in-app chat."""
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ..database import Base


class MessageChannel(str, enum.Enum):
    """Message channel."""
    IN_APP = "inapp"
    SMS = "sms"
    EMAIL = "email"
    WHATSAPP = "whatsapp"


class MessageStatus(str, enum.Enum):
    """Message status."""
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class Conversation(Base):
    """Conversation between freelancer and business owner."""
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True)
    freelancer_id = Column(String(36), ForeignKey("freelancers.id", ondelete="CASCADE"), nullable=False, index=True)
    business_owner_id = Column(String(36), ForeignKey("business_owners.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    last_message_at = Column(DateTime(timezone=True), nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")


class Message(Base):
    """Message in a conversation."""
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id = Column(String(36), ForeignKey("freelancers.id", ondelete="CASCADE"), nullable=True, index=True)
    recipient_id = Column(String(36), ForeignKey("business_owners.id", ondelete="CASCADE"), nullable=True, index=True)
    
    channel = Column(String(50), default="inapp", nullable=False, index=True)  # Use String instead of Enum
    content = Column(Text, nullable=False)
    attachments = Column(JSON, nullable=True)  # JSON array of attachment URLs
    status = Column(String(50), default="sent", nullable=False, index=True)  # Use String instead of Enum
    
    # Timestamps
    sent_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    sender = relationship("Freelancer", back_populates="sent_messages", foreign_keys=[sender_id])
    recipient = relationship("BusinessOwner", back_populates="received_messages", foreign_keys=[recipient_id])
