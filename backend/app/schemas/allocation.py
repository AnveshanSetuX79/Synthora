"""Lead allocation API request/response schemas."""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class ClaimLeadRequest(BaseModel):
    """Request schema for claiming a lead."""
    pass  # No body needed, lead_id comes from path


class ClaimLeadResponse(BaseModel):
    """Response schema for claiming a lead."""
    success: bool
    contact_id: str
    lead_id: str
    freelancer_id: str
    exclusivity_expires_at: datetime
    message: str


class AvailableLeadItem(BaseModel):
    """Single available lead item."""
    lead_id: str
    business_id: str
    business_name: str
    category: str
    address: str
    city: str
    score: int
    digital_score: int
    freshness: str
    has_website: bool
    rating: Optional[float]
    review_count: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class AvailableLeadsResponse(BaseModel):
    """Response schema for available leads."""
    success: bool
    remaining_allocations: int
    daily_limit: int
    available_count: int
    leads: List[AvailableLeadItem]


class MyLeadItem(BaseModel):
    """Single allocated lead item."""
    contact_id: str
    lead_id: str
    business_id: str
    business_name: str
    category: str
    address: str
    city: str
    phone: Optional[str]
    score: int
    digital_score: int
    status: str
    exclusivity_active: bool
    exclusivity_expires_at: Optional[str]
    first_contact_at: str
    last_contact_at: str
    consent_status: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class MyLeadsResponse(BaseModel):
    """Response schema for my leads."""
    success: bool
    total: int
    leads: List[MyLeadItem]
