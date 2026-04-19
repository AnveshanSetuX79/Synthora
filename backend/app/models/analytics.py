"""Analytics and intelligence models."""
from sqlalchemy import Column, String, DateTime, Integer, Float, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ..database import Base


class EventType(str, enum.Enum):
    """Analytics event types."""
    LEAD_VIEWED = "lead_viewed"
    DEMO_GENERATED = "demo_generated"
    DEMO_VIEWED = "demo_viewed"
    MESSAGE_SENT = "message_sent"
    DEAL_CREATED = "deal_created"
    PAYMENT_COMPLETED = "payment_completed"
    MILESTONE_SUBMITTED = "milestone_submitted"
    MILESTONE_APPROVED = "milestone_approved"


class ROIPeriod(str, enum.Enum):
    """ROI calculation period."""
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    ALL_TIME = "alltime"


class AnalyticsEvent(Base):
    """Analytics event tracking."""
    __tablename__ = "analytics_events"

    id = Column(String(36), primary_key=True)
    event_type = Column(String(50), nullable=False, index=True)  # Use String instead of Enum
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    event_metadata = Column(JSON, nullable=True)  # JSON object with event-specific data (renamed from metadata)
    
    # Timestamps
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User")


class FreelancerROI(Base):
    """Freelancer ROI metrics."""
    __tablename__ = "freelancer_roi"

    id = Column(String(36), primary_key=True)
    freelancer_id = Column(String(36), ForeignKey("freelancers.id", ondelete="CASCADE"), nullable=False, index=True)
    period = Column(String(50), nullable=False, index=True)  # Use String instead of Enum
    
    # Metrics
    total_earnings = Column(Integer, default=0, nullable=False)  # In paise
    leads_used = Column(Integer, default=0, nullable=False)
    cost_per_acquisition = Column(Integer, default=0, nullable=False)  # In paise
    win_rate = Column(Float, default=0.0, nullable=False)  # 0.0 to 1.0
    avg_time_to_close = Column(Integer, default=0, nullable=False)  # In days
    lead_quality_score = Column(Float, default=0.0, nullable=False)  # 0.0 to 100.0
    
    # Timestamps
    calculated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    freelancer = relationship("Freelancer")


class ConversionIntelligence(Base):
    """Conversion intelligence data moat."""
    __tablename__ = "conversion_intelligence"

    id = Column(String(36), primary_key=True)
    category = Column(String(100), nullable=False, index=True)
    
    # Business characteristics
    business_characteristics = Column(JSON, nullable=False)  # JSON object with ranges
    
    # Conversion metrics
    conversion_rate = Column(Float, nullable=False)  # 0.0 to 1.0
    avg_deal_value = Column(Integer, nullable=False)  # In paise
    avg_time_to_close = Column(Integer, nullable=False)  # In days
    top_objections = Column(JSON, nullable=True)  # JSON array of objections
    optimal_pricing = Column(Integer, nullable=False)  # In paise
    
    # Sample size for statistical validity
    sample_size = Column(Integer, nullable=False)
    
    # Timestamps
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
