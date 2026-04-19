"""Spam detection and prevention service.

This service handles:
- Opt-out rate monitoring
- High opt-out flagging
- Suspicious activity detection
- Automated suspension for spam violations

Requirements: 9.3
"""
import logging
from typing import Dict, List
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models.lead import LeadContact
from ..models.user import Freelancer, User

logger = logging.getLogger(__name__)


class SpamDetectionService:
    """Service for detecting and preventing spam."""
    
    # Thresholds
    HIGH_OPTOUT_THRESHOLD = 0.30  # 30% opt-out rate - warning
    SUSPICIOUS_ACTIVITY_THRESHOLD = 0.50  # 50% opt-out rate - suspension
    MIN_CONTACTS_FOR_ANALYSIS = 10  # Minimum contacts before analyzing
    
    @classmethod
    def check_spam_indicators(
        cls,
        db: Session,
        freelancer_id: str
    ) -> Dict:
        """Check for spam indicators for a freelancer.
        
        Args:
            db: Database session
            freelancer_id: Freelancer ID
            
        Returns:
            Dict with spam analysis results
        """
        freelancer = db.query(Freelancer).filter(
            Freelancer.id == freelancer_id
        ).first()
        
        if not freelancer:
            return {"error": "Freelancer not found"}
        
        # Get contact statistics
        total_contacts = db.query(LeadContact).filter(
            LeadContact.freelancer_id == freelancer_id
        ).count()
        
        if total_contacts < cls.MIN_CONTACTS_FOR_ANALYSIS:
            return {
                "freelancer_id": freelancer_id,
                "status": "insufficient_data",
                "total_contacts": total_contacts,
                "min_required": cls.MIN_CONTACTS_FOR_ANALYSIS,
                "message": f"Need at least {cls.MIN_CONTACTS_FOR_ANALYSIS} contacts for analysis"
            }
        
        # Calculate opt-out rate
        opt_outs = db.query(LeadContact).filter(
            LeadContact.freelancer_id == freelancer_id,
            LeadContact.consent_status == "opted_out"
        ).count()
        
        opt_out_rate = opt_outs / total_contacts if total_contacts > 0 else 0
        
        # Determine status
        if opt_out_rate >= cls.SUSPICIOUS_ACTIVITY_THRESHOLD:
            status = "suspicious"
            action = "suspend"
            message = f"Critical: {opt_out_rate*100:.1f}% opt-out rate. Account suspended."
        elif opt_out_rate >= cls.HIGH_OPTOUT_THRESHOLD:
            status = "warning"
            action = "flag"
            message = f"Warning: {opt_out_rate*100:.1f}% opt-out rate. Account flagged for review."
        else:
            status = "normal"
            action = "none"
            message = f"Normal: {opt_out_rate*100:.1f}% opt-out rate."
        
        return {
            "freelancer_id": freelancer_id,
            "freelancer_name": freelancer.name,
            "status": status,
            "action": action,
            "total_contacts": total_contacts,
            "opt_outs": opt_outs,
            "opt_out_rate": round(opt_out_rate, 3),
            "opt_out_percentage": round(opt_out_rate * 100, 1),
            "message": message,
            "thresholds": {
                "warning": cls.HIGH_OPTOUT_THRESHOLD,
                "suspension": cls.SUSPICIOUS_ACTIVITY_THRESHOLD
            }
        }
    
    @classmethod
    def flag_freelancer(
        cls,
        db: Session,
        freelancer_id: str,
        reason: str
    ) -> bool:
        """Flag a freelancer for review.
        
        Args:
            db: Database session
            freelancer_id: Freelancer ID
            reason: Reason for flagging
            
        Returns:
            True if flagged successfully
        """
        try:
            freelancer = db.query(Freelancer).filter(
                Freelancer.id == freelancer_id
            ).first()
            
            if not freelancer:
                return False
            
            # Add flag fields (these would need to be added to Freelancer model)
            # For now, we'll log it
            logger.warning(
                f"FLAGGED: Freelancer {freelancer_id} ({freelancer.name}) - {reason}"
            )
            
            # In production, you would:
            # freelancer.is_flagged = True
            # freelancer.flag_reason = reason
            # freelancer.flagged_at = datetime.now(timezone.utc)
            # db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error flagging freelancer: {str(e)}")
            return False
    
    @classmethod
    def suspend_freelancer(
        cls,
        db: Session,
        freelancer_id: str,
        reason: str
    ) -> bool:
        """Suspend a freelancer for spam violations.
        
        Args:
            db: Database session
            freelancer_id: Freelancer ID
            reason: Reason for suspension
            
        Returns:
            True if suspended successfully
        """
        try:
            freelancer = db.query(Freelancer).filter(
                Freelancer.id == freelancer_id
            ).first()
            
            if not freelancer:
                return False
            
            # Suspend user account
            user = db.query(User).filter(User.id == freelancer.user_id).first()
            if user:
                user.is_active = False
                db.commit()
                
                logger.warning(
                    f"SUSPENDED: Freelancer {freelancer_id} ({freelancer.name}) - {reason}"
                )
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error suspending freelancer: {str(e)}")
            db.rollback()
            return False
    
    @classmethod
    def check_all_freelancers(
        cls,
        db: Session
    ) -> Dict:
        """Check all freelancers for spam indicators.
        
        This should be run as a background job.
        
        Args:
            db: Database session
            
        Returns:
            Dict with summary of actions taken
        """
        freelancers = db.query(Freelancer).join(User).filter(
            User.is_active == True
        ).all()
        
        flagged = []
        suspended = []
        warnings = []
        
        for freelancer in freelancers:
            result = cls.check_spam_indicators(db, freelancer.id)
            
            if result.get("status") == "insufficient_data":
                continue
            
            if result.get("action") == "suspend":
                if cls.suspend_freelancer(
                    db,
                    freelancer.id,
                    f"High opt-out rate: {result['opt_out_percentage']}%"
                ):
                    suspended.append({
                        "freelancer_id": freelancer.id,
                        "name": freelancer.name,
                        "opt_out_rate": result["opt_out_percentage"]
                    })
            
            elif result.get("action") == "flag":
                if cls.flag_freelancer(
                    db,
                    freelancer.id,
                    f"High opt-out rate: {result['opt_out_percentage']}%"
                ):
                    flagged.append({
                        "freelancer_id": freelancer.id,
                        "name": freelancer.name,
                        "opt_out_rate": result["opt_out_percentage"]
                    })
            
            if result.get("status") == "warning":
                warnings.append({
                    "freelancer_id": freelancer.id,
                    "name": freelancer.name,
                    "opt_out_rate": result["opt_out_percentage"]
                })
        
        summary = {
            "total_checked": len(freelancers),
            "flagged_count": len(flagged),
            "suspended_count": len(suspended),
            "warning_count": len(warnings),
            "flagged": flagged,
            "suspended": suspended,
            "warnings": warnings,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        if suspended:
            logger.warning(f"Spam detection: Suspended {len(suspended)} freelancers")
        if flagged:
            logger.warning(f"Spam detection: Flagged {len(flagged)} freelancers")
        
        return summary
    
    @classmethod
    def get_flagged_freelancers(
        cls,
        db: Session
    ) -> List[Dict]:
        """Get all freelancers with high opt-out rates.
        
        Args:
            db: Database session
            
        Returns:
            List of freelancers with spam indicators
        """
        freelancers = db.query(Freelancer).join(User).filter(
            User.is_active == True
        ).all()
        
        flagged = []
        
        for freelancer in freelancers:
            result = cls.check_spam_indicators(db, freelancer.id)
            
            if result.get("status") in ["warning", "suspicious"]:
                flagged.append(result)
        
        return flagged
