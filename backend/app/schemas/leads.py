"""Lead API request/response schemas."""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class LeadDiscoverRequest(BaseModel):
    """Request schema for lead discovery."""
    category: str = Field(..., description="Business category (e.g., restaurant, school)")
    location: str = Field(..., description="City name or coordinates (lat,lng)")
    limit: Optional[int] = Field(default=20, ge=1, le=100, description="Maximum number of leads to discover")


class BusinessInsightResponse(BaseModel):
    """Business insight data in response."""
    digital_score: int
    digital_score_breakdown: dict
    priority_score: int
    freshness: str
    rating: Optional[float]
    review_count: int
    has_website: bool
    website_url: Optional[str]
    last_verified: datetime
    
    # AI Enrichment fields
    ai_description: Optional[str] = None
    ai_specialties: Optional[List[str]] = None
    ai_target_customers: Optional[List[str]] = None
    ai_pain_points: Optional[List[str]] = None
    ai_recommended_solutions: Optional[List[str]] = None
    ai_competitive_advantages: Optional[List[str]] = None
    ai_digital_maturity: Optional[str] = None
    ai_growth_potential: Optional[str] = None
    ai_estimated_size: Optional[str] = None
    ai_online_presence_score: Optional[int] = None
    ai_urgency_score: Optional[int] = None
    ai_enrichment_confidence: Optional[float] = None
    ai_enriched_at: Optional[datetime] = None
    ai_pitch_suggestions: Optional[List[str]] = None
    
    class Config:
        from_attributes = True
        # Map database column names to schema field names
        populate_by_name = True
        
    @classmethod
    def from_orm(cls, obj):
        """Custom from_orm to handle column name mapping."""
        data = {
            'digital_score': obj.digital_score,
            'digital_score_breakdown': obj.digital_score_breakdown,
            'priority_score': obj.lead_priority_score,  # Map from DB column
            'freshness': obj.lead_freshness_score,  # Map from DB column
            'rating': obj.rating,
            'review_count': obj.review_count,
            'has_website': obj.has_website,
            'website_url': obj.website_url,
            'last_verified': obj.last_verified,
            'ai_description': obj.ai_description,
            'ai_specialties': obj.ai_specialties,
            'ai_target_customers': obj.ai_target_customers,
            'ai_pain_points': obj.ai_pain_points,
            'ai_recommended_solutions': obj.ai_recommended_solutions,
            'ai_competitive_advantages': obj.ai_competitive_advantages,
            'ai_digital_maturity': obj.ai_digital_maturity,
            'ai_growth_potential': obj.ai_growth_potential,
            'ai_estimated_size': obj.ai_estimated_size,
            'ai_online_presence_score': obj.ai_online_presence_score,
            'ai_urgency_score': obj.ai_urgency_score,
            'ai_enrichment_confidence': obj.ai_enrichment_confidence,
            'ai_enriched_at': obj.ai_enriched_at,
            'ai_pitch_suggestions': obj.ai_pitch_suggestions,
        }
        return cls(**data)


class BusinessResponse(BaseModel):
    """Business data in response."""
    id: str
    place_id: str
    name: str
    category: str
    address: str
    city: str
    phone: Optional[str]
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: datetime
    updated_at: datetime


class LeadResponse(BaseModel):
    """Lead data in response."""
    id: str
    business_id: str
    source: str
    score: int
    status: str
    created_at: datetime
    business: BusinessResponse
    insights: Optional[BusinessInsightResponse]


class LeadListResponse(BaseModel):
    """Response for lead list endpoint."""
    success: bool
    total: int
    leads: List[LeadResponse]


class LeadDetailResponse(BaseModel):
    """Response for lead detail endpoint."""
    success: bool
    lead: LeadResponse


class LeadDiscoverResponse(BaseModel):
    """Response for lead discovery endpoint."""
    success: bool
    discovered: int
    stored: int
    leads: List[LeadResponse]

