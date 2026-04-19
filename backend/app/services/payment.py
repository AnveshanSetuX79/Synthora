"""Payment service for Razorpay integration and payment processing.

This service handles:
- Razorpay order creation
- Payment tracking and status updates
- Webhook handling
- Refund processing
- Commission calculations
- Razorpay Route (escrow) for milestone-based payouts
- KYC verification for payouts

Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7
"""
import logging
from typing import Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import uuid
import os
import hmac
import hashlib

from ..models.payment import Payment, Transaction, PaymentStatus, TransactionType
from ..models.deal import Deal, Milestone, MilestoneStatus
from ..models.user import Freelancer
from ..models.kyc import KYCDocument, KYCVerificationStatus

logger = logging.getLogger(__name__)


class PaymentError(Exception):
    """Base exception for payment errors."""
    pass


class RazorpayError(PaymentError):
    """Raised when Razorpay API fails."""
    pass


class InvalidWebhookError(PaymentError):
    """Raised when webhook signature is invalid."""
    pass


class PaymentService:
    """Service for managing payments via Razorpay."""
    
    # Commission rates
    # IMPORTANT: Business owner pays the full amount
    # Platform keeps 15% commission
    # Freelancer receives 85% of the amount
    PLATFORM_COMMISSION_RATE = 0.15  # 15% kept by platform
    FREELANCER_PAYOUT_RATE = 0.85  # 85% paid to freelancer
    
    # Legacy rates (kept for reference, not used in calculations)
    FREELANCER_COMMISSION_RATE = 0.10  # 10% from freelancer (OLD - INCORRECT)
    BUSINESS_COMMISSION_RATE = 0.05  # 5% from business (OLD - INCORRECT)
    
    def __init__(self):
        """Initialize payment service with Razorpay credentials."""
        self.razorpay_key_id = os.getenv("RAZORPAY_KEY_ID")
        self.razorpay_key_secret = os.getenv("RAZORPAY_KEY_SECRET")
        self.webhook_secret = os.getenv("RAZORPAY_WEBHOOK_SECRET")
        
        # In production, initialize Razorpay client here
        # import razorpay
        # self.client = razorpay.Client(auth=(self.razorpay_key_id, self.razorpay_key_secret))
        
        self.razorpay_enabled = self.razorpay_key_id is not None
        
        logger.info(f"Payment service initialized. Razorpay: {self.razorpay_enabled}")
    
    def create_order(
        self,
        db: Session,
        deal_id: str,
        amount: int,
        milestone_id: Optional[str] = None
    ) -> Payment:
        """Create Razorpay order for payment.
        
        PAYMENT FLOW:
        1. Business owner pays FULL amount (e.g., ₹10,000)
        2. Platform keeps 15% commission (₹1,500)
        3. Freelancer receives 85% (₹8,500)
        
        Args:
            db: Database session
            deal_id: Deal ID
            amount: Amount in rupees (what business owner pays)
            milestone_id: Optional milestone ID
            
        Returns:
            Payment object with Razorpay order details
            
        Raises:
            PaymentError: If order creation fails
        """
        try:
            # Get deal
            deal = db.query(Deal).filter(Deal.id == deal_id).first()
            if not deal:
                raise PaymentError(f"Deal {deal_id} not found")
            
            # Convert to paise
            amount_paise = amount * 100
            
            # Calculate commission (platform keeps 15%)
            commission_paise = int(amount_paise * self.PLATFORM_COMMISSION_RATE)
            
            # Calculate freelancer payout (85% of total)
            freelancer_payout_paise = amount_paise - commission_paise
            
            # Create Razorpay order FIRST (before any database operations)
            razorpay_order_id = None
            
            if self.razorpay_enabled:
                try:
                    # In production, use actual Razorpay API
                    # order = self.client.order.create({
                    #     "amount": amount_paise,
                    #     "currency": "INR",
                    #     "receipt": str(uuid.uuid4()),
                    #     "notes": {
                    #         "deal_id": deal_id,
                    #         "milestone_id": milestone_id or "",
                    #         "commission": commission_paise,
                    #         "freelancer_payout": freelancer_payout_paise
                    #     }
                    # })
                    # razorpay_order_id = order["id"]
                    
                    # Mock for development
                    razorpay_order_id = f"order_mock_{uuid.uuid4().hex[:16]}"
                    logger.info(f"[MOCK] Created Razorpay order: {razorpay_order_id}")
                    
                except Exception as e:
                    logger.error(f"Razorpay order creation failed: {str(e)}")
                    # Don't create payment record if Razorpay fails
                    raise RazorpayError(f"Failed to create Razorpay order: {str(e)}")
            else:
                # Mock order ID for development
                razorpay_order_id = f"order_dev_{uuid.uuid4().hex[:16]}"
                logger.info(f"[DEV] Created mock order: {razorpay_order_id}")
            
            # Only create payment record if Razorpay order succeeded
            # amount = what business owner pays
            # commission = what platform keeps
            # freelancer receives = amount - commission
            payment = Payment(
                id=str(uuid.uuid4()),
                deal_id=deal_id,
                milestone_id=milestone_id,
                amount=amount_paise,  # Business owner pays this
                commission=commission_paise,  # Platform keeps this
                status=PaymentStatus.PENDING,
                razorpay_order_id=razorpay_order_id
            )
            
            logger.info(
                f"Payment breakdown: Business pays ₹{amount}, "
                f"Platform keeps ₹{commission_paise/100}, "
                f"Freelancer receives ₹{freelancer_payout_paise/100}"
            )
            
            db.add(payment)
            
            # Create transaction record
            transaction = Transaction(
                id=str(uuid.uuid4()),
                payment_id=payment.id,
                deal_id=deal_id,
                milestone_id=milestone_id,
                type=TransactionType.DEPOSIT,
                amount=amount_paise,
                commission=commission_paise,
                status=PaymentStatus.PENDING,
                payment_provider_id=razorpay_order_id
            )
            
            db.add(transaction)
            db.commit()
            db.refresh(payment)
            
            logger.info(
                f"Created payment order {payment.id} for deal {deal_id}: "
                f"Business pays ₹{amount}, Platform keeps ₹{commission_paise/100}, "
                f"Freelancer receives ₹{freelancer_payout_paise/100}"
            )
            
            return payment
            
        except (PaymentError, RazorpayError):
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating payment order: {str(e)}")
            raise PaymentError(f"Failed to create payment order: {str(e)}")
    
    def verify_payment(
        self,
        db: Session,
        payment_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str
    ) -> Payment:
        """Verify and complete payment.
        
        Args:
            db: Database session
            payment_id: Payment ID
            razorpay_payment_id: Razorpay payment ID
            razorpay_signature: Payment signature
            
        Returns:
            Updated Payment object
            
        Raises:
            PaymentError: If verification fails
        """
        try:
            payment = db.query(Payment).filter(Payment.id == payment_id).first()
            
            if not payment:
                raise PaymentError(f"Payment {payment_id} not found")
            
            # Verify signature
            if self.razorpay_enabled and self.webhook_secret:
                expected_signature = self._generate_signature(
                    payment.razorpay_order_id,
                    razorpay_payment_id
                )
                
                if not hmac.compare_digest(expected_signature, razorpay_signature):
                    raise InvalidWebhookError("Invalid payment signature")
            
            # Update payment
            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.status = PaymentStatus.COMPLETED
            payment.completed_at = datetime.utcnow()
            
            # Update transaction
            transaction = db.query(Transaction).filter(
                Transaction.payment_id == payment.id
            ).first()
            
            if transaction:
                transaction.status = PaymentStatus.COMPLETED
                transaction.completed_at = datetime.utcnow()
            
            db.commit()
            db.refresh(payment)
            
            logger.info(f"Payment {payment_id} verified and completed")
            
            return payment
            
        except (PaymentError, InvalidWebhookError):
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error verifying payment: {str(e)}")
            raise PaymentError(f"Failed to verify payment: {str(e)}")
    
    def handle_webhook(
        self,
        db: Session,
        payload: Dict,
        signature: str
    ) -> bool:
        """Handle Razorpay webhook.
        
        Args:
            db: Database session
            payload: Webhook payload
            signature: Webhook signature
            
        Returns:
            True if handled successfully
            
        Raises:
            InvalidWebhookError: If signature is invalid
        """
        try:
            # Verify webhook signature
            if self.razorpay_enabled and self.webhook_secret:
                expected_signature = self._generate_webhook_signature(payload)
                
                if not hmac.compare_digest(expected_signature, signature):
                    raise InvalidWebhookError("Invalid webhook signature")
            
            # Handle different event types
            event = payload.get("event")
            
            if event == "payment.captured":
                self._handle_payment_captured(db, payload)
            elif event == "payment.failed":
                self._handle_payment_failed(db, payload)
            elif event == "refund.created":
                self._handle_refund_created(db, payload)
            else:
                logger.info(f"Unhandled webhook event: {event}")
            
            return True
            
        except InvalidWebhookError:
            raise
        except Exception as e:
            logger.error(f"Error handling webhook: {str(e)}")
            return False
    
    def _handle_payment_captured(self, db: Session, payload: Dict) -> None:
        """Handle payment captured webhook."""
        payment_entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
        order_id = payment_entity.get("order_id")
        payment_id = payment_entity.get("id")
        
        # Find payment by order ID
        payment = db.query(Payment).filter(
            Payment.razorpay_order_id == order_id
        ).first()
        
        if payment:
            payment.razorpay_payment_id = payment_id
            payment.status = PaymentStatus.COMPLETED
            payment.completed_at = datetime.utcnow()
            payment.payment_method = payment_entity.get("method")
            
            db.commit()
            logger.info(f"Payment captured: {payment_id}")
    
    def _handle_payment_failed(self, db: Session, payload: Dict) -> None:
        """Handle payment failed webhook."""
        payment_entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
        order_id = payment_entity.get("order_id")
        error_description = payment_entity.get("error_description")
        
        # Find payment by order ID
        payment = db.query(Payment).filter(
            Payment.razorpay_order_id == order_id
        ).first()
        
        if payment:
            payment.status = PaymentStatus.FAILED
            payment.error_message = error_description
            
            db.commit()
            logger.warning(f"Payment failed: {order_id} - {error_description}")
    
    def _handle_refund_created(self, db: Session, payload: Dict) -> None:
        """Handle refund created webhook."""
        refund_entity = payload.get("payload", {}).get("refund", {}).get("entity", {})
        payment_id = refund_entity.get("payment_id")
        
        # Find payment by Razorpay payment ID
        payment = db.query(Payment).filter(
            Payment.razorpay_payment_id == payment_id
        ).first()
        
        if payment:
            payment.status = PaymentStatus.REFUNDED
            
            db.commit()
            logger.info(f"Refund processed: {payment_id}")
    
    def get_payment_status(
        self,
        db: Session,
        deal_id: str
    ) -> Dict:
        """Get payment status for a deal.
        
        Args:
            db: Database session
            deal_id: Deal ID
            
        Returns:
            Dictionary with payment information
        """
        payments = db.query(Payment).filter(
            Payment.deal_id == deal_id
        ).order_by(Payment.created_at.desc()).all()
        
        return {
            "deal_id": deal_id,
            "total_payments": len(payments),
            "payments": [
                {
                    "id": p.id,
                    "amount": p.amount / 100,  # Convert to rupees
                    "commission": p.commission / 100,
                    "status": p.status.value,
                    "razorpay_order_id": p.razorpay_order_id,
                    "razorpay_payment_id": p.razorpay_payment_id,
                    "payment_method": p.payment_method,
                    "created_at": p.created_at.isoformat(),
                    "completed_at": p.completed_at.isoformat() if p.completed_at else None
                }
                for p in payments
            ]
        }
    
    def process_refund(
        self,
        db: Session,
        payment_id: str,
        amount: Optional[int] = None,
        reason: Optional[str] = None
    ) -> Payment:
        """Process refund for a payment.
        
        Args:
            db: Database session
            payment_id: Payment ID
            amount: Optional partial refund amount in rupees (None for full refund)
            reason: Optional refund reason
            
        Returns:
            Updated Payment object
            
        Raises:
            PaymentError: If refund fails
        """
        try:
            payment = db.query(Payment).filter(Payment.id == payment_id).first()
            
            if not payment:
                raise PaymentError(f"Payment {payment_id} not found")
            
            if payment.status != PaymentStatus.COMPLETED:
                raise PaymentError(f"Cannot refund payment with status {payment.status.value}")
            
            # Calculate refund amount
            refund_amount_paise = amount * 100 if amount else payment.amount
            
            # Process refund via Razorpay
            if self.razorpay_enabled and payment.razorpay_payment_id:
                try:
                    # In production, use actual Razorpay API
                    # refund = self.client.payment.refund(
                    #     payment.razorpay_payment_id,
                    #     {
                    #         "amount": refund_amount_paise,
                    #         "notes": {"reason": reason or ""}
                    #     }
                    # )
                    
                    # Mock for development
                    logger.info(f"[MOCK] Processing refund: ₹{refund_amount_paise/100}")
                    
                except Exception as e:
                    logger.error(f"Razorpay refund failed: {str(e)}")
                    raise RazorpayError(f"Failed to process refund: {str(e)}")
            
            # Update payment status
            payment.status = PaymentStatus.REFUNDED
            payment.error_message = reason
            
            # Create refund transaction
            transaction = Transaction(
                id=str(uuid.uuid4()),
                payment_id=payment.id,
                deal_id=payment.deal_id,
                milestone_id=payment.milestone_id,
                type=TransactionType.REFUND,
                amount=refund_amount_paise,
                status=PaymentStatus.COMPLETED,
                completed_at=datetime.utcnow()
            )
            
            db.add(transaction)
            db.commit()
            db.refresh(payment)
            
            logger.info(f"Refund processed for payment {payment_id}: ₹{refund_amount_paise/100}")
            
            return payment
            
        except (PaymentError, RazorpayError):
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error processing refund: {str(e)}")
            raise PaymentError(f"Failed to process refund: {str(e)}")
    
    def _generate_signature(self, order_id: str, payment_id: str) -> str:
        """Generate payment signature for verification.
        
        Args:
            order_id: Razorpay order ID
            payment_id: Razorpay payment ID
            
        Returns:
            HMAC signature
        """
        message = f"{order_id}|{payment_id}"
        signature = hmac.new(
            self.razorpay_key_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _generate_webhook_signature(self, payload: Dict) -> str:
        """Generate webhook signature for verification.
        
        Args:
            payload: Webhook payload
            
        Returns:
            HMAC signature
        """
        import json
        message = json.dumps(payload, separators=(',', ':'))
        signature = hmac.new(
            self.webhook_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def create_linked_account(
        self,
        db: Session,
        freelancer_id: str,
        kyc_document_id: str
    ) -> str:
        """Create Razorpay linked account for freelancer (for Route/escrow).
        
        This creates a linked account that allows the platform to hold
        payments in escrow and release them to freelancers after milestone approval.
        
        Args:
            db: Database session
            freelancer_id: Freelancer ID
            kyc_document_id: KYC document ID
            
        Returns:
            Razorpay account ID
            
        Raises:
            PaymentError: If account creation fails
        """
        try:
            # Get freelancer and KYC document
            freelancer = db.query(Freelancer).filter(Freelancer.id == freelancer_id).first()
            kyc_doc = db.query(KYCDocument).filter(KYCDocument.id == kyc_document_id).first()
            
            if not freelancer:
                raise PaymentError(f"Freelancer {freelancer_id} not found")
            
            if not kyc_doc:
                raise PaymentError(f"KYC document {kyc_document_id} not found")
            
            if kyc_doc.status != KYCVerificationStatus.APPROVED:
                raise PaymentError("KYC must be approved before creating linked account")
            
            # Check if account already exists
            if kyc_doc.razorpay_account_id:
                logger.info(f"Linked account already exists: {kyc_doc.razorpay_account_id}")
                return kyc_doc.razorpay_account_id
            
            # Create linked account via Razorpay Route
            if self.razorpay_enabled:
                try:
                    # In production, use actual Razorpay Route API
                    # account = self.client.account.create({
                    #     "email": freelancer.user.email,
                    #     "phone": freelancer.user.phone,
                    #     "type": "route",
                    #     "legal_business_name": freelancer.name,
                    #     "business_type": "individual",
                    #     "contact_name": freelancer.name,
                    #     "profile": {
                    #         "category": "services",
                    #         "subcategory": "web_development"
                    #     },
                    #     "legal_info": {
                    #         "pan": kyc_doc.document_number if kyc_doc.document_type == "pan" else None
                    #     },
                    #     "bank_account": {
                    #         "ifsc": kyc_doc.bank_ifsc_code,
                    #         "account_number": kyc_doc.bank_account_number,
                    #         "beneficiary_name": kyc_doc.bank_account_holder_name
                    #     }
                    # })
                    # account_id = account["id"]
                    
                    # Mock for development
                    account_id = f"acc_mock_{uuid.uuid4().hex[:16]}"
                    logger.info(f"[MOCK] Created linked account: {account_id}")
                    
                except Exception as e:
                    logger.error(f"Razorpay linked account creation failed: {str(e)}")
                    raise RazorpayError(f"Failed to create linked account: {str(e)}")
            else:
                # Mock account ID for development
                account_id = f"acc_dev_{uuid.uuid4().hex[:16]}"
                logger.info(f"[DEV] Created mock linked account: {account_id}")
            
            # Update KYC document with account ID
            kyc_doc.razorpay_account_id = account_id
            kyc_doc.razorpay_account_status = "active"
            
            db.commit()
            
            logger.info(f"Created linked account {account_id} for freelancer {freelancer_id}")
            
            return account_id
            
        except (PaymentError, RazorpayError):
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating linked account: {str(e)}")
            raise PaymentError(f"Failed to create linked account: {str(e)}")
    
    def process_payout(
        self,
        db: Session,
        milestone_id: str,
        freelancer_id: str
    ) -> Transaction:
        """Process payout to freelancer after milestone approval.
        
        This releases funds from escrow to the freelancer's linked account
        after deducting platform commission.
        
        Args:
            db: Database session
            milestone_id: Milestone ID
            freelancer_id: Freelancer ID
            
        Returns:
            Transaction object
            
        Raises:
            PaymentError: If payout fails
        """
        try:
            # Get milestone
            milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
            
            if not milestone:
                raise PaymentError(f"Milestone {milestone_id} not found")
            
            if milestone.status != MilestoneStatus.APPROVED:
                raise PaymentError("Milestone must be approved before payout")
            
            # Get deal and freelancer
            deal = milestone.deal
            freelancer = db.query(Freelancer).filter(Freelancer.id == freelancer_id).first()
            
            if not freelancer:
                raise PaymentError(f"Freelancer {freelancer_id} not found")
            
            if deal.freelancer_id != freelancer_id:
                raise PaymentError("Freelancer doesn't own this deal")
            
            # Check KYC status
            if freelancer.kyc_status != "Approved":
                raise PaymentError("KYC must be approved before payout")
            
            # Get KYC document with linked account
            kyc_doc = db.query(KYCDocument).filter(
                KYCDocument.freelancer_id == freelancer_id,
                KYCDocument.status == "approved"  # Use lowercase string
            ).first()
            
            if not kyc_doc or not kyc_doc.razorpay_account_id:
                raise PaymentError("Linked account not found. Please complete KYC setup.")
            
            # Get payment for this milestone
            payment = db.query(Payment).filter(
                Payment.milestone_id == milestone_id,
                Payment.status == "completed"  # Use lowercase string
            ).first()
            
            if not payment:
                raise PaymentError("No completed payment found for this milestone")
            
            # Calculate payout amount
            # The milestone.amount is what business owner paid
            # Platform commission is already calculated in payment record
            # Freelancer receives 85% of milestone amount
            milestone_amount = milestone.amount
            platform_commission = int(milestone_amount * self.PLATFORM_COMMISSION_RATE)
            payout_amount = milestone_amount - platform_commission
            
            logger.info(
                f"Payout calculation: Milestone amount ₹{milestone_amount/100}, "
                f"Platform commission ₹{platform_commission/100}, "
                f"Freelancer payout ₹{payout_amount/100}"
            )
            
            # Create payout via Razorpay Route
            if self.razorpay_enabled and kyc_doc.razorpay_account_id:
                try:
                    # In production, use actual Razorpay Route transfer API
                    # transfer = self.client.transfer.create({
                    #     "account": kyc_doc.razorpay_account_id,
                    #     "amount": payout_amount,
                    #     "currency": "INR",
                    #     "notes": {
                    #         "deal_id": deal.id,
                    #         "milestone_id": milestone_id,
                    #         "freelancer_id": freelancer_id
                    #     }
                    # })
                    # transfer_id = transfer["id"]
                    
                    # Mock for development
                    transfer_id = f"trf_mock_{uuid.uuid4().hex[:16]}"
                    logger.info(f"[MOCK] Created transfer: {transfer_id} for ₹{payout_amount/100}")
                    
                except Exception as e:
                    logger.error(f"Razorpay transfer failed: {str(e)}")
                    raise RazorpayError(f"Failed to process payout: {str(e)}")
            else:
                # Mock transfer ID for development
                transfer_id = f"trf_dev_{uuid.uuid4().hex[:16]}"
                logger.info(f"[DEV] Mock transfer: {transfer_id} for ₹{payout_amount/100}")
            
            # Create release transaction
            transaction = Transaction(
                id=str(uuid.uuid4()),
                payment_id=payment.id,
                deal_id=deal.id,
                milestone_id=milestone_id,
                type=TransactionType.RELEASE,
                amount=payout_amount,  # Amount freelancer receives
                commission=platform_commission,  # Amount platform keeps
                status=PaymentStatus.COMPLETED,
                payment_provider_id=transfer_id,
                completed_at=datetime.utcnow()
            )
            
            db.add(transaction)
            
            # Update milestone status
            milestone.status = MilestoneStatus.PAID
            milestone.paid_at = datetime.utcnow()
            
            # Update freelancer earnings
            freelancer.total_earnings += payout_amount
            
            db.commit()
            db.refresh(transaction)
            
            logger.info(
                f"Payout processed for milestone {milestone_id}: "
                f"₹{payout_amount/100} (platform commission: ₹{platform_commission/100})"
            )
            
            return transaction
            
        except (PaymentError, RazorpayError):
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error processing payout: {str(e)}")
            raise PaymentError(f"Failed to process payout: {str(e)}")
    
    def get_payout_eligibility(
        self,
        db: Session,
        freelancer_id: str
    ) -> Dict:
        """Check if freelancer is eligible for payouts.
        
        Args:
            db: Database session
            freelancer_id: Freelancer ID
            
        Returns:
            Dictionary with eligibility status and details
        """
        freelancer = db.query(Freelancer).filter(Freelancer.id == freelancer_id).first()
        
        if not freelancer:
            return {
                "eligible": False,
                "reason": "Freelancer not found"
            }
        
        # Check KYC status
        if freelancer.kyc_status != "Approved":
            return {
                "eligible": False,
                "reason": "KYC not approved",
                "kyc_status": freelancer.kyc_status
            }
        
        # Check linked account
        kyc_doc = db.query(KYCDocument).filter(
            KYCDocument.freelancer_id == freelancer_id,
            KYCDocument.status == "approved"  # Use lowercase string
        ).first()
        
        if not kyc_doc or not kyc_doc.razorpay_account_id:
            return {
                "eligible": False,
                "reason": "Linked account not created",
                "kyc_status": freelancer.kyc_status
            }
        
        return {
            "eligible": True,
            "kyc_status": freelancer.kyc_status,
            "razorpay_account_id": kyc_doc.razorpay_account_id,
            "total_earnings": freelancer.total_earnings / 100  # Convert to rupees
        }
