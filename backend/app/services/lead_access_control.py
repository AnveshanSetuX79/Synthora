"""Lead access control service.

Handles:
- 5-freelancer limit per business
- Contact count tracking
- Business status transitions
- Follow-up tracking and cold lead detection

Requirements: 2.3, 2.4
"""
import logging
from typing import Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models.business import Business, BusinessInsight
from ..models.lead import Lead, LeadContact
from ..models.user import Freelancer

logger = logging.getLogger(__name__)


class LeadAccessControlError(Exception):
    """Base exception for lead access control errors."""
    pass


class ContactLimitExceededError(LeadAccessControlError):
    """Raised when business has reached maximum contact limit."""
    pass


class LeadAccessControlService:
    """Service for managing lead access control and state transitions."""
    
    MAX_CONTACTS_PER_BUSINESS = 5
    COLD_FOLLOW_UP_THRESHOLD = 2
    
    @classmethod
    def can_contact_business(
        cls,
        db: Session,
        business_id: str,
        freelancer_id: str = None
    ) -> Tuple[bool, str, int]:
        """Check if a business can be contacted by another freelancer.
        
        Args:
            db: Database session
            business_id: Business ID to check
            freelancer_id: Optional freelancer ID (to check if already contacted)
            
        Returns:
            Tuple of (can_contact, message, available_slots)
        """
        # Get business insight
        insight = db.query(BusinessInsight).filter(
            BusinessInsight.business_id == business_id
        ).first()
        
        if not insight:
            return True, "No contact history", cls.MAX_CONTACTS_PER_BUSINESS
        
        # Check if business is unavailable
        if insight.status == "Unavailable":
            return False, "Business is unavailable (maximum contacts reached)", 0
        
        # Check contact count
        contact_count = insight.contact_count
        available_slots = cls.MAX_CONTACTS_PER_BUSINESS - contact_count
        
        if contact_count >= cls.MAX_CONTACTS_PER_BUSINESS:
            return False, f"Maximum {cls.MAX_CONTACTS_PER_BUSINESS} freelancers already contacted", 0
        
        # Check if this freelancer already contacted this business
        if freelancer_id:
            existing_contact = db.query(LeadContact).join(Lead).filter(
                Lead.business_id == business_id,
                LeadContact.freelancer_id == freelancer_id
            ).first()
            
            if existing_contact:
                return False, "You have already contacted this business", available_slots
        
        return True, f"{available_slots} slots remaining", available_slots
    
    @classmethod
    def increment_contact_count(
        cls,
        db: Session,
        business_id: str,
        is_first_contact: bool = True
    ) -> None:
        """Increment contact count and update business status.
        
        Args:
            db: Database session
            business_id: Business ID
            is_first_contact: Whether this is the first contact from this freelancer
        """
        insight = db.query(BusinessInsight).filter(
            BusinessInsight.business_id == business_id
        ).first()
        
        if not insight:
            logger.warning(f"No insight found for business {business_id}")
            return
        
        # Only increment if this is a first contact (not a follow-up)
        if is_first_contact:
            old_count = insight.contact_count
            insight.contact_count += 1
            new_count = insight.contact_count
            
            logger.info(f"Business {business_id} contact count: {old_count} → {new_count}")
            
            # Update status based on count
            if new_count == 1 and insight.status == "Active":
                insight.status = "Contacted"
                logger.info(f"Business {business_id} status: Active → Contacted")
            
            elif new_count >= cls.MAX_CONTACTS_PER_BUSINESS:
                insight.status = "Unavailable"
                logger.info(f"Business {business_id} status: → Unavailable (max contacts reached)")
            
            db.commit()
    
    @classmethod
    def increment_follow_up_count(
        cls,
        db: Session,
        lead_contact_id: str
    ) -> None:
        """Increment follow-up count for a lead contact.
        
        Args:
            db: Database session
            lead_contact_id: LeadContact ID
        """
        lead_contact = db.query(LeadContact).filter(
            LeadContact.id == lead_contact_id
        ).first()
        
        if not lead_contact:
            logger.warning(f"No lead contact found: {lead_contact_id}")
            return
        
        lead_contact.follow_up_count += 1
        logger.info(f"Lead contact {lead_contact_id} follow-up count: {lead_contact.follow_up_count}")
        
        db.commit()
    
    @classmethod
    def check_and_mark_cold(
        cls,
        db: Session,
        lead_contact_id: str,
        has_response: bool = False
    ) -> bool:
        """Check if lead should be marked as cold and update status.
        
        A lead is marked cold if:
        - 2 or more follow-ups sent
        - No response received
        
        Args:
            db: Database session
            lead_contact_id: LeadContact ID
            has_response: Whether business has responded
            
        Returns:
            True if marked as cold, False otherwise
        """
        lead_contact = db.query(LeadContact).filter(
            LeadContact.id == lead_contact_id
        ).first()
        
        if not lead_contact:
            logger.warning(f"No lead contact found: {lead_contact_id}")
            return False
        
        # Don't mark as cold if there's been a response
        if has_response:
            return False
        
        # Check if threshold reached
        if lead_contact.follow_up_count >= cls.COLD_FOLLOW_UP_THRESHOLD:
            # Mark lead contact as cold
            old_status = lead_contact.status
            lead_contact.status = "cold"
            logger.info(f"Lead contact {lead_contact_id} status: {old_status} → cold")
            
            # Update business insight status to Cold
            lead = db.query(Lead).filter(Lead.id == lead_contact.lead_id).first()
            if lead:
                insight = db.query(BusinessInsight).filter(
                    BusinessInsight.business_id == lead.business_id
                ).first()
                
                if insight and insight.status == "Contacted":
                    insight.status = "Cold"
                    logger.info(f"Business {lead.business_id} status: Contacted → Cold")
            
            db.commit()
            return True
        
        return False
    
    @classmethod
    def get_contact_stats(
        cls,
        db: Session,
        business_id: str
    ) -> dict:
        """Get contact statistics for a business.
        
        Args:
            db: Database session
            business_id: Business ID
            
        Returns:
            Dictionary with contact stats
        """
        insight = db.query(BusinessInsight).filter(
            BusinessInsight.business_id == business_id
        ).first()
        
        if not insight:
            return {
                "contact_count": 0,
                "available_slots": cls.MAX_CONTACTS_PER_BUSINESS,
                "status": "Active",
                "is_available": True
            }
        
        available_slots = max(0, cls.MAX_CONTACTS_PER_BUSINESS - insight.contact_count)
        is_available = insight.status not in ["Unavailable", "Cold"]
        
        return {
            "contact_count": insight.contact_count,
            "available_slots": available_slots,
            "status": insight.status or "Active",
            "is_available": is_available
        }
    
    @classmethod
    def reset_cold_leads(
        cls,
        db: Session,
        days_since_last_contact: int = 30
    ) -> int:
        """Reset cold leads that haven't been contacted in X days.
        
        This allows businesses to become available again after a period.
        
        Args:
            db: Database session
            days_since_last_contact: Days threshold
            
        Returns:
            Number of leads reset
        """
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_since_last_contact)
        
        # Find cold lead contacts with no recent activity
        cold_contacts = db.query(LeadContact).filter(
            LeadContact.status == "cold",
            LeadContact.last_contact_at < cutoff_date
        ).all()
        
        count = 0
        for contact in cold_contacts:
            # Reset to contacted status
            contact.status = "contacted"
            contact.follow_up_count = 0
            count += 1
        
        if count > 0:
            db.commit()
            logger.info(f"Reset {count} cold leads")
        
        return count
