"""Retry service for handling failed operations."""
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_
import uuid

from ..models.failure_log import FailureLog, FailureStatus
from .sms import SMSService, SMSError
from .email import EmailService
from .payment import PaymentService

logger = logging.getLogger(__name__)


class RetryService:
    """Service for managing retry logic and failure recovery."""
    
    # Retry configuration
    SMS_MAX_ATTEMPTS = 3
    SMS_RETRY_INTERVAL = 300  # 5 minutes in seconds
    
    EMAIL_MAX_ATTEMPTS = 3
    EMAIL_RETRY_INTERVAL = 300  # 5 minutes in seconds
    
    PAYMENT_MAX_ATTEMPTS = 3
    PAYMENT_RETRY_INTERVAL = 3600  # 1 hour in seconds
    
    def __init__(self, db: Session):
        """Initialize retry service."""
        self.db = db
        self.sms_service = SMSService()
        self.email_service = EmailService()
        self.payment_service = PaymentService()
    
    def log_failure(
        self,
        service: str,
        operation: str,
        target: str,
        error_message: str,
        error_code: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> FailureLog:
        """Log a failure for retry processing.
        
        Args:
            service: Service name ('sms', 'email', 'payment')
            operation: Operation that failed
            target: Target identifier (phone/email/payment_id)
            error_message: Error message
            error_code: Optional error code
            metadata: Optional metadata
            
        Returns:
            FailureLog object
        """
        try:
            # Determine max attempts and retry interval based on service
            if service == 'sms':
                max_attempts = self.SMS_MAX_ATTEMPTS
                retry_interval = self.SMS_RETRY_INTERVAL
            elif service == 'email':
                max_attempts = self.EMAIL_MAX_ATTEMPTS
                retry_interval = self.EMAIL_RETRY_INTERVAL
            elif service == 'payment':
                max_attempts = self.PAYMENT_MAX_ATTEMPTS
                retry_interval = self.PAYMENT_RETRY_INTERVAL
            else:
                max_attempts = 3
                retry_interval = 300
            
            # Calculate next retry time
            next_retry_at = datetime.now(timezone.utc) + timedelta(seconds=retry_interval)
            
            # Create failure log
            failure_log = FailureLog(
                id=str(uuid.uuid4()),
                service=service,
                operation=operation,
                target=target,
                attempt_number=1,
                max_attempts=max_attempts,
                error_message=error_message,
                error_code=error_code,
                failure_metadata=metadata or {},  # Renamed from 'metadata'
                status=FailureStatus.PENDING.value,
                next_retry_at=next_retry_at
            )
            
            self.db.add(failure_log)
            self.db.commit()
            self.db.refresh(failure_log)
            
            logger.info(f"Logged failure for {service}/{operation}: {failure_log.id}")
            
            return failure_log
            
        except Exception as e:
            logger.error(f"Error logging failure: {str(e)}")
            self.db.rollback()
            raise
    
    async def process_retry_queue(self) -> Dict[str, int]:
        """Process all pending retries.
        
        Returns:
            Dictionary with retry statistics
        """
        try:
            now = datetime.now(timezone.utc)
            
            # Get all pending retries that are due
            pending_retries = self.db.query(FailureLog).filter(
                and_(
                    FailureLog.status.in_([FailureStatus.PENDING.value, FailureStatus.RETRYING.value]),
                    FailureLog.next_retry_at <= now,
                    FailureLog.attempt_number < FailureLog.max_attempts
                )
            ).all()
            
            stats = {
                'processed': 0,
                'succeeded': 0,
                'failed': 0,
                'fallback': 0
            }
            
            for failure_log in pending_retries:
                stats['processed'] += 1
                
                try:
                    # Attempt retry based on service
                    if failure_log.service == 'sms':
                        success = await self._retry_sms(failure_log)
                    elif failure_log.service == 'email':
                        success = await self._retry_email(failure_log)
                    elif failure_log.service == 'payment':
                        success = await self._retry_payment(failure_log)
                    else:
                        logger.warning(f"Unknown service: {failure_log.service}")
                        continue
                    
                    if success:
                        stats['succeeded'] += 1
                        failure_log.status = FailureStatus.RESOLVED.value
                        failure_log.resolved_at = datetime.now(timezone.utc)
                    else:
                        stats['failed'] += 1
                        failure_log.attempt_number += 1
                        
                        # Check if max attempts reached
                        if failure_log.attempt_number >= failure_log.max_attempts:
                            failure_log.status = FailureStatus.FAILED.value
                            
                            # Attempt fallback for SMS
                            if failure_log.service == 'sms' and not failure_log.fallback_attempted:
                                await self._fallback_sms_to_email(failure_log)
                                stats['fallback'] += 1
                            
                            # Notify admin for email and payment failures
                            if failure_log.service in ['email', 'payment'] and not failure_log.admin_notified:
                                await self._notify_admin(failure_log)
                        else:
                            # Schedule next retry
                            failure_log.status = FailureStatus.RETRYING.value
                            retry_interval = self._get_retry_interval(failure_log.service)
                            failure_log.next_retry_at = datetime.now(timezone.utc) + timedelta(seconds=retry_interval)
                    
                    failure_log.updated_at = datetime.now(timezone.utc)
                    self.db.commit()
                    
                except Exception as e:
                    logger.error(f"Error processing retry for {failure_log.id}: {str(e)}")
                    self.db.rollback()
                    continue
            
            logger.info(f"Processed {stats['processed']} retries: {stats['succeeded']} succeeded, {stats['failed']} failed, {stats['fallback']} fallback")
            
            return stats
            
        except Exception as e:
            logger.error(f"Error processing retry queue: {str(e)}")
            return {'processed': 0, 'succeeded': 0, 'failed': 0, 'fallback': 0}
    
    async def _retry_sms(self, failure_log: FailureLog) -> bool:
        """Retry SMS sending.
        
        Args:
            failure_log: FailureLog object
            
        Returns:
            True if successful, False otherwise
        """
        try:
            metadata = failure_log.failure_metadata or {}
            phone = failure_log.target
            message = metadata.get('message', '')
            opt_out_link = metadata.get('opt_out_link')
            
            result = self.sms_service.send_sms(phone, message, opt_out_link)
            
            if result.get('status') in ['sent', 'delivered', 'simulated']:
                logger.info(f"SMS retry successful for {failure_log.id}")
                return True
            else:
                logger.warning(f"SMS retry failed for {failure_log.id}")
                return False
                
        except SMSError as e:
            logger.error(f"SMS retry error for {failure_log.id}: {str(e)}")
            failure_log.error_message = str(e)
            return False
        except Exception as e:
            logger.error(f"Unexpected error in SMS retry for {failure_log.id}: {str(e)}")
            failure_log.error_message = str(e)
            return False
    
    async def _retry_email(self, failure_log: FailureLog) -> bool:
        """Retry email sending.
        
        Args:
            failure_log: FailureLog object
            
        Returns:
            True if successful, False otherwise
        """
        try:
            metadata = failure_log.failure_metadata or {}
            to_email = failure_log.target
            subject = metadata.get('subject', 'Message from LocalAI Leads')
            body_text = metadata.get('body_text', '')
            body_html = metadata.get('body_html')
            
            result = self.email_service.send_email(to_email, subject, body_text, body_html)
            
            if result.get('success'):
                logger.info(f"Email retry successful for {failure_log.id}")
                return True
            else:
                logger.warning(f"Email retry failed for {failure_log.id}")
                return False
                
        except Exception as e:
            logger.error(f"Email retry error for {failure_log.id}: {str(e)}")
            failure_log.error_message = str(e)
            return False
    
    async def _retry_payment(self, failure_log: FailureLog) -> bool:
        """Retry payment processing.
        
        Args:
            failure_log: FailureLog object
            
        Returns:
            True if successful, False otherwise
        """
        try:
            metadata = failure_log.failure_metadata or {}
            payment_id = failure_log.target
            
            # Payment retry logic would go here
            # This depends on your payment provider's retry capabilities
            logger.info(f"Payment retry attempted for {failure_log.id}")
            
            # For now, return False as payment retries need specific implementation
            return False
                
        except Exception as e:
            logger.error(f"Payment retry error for {failure_log.id}: {str(e)}")
            failure_log.error_message = str(e)
            return False
    
    async def _fallback_sms_to_email(self, failure_log: FailureLog) -> bool:
        """Fallback from SMS to email after max attempts.
        
        Args:
            failure_log: FailureLog object
            
        Returns:
            True if fallback successful, False otherwise
        """
        try:
            metadata = failure_log.failure_metadata or {}
            email = metadata.get('fallback_email')
            
            if not email:
                logger.warning(f"No fallback email for SMS failure {failure_log.id}")
                return False
            
            message = metadata.get('message', '')
            subject = "Important Message from LocalAI Leads"
            body_text = f"We tried to reach you via SMS but were unable to deliver the message.\n\n{message}"
            
            result = self.email_service.send_email(email, subject, body_text)
            
            failure_log.fallback_attempted = True
            failure_log.status = FailureStatus.FALLBACK.value
            
            if result.get('success'):
                logger.info(f"SMS fallback to email successful for {failure_log.id}")
                return True
            else:
                logger.warning(f"SMS fallback to email failed for {failure_log.id}")
                return False
                
        except Exception as e:
            logger.error(f"Error in SMS fallback for {failure_log.id}: {str(e)}")
            return False
    
    async def _notify_admin(self, failure_log: FailureLog) -> bool:
        """Notify admin of critical failure.
        
        Args:
            failure_log: FailureLog object
            
        Returns:
            True if notification successful, False otherwise
        """
        try:
            admin_email = "admin@localaileads.com"  # Configure this
            subject = f"Critical Failure Alert: {failure_log.service.upper()}"
            body_text = f"""Critical failure detected:

Service: {failure_log.service}
Operation: {failure_log.operation}
Target: {failure_log.target}
Attempts: {failure_log.attempt_number}/{failure_log.max_attempts}
Error: {failure_log.error_message}
Created: {failure_log.created_at}

Please review and take action in the admin panel.
"""
            
            result = self.email_service.send_email(admin_email, subject, body_text)
            
            failure_log.admin_notified = True
            
            if result.get('success'):
                logger.info(f"Admin notified for failure {failure_log.id}")
                return True
            else:
                logger.warning(f"Failed to notify admin for {failure_log.id}")
                return False
                
        except Exception as e:
            logger.error(f"Error notifying admin for {failure_log.id}: {str(e)}")
            return False
    
    def _get_retry_interval(self, service: str) -> int:
        """Get retry interval for service.
        
        Args:
            service: Service name
            
        Returns:
            Retry interval in seconds
        """
        if service == 'sms':
            return self.SMS_RETRY_INTERVAL
        elif service == 'email':
            return self.EMAIL_RETRY_INTERVAL
        elif service == 'payment':
            return self.PAYMENT_RETRY_INTERVAL
        else:
            return 300  # Default 5 minutes
    
    def manual_retry(self, failure_log_id: str, admin_id: str) -> bool:
        """Manually retry a failed operation.
        
        Args:
            failure_log_id: FailureLog ID
            admin_id: Admin user ID
            
        Returns:
            True if retry initiated, False otherwise
        """
        try:
            failure_log = self.db.query(FailureLog).filter(FailureLog.id == failure_log_id).first()
            
            if not failure_log:
                logger.warning(f"Failure log not found: {failure_log_id}")
                return False
            
            # Reset for manual retry
            failure_log.status = FailureStatus.PENDING.value
            failure_log.next_retry_at = datetime.now(timezone.utc)
            failure_log.updated_at = datetime.now(timezone.utc)
            
            self.db.commit()
            
            logger.info(f"Manual retry initiated for {failure_log_id} by admin {admin_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error in manual retry: {str(e)}")
            self.db.rollback()
            return False
    
    def resolve_failure(self, failure_log_id: str, admin_id: str) -> bool:
        """Manually resolve a failure.
        
        Args:
            failure_log_id: FailureLog ID
            admin_id: Admin user ID
            
        Returns:
            True if resolved, False otherwise
        """
        try:
            failure_log = self.db.query(FailureLog).filter(FailureLog.id == failure_log_id).first()
            
            if not failure_log:
                logger.warning(f"Failure log not found: {failure_log_id}")
                return False
            
            failure_log.status = FailureStatus.RESOLVED.value
            failure_log.resolved_at = datetime.now(timezone.utc)
            failure_log.resolved_by = admin_id
            failure_log.updated_at = datetime.now(timezone.utc)
            
            self.db.commit()
            
            logger.info(f"Failure {failure_log_id} resolved by admin {admin_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error resolving failure: {str(e)}")
            self.db.rollback()
            return False
