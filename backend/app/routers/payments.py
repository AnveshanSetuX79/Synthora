"""Payment API endpoints for Razorpay integration."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Body, Header, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import logging

from ..database import get_db
from ..middleware.auth import get_current_user
from ..services.payment import (
    PaymentService,
    PaymentError,
    RazorpayError,
    InvalidWebhookError
)
from ..services.kyc import KYCService, KYCError
from ..models.user import Freelancer, BusinessOwner

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/payments", tags=["payments"])


# Request/Response Schemas

class CreateOrderRequest(BaseModel):
    """Request schema for creating payment order."""
    deal_id: str
    amount: int = Field(..., gt=0, description="Amount in rupees")
    milestone_id: Optional[str] = None


class CreateOrderResponse(BaseModel):
    """Response schema for creating payment order."""
    success: bool
    payment_id: str
    razorpay_order_id: str
    amount: int
    commission: int
    message: str


class VerifyPaymentRequest(BaseModel):
    """Request schema for verifying payment."""
    payment_id: str
    razorpay_payment_id: str
    razorpay_signature: str


class VerifyPaymentResponse(BaseModel):
    """Response schema for verifying payment."""
    success: bool
    payment_id: str
    status: str
    message: str


class PaymentStatusResponse(BaseModel):
    """Response schema for payment status."""
    success: bool
    payment_info: dict


class RefundRequest(BaseModel):
    """Request schema for refund."""
    payment_id: str
    amount: Optional[int] = Field(None, gt=0, description="Partial refund amount in rupees (None for full refund)")
    reason: Optional[str] = None


class RefundResponse(BaseModel):
    """Response schema for refund."""
    success: bool
    payment_id: str
    status: str
    message: str


class KYCSubmitRequest(BaseModel):
    """Request schema for KYC submission."""
    document_type: str = Field(..., description="Document type: Aadhaar, PAN, DrivingLicense, Passport")
    document_number: str = Field(..., min_length=5, max_length=100)
    document_url: Optional[str] = None
    bank_account_number: str = Field(..., min_length=9, max_length=18)
    bank_ifsc_code: str = Field(..., min_length=11, max_length=11)
    bank_account_holder_name: str = Field(..., min_length=2, max_length=255)


class KYCSubmitResponse(BaseModel):
    """Response schema for KYC submission."""
    success: bool
    kyc_id: str
    status: str
    message: str


class KYCStatusResponse(BaseModel):
    """Response schema for KYC status."""
    success: bool
    kyc_status: dict


class PayoutRequest(BaseModel):
    """Request schema for payout."""
    milestone_id: str


class PayoutResponse(BaseModel):
    """Response schema for payout."""
    success: bool
    transaction_id: str
    amount: float
    commission: float
    message: str


class PayoutEligibilityResponse(BaseModel):
    """Response schema for payout eligibility."""
    success: bool
    eligibility: dict


# API Endpoints

@router.post("/create-order", response_model=CreateOrderResponse)
async def create_payment_order(
    request: CreateOrderRequest = Body(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create Razorpay order for payment.
    
    This endpoint:
    1. Creates a payment record
    2. Generates Razorpay order
    3. Calculates platform commission (15%)
    4. Returns order details for frontend integration
    
    **Requirements**: 8.1, 8.2
    
    Args:
        request: Order details (deal_id, amount, milestone_id)
        current_user: Authenticated user from JWT
        
    Returns:
        Razorpay order details
        
    Raises:
        400: Invalid request or payment creation failed
        403: User doesn't have permission
        404: Deal not found
    """
    try:
        # Create payment order
        payment_service = PaymentService()
        payment = payment_service.create_order(
            db=db,
            deal_id=request.deal_id,
            amount=request.amount,
            milestone_id=request.milestone_id
        )
        
        return CreateOrderResponse(
            success=True,
            payment_id=payment.id,
            razorpay_order_id=payment.razorpay_order_id,
            amount=payment.amount // 100,  # Convert to rupees
            commission=payment.commission // 100,
            message="Payment order created successfully"
        )
        
    except (PaymentError, RazorpayError) as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "PAYMENT_ERROR",
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Error creating payment order: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": str(e)
            }
        )


@router.post("/verify", response_model=VerifyPaymentResponse)
async def verify_payment(
    request: VerifyPaymentRequest = Body(...),
    db: Session = Depends(get_db)
):
    """Verify payment after Razorpay checkout.
    
    This endpoint verifies the payment signature and updates
    the payment status to completed.
    
    **Requirements**: 8.1, 8.2
    
    Args:
        request: Payment verification details
        
    Returns:
        Payment verification status
        
    Raises:
        400: Invalid signature or verification failed
    """
    try:
        payment_service = PaymentService()
        payment = payment_service.verify_payment(
            db=db,
            payment_id=request.payment_id,
            razorpay_payment_id=request.razorpay_payment_id,
            razorpay_signature=request.razorpay_signature
        )
        
        return VerifyPaymentResponse(
            success=True,
            payment_id=payment.id,
            status=payment.status.value,
            message="Payment verified successfully"
        )
        
    except InvalidWebhookError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_SIGNATURE",
                "message": str(e)
            }
        )
    except PaymentError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "VERIFICATION_FAILED",
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Error verifying payment: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": str(e)
            }
        )


@router.post("/webhook")
async def handle_webhook(
    request: Request,
    x_razorpay_signature: str = Header(None),
    db: Session = Depends(get_db)
):
    """Handle Razorpay webhooks.
    
    This endpoint receives and processes webhooks from Razorpay
    for payment events (captured, failed, refunded).
    
    **Requirements**: 8.1, 8.2, 8.3
    
    Args:
        request: FastAPI request object
        x_razorpay_signature: Webhook signature header
        
    Returns:
        Webhook processing status
    """
    try:
        # Get webhook payload
        payload = await request.json()
        
        # Handle webhook
        payment_service = PaymentService()
        success = payment_service.handle_webhook(
            db=db,
            payload=payload,
            signature=x_razorpay_signature or ""
        )
        
        if success:
            return {"success": True, "message": "Webhook processed successfully"}
        else:
            return {"success": False, "message": "Webhook processing failed"}
        
    except InvalidWebhookError as e:
        logger.warning(f"Invalid webhook signature: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_SIGNATURE",
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Error handling webhook: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": str(e)
            }
        )


@router.get("/{deal_id}", response_model=PaymentStatusResponse)
async def get_payment_status(
    deal_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get payment status for a deal.
    
    **Requirements**: 8.1
    
    Args:
        deal_id: Deal ID
        current_user: Authenticated user from JWT
        
    Returns:
        Payment information for the deal
        
    Raises:
        403: User doesn't have permission
        404: Deal not found
    """
    try:
        payment_service = PaymentService()
        payment_info = payment_service.get_payment_status(db, deal_id)
        
        return PaymentStatusResponse(
            success=True,
            payment_info=payment_info
        )
        
    except Exception as e:
        logger.error(f"Error getting payment status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": str(e)
            }
        )


@router.post("/refund", response_model=RefundResponse)
async def process_refund(
    request: RefundRequest = Body(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process refund for a payment.
    
    This endpoint processes full or partial refunds through Razorpay.
    Only admins or authorized users can process refunds.
    
    **Requirements**: 8.7
    
    Args:
        request: Refund details (payment_id, amount, reason)
        current_user: Authenticated user from JWT
        
    Returns:
        Refund processing status
        
    Raises:
        400: Invalid refund request
        403: User doesn't have permission
    """
    try:
        # Verify user has permission (admin or deal owner)
        role = current_user.get("role")
        if role not in ["admin", "founder"]:
            # TODO: Add additional permission checks for deal owners
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "FORBIDDEN",
                    "message": "Only admins can process refunds"
                }
            )
        
        # Process refund
        payment_service = PaymentService()
        payment = payment_service.process_refund(
            db=db,
            payment_id=request.payment_id,
            amount=request.amount,
            reason=request.reason
        )
        
        return RefundResponse(
            success=True,
            payment_id=payment.id,
            status=payment.status.value,
            message="Refund processed successfully"
        )
        
    except (PaymentError, RazorpayError) as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "REFUND_ERROR",
                "message": str(e)
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing refund: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": str(e)
            }
        )



@router.post("/kyc/submit", response_model=KYCSubmitResponse)
async def submit_kyc(
    request: KYCSubmitRequest = Body(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit KYC documents for verification.
    
    This endpoint allows freelancers to submit KYC documents
    including identity proof and bank account details for payouts.
    
    **Requirements**: 4.4, 4.5, 8.6
    
    Args:
        request: KYC document details
        current_user: Authenticated user from JWT
        
    Returns:
        KYC submission confirmation
        
    Raises:
        400: Invalid KYC data or already submitted
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
                    "message": "Only freelancers can submit KYC"
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
        
        # Submit KYC
        kyc_service = KYCService()
        kyc_doc = kyc_service.submit_kyc(
            db=db,
            freelancer_id=freelancer.id,
            document_type=request.document_type,
            document_number=request.document_number,
            document_url=request.document_url,
            bank_account_number=request.bank_account_number,
            bank_ifsc_code=request.bank_ifsc_code,
            bank_account_holder_name=request.bank_account_holder_name
        )
        
        return KYCSubmitResponse(
            success=True,
            kyc_id=kyc_doc.id,
            status=kyc_doc.status.value,
            message="KYC documents submitted successfully. Verification in progress."
        )
        
    except KYCError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "KYC_ERROR",
                "message": str(e)
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting KYC: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": str(e)
            }
        )


@router.get("/kyc/status", response_model=KYCStatusResponse)
async def get_kyc_status(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get KYC status for current freelancer.
    
    **Requirements**: 4.4, 4.5
    
    Args:
        current_user: Authenticated user from JWT
        
    Returns:
        KYC status information
        
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
                    "message": "Only freelancers can check KYC status"
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
        
        # Get KYC status
        kyc_service = KYCService()
        kyc_status = kyc_service.get_kyc_status(db, freelancer.id)
        
        return KYCStatusResponse(
            success=True,
            kyc_status=kyc_status
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting KYC status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": str(e)
            }
        )


@router.post("/payout", response_model=PayoutResponse)
async def process_payout(
    request: PayoutRequest = Body(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process payout to freelancer after milestone approval.
    
    This endpoint releases funds from escrow to the freelancer's
    linked account after deducting platform commission (10%).
    
    **Requirements**: 8.4, 8.5, 8.6
    
    Args:
        request: Payout details (milestone_id)
        current_user: Authenticated user from JWT
        
    Returns:
        Payout processing confirmation
        
    Raises:
        400: Invalid payout request or KYC not approved
        403: User doesn't have permission
        404: Milestone not found
    """
    try:
        # Verify user is a freelancer
        if current_user.get("role") != "freelancer":
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "FORBIDDEN",
                    "message": "Only freelancers can request payouts"
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
        
        # Process payout
        payment_service = PaymentService()
        transaction = payment_service.process_payout(
            db=db,
            milestone_id=request.milestone_id,
            freelancer_id=freelancer.id
        )
        
        return PayoutResponse(
            success=True,
            transaction_id=transaction.id,
            amount=transaction.amount / 100,  # Convert to rupees
            commission=transaction.commission / 100,
            message="Payout processed successfully"
        )
        
    except (PaymentError, RazorpayError) as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "PAYOUT_ERROR",
                "message": str(e)
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing payout: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": str(e)
            }
        )


@router.get("/payout/eligibility", response_model=PayoutEligibilityResponse)
async def check_payout_eligibility(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if freelancer is eligible for payouts.
    
    **Requirements**: 4.4, 8.6
    
    Args:
        current_user: Authenticated user from JWT
        
    Returns:
        Payout eligibility status
        
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
                    "message": "Only freelancers can check payout eligibility"
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
        
        # Check eligibility
        payment_service = PaymentService()
        eligibility = payment_service.get_payout_eligibility(db, freelancer.id)
        
        return PayoutEligibilityResponse(
            success=True,
            eligibility=eligibility
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking payout eligibility: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": str(e)
            }
        )


@router.post("/linked-account/create")
async def create_linked_account(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create Razorpay linked account for freelancer.
    
    This endpoint creates a linked account (Razorpay Route) that
    allows the platform to hold payments in escrow and release
    them after milestone approval.
    
    **Requirements**: 8.4, 8.5, 8.6
    
    Args:
        current_user: Authenticated user from JWT
        
    Returns:
        Linked account creation confirmation
        
    Raises:
        400: KYC not approved or account creation failed
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
                    "message": "Only freelancers can create linked accounts"
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
        
        # Get approved KYC document
        from ..models.kyc import KYCDocument, KYCVerificationStatus
        kyc_doc = db.query(KYCDocument).filter(
            KYCDocument.freelancer_id == freelancer.id,
            KYCDocument.status == "approved"  # Use lowercase string
        ).first()
        
        if not kyc_doc:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "KYC_NOT_APPROVED",
                    "message": "KYC must be approved before creating linked account"
                }
            )
        
        # Create linked account
        payment_service = PaymentService()
        account_id = payment_service.create_linked_account(
            db=db,
            freelancer_id=freelancer.id,
            kyc_document_id=kyc_doc.id
        )
        
        return {
            "success": True,
            "razorpay_account_id": account_id,
            "message": "Linked account created successfully"
        }
        
    except (PaymentError, RazorpayError) as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "ACCOUNT_CREATION_ERROR",
                "message": str(e)
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating linked account: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": str(e)
            }
        )
