"""Outreach API endpoints for messaging businesses."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
import logging

from ..database import get_db
from ..middleware.auth import get_current_user
from ..services.outreach import (
    OutreachService,
    RateLimitExceededError,
    OptedOutError,
    OutreachError
)
from ..services.whatsapp import WhatsAppService
from ..models.user import Freelancer
from ..models.lead import LeadContact
from ..models.business import Business
from ..models.demo import DemoWebsite

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/outreach", tags=["outreach"])


# Request/Response Schemas

class GenerateWhatsAppLinkRequest(BaseModel):
    """Request schema for generating WhatsApp link."""
    lead_contact_id: str
    template_type: str = "first_contact"  # first_contact, follow_up


class GenerateWhatsAppLinkResponse(BaseModel):
    """Response schema for WhatsApp link generation."""
    success: bool
    whatsapp_link: str
    phone: str
    message_preview: str
    instructions: str

class SendMessageRequest(BaseModel):
    """Request schema for sending a message."""
    lead_contact_id: str
    template_type: str = "first_contact"  # first_contact, follow_up, demo_link
    channel: str = "WhatsApp"  # WhatsApp, SMS, Email
    custom_message: Optional[str] = None


class SendMessageResponse(BaseModel):
    """Response schema for sending a message."""
    success: bool
    message_id: str
    delivery_status: str
    sent_at: str
    message: str


class MessageHistoryResponse(BaseModel):
    """Response schema for message history."""
    success: bool
    lead_contact_id: str
    total_messages: int
    messages: list


class OptOutRequest(BaseModel):
    """Request schema for opt-out."""
    business_id: str


class OptOutResponse(BaseModel):
    """Response schema for opt-out."""
    success: bool
    message: str


class OutreachStatsResponse(BaseModel):
    """Response schema for outreach stats."""
    success: bool
    stats: dict


# API Endpoints

@router.post("/send", response_model=SendMessageResponse)
async def send_message(
    request: SendMessageRequest = Body(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send outreach message to a business.
    
    This endpoint:
    1. Checks rate limits (50 messages/day per freelancer)
    2. Checks if business has opted out
    3. Sends message via WhatsApp or SMS
    4. Tracks delivery status
    
    **Requirements**: 6.1, 36.1
    
    Args:
        request: Message details (lead_contact_id, template_type, channel)
        current_user: Authenticated user from JWT
        
    Returns:
        Message sent confirmation with delivery status
        
    Raises:
        400: Rate limit exceeded or business opted out
        403: User is not a freelancer
        404: Lead contact not found
    """
    try:
        # Verify user is a freelancer
        if current_user.get("role") != "freelancer":
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "FORBIDDEN",
                    "message": "Only freelancers can send outreach messages"
                }
            )
        
        # Get freelancer
        user_id = current_user.get("user_id")
        freelancer = db.query(Freelancer).filter(Freelancer.user_id == user_id).first()
        
        if not freelancer:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "NOT_FOUND",
                    "message": "Freelancer profile not found"
                }
            )
        
        # Send message
        outreach_service = OutreachService()
        outreach_message = outreach_service.send_message(
            db=db,
            lead_contact_id=request.lead_contact_id,
            freelancer_id=freelancer.id,
            template_type=request.template_type,
            channel=request.channel,
            custom_message=request.custom_message
        )
        
        return SendMessageResponse(
            success=True,
            message_id=outreach_message.id,
            delivery_status=outreach_message.delivery_status.value,
            sent_at=outreach_message.sent_at.isoformat(),
            message=f"Message sent successfully via {request.channel}"
        )
        
    except RateLimitExceededError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "RATE_LIMIT_EXCEEDED",
                "message": str(e)
            }
        )
    except OptedOutError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "OPTED_OUT",
                "message": str(e)
            }
        )
    except OutreachError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "OUTREACH_ERROR",
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": str(e)
            }
        )


@router.get("/history/{lead_contact_id}", response_model=MessageHistoryResponse)
async def get_message_history(
    lead_contact_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get message history for a lead contact.
    
    **Requirements**: 6.1
    
    Args:
        lead_contact_id: Lead contact ID
        current_user: Authenticated user from JWT
        
    Returns:
        List of messages sent to this lead
        
    Raises:
        403: User is not a freelancer or doesn't own this lead contact
        404: Lead contact not found
    """
    try:
        # Verify user is a freelancer
        if current_user.get("role") != "freelancer":
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "FORBIDDEN",
                    "message": "Only freelancers can access message history"
                }
            )
        
        # Get freelancer
        user_id = current_user.get("user_id")
        freelancer = db.query(Freelancer).filter(Freelancer.user_id == user_id).first()
        
        if not freelancer:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "NOT_FOUND",
                    "message": "Freelancer profile not found"
                }
            )
        
        # Verify lead contact belongs to this freelancer
        lead_contact = db.query(LeadContact).filter(
            LeadContact.id == lead_contact_id
        ).first()
        
        if not lead_contact:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "NOT_FOUND",
                    "message": "Lead contact not found"
                }
            )
        
        if lead_contact.freelancer_id != freelancer.id:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "FORBIDDEN",
                    "message": "You don't have access to this lead contact"
                }
            )
        
        # Get message history
        outreach_service = OutreachService()
        messages = outreach_service.get_message_history(db, lead_contact_id)
        
        return MessageHistoryResponse(
            success=True,
            lead_contact_id=lead_contact_id,
            total_messages=len(messages),
            messages=messages
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting message history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": str(e)
            }
        )


@router.post("/opt-out", response_model=OptOutResponse)
async def handle_opt_out(
    request: OptOutRequest = Body(...),
    db: Session = Depends(get_db)
):
    """Handle opt-out request from a business.
    
    This endpoint marks a business as opted out and prevents
    all future outreach messages.
    
    **Requirements**: 31.1, 31.2, 31.3, 31.4, 36.3
    
    Args:
        request: Business ID to opt out
        
    Returns:
        Opt-out confirmation
    """
    try:
        outreach_service = OutreachService()
        success = outreach_service.handle_opt_out(db, request.business_id)
        
        if success:
            return OptOutResponse(
                success=True,
                message=f"Business {request.business_id} has been opted out successfully"
            )
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "OPT_OUT_FAILED",
                    "message": "Failed to process opt-out request"
                }
            )
        
    except Exception as e:
        logger.error(f"Error handling opt-out: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": str(e)
            }
        )


@router.get("/stats", response_model=OutreachStatsResponse)
async def get_outreach_stats(
    days: int = Query(7, ge=1, le=90, description="Number of days to look back"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get outreach statistics for current freelancer.
    
    Returns metrics including:
    - Total messages sent
    - Delivery rate
    - View rate
    - Reply rate
    - Today's remaining quota
    
    **Requirements**: 36.1
    
    Args:
        days: Number of days to look back (default: 7)
        current_user: Authenticated user from JWT
        
    Returns:
        Outreach statistics
        
    Raises:
        403: User is not a freelancer
        404: Freelancer profile not found
    """
    try:
        # Verify user is a freelancer
        if current_user.get("role") != "freelancer":
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "FORBIDDEN",
                    "message": "Only freelancers can access outreach stats"
                }
            )
        
        # Get freelancer
        user_id = current_user.get("user_id")
        freelancer = db.query(Freelancer).filter(Freelancer.user_id == user_id).first()
        
        if not freelancer:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "NOT_FOUND",
                    "message": "Freelancer profile not found"
                }
            )
        
        # Get stats
        outreach_service = OutreachService()
        stats = outreach_service.get_outreach_stats(db, freelancer.id, days)
        
        return OutreachStatsResponse(
            success=True,
            stats=stats
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting outreach stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": str(e)
            }
        )


@router.post("/schedule-followups")
async def schedule_auto_followups(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Schedule automatic follow-up messages for leads without response.
    
    This endpoint triggers the auto follow-up system which:
    - Finds leads contacted 48+ hours ago with no response
    - Sends follow-up if follow_up_count < 2
    - Marks as "Cold" if follow_up_count >= 2
    
    Can be called manually or via cron job.
    
    **Requirements**: 35.1, 35.2, 35.3
    
    Args:
        current_user: Authenticated user from JWT
        
    Returns:
        Number of follow-ups scheduled/sent
        
    Raises:
        403: User is not authorized (admin or freelancer only)
    """
    try:
        # Only allow freelancers and admins to trigger follow-ups
        user_role = current_user.get("role")
        if user_role not in ["freelancer", "admin"]:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "FORBIDDEN",
                    "message": "Only freelancers and admins can schedule follow-ups"
                }
            )
        
        # Schedule follow-ups
        outreach_service = OutreachService()
        followups_sent = outreach_service.schedule_auto_followups(db)
        
        return {
            "success": True,
            "followups_sent": followups_sent,
            "message": f"Scheduled {followups_sent} auto follow-ups"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scheduling follow-ups: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": str(e)
            }
        )


@router.get("/leads-needing-followup")
async def get_leads_needing_followup(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of leads that need follow-up.
    
    Returns leads that:
    - Were contacted 48+ hours ago
    - Have not replied
    - Have follow_up_count < 2
    - Are not opted out
    
    **Requirements**: 35.1, 35.2
    
    Args:
        current_user: Authenticated user from JWT
        
    Returns:
        List of leads needing follow-up
        
    Raises:
        403: User is not a freelancer
        404: Freelancer profile not found
    """
    try:
        # Verify user is a freelancer
        if current_user.get("role") != "freelancer":
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "FORBIDDEN",
                    "message": "Only freelancers can access this endpoint"
                }
            )
        
        # Get freelancer
        user_id = current_user.get("user_id")
        freelancer = db.query(Freelancer).filter(Freelancer.user_id == user_id).first()
        
        if not freelancer:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "NOT_FOUND",
                    "message": "Freelancer profile not found"
                }
            )
        
        # Get leads needing follow-up
        outreach_service = OutreachService()
        leads = outreach_service.get_leads_needing_followup(db, freelancer.id)
        
        return {
            "success": True,
            "total": len(leads),
            "leads": leads
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting leads needing follow-up: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": str(e)
            }
        )



# WhatsApp MVP Endpoints

@router.post("/whatsapp/generate-link")
async def generate_whatsapp_link(
    lead_contact_id: str = Body(..., embed=True),
    template_type: str = Body("first_contact", embed=True),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate WhatsApp wa.me link for manual sending (MVP approach).
    
    This is the FREE, instant way to send demo links:
    1. Generates wa.me link with pre-filled message
    2. Freelancer clicks link
    3. Opens WhatsApp with message ready
    4. Freelancer clicks "Send"
    
    Benefits:
    - FREE (no SMS costs)
    - 10x better open rates than SMS
    - No TRAI DLT registration needed
    - Instant setup
    - Perfect for MVP
    
    **Requirements**: 6.1, 36.1
    
    Args:
        lead_contact_id: Lead contact ID
        template_type: Message template (first_contact or follow_up)
        current_user: Authenticated user from JWT
        
    Returns:
        WhatsApp link and instructions
        
    Raises:
        403: User is not a freelancer
        404: Lead contact or business not found
    """
    try:
        # Verify user is a freelancer
        if current_user.get("role") != "freelancer":
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "FORBIDDEN",
                    "message": "Only freelancers can generate WhatsApp links"
                }
            )
        
        # Get freelancer
        user_id = current_user.get("user_id")
        freelancer = db.query(Freelancer).filter(Freelancer.user_id == user_id).first()
        
        if not freelancer:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "NOT_FOUND",
                    "message": "Freelancer profile not found"
                }
            )
        
        # Get lead contact
        lead_contact = db.query(LeadContact).filter(
            LeadContact.id == lead_contact_id
        ).first()
        
        if not lead_contact:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "NOT_FOUND",
                    "message": "Lead contact not found"
                }
            )
        
        # Verify ownership
        if lead_contact.freelancer_id != freelancer.id:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "FORBIDDEN",
                    "message": "You don't have access to this lead contact"
                }
            )
        
        # Get business details
        from ..models.lead import Lead
        from ..models.business import Business
        from ..models.demo import DemoWebsite
        from ..services.whatsapp import WhatsAppService
        
        lead = db.query(Lead).filter(Lead.id == lead_contact.lead_id).first()
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        business = db.query(Business).filter(Business.id == lead.business_id).first()
        if not business or not business.phone:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "NO_PHONE",
                    "message": "Business phone number not available"
                }
            )
        
        # Get demo website URL
        demo = db.query(DemoWebsite).filter(
            DemoWebsite.business_id == business.id
        ).first()
        
        demo_url = None
        if demo:
            # Use SEO-friendly URL if available
            if demo.slug:
                demo_url = f"https://yourdomain.com/api/demos/view/{demo.slug}"
            else:
                demo_url = f"https://yourdomain.com/api/demos/public/{demo.id}"
        else:
            demo_url = "https://yourdomain.com/demo"
        
        # Generate WhatsApp message
        whatsapp_service = WhatsAppService()
        
        if template_type == "first_contact":
            message = whatsapp_service.create_demo_message(
                business_name=business.name,
                freelancer_name=freelancer.name,
                demo_url=demo_url,
                business_category=business.category
            )
        else:  # follow_up
            message = whatsapp_service.create_follow_up_message(
                business_name=business.name,
                freelancer_name=freelancer.name,
                demo_url=demo_url
            )
        
        # Generate WhatsApp link
        whatsapp_link = whatsapp_service.generate_whatsapp_link(
            phone=business.phone,
            message=message
        )
        
        logger.info(
            f"✅ Generated WhatsApp link for freelancer {freelancer.id} "
            f"to contact business {business.id}"
        )
        
        return {
            "success": True,
            "whatsapp_link": whatsapp_link,
            "phone": business.phone,
            "business_name": business.name,
            "message_preview": message[:150] + "..." if len(message) > 150 else message,
            "full_message": message,
            "instructions": "Click the link to open WhatsApp. The message is pre-filled - just click Send!",
            "mode": "mvp",
            "cost": "FREE"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating WhatsApp link: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": str(e)
            }
        )
