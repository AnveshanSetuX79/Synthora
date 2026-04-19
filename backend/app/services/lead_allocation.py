"""Lead allocation service for managing freelancer access to leads.

This service implements:
- 6-hour exclusivity windows per freelancer
- Tier-based daily limits (New: 3, Verified: 10, Top Rated: 20)
- Allocation tracking and history
- Duplicate allocation prevention

Requirements: 41.1, 41.2, 41.3, 41.4, 33.1, 33.2, 33.3, 33.4
"""
import logging
from typing import Optional, List, Dict
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import uuid

from ..models.lead import Lead, LeadContact, LeadContactStatus, LeadStatus
from ..models.user import Freelancer, FreelancerTier
from ..models.business import Business, BusinessInsight
from .lead_access_control import LeadAccessControlService, ContactLimitExceededError

logger = logging.getLogger(__name__)


class AllocationError(Exception):
    """Base exception for allocation errors."""
    pass


class ExclusivityViolationError(AllocationError):
    """Raised when trying to allocate a lead within exclusivity window."""
    pass


class DailyLimitExceededError(AllocationError):
    """Raised when freelancer exceeds daily allocation limit."""
    pass


class LeadAllocationService:
    """Service for managing lead allocation to freelancers."""
    
    # Tier-based daily limits
    TIER_LIMITS = {
        FreelancerTier.NEW: 3,
        FreelancerTier.VERIFIED: 10,
        FreelancerTier.TOP_RATED: 20,
    }
    
    # Exclusivity window duration
    EXCLUSIVITY_HOURS = 6
    
    @classmethod
    def allocate_lead(
        cls,
        db: Session,
        lead_id: str,
        freelancer_id: str
    ) -> LeadContact:
        """Allocate a lead to a freelancer with exclusivity window.
        
        This method:
        1. Checks if lead is available (not in active exclusivity window)
        2. Checks freelancer's daily limit
        3. Creates lead contact with 6-hour exclusivity window
        4. Updates freelancer's remaining contacts
        
        Args:
            db: Database session
            lead_id: Lead ID to allocate
            freelancer_id: Freelancer ID to allocate to
            
        Returns:
            LeadContact object with exclusivity window
            
        Raises:
            ExclusivityViolationError: If lead is in active exclusivity window
            DailyLimitExceededError: If freelancer exceeded daily limit
            AllocationError: For other allocation errors
        """
        # Get lead
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise AllocationError(f"Lead {lead_id} not found")
        
        # Get freelancer
        freelancer = db.query(Freelancer).filter(Freelancer.id == freelancer_id).first()
        if not freelancer:
            raise AllocationError(f"Freelancer {freelancer_id} not found")
        
        # Check if freelancer already contacted this lead (MUST CHECK FIRST)
        existing_contact = db.query(LeadContact).filter(
            and_(
                LeadContact.lead_id == lead_id,
                LeadContact.freelancer_id == freelancer_id
            )
        ).first()
        
        if existing_contact:
            raise AllocationError(
                f"Freelancer {freelancer_id} has already contacted lead {lead_id}"
            )
        
        # Check if lead is in active exclusivity window by OTHER freelancers
        if cls._is_in_exclusivity_window(db, lead_id, exclude_freelancer_id=freelancer_id):
            raise ExclusivityViolationError(
                f"Lead {lead_id} is currently in an active exclusivity window by another freelancer"
            )
        
        # Check daily limit
        if not cls._check_daily_limit(db, freelancer):
            raise DailyLimitExceededError(
                f"Freelancer {freelancer_id} has exceeded daily allocation limit "
                f"({cls.TIER_LIMITS[freelancer.tier]} leads/day)"
            )
        
        # Check business contact limit (Requirement 2.3)
        can_contact, message, available_slots = LeadAccessControlService.can_contact_business(
            db=db,
            business_id=lead.business_id,
            freelancer_id=freelancer_id
        )
        
        if not can_contact:
            raise ContactLimitExceededError(message)
        
        # Create lead contact with exclusivity window
        exclusivity_expires_at = datetime.now(timezone.utc) + timedelta(hours=cls.EXCLUSIVITY_HOURS)
        
        lead_contact = LeadContact(
            id=str(uuid.uuid4()),
            lead_id=lead_id,
            freelancer_id=freelancer_id,
            status=LeadContactStatus.CONTACTED,
            exclusivity_active=True,
            exclusivity_expires_at=exclusivity_expires_at,
            first_contact_at=datetime.now(timezone.utc),
            last_contact_at=datetime.now(timezone.utc)
        )
        
        db.add(lead_contact)
        
        # Update lead status
        lead.status = LeadStatus.ASSIGNED
        
        # Decrement freelancer's remaining contacts
        freelancer.remaining_contacts -= 1
        
        db.commit()
        db.refresh(lead_contact)
        
        logger.info(
            f"Allocated lead {lead_id} to freelancer {freelancer_id}. "
            f"Exclusivity expires at {exclusivity_expires_at}"
        )
        
        return lead_contact
    
    @classmethod
    def _is_in_exclusivity_window(
        cls, 
        db: Session, 
        lead_id: str,
        exclude_freelancer_id: Optional[str] = None
    ) -> bool:
        """Check if lead is currently in an active exclusivity window.
        
        Args:
            db: Database session
            lead_id: Lead ID to check
            exclude_freelancer_id: Optional freelancer ID to exclude from check
            
        Returns:
            True if lead is in active exclusivity window by OTHER freelancers, False otherwise
        """
        now = datetime.now(timezone.utc)
        
        query = db.query(LeadContact).filter(
            and_(
                LeadContact.lead_id == lead_id,
                LeadContact.exclusivity_active == True,
                LeadContact.exclusivity_expires_at > now
            )
        )
        
        # Exclude specific freelancer if provided (to prevent same freelancer re-claiming)
        if exclude_freelancer_id:
            query = query.filter(LeadContact.freelancer_id != exclude_freelancer_id)
        
        active_contact = query.first()
        
        return active_contact is not None
    
    @classmethod
    def _check_daily_limit(cls, db: Session, freelancer: Freelancer) -> bool:
        """Check if freelancer has remaining allocations for today.
        
        Args:
            db: Database session
            freelancer: Freelancer object
            
        Returns:
            True if freelancer can allocate more leads, False otherwise
        """
        # Check remaining contacts (already tracked in freelancer model)
        return freelancer.remaining_contacts > 0
    
    @classmethod
    def reset_daily_limits(cls, db: Session) -> int:
        """Reset daily allocation limits for all freelancers.
        
        This should be called at midnight (UTC) via a scheduled job.
        
        Args:
            db: Database session
            
        Returns:
            Number of freelancers reset
        """
        freelancers = db.query(Freelancer).all()
        
        count = 0
        for freelancer in freelancers:
            daily_limit = cls.TIER_LIMITS.get(freelancer.tier, cls.TIER_LIMITS[FreelancerTier.NEW])
            freelancer.remaining_contacts = daily_limit
            count += 1
        
        db.commit()
        
        logger.info(f"Reset daily limits for {count} freelancers")
        return count
    
    @classmethod
    def get_available_leads(
        cls,
        db: Session,
        freelancer_id: str,
        category: Optional[str] = None,
        score_min: Optional[int] = None,
        limit: int = 20
    ) -> List[Dict]:
        """Get available leads for a freelancer (respects tier limits).
        
        Available leads are those:
        - Not in active exclusivity window
        - Not already contacted by this freelancer
        - Match optional filters
        
        Args:
            db: Database session
            freelancer_id: Freelancer ID
            category: Optional category filter
            score_min: Optional minimum score filter
            limit: Maximum number of leads to return
            
        Returns:
            List of available lead dictionaries
        """
        # Get freelancer
        freelancer = db.query(Freelancer).filter(Freelancer.id == freelancer_id).first()
        if not freelancer:
            return []
        
        # Check if freelancer has remaining allocations
        if freelancer.remaining_contacts <= 0:
            logger.info(f"Freelancer {freelancer_id} has no remaining allocations today")
            return []
        
        # Get leads already contacted by this freelancer (optimized)
        contacted_lead_ids_subquery = db.query(LeadContact.lead_id).filter(
            LeadContact.freelancer_id == freelancer_id
        ).subquery()
        
        # Get leads in active exclusivity windows (optimized)
        now = datetime.now(timezone.utc)
        exclusive_lead_ids_subquery = db.query(LeadContact.lead_id).filter(
            and_(
                LeadContact.exclusivity_active == True,
                LeadContact.exclusivity_expires_at > now
            )
        ).subquery()
        
        # Build optimized query for available leads
        query = db.query(
            Lead.id.label('lead_id'),
            Business.id.label('business_id'),
            Business.name.label('business_name'),
            Business.category,
            Business.address,
            Business.city,
            Business.latitude,
            Business.longitude,
            Lead.score,
            BusinessInsight.digital_score,
            BusinessInsight.lead_freshness_score.label('freshness'),
            BusinessInsight.has_website,
            BusinessInsight.rating,
            BusinessInsight.review_count
        ).select_from(Lead).join(
            Business, Lead.business_id == Business.id
        ).join(
            BusinessInsight, Business.id == BusinessInsight.business_id
        ).filter(
            Lead.is_active == True,
            Lead.status.in_(['new', 'assigned']),
            ~Lead.id.in_(contacted_lead_ids_subquery),
            ~Lead.id.in_(exclusive_lead_ids_subquery)
        )
        
        # Apply filters
        if category:
            query = query.filter(Business.category == category)
        if score_min is not None:
            query = query.filter(BusinessInsight.digital_score >= score_min)
        
        # Order by score and limit - use index
        results = query.order_by(BusinessInsight.digital_score.desc()).limit(limit).all()
        
        # Build response (results are already Row objects with named columns)
        available_leads = []
        for row in results:
            available_leads.append({
                "lead_id": row.lead_id,
                "business_id": row.business_id,
                "business_name": row.business_name,
                "category": row.category,
                "address": row.address,
                "city": row.city,
                "score": row.score,
                "digital_score": row.digital_score,
                "freshness": row.freshness,
                "has_website": row.has_website,
                "rating": row.rating,
                "review_count": row.review_count,
                "latitude": row.latitude,
                "longitude": row.longitude
            })
        
        logger.info(
            f"Found {len(available_leads)} available leads for freelancer {freelancer_id}"
        )
        
        return available_leads
    
    @classmethod
    def get_my_leads(
        cls,
        db: Session,
        freelancer_id: str,
        status: Optional[str] = None
    ) -> List[Dict]:
        """Get leads allocated to a freelancer.
        
        Args:
            db: Database session
            freelancer_id: Freelancer ID
            status: Optional status filter
            
        Returns:
            List of allocated lead dictionaries
        """
        query = db.query(LeadContact, Lead, Business, BusinessInsight).join(
            Lead, LeadContact.lead_id == Lead.id
        ).join(
            Business, Lead.business_id == Business.id
        ).join(
            BusinessInsight, Business.id == BusinessInsight.business_id
        ).filter(
            LeadContact.freelancer_id == freelancer_id
        )
        
        # Apply status filter
        if status:
            try:
                status_enum = LeadContactStatus(status)
                query = query.filter(LeadContact.status == status_enum)
            except ValueError:
                pass  # Invalid status, ignore
        
        # Order by most recent first
        results = query.order_by(LeadContact.first_contact_at.desc()).all()
        
        # Build response
        my_leads = []
        now = datetime.now(timezone.utc)
        
        for contact, lead, business, insights in results:
            # Check if exclusivity is still active
            exclusivity_active = (
                contact.exclusivity_active and 
                contact.exclusivity_expires_at > now
            )
            
            my_leads.append({
                "contact_id": contact.id,
                "lead_id": lead.id,
                "business_id": business.id,
                "business_name": business.name,
                "category": business.category,
                "address": business.address,
                "city": business.city,
                "phone": business.phone,
                "score": lead.score,
                "digital_score": insights.digital_score,
                "status": contact.status if isinstance(contact.status, str) else contact.status.value,
                "exclusivity_active": exclusivity_active,
                "exclusivity_expires_at": contact.exclusivity_expires_at.isoformat() if contact.exclusivity_expires_at else None,
                "first_contact_at": contact.first_contact_at.isoformat(),
                "last_contact_at": contact.last_contact_at.isoformat(),
                "consent_status": contact.consent_status if isinstance(contact.consent_status, str) else contact.consent_status.value,
                "latitude": business.latitude,
                "longitude": business.longitude
            })
        
        logger.info(f"Found {len(my_leads)} allocated leads for freelancer {freelancer_id}")
        
        return my_leads
    
    @classmethod
    def expire_exclusivity_windows(cls, db: Session) -> int:
        """Expire exclusivity windows that have passed their expiration time.
        
        This should be called periodically (e.g., every hour) via a scheduled job.
        
        Args:
            db: Database session
            
        Returns:
            Number of exclusivity windows expired
        """
        now = datetime.now(timezone.utc)
        
        expired_contacts = db.query(LeadContact).filter(
            and_(
                LeadContact.exclusivity_active == True,
                LeadContact.exclusivity_expires_at <= now
            )
        ).all()
        
        count = 0
        for contact in expired_contacts:
            contact.exclusivity_active = False
            count += 1
        
        db.commit()
        
        logger.info(f"Expired {count} exclusivity windows")
        return count
