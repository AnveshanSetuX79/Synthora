"""Notification service for creating and managing notifications.

Requirement 16: Notification System
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timezone
import uuid
import logging

from ..models.notification import Notification, NotificationPreference
from ..models.user import User
from .email import EmailService

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for managing notifications."""
    
    @staticmethod
    def create_notification(
        db: Session,
        user_id: str,
        type: str,
        title: str,
        message: str,
        link: Optional[str] = None
    ) -> Notification:
        """Create a new in-app notification.
        
        Args:
            db: Database session
            user_id: User ID to notify
            type: Notification type
            title: Notification title
            message: Notification message
            link: Optional link to relevant page
            
        Returns:
            Created notification
        """
        notification = Notification(
            id=str(uuid.uuid4()),
            user_id=user_id,
            type=type,
            title=title,
            message=message,
            link=link,
            is_read=False,
            created_at=datetime.now(timezone.utc)
        )
        
        db.add(notification)
        db.commit()
        db.refresh(notification)
        
        logger.info(f"Created notification for user {user_id}: {type}")
        return notification
    
    @staticmethod
    def get_user_notifications(
        db: Session,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        unread_only: bool = False
    ) -> List[Notification]:
        """Get user's notifications.
        
        Args:
            db: Database session
            user_id: User ID
            limit: Maximum number of notifications
            offset: Offset for pagination
            unread_only: Only return unread notifications
            
        Returns:
            List of notifications
        """
        query = db.query(Notification).filter(Notification.user_id == user_id)
        
        if unread_only:
            query = query.filter(Notification.is_read == False)
        
        notifications = query.order_by(Notification.created_at.desc()).limit(limit).offset(offset).all()
        return notifications
    
    @staticmethod
    def get_unread_count(db: Session, user_id: str) -> int:
        """Get count of unread notifications.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Count of unread notifications
        """
        count = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).count()
        return count
    
    @staticmethod
    def mark_as_read(db: Session, notification_id: str, user_id: str) -> bool:
        """Mark notification as read.
        
        Args:
            db: Database session
            notification_id: Notification ID
            user_id: User ID (for security)
            
        Returns:
            True if successful, False otherwise
        """
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if not notification:
            return False
        
        notification.is_read = True
        notification.read_at = datetime.now(timezone.utc)
        db.commit()
        
        return True
    
    @staticmethod
    def mark_all_as_read(db: Session, user_id: str) -> int:
        """Mark all notifications as read.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Number of notifications marked as read
        """
        count = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({
            'is_read': True,
            'read_at': datetime.now(timezone.utc)
        })
        
        db.commit()
        return count
    
    @staticmethod
    def delete_notification(db: Session, notification_id: str, user_id: str) -> bool:
        """Delete a notification.
        
        Args:
            db: Database session
            notification_id: Notification ID
            user_id: User ID (for security)
            
        Returns:
            True if successful, False otherwise
        """
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if not notification:
            return False
        
        db.delete(notification)
        db.commit()
        
        return True
    
    @staticmethod
    def clear_all_notifications(db: Session, user_id: str) -> int:
        """Clear all notifications for a user.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Number of notifications deleted
        """
        count = db.query(Notification).filter(
            Notification.user_id == user_id
        ).delete()
        
        db.commit()
        return count
    
    @staticmethod
    def get_preferences(db: Session, user_id: str) -> NotificationPreference:
        """Get user's notification preferences.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Notification preferences (creates default if not exists)
        """
        prefs = db.query(NotificationPreference).filter(
            NotificationPreference.user_id == user_id
        ).first()
        
        if not prefs:
            # Create default preferences
            prefs = NotificationPreference(
                id=str(uuid.uuid4()),
                user_id=user_id
            )
            db.add(prefs)
            db.commit()
            db.refresh(prefs)
        
        return prefs
    
    @staticmethod
    def update_preferences(
        db: Session,
        user_id: str,
        preferences: dict
    ) -> NotificationPreference:
        """Update user's notification preferences.
        
        Args:
            db: Database session
            user_id: User ID
            preferences: Dictionary of preference updates
            
        Returns:
            Updated preferences
        """
        prefs = NotificationService.get_preferences(db, user_id)
        
        # Update preferences
        for key, value in preferences.items():
            if hasattr(prefs, key):
                setattr(prefs, key, value)
        
        prefs.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(prefs)
        
        return prefs
    
    @staticmethod
    def notify_new_message(
        db: Session,
        recipient_id: str,
        sender_name: str,
        message_preview: str,
        conversation_link: str
    ):
        """Send notification for new message.
        
        Args:
            db: Database session
            recipient_id: User ID of recipient
            sender_name: Name of sender
            message_preview: Preview of message
            conversation_link: Link to conversation
        """
        # Get preferences
        prefs = NotificationService.get_preferences(db, recipient_id)
        
        # Create in-app notification
        if prefs.inapp_new_message:
            NotificationService.create_notification(
                db=db,
                user_id=recipient_id,
                type='message',
                title=f'New message from {sender_name}',
                message=message_preview,
                link=conversation_link
            )
        
        # Send email notification
        if prefs.email_new_message:
            user = db.query(User).filter(User.id == recipient_id).first()
            if user:
                email_service = EmailService()
                try:
                    email_service.send_notification_email(
                        to_email=user.email,
                        recipient_name=user.email.split('@')[0],
                        notification_type='new_message',
                        sender_name=sender_name,
                        message_preview=message_preview,
                        link=conversation_link
                    )
                except Exception as e:
                    logger.error(f"Failed to send email notification: {e}")
    
    @staticmethod
    def notify_milestone_submitted(
        db: Session,
        business_owner_id: str,
        freelancer_name: str,
        deal_title: str,
        milestone_title: str,
        milestone_link: str
    ):
        """Send notification for milestone submission.
        
        Args:
            db: Database session
            business_owner_id: Business owner user ID
            freelancer_name: Name of freelancer
            deal_title: Deal title
            milestone_title: Milestone title
            milestone_link: Link to milestone
        """
        prefs = NotificationService.get_preferences(db, business_owner_id)
        
        if prefs.inapp_milestone_submitted:
            NotificationService.create_notification(
                db=db,
                user_id=business_owner_id,
                type='milestone',
                title=f'Milestone submitted: {milestone_title}',
                message=f'{freelancer_name} submitted a milestone for {deal_title}',
                link=milestone_link
            )
        
        if prefs.email_milestone_submitted:
            user = db.query(User).filter(User.id == business_owner_id).first()
            if user:
                email_service = EmailService()
                try:
                    email_service.send_notification_email(
                        to_email=user.email,
                        recipient_name=user.email.split('@')[0],
                        notification_type='milestone_submitted',
                        freelancer_name=freelancer_name,
                        deal_title=deal_title,
                        milestone_title=milestone_title,
                        link=milestone_link
                    )
                except Exception as e:
                    logger.error(f"Failed to send email notification: {e}")
    
    @staticmethod
    def notify_payment_processed(
        db: Session,
        user_id: str,
        amount: int,
        deal_title: str,
        payment_link: str
    ):
        """Send notification for payment processed.
        
        Args:
            db: Database session
            user_id: User ID
            amount: Payment amount in paise
            deal_title: Deal title
            payment_link: Link to payment details
        """
        prefs = NotificationService.get_preferences(db, user_id)
        
        amount_rupees = amount / 100
        
        if prefs.inapp_payment_processed:
            NotificationService.create_notification(
                db=db,
                user_id=user_id,
                type='payment',
                title=f'Payment processed: ₹{amount_rupees:.2f}',
                message=f'Payment for {deal_title} has been processed',
                link=payment_link
            )
        
        if prefs.email_payment_processed:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                email_service = EmailService()
                try:
                    email_service.send_notification_email(
                        to_email=user.email,
                        recipient_name=user.email.split('@')[0],
                        notification_type='payment_processed',
                        amount=amount_rupees,
                        deal_title=deal_title,
                        link=payment_link
                    )
                except Exception as e:
                    logger.error(f"Failed to send email notification: {e}")
