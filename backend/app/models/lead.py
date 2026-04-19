"""Lead contact and outreach models."""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Enum, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ..database import Base


class LeadContactStatus(str, enum.Enum):
    """Lead contact status."""
    CONTACTED = "contacted"
    INTERESTED = "interested"
    NEGOTIATING = "negotiating"
    CLOSED = "closed"
    LOST = "lost"
    COLD = "cold"


class ConsentStatus(str, enum.Enum):
    """Business consent tracking."""
    CONTACTED = "contacted"
    VIEWED_DEMO = "vieweddemo"
    CONSENTED = "consented"
    REGISTERED = "registered"
    OPTED_OUT = "optedout"


class OutreachChannel(str, enum.Enum):
    """Communication channel for outreach."""
    SMS = "sms"
    EMAIL = "email"
    WHATSAPP = "whatsapp"


class DeliveryStatus(str, enum.Enum):
    """Message delivery status."""
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"


class LeadSource(str, enum.Enum):
    """Lead source type."""
    GOOGLE = "google"
    MANUAL = "manual"
    REFERRAL = "referral"
    IMPORT = "import"


class LeadStatus(str, enum.Enum):
    """Lead lifecycle status."""
    NEW = "new"
    ASSIGNED = "assigned"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    CONVERTED = "converted"
    LOST = "lost"
    ARCHIVED = "archived"


class Lead(Base):
    """Central lead abstraction - enables multiple lead cycles per business."""
    __tablename__ = "leads"

    id = Column(String(36), primary_key=True)
    business_id = Column(String(36), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True)
    source = Column(String(50), nullable=False, index=True)  # Use String instead of Enum
    score = Column(Integer, nullable=False, index=True)  # 0-100 digital presence score
    status = Column(String(50), default="new", nullable=False, index=True)  # Use String instead of Enum
    campaign_id = Column(String(36), ForeignKey("campaigns.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Soft delete
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    business = relationship("Business", back_populates="leads")
    campaign = relationship("Campaign", back_populates="leads")
    lead_contacts = relationship("LeadContact", back_populates="lead", cascade="all, delete-orphan")


class LeadContact(Base):
    """Tracks freelancer contact with leads - who contacted whom."""
    __tablename__ = "lead_contacts"

    id = Column(String(36), primary_key=True)
    lead_id = Column(String(36), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, index=True)
    freelancer_id = Column(String(36), ForeignKey("freelancers.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), default="contacted", nullable=False, index=True)  # Use String instead of Enum
    
    # Exclusivity window
    exclusivity_active = Column(Boolean, default=True, nullable=False)
    exclusivity_expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Basic contact tracking
    first_contact_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    last_contact_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    consent_status = Column(String(50), default="contacted", nullable=False, index=True)  # Use String instead of Enum
    notes = Column(Text, nullable=True)
    
    # AI Copilot usage tracking
    copilot_uses = Column(Integer, default=0, nullable=False)
    last_copilot_use = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    lead = relationship("Lead", back_populates="lead_contacts")
    freelancer = relationship("Freelancer", back_populates="lead_contacts")
    activities = relationship("LeadActivity", back_populates="lead_contact", cascade="all, delete-orphan")
    outreach_messages = relationship("OutreachMessage", back_populates="lead_contact", cascade="all, delete-orphan")


class OutreachMessage(Base):
    """Tracks outreach messages sent to businesses."""
    __tablename__ = "outreach_messages"

    id = Column(String(36), primary_key=True)
    lead_contact_id = Column(String(36), ForeignKey("lead_contacts.id", ondelete="CASCADE"), nullable=False, index=True)
    channel = Column(String(50), nullable=False, index=True)  # Use String instead of Enum
    template_id = Column(String(100), nullable=True)
    content = Column(Text, nullable=False)
    delivery_status = Column(String(50), default="sent", nullable=False, index=True)  # Use String instead of Enum
    
    # Timestamps
    sent_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    viewed_at = Column(DateTime(timezone=True), nullable=True)
    replied_at = Column(DateTime(timezone=True), nullable=True)
    
    # Opt-out tracking
    opted_out = Column(Boolean, default=False, nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    lead_contact = relationship("LeadContact", back_populates="outreach_messages")


class ActivityType(str, enum.Enum):
    """Lead activity types."""
    FOLLOW_UP = "followup"
    CALL = "call"
    MEETING = "meeting"
    EMAIL = "email"
    NOTE = "note"
    STATUS_CHANGE = "statuschange"


class LeadActivity(Base):
    """Detailed activity tracking for lead contacts."""
    __tablename__ = "lead_activities"

    id = Column(String(36), primary_key=True)
    lead_contact_id = Column(String(36), ForeignKey("lead_contacts.id", ondelete="CASCADE"), nullable=False, index=True)
    activity_type = Column(String(50), nullable=False, index=True)  # Use String instead of Enum
    description = Column(Text, nullable=False)
    activity_metadata = Column(JSON, nullable=True)  # Additional structured data (renamed from metadata)
    
    # Timestamps
    activity_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    lead_contact = relationship("LeadContact", back_populates="activities")
