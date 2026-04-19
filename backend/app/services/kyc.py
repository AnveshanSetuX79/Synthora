"""KYC verification service.

This service handles:
- KYC document submission
- Document verification
- Status tracking
- Bank account validation

Requirements: 4.4, 4.5, 8.6
"""
import logging
from typing import Dict, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
import uuid

from ..models.kyc import KYCDocument, KYCDocumentType, KYCVerificationStatus
from ..models.user import Freelancer

logger = logging.getLogger(__name__)


class KYCError(Exception):
    """Base exception for KYC errors."""
    pass


class KYCService:
    """Service for managing KYC verification."""
    
    def submit_kyc(
        self,
        db: Session,
        freelancer_id: str,
        document_type: str,
        document_number: str,
        document_url: Optional[str] = None,
        bank_account_number: Optional[str] = None,
        bank_ifsc_code: Optional[str] = None,
        bank_account_holder_name: Optional[str] = None
    ) -> KYCDocument:
        """Submit KYC documents for verification.
        
        Args:
            db: Database session
            freelancer_id: Freelancer ID
            document_type: Document type (Aadhaar, PAN, etc.)
            document_number: Document number
            document_url: Optional document file URL
            bank_account_number: Bank account number
            bank_ifsc_code: Bank IFSC code
            bank_account_holder_name: Account holder name
            
        Returns:
            KYCDocument object
            
        Raises:
            KYCError: If submission fails
        """
        try:
            # Get freelancer
            freelancer = db.query(Freelancer).filter(Freelancer.id == freelancer_id).first()
            
            if not freelancer:
                raise KYCError(f"Freelancer {freelancer_id} not found")
            
            # Check if KYC already submitted
            existing_kyc = db.query(KYCDocument).filter(
                KYCDocument.freelancer_id == freelancer_id,
                KYCDocument.status.in_([
                    KYCVerificationStatus.SUBMITTED,
                    KYCVerificationStatus.UNDER_REVIEW,
                    KYCVerificationStatus.APPROVED
                ])
            ).first()
            
            if existing_kyc:
                raise KYCError(f"KYC already submitted with status: {existing_kyc.status.value}")
            
            # Validate document type
            try:
                doc_type = KYCDocumentType(document_type)
            except ValueError:
                raise KYCError(f"Invalid document type: {document_type}")
            
            # Create KYC document
            kyc_doc = KYCDocument(
                id=str(uuid.uuid4()),
                freelancer_id=freelancer_id,
                document_type=doc_type,
                document_number=document_number,
                document_url=document_url,
                bank_account_number=bank_account_number,
                bank_ifsc_code=bank_ifsc_code,
                bank_account_holder_name=bank_account_holder_name,
                status=KYCVerificationStatus.SUBMITTED,
                submitted_at=datetime.utcnow()
            )
            
            db.add(kyc_doc)
            
            # Update freelancer KYC status
            freelancer.kyc_status = "Submitted"
            
            db.commit()
            db.refresh(kyc_doc)
            
            logger.info(f"KYC submitted for freelancer {freelancer_id}: {document_type}")
            
            return kyc_doc
            
        except KYCError:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error submitting KYC: {str(e)}")
            raise KYCError(f"Failed to submit KYC: {str(e)}")
    
    def verify_kyc(
        self,
        db: Session,
        kyc_document_id: str,
        admin_id: str,
        approved: bool,
        rejection_reason: Optional[str] = None
    ) -> KYCDocument:
        """Verify or reject KYC document (admin only).
        
        Args:
            db: Database session
            kyc_document_id: KYC document ID
            admin_id: Admin user ID
            approved: True to approve, False to reject
            rejection_reason: Optional rejection reason
            
        Returns:
            Updated KYCDocument object
            
        Raises:
            KYCError: If verification fails
        """
        try:
            kyc_doc = db.query(KYCDocument).filter(KYCDocument.id == kyc_document_id).first()
            
            if not kyc_doc:
                raise KYCError(f"KYC document {kyc_document_id} not found")
            
            status_value = kyc_doc.status.value if hasattr(kyc_doc.status, 'value') else kyc_doc.status
            if status_value == "approved":
                raise KYCError("KYC already approved")
            
            # Update status
            if approved:
                kyc_doc.status = KYCVerificationStatus.APPROVED
                kyc_doc.verified_at = datetime.utcnow()
                
                # Update freelancer KYC status
                freelancer = kyc_doc.freelancer
                freelancer.kyc_status = "Approved"
                
                logger.info(f"KYC approved for document {kyc_document_id}")
            else:
                kyc_doc.status = KYCVerificationStatus.REJECTED
                kyc_doc.rejection_reason = rejection_reason
                
                # Update freelancer KYC status
                freelancer = kyc_doc.freelancer
                freelancer.kyc_status = "Rejected"
                
                logger.info(f"KYC rejected for document {kyc_document_id}: {rejection_reason}")
            
            kyc_doc.verified_by = admin_id
            
            db.commit()
            db.refresh(kyc_doc)
            
            return kyc_doc
            
        except KYCError:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error verifying KYC: {str(e)}")
            raise KYCError(f"Failed to verify KYC: {str(e)}")
    
    def get_kyc_status(
        self,
        db: Session,
        freelancer_id: str
    ) -> Dict:
        """Get KYC status for a freelancer.
        
        Args:
            db: Database session
            freelancer_id: Freelancer ID
            
        Returns:
            Dictionary with KYC status information
        """
        freelancer = db.query(Freelancer).filter(Freelancer.id == freelancer_id).first()
        
        if not freelancer:
            return {
                "status": "NotFound",
                "message": "Freelancer not found"
            }
        
        # Get latest KYC document
        kyc_doc = db.query(KYCDocument).filter(
            KYCDocument.freelancer_id == freelancer_id
        ).order_by(KYCDocument.created_at.desc()).first()
        
        if not kyc_doc:
            return {
                "status": "Pending",
                "message": "No KYC documents submitted",
                "kyc_required": True
            }
        
        return {
            "status": kyc_doc.status.value,
            "document_type": kyc_doc.document_type.value if kyc_doc.document_type else None,
            "submitted_at": kyc_doc.submitted_at.isoformat() if kyc_doc.submitted_at else None,
            "verified_at": kyc_doc.verified_at.isoformat() if kyc_doc.verified_at else None,
            "rejection_reason": kyc_doc.rejection_reason,
            "has_bank_details": bool(kyc_doc.bank_account_number),
            "has_linked_account": bool(kyc_doc.razorpay_account_id),
            "kyc_required": kyc_doc.status != KYCVerificationStatus.APPROVED
        }
    
    def get_pending_kyc_submissions(
        self,
        db: Session,
        limit: int = 50
    ) -> List[Dict]:
        """Get pending KYC submissions for admin review.
        
        Args:
            db: Database session
            limit: Maximum number of submissions to return
            
        Returns:
            List of pending KYC submissions
        """
        kyc_docs = db.query(KYCDocument).filter(
            KYCDocument.status.in_([
                KYCVerificationStatus.SUBMITTED,
                KYCVerificationStatus.UNDER_REVIEW
            ])
        ).order_by(KYCDocument.submitted_at.asc()).limit(limit).all()
        
        return [
            {
                "id": doc.id,
                "freelancer_id": doc.freelancer_id,
                "freelancer_name": doc.freelancer.name,
                "document_type": doc.document_type.value,
                "document_number": doc.document_number,
                "document_url": doc.document_url,
                "bank_account_number": doc.bank_account_number,
                "bank_ifsc_code": doc.bank_ifsc_code,
                "bank_account_holder_name": doc.bank_account_holder_name,
                "status": doc.status.value,
                "submitted_at": doc.submitted_at.isoformat() if doc.submitted_at else None
            }
            for doc in kyc_docs
        ]
