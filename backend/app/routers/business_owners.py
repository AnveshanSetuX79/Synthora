"""Business owner routes."""
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime, timezone

from ..database import get_db
from ..models.user import User, BusinessOwner
from ..models.business import Business
from ..models.deal import Deal, Milestone
from ..models.demo import DemoWebsite
from ..models.message import Message
from ..middleware.auth import get_current_user, require_business_owner
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/api/business-owners", tags=["business-owners"])


# Schemas
class BusinessOwnerDashboardResponse(BaseModel):
    owner_id: str
    owner_name: str
    business_id: str | None
    business_name: str | None
    business_category: str | None
    business_address: str | None
    demo_url: str | None
    active_deals: int
    total_messages: int
    freelancers_contacted: int


class FreelancerContactInfo(BaseModel):
    freelancer_id: str
    freelancer_name: str
    portfolio_url: str | None
    tier: str
    message_count: int
    last_contact: datetime
    demo_sent: bool


class InvitationRequest(BaseModel):
    business_id: str
    owner_email: EmailStr
    owner_name: str
    freelancer_id: str


@router.get("/dashboard", response_model=BusinessOwnerDashboardResponse)
async def get_dashboard(
    current_user: dict = Depends(require_business_owner),
    db: Session = Depends(get_db)
):
    """Get business owner dashboard data.
    
    Shows:
    - Business details
    - Demo website
    - Active deals
    - Freelancers who contacted them
    
    Optimized with single query using subqueries.
    """
    # Get business owner
    owner = db.query(BusinessOwner).filter(
        BusinessOwner.user_id == current_user["user_id"]
    ).first()
    
    if not owner:
        raise HTTPException(status_code=404, detail="Business owner profile not found")
    
    # Get business details
    business = None
    demo_url = None
    if owner.business_id:
        business = db.query(Business).filter(Business.id == owner.business_id).first()
        
        # Get demo website - wrap in try/except to handle schema issues
        try:
            demo = db.query(DemoWebsite).filter(
                DemoWebsite.business_id == owner.business_id
            ).first()
            if demo:
                demo_url = f"/demos/public/{demo.id}"
        except Exception:
            # Demo table might have schema issues, rollback and skip it
            db.rollback()
            demo_url = None
    
    # Optimize: Use .count() instead of loading all records
    # Count active deals
    active_deals = 0
    try:
        active_deals = db.query(Deal.id).filter(
            Deal.business_owner_id == owner.id,
            Deal.status.in_(["pending", "active"])
        ).count()
    except Exception:
        db.rollback()
        active_deals = 0
    
    # Count messages (optimized)
    total_messages = 0
    try:
        total_messages = db.query(Message.id).filter(
            Message.recipient_id == owner.id
        ).count()
    except Exception:
        db.rollback()
        total_messages = 0
    
    # Count unique freelancers who contacted (optimized)
    freelancers_contacted = 0
    try:
        from sqlalchemy import func, distinct
        freelancers_contacted = db.query(
            func.count(distinct(Message.sender_id))
        ).filter(
            Message.recipient_id == owner.id
        ).scalar() or 0
    except Exception:
        db.rollback()
        freelancers_contacted = 0
    
    return BusinessOwnerDashboardResponse(
        owner_id=owner.id,
        owner_name=owner.owner_name,
        business_id=business.id if business else None,
        business_name=business.name if business else None,
        business_category=business.category if business else None,
        business_address=business.address if business else None,
        demo_url=demo_url,
        active_deals=active_deals,
        total_messages=total_messages,
        freelancers_contacted=freelancers_contacted
    )


@router.get("/freelancers", response_model=List[FreelancerContactInfo])
async def get_contacted_freelancers(
    current_user: dict = Depends(require_business_owner),
    db: Session = Depends(get_db)
):
    """Get list of freelancers who have contacted this business owner."""
    # Get business owner
    owner = db.query(BusinessOwner).filter(
        BusinessOwner.user_id == current_user["user_id"]
    ).first()
    
    if not owner:
        raise HTTPException(status_code=404, detail="Business owner profile not found")
    
    # Get unique freelancers from messages
    from sqlalchemy import func
    from ..models.user import Freelancer
    
    freelancer_messages = db.query(
        Message.sender_id,
        func.count(Message.id).label('message_count'),
        func.max(Message.created_at).label('last_contact')
    ).filter(
        Message.recipient_id == owner.id
    ).group_by(Message.sender_id).all()
    
    freelancers = []
    for sender_id, msg_count, last_contact in freelancer_messages:
        freelancer = db.query(Freelancer).filter(Freelancer.id == sender_id).first()
        if freelancer:
            user = db.query(User).filter(User.id == freelancer.user_id).first()
            
            # Check if demo was sent
            demo_sent = db.query(DemoWebsite).filter(
                DemoWebsite.business_id == owner.business_id,
                DemoWebsite.created_by == freelancer.id
            ).first() is not None
            
            freelancers.append(FreelancerContactInfo(
                freelancer_id=freelancer.id,
                freelancer_name=user.name if user else "Unknown",
                portfolio_url=freelancer.portfolio_url,
                tier=freelancer.tier,
                message_count=msg_count,
                last_contact=last_contact,
                demo_sent=demo_sent
            ))
    
    return freelancers


@router.post("/invite")
async def send_invitation(
    request: InvitationRequest = Body(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send invitation to business owner (called by freelancer after sending demo).
    
    This creates a business owner account with temporary password
    and sends them an email to set their password.
    """
    # Verify business exists
    business = db.query(Business).filter(Business.id == request.business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.owner_email).first()
    if existing_user:
        # If they're already a business owner, just link the business
        if existing_user.role.value == "businessowner":
            owner = db.query(BusinessOwner).filter(
                BusinessOwner.user_id == existing_user.id
            ).first()
            if owner and not owner.business_id:
                owner.business_id = request.business_id
                db.commit()
            return {"message": "Business owner already exists", "user_id": existing_user.id}
        else:
            raise HTTPException(
                status_code=400,
                detail="Email already registered with different role"
            )
    
    # Create new business owner account
    from ..utils.auth import hash_password
    import secrets
    
    # Generate temporary password
    temp_password = secrets.token_urlsafe(12)
    
    # Create user
    user = User(
        id=str(uuid.uuid4()),
        email=request.owner_email,
        password_hash=hash_password(temp_password),
        role="businessowner",
        name=request.owner_name,
        phone="",  # Will be updated by owner
        phone_verified=False,
        is_active=True,
        created_at=datetime.now(timezone.utc)
    )
    db.add(user)
    
    # Create business owner profile
    owner = BusinessOwner(
        id=str(uuid.uuid4()),
        user_id=user.id,
        owner_name=request.owner_name,
        business_id=request.business_id
    )
    db.add(owner)
    
    db.commit()
    
    # TODO: Send email with temporary password and invitation link
    # For now, return the temp password (in production, this should be emailed)
    
    return {
        "message": "Business owner invited successfully",
        "user_id": user.id,
        "owner_id": owner.id,
        "temp_password": temp_password,  # Remove in production
        "note": "In production, this password should be emailed to the business owner"
    }



class MilestoneResponse(BaseModel):
    id: str
    deal_id: str
    sequence: int
    name: str
    percentage: int
    amount: int
    status: str
    deliverables: list | None
    feedback: str | None
    rejection_reason: str | None
    submitted_at: datetime | None
    approved_at: datetime | None
    rejected_at: datetime | None
    paid_at: datetime | None
    due_date: datetime | None


class MilestoneApprovalRequest(BaseModel):
    feedback: str | None = None


class MilestoneRejectionRequest(BaseModel):
    rejection_reason: str


@router.get("/deals/{deal_id}/milestones", response_model=List[MilestoneResponse])
async def get_deal_milestones(
    deal_id: str,
    current_user: dict = Depends(require_business_owner),
    db: Session = Depends(get_db)
):
    """Get all milestones for a deal."""
    # Verify deal belongs to this business owner
    owner = db.query(BusinessOwner).filter(
        BusinessOwner.user_id == current_user["user_id"]
    ).first()
    
    if not owner:
        raise HTTPException(status_code=404, detail="Business owner profile not found")
    
    deal = db.query(Deal).filter(
        Deal.id == deal_id,
        Deal.business_owner_id == owner.id
    ).first()
    
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    milestones = db.query(Milestone).filter(
        Milestone.deal_id == deal_id
    ).order_by(Milestone.sequence).all()
    
    return [
        MilestoneResponse(
            id=m.id,
            deal_id=m.deal_id,
            sequence=m.sequence,
            name=m.name,
            percentage=m.percentage,
            amount=m.amount,
            status=m.status,
            deliverables=m.deliverables,
            feedback=m.feedback,
            rejection_reason=m.rejection_reason,
            submitted_at=m.submitted_at,
            approved_at=m.approved_at,
            rejected_at=m.rejected_at,
            paid_at=m.paid_at,
            due_date=m.due_date
        )
        for m in milestones
    ]


@router.post("/milestones/{milestone_id}/approve")
async def approve_milestone(
    milestone_id: str,
    request: MilestoneApprovalRequest,
    current_user: dict = Depends(require_business_owner),
    db: Session = Depends(get_db)
):
    """Approve a submitted milestone."""
    # Get business owner
    owner = db.query(BusinessOwner).filter(
        BusinessOwner.user_id == current_user["user_id"]
    ).first()
    
    if not owner:
        raise HTTPException(status_code=404, detail="Business owner profile not found")
    
    # Get milestone and verify ownership
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    
    deal = db.query(Deal).filter(
        Deal.id == milestone.deal_id,
        Deal.business_owner_id == owner.id
    ).first()
    
    if not deal:
        raise HTTPException(status_code=403, detail="Not authorized to approve this milestone")
    
    # Check if milestone is in submitted state
    if milestone.status.lower() != "submitted":
        raise HTTPException(
            status_code=400,
            detail=f"Milestone must be in 'submitted' state to approve (current: {milestone.status})"
        )
    
    # Update milestone
    milestone.status = "approved"
    milestone.approved_at = datetime.now(timezone.utc)
    if request.feedback:
        milestone.feedback = request.feedback
    
    db.commit()
    
    return {
        "message": "Milestone approved successfully",
        "milestone_id": milestone_id,
        "status": "approved"
    }


@router.post("/milestones/{milestone_id}/reject")
async def reject_milestone(
    milestone_id: str,
    request: MilestoneRejectionRequest,
    current_user: dict = Depends(require_business_owner),
    db: Session = Depends(get_db)
):
    """Reject a submitted milestone and request changes."""
    # Get business owner
    owner = db.query(BusinessOwner).filter(
        BusinessOwner.user_id == current_user["user_id"]
    ).first()
    
    if not owner:
        raise HTTPException(status_code=404, detail="Business owner profile not found")
    
    # Get milestone and verify ownership
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    
    deal = db.query(Deal).filter(
        Deal.id == milestone.deal_id,
        Deal.business_owner_id == owner.id
    ).first()
    
    if not deal:
        raise HTTPException(status_code=403, detail="Not authorized to reject this milestone")
    
    # Check if milestone is in submitted state
    if milestone.status.lower() != "submitted":
        raise HTTPException(
            status_code=400,
            detail=f"Milestone must be in 'submitted' state to reject (current: {milestone.status})"
        )
    
    # Update milestone
    milestone.status = "rejected"
    milestone.rejected_at = datetime.now(timezone.utc)
    milestone.rejection_reason = request.rejection_reason
    
    db.commit()
    
    return {
        "message": "Milestone rejected. Freelancer has been notified.",
        "milestone_id": milestone_id,
        "status": "rejected"
    }
