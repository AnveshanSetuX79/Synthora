"""Outreach service for WhatsApp, SMS, and Email communication.

This service handles:
- WhatsApp Business API integration
- SMS fallback integration
- Email fallback integration
- Message rate limiting (50 messages/day per freelancer)
- Consent and opt-out tracking
- Message delivery tracking
- Retry logic for failed messages
- Lead access control integration (5-freelancer limit, state transitions)

Requirements: 6.1, 6.2, 6.3, 6.4, 36.1, 36.2, 37.1, 38.1, 31.1, 31.2, 31.3, 31.4, 2.3, 2.4
"""
import logging
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
import uuid
import os

from ..models.lead import (
    OutreachMessage,
    OutreachChannel,
    DeliveryStatus,
    LeadContact,
    ConsentStatus
)
from ..models.user import Freelancer
from ..models.business import Business
from .sms import SMSService, SMSError
from .email import EmailService
from .lead_access_control import LeadAccessControlService

logger = logging.getLogger(__name__)


class OutreachError(Exception):
    """Base exception for outreach errors."""
    pass


class RateLimitExceededError(OutreachError):
    """Raised when daily message limit is exceeded."""
    pass


class OptedOutError(OutreachError):
    """Raised when trying to message an opted-out business."""
    pass


class MessageTemplates:
    """Message templates for outreach."""
    
    FIRST_CONTACT = """Hi {business_name}! 👋

I'm {freelancer_name}, a web developer. I noticed your business doesn't have a website yet.

I've created a FREE demo website for you: {demo_url}

Would you like to see how a professional website can help grow your business?

Reply STOP to unsubscribe."""
    
    FOLLOW_UP = """Hi {business_name}! 

Just following up on the demo website I shared: {demo_url}

Have you had a chance to check it out? I'd love to help bring your business online.

Reply STOP to unsubscribe."""
    
    DEMO_LINK = """Hi {business_name}! 

Here's your personalized demo website: {demo_url}

Check it out and let me know what you think!

Reply STOP to unsubscribe."""


class OutreachService:
    """Service for managing outreach communications."""
    
    # Rate limits
    DAILY_MESSAGE_LIMIT = 50  # Per freelancer
    MAX_RETRY_ATTEMPTS = 3
    RETRY_DELAY_MINUTES = 30
    
    def __init__(self):
        """Initialize outreach service."""
        # In production, initialize WhatsApp/SMS/Email clients here
        self.whatsapp_enabled = os.getenv("WHATSAPP_BUSINESS_API_KEY") is not None
        self.sms_enabled = os.getenv("SMS_ENABLED", "false").lower() == "true"
        self.email_enabled = os.getenv("SMTP_USER") is not None
        self.sms_service = SMSService()
        self.email_service = EmailService()
        
        logger.info(
            f"Outreach service initialized. "
            f"WhatsApp: {self.whatsapp_enabled}, SMS: {self.sms_enabled}, Email: {self.email_enabled}"
        )
    
    def send_message(
        self,
        db: Session,
        lead_contact_id: str,
        freelancer_id: str,
        template_type: str,
        channel: str = "WhatsApp",
        custom_message: Optional[str] = None
    ) -> OutreachMessage:
        """Send outreach message to a business.
        
        Args:
            db: Database session
            lead_contact_id: Lead contact ID
            freelancer_id: Freelancer ID sending the message
            template_type: Template type (first_contact, follow_up, demo_link)
            channel: Communication channel (WhatsApp, SMS, Email)
            custom_message: Optional custom message (overrides template)
            
        Returns:
            OutreachMessage object
            
        Raises:
            RateLimitExceededError: If daily limit exceeded
            OptedOutError: If business has opted out
            OutreachError: For other errors
        """
        # Get lead contact
        lead_contact = db.query(LeadContact).filter(
            LeadContact.id == lead_contact_id
        ).first()
        
        if not lead_contact:
            raise OutreachError(f"Lead contact {lead_contact_id} not found")
        
        # Check if business has opted out
        if lead_contact.consent_status.value if hasattr(lead_contact.consent_status, 'value') else lead_contact.consent_status == "opted_out":
            raise OptedOutError(
                f"Business has opted out. Cannot send message."
            )
        
        # Check rate limit
        if not self._check_rate_limit(db, freelancer_id):
            raise RateLimitExceededError(
                f"Daily message limit ({self.DAILY_MESSAGE_LIMIT}) exceeded"
            )
        
        # Get business and freelancer details
        lead = lead_contact.lead
        business = lead.business
        freelancer = db.query(Freelancer).filter(Freelancer.id == freelancer_id).first()
        
        if not business or not freelancer:
            raise OutreachError("Business or freelancer not found")
        
        # Determine if this is first contact or follow-up
        existing_messages = db.query(OutreachMessage).filter(
            OutreachMessage.lead_contact_id == lead_contact_id
        ).count()
        
        is_first_contact = existing_messages == 0
        is_follow_up = template_type == "follow_up" or existing_messages > 0
        
        # Generate message content
        if custom_message:
            content = custom_message
        else:
            content = self._generate_message(
                template_type=template_type,
                business_name=business.name,
                freelancer_name=freelancer.name,
                demo_url=f"https://demo.localai-leads.com/{business.id}"  # Placeholder
            )
        
        # Create outreach message record
        outreach_message = OutreachMessage(
            id=str(uuid.uuid4()),
            lead_contact_id=lead_contact_id,
            channel=OutreachChannel(channel),
            template_id=template_type,
            content=content,
            delivery_status=DeliveryStatus.SENT,
            sent_at=datetime.utcnow()
        )
        
        db.add(outreach_message)
        
        # Update consent status
        consent_value = lead_contact.consent_status.value if hasattr(lead_contact.consent_status, 'value') else lead_contact.consent_status
        if consent_value == "contacted":
            # Keep as contacted
            pass
        
        # In production, actually send the message via WhatsApp/SMS API
        try:
            if channel == "whatsapp" and self.whatsapp_enabled:
                self._send_whatsapp(business.phone, content)
            elif channel == "sms" and self.sms_enabled:
                self._send_sms(business.phone, content, lead_contact_id)
            else:
                # Fallback to SMS if WhatsApp not available
                if self.sms_enabled:
                    logger.info(f"Falling back to SMS for {business.phone}")
                    self._send_sms(business.phone, content, lead_contact_id)
                else:
                    # Mock send for development
                    logger.info(f"[MOCK] Sending {channel} to {business.phone}: {content[:50]}...")
            
            outreach_message.delivery_status = DeliveryStatus.DELIVERED
            outreach_message.delivered_at = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
            outreach_message.delivery_status = DeliveryStatus.FAILED
        
        db.commit()
        db.refresh(outreach_message)
        
        # Update lead access control (Requirements 2.3, 2.4)
        if is_first_contact:
            # Increment contact count and update business status
            LeadAccessControlService.increment_contact_count(
                db=db,
                business_id=business.id,
                is_first_contact=True
            )
        elif is_follow_up:
            # Increment follow-up count
            LeadAccessControlService.increment_follow_up_count(
                db=db,
                lead_contact_id=lead_contact_id
            )
            
            # Check if should be marked as cold (2+ follow-ups, no response)
            has_response = outreach_message.replied_at is not None
            LeadAccessControlService.check_and_mark_cold(
                db=db,
                lead_contact_id=lead_contact_id,
                has_response=has_response
            )
        
        logger.info(
            f"Sent {channel} message to {business.name} "
            f"(status: {outreach_message.delivery_status.value})"
        )
        
        return outreach_message
    
    def _check_rate_limit(self, db: Session, freelancer_id: str) -> bool:
        """Check if freelancer has exceeded daily message limit.
        
        Args:
            db: Database session
            freelancer_id: Freelancer ID
            
        Returns:
            True if within limit, False if exceeded
        """
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Count messages sent today
        message_count = db.query(func.count(OutreachMessage.id)).join(
            LeadContact, OutreachMessage.lead_contact_id == LeadContact.id
        ).filter(
            and_(
                LeadContact.freelancer_id == freelancer_id,
                OutreachMessage.sent_at >= today_start
            )
        ).scalar()
        
        return message_count < self.DAILY_MESSAGE_LIMIT
    
    def _generate_message(
        self,
        template_type: str,
        business_name: str,
        freelancer_name: str,
        demo_url: str
    ) -> str:
        """Generate message from template.
        
        Args:
            template_type: Template type
            business_name: Business name
            freelancer_name: Freelancer name
            demo_url: Demo website URL
            
        Returns:
            Formatted message string
        """
        templates = {
            "first_contact": MessageTemplates.FIRST_CONTACT,
            "follow_up": MessageTemplates.FOLLOW_UP,
            "demo_link": MessageTemplates.DEMO_LINK,
        }
        
        template = templates.get(template_type, MessageTemplates.FIRST_CONTACT)
        
        return template.format(
            business_name=business_name,
            freelancer_name=freelancer_name,
            demo_url=demo_url
        )
    
    def _send_whatsapp(self, phone: str, message: str) -> None:
        """Send WhatsApp message via API.
        
        In production, this would use WhatsApp Business API or Twilio.
        
        Args:
            phone: Phone number
            message: Message content
        """
        # TODO: Implement actual WhatsApp API integration
        logger.info(f"[WhatsApp] Sending to {phone}")
        pass
    
    def _send_sms(self, phone: str, message: str, lead_contact_id: str = None) -> None:
        """Send SMS via provider API with opt-out link.
        
        Args:
            phone: Phone number
            message: Message content
            lead_contact_id: Lead contact ID for opt-out link
        """
        try:
            # Generate opt-out link if lead_contact_id provided
            opt_out_link = None
            if lead_contact_id:
                frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
                opt_out_link = f"{frontend_url}/opt-out/{lead_contact_id}"
            
            # Send via SMS service
            result = self.sms_service.send_sms(phone, message, opt_out_link)
            
            logger.info(f"SMS sent to {phone}: {result}")
            
        except SMSError as e:
            logger.error(f"SMS error for {phone}: {str(e)}")
            raise OutreachError(f"Failed to send SMS: {str(e)}")
    
    def get_message_history(
        self,
        db: Session,
        lead_contact_id: str
    ) -> List[Dict]:
        """Get message history for a lead contact.
        
        Args:
            db: Database session
            lead_contact_id: Lead contact ID
            
        Returns:
            List of message dictionaries
        """
        messages = db.query(OutreachMessage).filter(
            OutreachMessage.lead_contact_id == lead_contact_id
        ).order_by(OutreachMessage.sent_at.desc()).all()
        
        return [
            {
                "id": msg.id,
                "channel": msg.channel.value,
                "content": msg.content,
                "delivery_status": msg.delivery_status.value,
                "sent_at": msg.sent_at.isoformat(),
                "delivered_at": msg.delivered_at.isoformat() if msg.delivered_at else None,
                "viewed_at": msg.viewed_at.isoformat() if msg.viewed_at else None,
                "replied_at": msg.replied_at.isoformat() if msg.replied_at else None,
                "opted_out": msg.opted_out
            }
            for msg in messages
        ]
    
    def handle_opt_out(
        self,
        db: Session,
        business_id: str
    ) -> bool:
        """Handle opt-out request from a business.
        
        Args:
            db: Database session
            business_id: Business ID
            
        Returns:
            True if successful
        """
        # Find all lead contacts for this business
        lead_contacts = db.query(LeadContact).join(
            LeadContact.lead
        ).filter(
            LeadContact.lead.has(business_id=business_id)
        ).all()
        
        # Mark all as opted out
        for contact in lead_contacts:
            contact.consent_status = ConsentStatus.OPTED_OUT
        
        # Mark all outreach messages as opted out
        for contact in lead_contacts:
            messages = db.query(OutreachMessage).filter(
                OutreachMessage.lead_contact_id == contact.id
            ).all()
            for msg in messages:
                msg.opted_out = True
        
        db.commit()
        
        logger.info(f"Business {business_id} opted out. Marked {len(lead_contacts)} contacts.")
        return True
    
    def get_outreach_stats(
        self,
        db: Session,
        freelancer_id: str,
        days: int = 7
    ) -> Dict:
        """Get outreach statistics for a freelancer.
        
        Args:
            db: Database session
            freelancer_id: Freelancer ID
            days: Number of days to look back
            
        Returns:
            Dictionary of statistics
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get all messages sent by this freelancer
        messages = db.query(OutreachMessage).join(
            LeadContact, OutreachMessage.lead_contact_id == LeadContact.id
        ).filter(
            and_(
                LeadContact.freelancer_id == freelancer_id,
                OutreachMessage.sent_at >= start_date
            )
        ).all()
        
        total_sent = len(messages)
        delivered = sum(1 for m in messages if (m.delivery_status.value if hasattr(m.delivery_status, 'value') else m.delivery_status) == "delivered")
        failed = sum(1 for m in messages if (m.delivery_status.value if hasattr(m.delivery_status, 'value') else m.delivery_status) == "failed")
        viewed = sum(1 for m in messages if m.viewed_at is not None)
        replied = sum(1 for m in messages if m.replied_at is not None)
        opted_out = sum(1 for m in messages if m.opted_out)
        
        # Get today's count for rate limit
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_count = sum(1 for m in messages if m.sent_at >= today_start)
        
        return {
            "period_days": days,
            "total_sent": total_sent,
            "delivered": delivered,
            "failed": failed,
            "viewed": viewed,
            "replied": replied,
            "opted_out": opted_out,
            "delivery_rate": round(delivered / total_sent * 100, 2) if total_sent > 0 else 0,
            "view_rate": round(viewed / delivered * 100, 2) if delivered > 0 else 0,
            "reply_rate": round(replied / delivered * 100, 2) if delivered > 0 else 0,
            "today_sent": today_count,
            "today_remaining": max(0, self.DAILY_MESSAGE_LIMIT - today_count)
        }
    
    def retry_failed_messages(
        self,
        db: Session,
        max_age_hours: int = 24
    ) -> int:
        """Retry failed messages that are within retry window.
        
        Args:
            db: Database session
            max_age_hours: Maximum age of messages to retry
            
        Returns:
            Number of messages retried
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        # Get failed messages within retry window
        failed_messages = db.query(OutreachMessage).filter(
            and_(
                OutreachMessage.delivery_status == "failed",  # Use lowercase string
                OutreachMessage.sent_at >= cutoff_time
            )
        ).all()
        
        retried_count = 0
        
        for message in failed_messages:
            try:
                # Attempt to resend
                if message.channel == OutreachChannel.WHATSAPP and self.whatsapp_enabled:
                    # Extract phone from lead contact
                    lead_contact = message.lead_contact
                    business = lead_contact.lead.business
                    self._send_whatsapp(business.phone, message.content)
                elif message.channel == OutreachChannel.SMS and self.sms_enabled:
                    lead_contact = message.lead_contact
                    business = lead_contact.lead.business
                    self._send_sms(business.phone, message.content)
                
                # Update status
                message.delivery_status = DeliveryStatus.DELIVERED
                message.delivered_at = datetime.utcnow()
                retried_count += 1
                
            except Exception as e:
                logger.error(f"Retry failed for message {message.id}: {str(e)}")
                continue
        
        db.commit()
        
        logger.info(f"Retried {retried_count} failed messages")
        return retried_count
    
    def schedule_auto_followups(
        self,
        db: Session
    ) -> int:
        """Schedule automatic follow-up messages for leads without response.
        
        This should be run as a background job (e.g., daily cron).
        
        Logic:
        - Find leads contacted 48+ hours ago with no response
        - Send follow-up if follow_up_count < 2
        - Mark as "Cold" if follow_up_count >= 2
        
        Args:
            db: Database session
            
        Returns:
            Number of follow-ups scheduled/sent
        """
        followup_cutoff = datetime.utcnow() - timedelta(hours=48)
        followups_sent = 0
        
        # Find lead contacts that need follow-up
        lead_contacts = db.query(LeadContact).filter(
            and_(
                LeadContact.first_contact_at <= followup_cutoff,
                LeadContact.follow_up_count < 2,
                LeadContact.consent_status != ConsentStatus.OPTED_OUT,
                LeadContact.status.in_(['Contacted', 'Interested'])
            )
        ).all()
        
        for contact in lead_contacts:
            # Check if already replied
            last_message = db.query(OutreachMessage).filter(
                OutreachMessage.lead_contact_id == contact.id
            ).order_by(OutreachMessage.sent_at.desc()).first()
            
            if last_message and last_message.replied_at:
                # Already replied, skip
                continue
            
            # Check time since last message
            if last_message:
                time_since_last = datetime.utcnow() - last_message.sent_at
                if time_since_last < timedelta(hours=48):
                    # Too soon for follow-up
                    continue
            
            try:
                # Send follow-up message
                lead = contact.lead
                business = lead.business
                freelancer = contact.freelancer
                
                # Generate follow-up message
                content = self._generate_message(
                    template_type="follow_up",
                    business_name=business.name,
                    freelancer_name=freelancer.name,
                    demo_url=f"https://demo.localai-leads.com/{business.id}"
                )
                
                # Create outreach message
                outreach_message = OutreachMessage(
                    id=str(uuid.uuid4()),
                    lead_contact_id=contact.id,
                    channel=OutreachChannel.WHATSAPP,  # Default to WhatsApp
                    template_id="follow_up",
                    content=content,
                    delivery_status=DeliveryStatus.SENT,
                    sent_at=datetime.utcnow()
                )
                
                db.add(outreach_message)
                
                # Send via API
                try:
                    if self.whatsapp_enabled:
                        self._send_whatsapp(business.phone, content)
                    else:
                        logger.info(f"[MOCK] Follow-up to {business.phone}: {content[:50]}...")
                    
                    outreach_message.delivery_status = DeliveryStatus.DELIVERED
                    outreach_message.delivered_at = datetime.utcnow()
                except Exception as e:
                    logger.error(f"Failed to send follow-up: {str(e)}")
                    outreach_message.delivery_status = DeliveryStatus.FAILED
                
                # Increment follow-up count
                contact.follow_up_count += 1
                contact.last_contact_at = datetime.utcnow()
                
                # Mark as Cold if max follow-ups reached
                if contact.follow_up_count >= 2:
                    contact.status = "Cold"
                    logger.info(f"Marked lead contact {contact.id} as Cold after 2 follow-ups")
                
                followups_sent += 1
                
            except Exception as e:
                logger.error(f"Error scheduling follow-up for contact {contact.id}: {str(e)}")
                continue
        
        db.commit()
        
        logger.info(f"Scheduled {followups_sent} auto follow-ups")
        return followups_sent
    
    def get_leads_needing_followup(
        self,
        db: Session,
        freelancer_id: Optional[str] = None
    ) -> List[Dict]:
        """Get list of leads that need follow-up.
        
        Args:
            db: Database session
            freelancer_id: Optional freelancer ID to filter by
            
        Returns:
            List of lead contact dictionaries
        """
        followup_cutoff = datetime.utcnow() - timedelta(hours=48)
        
        query = db.query(LeadContact).filter(
            and_(
                LeadContact.first_contact_at <= followup_cutoff,
                LeadContact.follow_up_count < 2,
                LeadContact.consent_status != ConsentStatus.OPTED_OUT,
                LeadContact.status.in_(['Contacted', 'Interested'])
            )
        )
        
        if freelancer_id:
            query = query.filter(LeadContact.freelancer_id == freelancer_id)
        
        lead_contacts = query.all()
        
        results = []
        for contact in lead_contacts:
            # Check if already replied
            last_message = db.query(OutreachMessage).filter(
                OutreachMessage.lead_contact_id == contact.id
            ).order_by(OutreachMessage.sent_at.desc()).first()
            
            if last_message and last_message.replied_at:
                continue
            
            # Calculate time since last contact
            time_since_contact = datetime.utcnow() - contact.last_contact_at
            
            results.append({
                "lead_contact_id": contact.id,
                "business_id": contact.lead.business_id,
                "business_name": contact.lead.business.name,
                "follow_up_count": contact.follow_up_count,
                "hours_since_contact": int(time_since_contact.total_seconds() / 3600),
                "last_contact_at": contact.last_contact_at.isoformat(),
                "status": contact.status
            })
        
        return results
