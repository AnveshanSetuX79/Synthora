"""Business model for lead discovery and management."""
from sqlalchemy import Column, String, Boolean, DateTime, Float, Integer, Enum, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ..database import Base


class FreshnessScore(str, enum.Enum):
    """Lead freshness classification."""
    HIGH = "high"  # < 7 days
    MEDIUM = "medium"  # 7-30 days
    LOW = "low"  # > 30 days


class Business(Base):
    """Business entity - static data only."""
    __tablename__ = "businesses"

    id = Column(String(36), primary_key=True)
    place_id = Column(String(255), unique=True, nullable=False, index=True)  # Google Places ID
    name = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    address = Column(String(500), nullable=False)
    city = Column(String(100), nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    latitude = Column(Float, nullable=True)  # For map display
    longitude = Column(Float, nullable=True)  # For map display
    
    # Soft delete
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Verification
    is_verified = Column(Boolean, default=False, nullable=False, index=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    owner = relationship("BusinessOwner", back_populates="business", uselist=False)
    insights = relationship("BusinessInsight", back_populates="business", uselist=False, cascade="all, delete-orphan")
    leads = relationship("Lead", back_populates="business", cascade="all, delete-orphan")
    demos = relationship("DemoWebsite", back_populates="business", cascade="all, delete-orphan")
    deals = relationship("Deal", back_populates="business", cascade="all, delete-orphan")


class BusinessInsight(Base):
    """Business insights - dynamic scoring and metrics."""
    __tablename__ = "business_insights"

    id = Column(String(36), primary_key=True)
    business_id = Column(String(36), ForeignKey("businesses.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    # Scoring fields (frequently updated)
    digital_score = Column(Integer, nullable=False, index=True)  # 0-100
    digital_score_breakdown = Column(JSON, nullable=True)  # JSON object with breakdown
    lead_priority_score = Column(Integer, nullable=False, index=True)  # Calculated priority (database column name)
    opportunity_tag = Column(String(50), nullable=True, index=True)  # Opportunity classification
    lead_freshness_score = Column(String(50), default="high", nullable=False, index=True)  # Database column name
    
    # Dynamic metrics (not in database yet - will be added later)
    rating = Column(Float, nullable=True)
    review_count = Column(Integer, default=0, nullable=True)
    has_website = Column(Boolean, default=False, nullable=True, index=True)
    website_url = Column(String(500), nullable=True)
    contact_count = Column(Integer, default=0, nullable=False)
    
    # Status tracking
    last_verified = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    status = Column(String(50), nullable=True)
    
    # AI Enrichment fields
    ai_description = Column(String, nullable=True)  # AI-generated business description
    ai_specialties = Column(JSON, nullable=True)  # List of specialties
    ai_target_customers = Column(JSON, nullable=True)  # List of target customer segments
    ai_pain_points = Column(JSON, nullable=True)  # List of business pain points
    ai_recommended_solutions = Column(JSON, nullable=True)  # List of recommended solutions
    ai_competitive_advantages = Column(JSON, nullable=True)  # List of competitive advantages
    ai_digital_maturity = Column(String(50), nullable=True)  # low, medium, high
    ai_growth_potential = Column(String(50), nullable=True)  # low, medium, high
    ai_estimated_size = Column(String(50), nullable=True)  # small, medium, large
    ai_online_presence_score = Column(Integer, nullable=True)  # 0-100
    ai_urgency_score = Column(Integer, nullable=True)  # 0-100 (how urgently they need help)
    ai_enrichment_confidence = Column(Float, nullable=True)  # 0-1
    ai_enriched_at = Column(DateTime(timezone=True), nullable=True)  # When AI enrichment was done
    ai_pitch_suggestions = Column(JSON, nullable=True)  # List of pitch suggestions for freelancers
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    business = relationship("Business", back_populates="insights")
    
    # Property aliases for backward compatibility
    @property
    def priority_score(self):
        """Alias for lead_priority_score."""
        return self.lead_priority_score
    
    @priority_score.setter
    def priority_score(self, value):
        """Alias setter for lead_priority_score."""
        self.lead_priority_score = value
    
    @property
    def freshness(self):
        """Alias for lead_freshness_score."""
        return self.lead_freshness_score
    
    @freshness.setter
    def freshness(self, value):
        """Alias setter for lead_freshness_score."""
        if isinstance(value, FreshnessScore):
            self.lead_freshness_score = value.value
        else:
            self.lead_freshness_score = value
