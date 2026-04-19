"""Dispute resolution service.

This service handles:
- Dispute creation and management
- 48-hour self-resolution period
- Admin mediation and resolution
- Dispute chat interface
- Payment execution after resolution

Requirements: 8.1, 8.2, 8.3
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
import uuid

from ..models.dispute import Dispute, DisputeMessage, DisputeStatus, DisputeResolution
from ..models.deal import Deal, DealStatus
from ..models.user import User
from ..models.payment import Payment

logger = logging.getLogger(__name__)


class DisputeError(Exception):
    """Base exception for dispute errors."""
    pass


class DisputeResolutionService:
    """Service for managing dispute resolution."""
    
    SELF_RESOLUTION_HOURS = 48
    ADMIN_RESOLUTION_HOURS = 24
    
    @classmethod
    def create_dispute(
        cls,
        db: Session,
        deal_id: str,
        raised_by: str,
        raised_by_role: str,
        reason: str,
        description: Optional[str] = None
    ) -> Dispute:
        """Create a new dispute.
        
        Args:
            db: Database session
            deal_id: Deal ID
            raised_by: User ID who raised the dispute
            raised_by_role: Role (freelancer or business_owner)
            reason: Dispute reason
            description: Optional detailed description
            
        Returns:
            Created Dispute object
            
        Raises:
            DisputeError: If dispute creation fails
        """
        try:
            # Check if deal exists
            deal = db.query(Deal).filter(Deal.id == deal_id).first()
            if not deal:
                raise DisputeError(f"Deal {deal_id} not found")
            
            # Check if dispute already exists
            existing_dispute = db.query(Dispute).filter(
                Dispute.deal_id == deal_id
            ).first()
            
            if existing_dispute:
                raise DisputeError("Dispute already exists for this deal")
            
            # Calculate self-resolution deadline (48 hours)
            now = datetime.now(timezone.utc)
            deadline = now + timedelta(hours=cls.SELF_RESOLUTION_HOURS)
            
            # Create dispute
            dispute = Dispute(
                id=str(uuid.uuid4()),
                deal_id=deal_id,
                raised_by=raised_by,
                raised_by_role=raised_by_role,
                reason=reason,
                description=description,
                status=DisputeStatus.SELF_RESOLUTION.value,
                self_resolution_deadline=deadline
            )
            
            db.add(dispute)
            
            # Update deal status
            deal.status = DealStatus.DISPUTED.value
            
            # Create system message
            system_msg = DisputeMessage(
                id=str(uuid.uuid4()),
                dispute_id=dispute.id,
                sender_id=raised_by,
                sender_role="system",
                message=f"Dispute raised by {raised_by_role}. Reason: {reason}. Both parties have 48 hours to resolve this dispute before admin mediation.",
                is_system_message="true"
            )
            
            db.add(system_msg)
            db.commit()
            db.refresh(dispute)
            
            logger.info(f"Dispute created for deal {deal_id} by {raised_by_role}")
            
            return dispute
            
        except DisputeError:
            raise
        except Exception as e:
            logger.error(f"Error creating dispute: {str(e)}")
            db.rollback()
            raise DisputeError(f"Failed to create dispute: {str(e)}")
    
    @classmethod
    def add_message(
        cls,
        db: Session,
        dispute_id: str,
        sender_id: str,
        sender_role: str,
        message: str
    ) -> DisputeMessage:
        """Add a message to dispute chat.
        
        Args:
            db: Database session
            dispute_id: Dispute ID
            sender_id: User ID sending the message
            sender_role: Role (freelancer, business_owner, admin)
            message: Message content
            
        Returns:
            Created DisputeMessage object
        """
        try:
            dispute = db.query(Dispute).filter(Dispute.id == dispute_id).first()
            if not dispute:
                raise DisputeError(f"Dispute {dispute_id} not found")
            
            msg = DisputeMessage(
                id=str(uuid.uuid4()),
                dispute_id=dispute_id,
                sender_id=sender_id,
                sender_role=sender_role,
                message=message,
                is_system_message="false"
            )
            
            db.add(msg)
            db.commit()
            db.refresh(msg)
            
            return msg
            
        except Exception as e:
            logger.error(f"Error adding dispute message: {str(e)}")
            db.rollback()
            raise DisputeError(f"Failed to add message: {str(e)}")
    
    @classmethod
    def escalate_to_admin(
        cls,
        db: Session,
        dispute_id: str
    ) -> Dispute:
        """Escalate dispute to admin mediation.
        
        Args:
            db: Database session
            dispute_id: Dispute ID
            
        Returns:
            Updated Dispute object
        """
        try:
            dispute = db.query(Dispute).filter(Dispute.id == dispute_id).first()
            if not dispute:
                raise DisputeError(f"Dispute {dispute_id} not found")
            
            # Update status
            dispute.status = DisputeStatus.ADMIN_MEDIATION.value
            dispute.escalated_at = datetime.now(timezone.utc)
            
            # Add system message
            system_msg = DisputeMessage(
                id=str(uuid.uuid4()),
                dispute_id=dispute_id,
                sender_id=dispute.raised_by,
                sender_role="system",
                message="Dispute escalated to admin mediation. An admin will review the case and make a decision within 24 hours.",
                is_system_message="true"
            )
            
            db.add(system_msg)
            db.commit()
            db.refresh(dispute)
            
            logger.info(f"Dispute {dispute_id} escalated to admin mediation")
            
            return dispute
            
        except Exception as e:
            logger.error(f"Error escalating dispute: {str(e)}")
            db.rollback()
            raise DisputeError(f"Failed to escalate dispute: {str(e)}")
    
    @classmethod
    def resolve_dispute(
        cls,
        db: Session,
        dispute_id: str,
        resolved_by: str,
        resolution_type: str,
        resolution_amount: Optional[int] = None,
        resolution_notes: Optional[str] = None
    ) -> Dispute:
        """Resolve a dispute (admin action).
        
        Args:
            db: Database session
            dispute_id: Dispute ID
            resolved_by: Admin user ID
            resolution_type: Resolution type (full_payment_freelancer, partial_payment, full_refund_business)
            resolution_amount: Amount for partial payment (in paise)
            resolution_notes: Admin notes explaining the decision
            
        Returns:
            Updated Dispute object
        """
        try:
            dispute = db.query(Dispute).filter(Dispute.id == dispute_id).first()
            if not dispute:
                raise DisputeError(f"Dispute {dispute_id} not found")
            
            deal = dispute.deal
            
            # Update dispute
            dispute.status = DisputeStatus.RESOLVED.value
            dispute.resolution_type = resolution_type
            dispute.resolution_amount = resolution_amount
            dispute.resolution_notes = resolution_notes
            dispute.resolved_by = resolved_by
            dispute.resolved_at = datetime.now(timezone.utc)
            
            # Execute resolution
            if resolution_type == DisputeResolution.FULL_PAYMENT_FREELANCER.value:
                deal.status = DealStatus.COMPLETED.value
                message = "Admin decision: Full payment released to freelancer."
                
            elif resolution_type == DisputeResolution.PARTIAL_PAYMENT.value:
                if not resolution_amount:
                    raise DisputeError("Resolution amount required for partial payment")
                deal.status = DealStatus.COMPLETED.value
                message = f"Admin decision: Partial payment of ₹{resolution_amount/100} to freelancer, remaining refunded to business."
                
            elif resolution_type == DisputeResolution.FULL_REFUND_BUSINESS.value:
                deal.status = DealStatus.CANCELLED.value
                message = "Admin decision: Full refund issued to business owner."
                
            else:
                raise DisputeError(f"Invalid resolution type: {resolution_type}")
            
            # Add system message
            system_msg = DisputeMessage(
                id=str(uuid.uuid4()),
                dispute_id=dispute_id,
                sender_id=resolved_by,
                sender_role="system",
                message=f"{message}\n\nReasoning: {resolution_notes or 'No additional notes provided.'}",
                is_system_message="true"
            )
            
            db.add(system_msg)
            db.commit()
            db.refresh(dispute)
            
            logger.info(f"Dispute {dispute_id} resolved: {resolution_type}")
            
            return dispute
            
        except DisputeError:
            raise
        except Exception as e:
            logger.error(f"Error resolving dispute: {str(e)}")
            db.rollback()
            raise DisputeError(f"Failed to resolve dispute: {str(e)}")
    
    @classmethod
    def close_dispute(
        cls,
        db: Session,
        dispute_id: str
    ) -> Dispute:
        """Close a resolved dispute.
        
        Args:
            db: Database session
            dispute_id: Dispute ID
            
        Returns:
            Updated Dispute object
        """
        try:
            dispute = db.query(Dispute).filter(Dispute.id == dispute_id).first()
            if not dispute:
                raise DisputeError(f"Dispute {dispute_id} not found")
            
            if dispute.status != DisputeStatus.RESOLVED.value:
                raise DisputeError("Can only close resolved disputes")
            
            dispute.status = DisputeStatus.CLOSED.value
            dispute.closed_at = datetime.now(timezone.utc)
            
            db.commit()
            db.refresh(dispute)
            
            logger.info(f"Dispute {dispute_id} closed")
            
            return dispute
            
        except Exception as e:
            logger.error(f"Error closing dispute: {str(e)}")
            db.rollback()
            raise DisputeError(f"Failed to close dispute: {str(e)}")
    
    @classmethod
    def get_dispute_details(
        cls,
        db: Session,
        dispute_id: str
    ) -> Dict:
        """Get full dispute details with messages.
        
        Args:
            db: Database session
            dispute_id: Dispute ID
            
        Returns:
            Dict with dispute details and messages
        """
        dispute = db.query(Dispute).filter(Dispute.id == dispute_id).first()
        if not dispute:
            raise DisputeError(f"Dispute {dispute_id} not found")
        
        # Get messages
        messages = []
        for msg in dispute.messages:
            sender = db.query(User).filter(User.id == msg.sender_id).first()
            messages.append({
                "id": msg.id,
                "sender_id": msg.sender_id,
                "sender_name": sender.name if sender else "System",
                "sender_role": msg.sender_role,
                "message": msg.message,
                "is_system_message": msg.is_system_message == "true",
                "created_at": msg.created_at.isoformat()
            })
        
        return {
            "id": dispute.id,
            "deal_id": dispute.deal_id,
            "raised_by": dispute.raised_by,
            "raised_by_role": dispute.raised_by_role,
            "reason": dispute.reason,
            "description": dispute.description,
            "status": dispute.status,
            "resolution_type": dispute.resolution_type,
            "resolution_amount": dispute.resolution_amount,
            "resolution_notes": dispute.resolution_notes,
            "resolved_by": dispute.resolved_by,
            "created_at": dispute.created_at.isoformat(),
            "self_resolution_deadline": dispute.self_resolution_deadline.isoformat(),
            "escalated_at": dispute.escalated_at.isoformat() if dispute.escalated_at else None,
            "resolved_at": dispute.resolved_at.isoformat() if dispute.resolved_at else None,
            "closed_at": dispute.closed_at.isoformat() if dispute.closed_at else None,
            "messages": messages
        }
    
    @classmethod
    def check_and_escalate_expired(
        cls,
        db: Session
    ) -> List[str]:
        """Check for disputes past self-resolution deadline and auto-escalate.
        
        Args:
            db: Database session
            
        Returns:
            List of escalated dispute IDs
        """
        now = datetime.now(timezone.utc)
        
        expired_disputes = db.query(Dispute).filter(
            Dispute.status == DisputeStatus.SELF_RESOLUTION.value,
            Dispute.self_resolution_deadline < now
        ).all()
        
        escalated_ids = []
        for dispute in expired_disputes:
            try:
                cls.escalate_to_admin(db, dispute.id)
                escalated_ids.append(dispute.id)
            except Exception as e:
                logger.error(f"Failed to auto-escalate dispute {dispute.id}: {str(e)}")
        
        return escalated_ids
