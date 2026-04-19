"""Deal management API endpoints."""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import logging

from ..database import get_db
from ..middleware.auth import get_current_user
from ..services.deal_management import (
    DealManagementService,
    InvalidPackageError,
    InvalidStatusTransitionError,
    DealManagementError
)
from ..models.user import Freelancer, BusinessOwner

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/deals", tags=["deals"])


# Request/Response Schemas

class CreateDealRequest(BaseModel):
    """Request schema for creating a deal."""
    business_id: str
    package_type: str = Field(..., description="Package type: starter, standard, or premium")
    amount: int = Field(..., gt=0, description="Deal amount in rupees")
    payment_flow: Optional[str] = Field(default=None, description="Payment flow: simplified or full. Auto-determined if not provided.")
    description: Optional[str] = None


class CreateDealResponse(BaseModel):
    """Response schema for creating a deal."""
    success: bool
    deal_id: str
    message: str
    deal: dict


class UpdateDealStatusRequest(BaseModel):
    """Request schema for updating deal status."""
    status: str = Field(..., description="New status: Pending, Active, InProgress, Completed, Disputed, Cancelled")


class UpdateDealStatusResponse(BaseModel):
    """Response schema for updating deal status."""
    success: bool
    deal_id: str
    old_status: str
    new_status: str
    message: str


class UpdateMilestoneRequest(BaseModel):
    """Request schema for updating milestone."""
    status: str = Field(..., description="New status: Pending, InProgress, Submitted, Approved, Rejected, Paid")
    deliverables: Optional[List[str]] = None
    feedback: Optional[str] = None
    rejection_reason: Optional[str] = None


class UpdateMilestoneResponse(BaseModel):
    """Response schema for updating milestone."""
    success: bool
    milestone_id: str
    new_status: str
    message: str


class DealDetailsResponse(BaseModel):
    """Response schema for deal details."""
    success: bool
    deal: dict


class MyDealsResponse(BaseModel):
    """Response schema for my deals."""
    success: bool
    total: int
    deals: List[dict]


# API Endpoints

@router.post("", response_model=CreateDealResponse)
async def create_deal(
    request: CreateDealRequest = Body(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new deal with milestones.
    
    This endpoint:
    1. Creates a deal record with status "pending"
    2. Generates milestones based on payment flow
    3. Calculates milestone amounts
    
    **Requirements**: 7.1, 7.2, 7.3
    
    Args:
        request: Deal details (business_id, package_type, amount, payment_flow)
        current_user: Authenticated user from JWT
        
    Returns:
        Created deal with milestones
        
    Raises:
        400: Invalid package type or amount
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
                    "message": "Only freelancers can create deals"
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
        
        # Create deal
        deal = DealManagementService.create_deal(
            db=db,
            freelancer_id=freelancer.id,
            business_id=request.business_id,
            package_type=request.package_type,
            amount=request.amount,
            payment_flow=request.payment_flow,
            description=request.description
        )
        
        # Get deal details
        deal_details = DealManagementService.get_deal_details(db, deal.id)
        
        return CreateDealResponse(
            success=True,
            deal_id=deal.id,
            message=f"Deal created successfully with {len(deal_details['milestones'])} milestones",
            deal=deal_details
        )
        
    except InvalidPackageError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_PACKAGE",
                "message": str(e)
            }
        )
    except DealManagementError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "DEAL_ERROR",
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Error creating deal: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": str(e)
            }
        )


@router.get("/{deal_id}", response_model=DealDetailsResponse)
async def get_deal_details(
    deal_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed information for a specific deal.
    
    **Requirements**: 7.1, 7.2
    
    Args:
        deal_id: Deal ID
        current_user: Authenticated user from JWT
        
    Returns:
        Deal details with milestones
        
    Raises:
        404: Deal not found
    """
    try:
        deal_details = DealManagementService.get_deal_details(db, deal_id)
        
        # Verify user has access to this deal
        user_id = current_user.get("user_id")
        role = current_user.get("role")
        
        if role == "freelancer":
            freelancer = db.query(Freelancer).filter(Freelancer.user_id == user_id).first()
            if not freelancer or deal_details["freelancer_id"] != freelancer.id:
                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "FORBIDDEN",
                        "message": "You don't have access to this deal"
                    }
                )
        elif role == "business_owner":
            business_owner = db.query(BusinessOwner).filter(BusinessOwner.user_id == user_id).first()
            if not business_owner or deal_details["business_owner_id"] != business_owner.id:
                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "FORBIDDEN",
                        "message": "You don't have access to this deal"
                    }
                )
        
        return DealDetailsResponse(
            success=True,
            deal=deal_details
        )
        
    except DealManagementError as e:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "NOT_FOUND",
                "message": str(e)
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting deal details: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": str(e)
            }
        )


@router.put("/{deal_id}/status", response_model=UpdateDealStatusResponse)
async def update_deal_status(
    deal_id: str,
    request: UpdateDealStatusRequest = Body(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update deal status.
    
    **Requirements**: 7.1, 7.5
    
    Args:
        deal_id: Deal ID
        request: New status
        current_user: Authenticated user from JWT
        
    Returns:
        Updated deal status
        
    Raises:
        400: Invalid status transition
        403: User doesn't have permission
        404: Deal not found
    """
    try:
        # Get deal to check permissions
        deal_details = DealManagementService.get_deal_details(db, deal_id)
        old_status = deal_details["status"]
        
        # Verify user has access
        user_id = current_user.get("user_id")
        role = current_user.get("role")
        
        if role == "freelancer":
            freelancer = db.query(Freelancer).filter(Freelancer.user_id == user_id).first()
            if not freelancer or deal_details["freelancer_id"] != freelancer.id:
                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "FORBIDDEN",
                        "message": "You don't have access to this deal"
                    }
                )
        elif role == "business_owner":
            business_owner = db.query(BusinessOwner).filter(BusinessOwner.user_id == user_id).first()
            if not business_owner or deal_details["business_owner_id"] != business_owner.id:
                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "FORBIDDEN",
                        "message": "You don't have access to this deal"
                    }
                )
        
        # Update status
        deal = DealManagementService.update_deal_status(
            db=db,
            deal_id=deal_id,
            new_status=request.status,
            user_id=user_id
        )
        
        return UpdateDealStatusResponse(
            success=True,
            deal_id=deal.id,
            old_status=old_status,
            new_status=deal.status.value,
            message=f"Deal status updated from {old_status} to {deal.status.value}"
        )
        
    except InvalidStatusTransitionError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_TRANSITION",
                "message": str(e)
            }
        )
    except DealManagementError as e:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "NOT_FOUND",
                "message": str(e)
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating deal status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": str(e)
            }
        )


@router.get("/my-deals", response_model=MyDealsResponse)
async def get_my_deals(
    status: Optional[str] = Query(None, description="Filter by status"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get deals for current user.
    
    **Requirements**: 7.1
    
    Args:
        status: Optional status filter
        current_user: Authenticated user from JWT
        
    Returns:
        List of user's deals
    """
    try:
        user_id = current_user.get("user_id")
        role = current_user.get("role")
        
        deals = DealManagementService.get_user_deals(
            db=db,
            user_id=user_id,
            role=role,
            status_filter=status
        )
        
        return MyDealsResponse(
            success=True,
            total=len(deals),
            deals=deals
        )
        
    except Exception as e:
        logger.error(f"Error getting my deals: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": str(e)
            }
        )


@router.put("/{deal_id}/milestones/{milestone_id}", response_model=UpdateMilestoneResponse)
async def update_milestone(
    deal_id: str,
    milestone_id: str,
    request: UpdateMilestoneRequest = Body(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update milestone status.
    
    **Requirements**: 7.2, 7.3, 7.4
    
    Args:
        deal_id: Deal ID
        milestone_id: Milestone ID
        request: Milestone update details
        current_user: Authenticated user from JWT
        
    Returns:
        Updated milestone status
        
    Raises:
        403: User doesn't have permission
        404: Deal or milestone not found
    """
    try:
        # Verify user has access to deal
        deal_details = DealManagementService.get_deal_details(db, deal_id)
        
        user_id = current_user.get("user_id")
        role = current_user.get("role")
        
        if role == "freelancer":
            freelancer = db.query(Freelancer).filter(Freelancer.user_id == user_id).first()
            if not freelancer or deal_details["freelancer_id"] != freelancer.id:
                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "FORBIDDEN",
                        "message": "You don't have access to this deal"
                    }
                )
        elif role == "business_owner":
            business_owner = db.query(BusinessOwner).filter(BusinessOwner.user_id == user_id).first()
            if not business_owner or deal_details["business_owner_id"] != business_owner.id:
                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "FORBIDDEN",
                        "message": "You don't have access to this deal"
                    }
                )
        
        # Update milestone
        milestone = DealManagementService.update_milestone_status(
            db=db,
            milestone_id=milestone_id,
            new_status=request.status,
            deliverables=request.deliverables,
            feedback=request.feedback,
            rejection_reason=request.rejection_reason
        )
        
        return UpdateMilestoneResponse(
            success=True,
            milestone_id=milestone.id,
            new_status=milestone.status.value,
            message=f"Milestone status updated to {milestone.status.value}"
        )
        
    except DealManagementError as e:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "NOT_FOUND",
                "message": str(e)
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating milestone: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": str(e)
            }
        )



@router.get("/payment-flow/{freelancer_id}")
async def get_payment_flow(
    freelancer_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get recommended payment flow for a freelancer based on completed deals.
    
    Auto-upgrade to full flow after 20 completed deals.
    
    Args:
        freelancer_id: Freelancer ID
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Recommended payment flow and deal count
    """
    try:
        # Verify freelancer exists
        freelancer = db.query(Freelancer).filter(Freelancer.id == freelancer_id).first()
        if not freelancer:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "NOT_FOUND",
                    "message": "Freelancer not found"
                }
            )
        
        # Get payment flow
        payment_flow = DealManagementService._determine_payment_flow(db, freelancer_id)
        
        # Get completed deal count
        from ..models.deal import Deal
        completed_count = db.query(Deal).filter(
            Deal.freelancer_id == freelancer_id,
            Deal.status == "completed"
        ).count()
        
        return {
            "success": True,
            "freelancer_id": freelancer_id,
            "payment_flow": payment_flow,
            "completed_deals": completed_count,
            "milestone_structure": "2 milestones (50%-50%)" if payment_flow == "simplified" else "3 milestones (30%-40%-30%)",
            "upgrade_threshold": 20,
            "deals_until_upgrade": max(0, 20 - completed_count) if payment_flow == "simplified" else 0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting payment flow: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": "Failed to get payment flow"
            }
        )
