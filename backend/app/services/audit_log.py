"""Authentication and audit logging service.

Requirement 14.2: Authentication logging - IP + timestamp
"""
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class AuditLogService:
    """Service for logging authentication events and user actions."""
    
    @staticmethod
    def log_login_attempt(
        db: Session,
        user_id: Optional[str],
        email: str,
        ip_address: str,
        user_agent: str,
        success: bool,
        failure_reason: Optional[str] = None
    ):
        """Log a login attempt.
        
        Args:
            db: Database session
            user_id: User ID if login successful
            email: Email used for login
            ip_address: Client IP address
            user_agent: Client user agent
            success: Whether login was successful
            failure_reason: Reason for failure if unsuccessful
        """
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": "login_attempt",
            "user_id": user_id,
            "email": email,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "success": success,
            "failure_reason": failure_reason
        }
        
        if success:
            logger.info(f"Login successful: {email} from {ip_address}")
        else:
            logger.warning(
                f"Login failed: {email} from {ip_address} - {failure_reason}"
            )
        
        # TODO: Store in database table for audit trail
        # For now, logging to application logs
        # In production, create auth_logs table
    
    @staticmethod
    def log_logout(
        db: Session,
        user_id: str,
        ip_address: str
    ):
        """Log a logout event.
        
        Args:
            db: Database session
            user_id: User ID
            ip_address: Client IP address
        """
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": "logout",
            "user_id": user_id,
            "ip_address": ip_address
        }
        
        logger.info(f"Logout: user {user_id} from {ip_address}")
    
    @staticmethod
    def log_password_change(
        db: Session,
        user_id: str,
        ip_address: str,
        success: bool
    ):
        """Log a password change attempt.
        
        Args:
            db: Database session
            user_id: User ID
            ip_address: Client IP address
            success: Whether change was successful
        """
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": "password_change",
            "user_id": user_id,
            "ip_address": ip_address,
            "success": success
        }
        
        if success:
            logger.info(f"Password changed: user {user_id} from {ip_address}")
        else:
            logger.warning(f"Password change failed: user {user_id} from {ip_address}")
    
    @staticmethod
    def log_suspicious_activity(
        db: Session,
        user_id: Optional[str],
        ip_address: str,
        activity_type: str,
        details: str
    ):
        """Log suspicious activity.
        
        Args:
            db: Database session
            user_id: User ID if known
            ip_address: Client IP address
            activity_type: Type of suspicious activity
            details: Additional details
        """
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": "suspicious_activity",
            "user_id": user_id,
            "ip_address": ip_address,
            "activity_type": activity_type,
            "details": details
        }
        
        logger.warning(
            f"Suspicious activity: {activity_type} from {ip_address} - {details}"
        )
    
    @staticmethod
    def check_failed_login_attempts(
        db: Session,
        email: str,
        ip_address: str,
        time_window_minutes: int = 15,
        max_attempts: int = 5
    ) -> bool:
        """Check if there have been too many failed login attempts.
        
        Args:
            db: Database session
            email: Email to check
            ip_address: IP address to check
            time_window_minutes: Time window to check
            max_attempts: Maximum allowed attempts
            
        Returns:
            True if account should be locked, False otherwise
        """
        # TODO: Implement database query to count failed attempts
        # For now, return False (no lockout)
        # In production, query auth_logs table
        return False
