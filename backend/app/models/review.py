"""Review and rating models."""
from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class Review(Base):
    """Review for freelancer after deal completion."""
    __tablename__ = "reviews"

    id = Column(String(36), primary_key=True)
    deal_id = Column(String(36), ForeignKey("deals.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    freelancer_id = Column(String(36), ForeignKey("freelancers.id", ondelete="CASCADE"), nullable=False, index=True)
    business_owner_id = Column(String(36), ForeignKey("business_owners.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Rating and review
    rating = Column(Integer, nullable=False)  # 1-5 stars
    review_text = Column(Text, nullable=False)  # Minimum 20 characters
    
    # Freelancer response
    response_text = Column(Text, nullable=True)
    responded_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
        CheckConstraint('LENGTH(review_text) >= 20', name='check_review_min_length'),
    )
    
    # Relationships
    deal = relationship("Deal", back_populates="review")
    freelancer = relationship("Freelancer", back_populates="reviews")
    business_owner = relationship("BusinessOwner", back_populates="reviews")
