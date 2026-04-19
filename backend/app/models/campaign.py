"""Campaign and template models for scalability."""
from sqlalchemy import Column, String, Boolean, DateTime, Float, Integer, Enum, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ..database import Base


class CampaignType(str, enum.Enum):
    """Campaign type."""
    GOOGLE_DISCOVERY = "googlediscovery"
    MANUAL_OUTREACH = "manualoutreach"
    REFERRAL = "referral"
    RETARGETING = "retargeting"


class CampaignStatus(str, enum.Enum):
    """Campaign status."""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Campaign(Base):
    """Marketing campaigns for lead generation."""
    __tablename__ = "campaigns"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    type = Column(String(50), nullable=False, index=True)  # Use String instead of Enum
    status = Column(String(50), default="draft", nullable=False, index=True)  # Use String instead of Enum
    description = Column(Text, nullable=True)
    
    # Campaign configuration
    target_criteria = Column(JSON, nullable=True)  # Targeting rules
    budget = Column(Integer, nullable=True)  # In paise
    
    # Metrics
    leads_generated = Column(Integer, default=0, nullable=False)
    conversion_rate = Column(Float, default=0.0, nullable=False)
    
    # Timestamps
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    leads = relationship("Lead", back_populates="campaign")


class MessageTemplate(Base):
    """Reusable message templates."""
    __tablename__ = "message_templates"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    channel = Column(String(50), nullable=False, index=True)  # SMS, Email, WhatsApp, InApp
    subject = Column(String(500), nullable=True)  # For email
    content = Column(Text, nullable=False)
    variables = Column(JSON, nullable=True)  # List of variable placeholders
    
    # Metadata
    is_active = Column(Boolean, default=True, nullable=False)
    usage_count = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
