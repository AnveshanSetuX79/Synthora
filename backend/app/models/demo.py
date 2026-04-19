"""Demo website model."""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class DemoWebsite(Base):
    """Demo website generated for businesses."""
    __tablename__ = "demo_websites"

    id = Column(String(36), primary_key=True)
    business_id = Column(String(36), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True)
    template_type = Column(String(100), nullable=False)  # restaurant, school, etc.
    html_content = Column(Text, nullable=False)  # Stored HTML content
    slug = Column(String(255), nullable=True, index=True)  # SEO-friendly URL slug
    
    # Analytics
    view_count = Column(Integer, default=0, nullable=False)
    claim_clicks = Column(Integer, default=0, nullable=False)
    last_viewed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    business = relationship("Business", back_populates="demos")
    creator = relationship("User", foreign_keys=[created_by])
