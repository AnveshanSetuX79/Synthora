"""Deal management service for handling projects and milestones.

This service handles:
- Deal creation with milestone generation
- Milestone tracking and status management
- Deal status transitions
- Payment milestone calculations

Requirements: 7.1, 7.2, 7.3, 7.4, 7.5
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import uuid

from ..models.deal import Deal, Milestone, DealStatus, MilestoneStatus, PaymentFlow
from ..models.business import Business
from ..models.user import Freelancer, BusinessOwner

logger = logging.getLogger(__name__)


class DealManagementError(Exception):
    """Base exception for deal management errors."""
    pass


class InvalidPackageError(DealManagementError):
    """Raised when package type is invalid."""
    pass


class InvalidStatusTransitionError(DealManagementError):
    """Raised when status transition is not allowed."""
    pass


class DealManagementService:
    """Service for managing deals and milestones."""
    
    # Package pricing (in rupees)
    PACKAGE_PRICING = {
        "starter": {"min": 2999, "max": 4999, "default": 3999},
        "standard": {"min": 10000, "max": 15000, "default": 12000},
        "premium": {"min": 35000, "max": 50000, "default": 40000},
    }
    
    # Milestone configurations
    SIMPLIFIED_MILESTONES = [
        {"sequence": 1, "name": "Advance Payment", "percentage": 50},
        {"sequence": 2, "name": "Final Delivery", "percentage": 50},
    ]
    
    FULL_MILESTONES = [
        {"sequence": 1, "name": "Design Phase", "percentage": 30},
        {"sequence": 2, "name": "Development Phase", "percentage": 40},
        {"sequence": 3, "name": "Final Delivery", "percentage": 30},
    ]
    
    @classmethod
    @classmethod
    def _determine_payment_flow(cls, db: Session, freelancer_id: str) -> str:
        """Determine payment flow based on freelancer's completed deals.
        
        Auto-upgrade to full flow after 20 completed deals.
        
        Args:
            db: Database session
            freelancer_id: Freelancer ID
            
        Returns:
            Payment flow type ("simplified" or "full")
        """
        completed_deals = db.query(Deal).filter(
            Deal.freelancer_id == freelancer_id,
            Deal.status == "completed"
        ).count()
        
        flow = "full" if completed_deals >= 20 else "simplified"
        
        logger.info(
            f"Freelancer {freelancer_id} has {completed_deals} completed deals. "
            f"Using {flow} payment flow."
        )
        
        return flow
    
    @classmethod
    def create_deal(
        cls,
        db: Session,
        freelancer_id: str,
        business_id: str,
        package_type: str,
        amount: int,
        payment_flow: Optional[str] = None,
        description: Optional[str] = None
    ) -> Deal:
        """Create a new deal with milestones.
        
        Args:
            db: Database session
            freelancer_id: Freelancer ID
            business_id: Business ID
            package_type: Package type (starter, standard, premium)
            amount: Deal amount in rupees
            payment_flow: Payment flow type (simplified or full). If None, auto-determined.
            description: Optional deal description
            
        Returns:
            Created Deal object with milestones
            
        Raises:
            InvalidPackageError: If package type is invalid
            DealManagementError: For other errors
        """
        try:
            # Auto-determine payment flow if not provided
            if payment_flow is None:
                payment_flow = cls._determine_payment_flow(db, freelancer_id)
            
            # Validate package type
            package_lower = package_type.lower()
            if package_lower not in cls.PACKAGE_PRICING:
                raise InvalidPackageError(
                    f"Invalid package type: {package_type}. "
                    f"Must be one of: {', '.join(cls.PACKAGE_PRICING.keys())}"
                )
            
            # Validate amount
            package_info = cls.PACKAGE_PRICING[package_lower]
            if amount < package_info["min"] or amount > package_info["max"]:
                logger.warning(
                    f"Amount {amount} outside recommended range "
                    f"({package_info['min']}-{package_info['max']}) for {package_type}"
                )
            
            # Get business owner if exists
            business = db.query(Business).filter(Business.id == business_id).first()
            business_owner_id = None
            if business and business.owner:
                business_owner_id = business.owner.id
            
            # Convert amount to paise
            amount_paise = amount * 100
            
            # Create deal
            deal = Deal(
                id=str(uuid.uuid4()),
                freelancer_id=freelancer_id,
                business_id=business_id,
                business_owner_id=business_owner_id,
                amount=amount_paise,
                payment_flow=PaymentFlow(payment_flow),
                status=DealStatus.PENDING,
                package_type=package_type.title(),
                description=description
            )
            
            db.add(deal)
            db.flush()  # Get deal ID
            
            # Generate milestones
            milestones = cls._generate_milestones(
                deal_id=deal.id,
                amount_paise=amount_paise,
                payment_flow=payment_flow
            )
            
            for milestone in milestones:
                db.add(milestone)
            
            db.commit()
            db.refresh(deal)
            
            logger.info(
                f"Created deal {deal.id} for ₹{amount} "
                f"({payment_flow} flow, {len(milestones)} milestones)"
            )
            
            return deal
            
        except InvalidPackageError:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating deal: {str(e)}")
            raise DealManagementError(f"Failed to create deal: {str(e)}")
    
    @classmethod
    def _generate_milestones(
        cls,
        deal_id: str,
        amount_paise: int,
        payment_flow: str
    ) -> List[Milestone]:
        """Generate milestones for a deal.
        
        Args:
            deal_id: Deal ID
            amount_paise: Total amount in paise
            payment_flow: Payment flow type
            
        Returns:
            List of Milestone objects
        """
        if payment_flow == "simplified":
            milestone_config = cls.SIMPLIFIED_MILESTONES
        else:
            milestone_config = cls.FULL_MILESTONES
        
        milestones = []
        
        for config in milestone_config:
            milestone_amount = int(amount_paise * config["percentage"] / 100)
            
            milestone = Milestone(
                id=str(uuid.uuid4()),
                deal_id=deal_id,
                sequence=config["sequence"],
                name=config["name"],
                percentage=config["percentage"],
                amount=milestone_amount,
                status=MilestoneStatus.PENDING
            )
            
            milestones.append(milestone)
        
        return milestones
    
    @classmethod
    def update_deal_status(
        cls,
        db: Session,
        deal_id: str,
        new_status: str,
        user_id: str
    ) -> Deal:
        """Update deal status with validation.
        
        Args:
            db: Database session
            deal_id: Deal ID
            new_status: New status
            user_id: User making the change
            
        Returns:
            Updated Deal object
            
        Raises:
            InvalidStatusTransitionError: If transition is not allowed
            DealManagementError: For other errors
        """
        try:
            deal = db.query(Deal).filter(Deal.id == deal_id).first()
            
            if not deal:
                raise DealManagementError(f"Deal {deal_id} not found")
            
            # Validate status transition
            old_status = deal.status
            new_status_enum = DealStatus(new_status)
            
            if not cls._is_valid_transition(old_status, new_status_enum):
                raise InvalidStatusTransitionError(
                    f"Invalid status transition: {old_status.value} -> {new_status}"
                )
            
            # Update status
            deal.status = new_status_enum
            
            # Set completed_at if status is completed
            if new_status_enum.value == "completed":
                deal.completed_at = datetime.utcnow()
            
            db.commit()
            db.refresh(deal)
            
            logger.info(
                f"Updated deal {deal_id} status: {old_status.value} -> {new_status}"
            )
            
            return deal
            
        except InvalidStatusTransitionError:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating deal status: {str(e)}")
            raise DealManagementError(f"Failed to update deal status: {str(e)}")
    
    @classmethod
    def _is_valid_transition(
        cls,
        old_status: DealStatus,
        new_status: DealStatus
    ) -> bool:
        """Check if status transition is valid.
        
        Args:
            old_status: Current status
            new_status: New status
            
        Returns:
            True if transition is valid
        """
        # Define valid transitions
        valid_transitions = {
            DealStatus.PENDING: [DealStatus.ACTIVE, DealStatus.CANCELLED],
            DealStatus.ACTIVE: [DealStatus.IN_PROGRESS, DealStatus.CANCELLED],
            DealStatus.IN_PROGRESS: [DealStatus.COMPLETED, DealStatus.DISPUTED, DealStatus.CANCELLED],
            DealStatus.DISPUTED: [DealStatus.IN_PROGRESS, DealStatus.CANCELLED],
            DealStatus.COMPLETED: [],  # Terminal state
            DealStatus.CANCELLED: [],  # Terminal state
        }
        
        return new_status in valid_transitions.get(old_status, [])
    
    @classmethod
    def update_milestone_status(
        cls,
        db: Session,
        milestone_id: str,
        new_status: str,
        deliverables: Optional[List[str]] = None,
        feedback: Optional[str] = None,
        rejection_reason: Optional[str] = None
    ) -> Milestone:
        """Update milestone status.
        
        Args:
            db: Database session
            milestone_id: Milestone ID
            new_status: New status
            deliverables: Optional deliverables list
            feedback: Optional feedback
            rejection_reason: Optional rejection reason
            
        Returns:
            Updated Milestone object
        """
        try:
            milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
            
            if not milestone:
                raise DealManagementError(f"Milestone {milestone_id} not found")
            
            old_status = milestone.status
            new_status_enum = MilestoneStatus(new_status)
            
            # Update status
            milestone.status = new_status_enum
            
            # Update timestamps based on status
            now = datetime.utcnow()
            
            status_value = new_status_enum.value if hasattr(new_status_enum, 'value') else new_status_enum
            
            if status_value == "submitted":
                milestone.submitted_at = now
                if deliverables:
                    milestone.deliverables = deliverables
            elif status_value == "approved":
                milestone.approved_at = now
                if feedback:
                    milestone.feedback = feedback
            elif status_value == "rejected":
                milestone.rejected_at = now
                if rejection_reason:
                    milestone.rejection_reason = rejection_reason
            elif status_value == "paid":
                milestone.paid_at = now
            
            db.commit()
            db.refresh(milestone)
            
            logger.info(
                f"Updated milestone {milestone_id} status: "
                f"{old_status.value} -> {new_status}"
            )
            
            return milestone
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating milestone status: {str(e)}")
            raise DealManagementError(f"Failed to update milestone status: {str(e)}")
    
    @classmethod
    def get_deal_details(
        cls,
        db: Session,
        deal_id: str
    ) -> Dict:
        """Get detailed deal information.
        
        Args:
            db: Database session
            deal_id: Deal ID
            
        Returns:
            Dictionary with deal details
        """
        deal = db.query(Deal).filter(Deal.id == deal_id).first()
        
        if not deal:
            raise DealManagementError(f"Deal {deal_id} not found")
        
        # Get milestones
        milestones = db.query(Milestone).filter(
            Milestone.deal_id == deal_id
        ).order_by(Milestone.sequence).all()
        
        return {
            "id": deal.id,
            "freelancer_id": deal.freelancer_id,
            "business_id": deal.business_id,
            "business_owner_id": deal.business_owner_id,
            "amount": deal.amount / 100,  # Convert to rupees
            "payment_flow": deal.payment_flow.value,
            "status": deal.status.value,
            "package_type": deal.package_type,
            "description": deal.description,
            "created_at": deal.created_at.isoformat(),
            "updated_at": deal.updated_at.isoformat(),
            "completed_at": deal.completed_at.isoformat() if deal.completed_at else None,
            "milestones": [
                {
                    "id": m.id,
                    "sequence": m.sequence,
                    "name": m.name,
                    "percentage": m.percentage,
                    "amount": m.amount / 100,  # Convert to rupees
                    "status": m.status.value,
                    "deliverables": m.deliverables,
                    "feedback": m.feedback,
                    "rejection_reason": m.rejection_reason,
                    "submitted_at": m.submitted_at.isoformat() if m.submitted_at else None,
                    "approved_at": m.approved_at.isoformat() if m.approved_at else None,
                    "paid_at": m.paid_at.isoformat() if m.paid_at else None,
                    "due_date": m.due_date.isoformat() if m.due_date else None,
                }
                for m in milestones
            ]
        }
    
    @classmethod
    def get_user_deals(
        cls,
        db: Session,
        user_id: str,
        role: str,
        status_filter: Optional[str] = None
    ) -> List[Dict]:
        """Get deals for a user (freelancer or business owner).
        
        Args:
            db: Database session
            user_id: User ID
            role: User role (freelancer or business_owner)
            status_filter: Optional status filter
            
        Returns:
            List of deal dictionaries
        """
        query = db.query(Deal)
        
        if role == "freelancer":
            freelancer = db.query(Freelancer).filter(Freelancer.user_id == user_id).first()
            if not freelancer:
                return []
            query = query.filter(Deal.freelancer_id == freelancer.id)
        elif role == "business_owner":
            business_owner = db.query(BusinessOwner).filter(BusinessOwner.user_id == user_id).first()
            if not business_owner:
                return []
            query = query.filter(Deal.business_owner_id == business_owner.id)
        else:
            return []
        
        # Apply status filter
        if status_filter:
            try:
                status_enum = DealStatus(status_filter)
                query = query.filter(Deal.status == status_enum)
            except ValueError:
                pass  # Invalid status, ignore
        
        deals = query.order_by(Deal.created_at.desc()).all()
        
        return [cls.get_deal_details(db, deal.id) for deal in deals]
