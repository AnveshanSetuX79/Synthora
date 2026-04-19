"""Dispute resolution routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from ..database import get_db
from ..middleware.auth import get_current_user, require_admin
from ..services.dispute_resolution import DisputeResolutionService, DisputeError
from ..models.dispute import Dispute, DisputeResolution

router = APIRouter(prefix="/api/disputes", tags=["disputes"])


# Schemas
class CreateDisputeRequest(BaseModel):
    deal_id: str
    reason: str
    description: Optional[str] = None


class AddMessageRequest(BaseModel):
    message: str


class ResolveDisputeRequest(BaseModel):
    resolution_type: str  # full_payment_freelancer, partial_payment, full_refund_business
    resolution_amount: Optional[int] = None  # For partial payment (in paise)
    resolution_notes: Optional[str] = None


@router.post("")
async def create_dispute(
    request: CreateDisputeRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new dispute for a deal.
    
    Requirement 8.1: Phase 1 - Self-Resolution (48 hours)
    """
    try:
        # Determine role
        role = current_user.get("role", "freelancer")
        
        dispute = DisputeResolutionService.create_dispute(
            db=db,
            deal_id=request.deal_id,
            raised_by=current_user["user_id"],
            raised_by_role=role,
            reason=request.reason,
            description=request.description
        )
        
        return {
            "message": "Dispute created successfully",
            "dispute_id": dispute.id,
            "status": dispute.status,
            "self_resolution_deadline": dispute.self_resolution_deadline.isoformat()
        }
    except DisputeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create dispute: {str(e)}")


@router.get("/{dispute_id}")
async def get_dispute(
    dispute_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dispute details with full conversation history.
    
    Requirement 8.2: Full conversation history for admin review
    """
    try:
        dispute_details = DisputeResolutionService.get_dispute_details(db, dispute_id)
        return dispute_details
    except DisputeError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dispute: {str(e)}")


@router.post("/{dispute_id}/messages")
async def add_dispute_message(
    dispute_id: str,
    request: AddMessageRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a message to dispute chat.
    
    Requirement 8.1: Dispute chat interface
    """
    try:
        role = current_user.get("role", "freelancer")
        
        message = DisputeResolutionService.add_message(
            db=db,
            dispute_id=dispute_id,
            sender_id=current_user["user_id"],
            sender_role=role,
            message=request.message
        )
        
        return {
            "message_id": message.id,
            "created_at": message.created_at.isoformat()
        }
    except DisputeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add message: {str(e)}")


@router.post("/{dispute_id}/escalate")
async def escalate_dispute(
    dispute_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Escalate dispute to admin mediation.
    
    Requirement 8.1: Phase 2 - Admin Mediation (after 48 hours)
    """
    try:
        dispute = DisputeResolutionService.escalate_to_admin(db, dispute_id)
        
        return {
            "message": "Dispute escalated to admin mediation",
            "dispute_id": dispute.id,
            "status": dispute.status,
            "escalated_at": dispute.escalated_at.isoformat()
        }
    except DisputeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to escalate dispute: {str(e)}")


@router.post("/{dispute_id}/resolve")
async def resolve_dispute(
    dispute_id: str,
    request: ResolveDisputeRequest,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Resolve a dispute (admin only).
    
    Requirement 8.2: Admin Decisions
    - Full payment to Freelancer
    - Partial payment based on work
    - Full refund to Business
    
    Requirement 8.3: Payment action within 24 hours
    """
    try:
        # Validate resolution type
        valid_resolutions = [
            DisputeResolution.FULL_PAYMENT_FREELANCER.value,
            DisputeResolution.PARTIAL_PAYMENT.value,
            DisputeResolution.FULL_REFUND_BUSINESS.value
        ]
        
        if request.resolution_type not in valid_resolutions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid resolution type. Must be one of: {', '.join(valid_resolutions)}"
            )
        
        # Validate partial payment amount
        if request.resolution_type == DisputeResolution.PARTIAL_PAYMENT.value:
            if not request.resolution_amount:
                raise HTTPException(
                    status_code=400,
                    detail="Resolution amount required for partial payment"
                )
        
        dispute = DisputeResolutionService.resolve_dispute(
            db=db,
            dispute_id=dispute_id,
            resolved_by=current_user["user_id"],
            resolution_type=request.resolution_type,
            resolution_amount=request.resolution_amount,
            resolution_notes=request.resolution_notes
        )
        
        return {
            "message": "Dispute resolved successfully",
            "dispute_id": dispute.id,
            "status": dispute.status,
            "resolution_type": dispute.resolution_type,
            "resolution_amount": dispute.resolution_amount,
            "resolved_at": dispute.resolved_at.isoformat()
        }
    except DisputeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resolve dispute: {str(e)}")


@router.post("/{dispute_id}/close")
async def close_dispute(
    dispute_id: str,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Close a resolved dispute (admin only).
    
    Requirement 8.3: Dispute closed
    """
    try:
        dispute = DisputeResolutionService.close_dispute(db, dispute_id)
        
        return {
            "message": "Dispute closed successfully",
            "dispute_id": dispute.id,
            "status": dispute.status,
            "closed_at": dispute.closed_at.isoformat()
        }
    except DisputeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to close dispute: {str(e)}")


@router.get("")
async def list_disputes(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List disputes (filtered by user role).
    
    Freelancers and business owners see only their disputes.
    Admins see all disputes.
    """
    query = db.query(Dispute)
    
    # Filter by status if provided
    if status:
        query = query.filter(Dispute.status == status)
    
    # Filter by user role
    role = current_user.get("role", "freelancer")
    if role != "admin":
        # Show only disputes where user is involved
        query = query.filter(Dispute.raised_by == current_user["user_id"])
    
    total = query.count()
    disputes = query.order_by(Dispute.created_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for dispute in disputes:
        result.append({
            "id": dispute.id,
            "deal_id": dispute.deal_id,
            "raised_by": dispute.raised_by,
            "raised_by_role": dispute.raised_by_role,
            "reason": dispute.reason,
            "status": dispute.status,
            "created_at": dispute.created_at.isoformat(),
            "self_resolution_deadline": dispute.self_resolution_deadline.isoformat(),
            "escalated_at": dispute.escalated_at.isoformat() if dispute.escalated_at else None,
            "resolved_at": dispute.resolved_at.isoformat() if dispute.resolved_at else None
        })
    
    return {
        "total": total,
        "disputes": result
    }
