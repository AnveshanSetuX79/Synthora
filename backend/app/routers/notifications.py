"""Notification API endpoints.

Requirement 16: Notification System
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from ..database import get_db
from ..middleware.auth import get_current_user
from ..services.notification_service import NotificationService
from ..models.notification import Notification, NotificationPreference

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


# Pydantic schemas
class NotificationResponse(BaseModel):
    id: str
    type: str
    title: str
    message: str
    link: Optional[str]
    is_read: bool
    created_at: str
    read_at: Optional[str]
    
    class Config:
        from_attributes = True


class NotificationPreferenceResponse(BaseModel):
    id: str
    user_id: str
    email_new_message: bool
    email_milestone_submitted: bool
    email_milestone_approved: bool
    email_milestone_rejected: bool
    email_dispute_raised: bool
    email_payment_processed: bool
    inapp_new_message: bool
    inapp_milestone_submitted: bool
    inapp_milestone_approved: bool
    inapp_milestone_rejected: bool
    inapp_dispute_raised: bool
    inapp_payment_processed: bool
    
    class Config:
        from_attributes = True


class NotificationPreferenceUpdate(BaseModel):
    email_new_message: Optional[bool] = None
    email_milestone_submitted: Optional[bool] = None
    email_milestone_approved: Optional[bool] = None
    email_milestone_rejected: Optional[bool] = None
    email_dispute_raised: Optional[bool] = None
    email_payment_processed: Optional[bool] = None
    inapp_new_message: Optional[bool] = None
    inapp_milestone_submitted: Optional[bool] = None
    inapp_milestone_approved: Optional[bool] = None
    inapp_milestone_rejected: Optional[bool] = None
    inapp_dispute_raised: Optional[bool] = None
    inapp_payment_processed: Optional[bool] = None


@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    limit: int = 50,
    offset: int = 0,
    unread_only: bool = False,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's notifications with pagination.
    
    Query Parameters:
    - limit: Maximum number of notifications (default: 50)
    - offset: Offset for pagination (default: 0)
    - unread_only: Only return unread notifications (default: false)
    """
    user_id = current_user.get("user_id")
    
    notifications = NotificationService.get_user_notifications(
        db=db,
        user_id=user_id,
        limit=limit,
        offset=offset,
        unread_only=unread_only
    )
    
    return [
        NotificationResponse(
            id=n.id,
            type=n.type,
            title=n.title,
            message=n.message,
            link=n.link,
            is_read=n.is_read,
            created_at=n.created_at.isoformat(),
            read_at=n.read_at.isoformat() if n.read_at else None
        )
        for n in notifications
    ]


@router.get("/unread-count")
async def get_unread_count(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get count of unread notifications."""
    user_id = current_user.get("user_id")
    
    count = NotificationService.get_unread_count(db=db, user_id=user_id)
    
    return {"unread_count": count}


@router.post("/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a notification as read."""
    user_id = current_user.get("user_id")
    
    success = NotificationService.mark_as_read(
        db=db,
        notification_id=notification_id,
        user_id=user_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return {"success": True, "message": "Notification marked as read"}


@router.post("/read-all")
async def mark_all_as_read(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read."""
    user_id = current_user.get("user_id")
    
    count = NotificationService.mark_all_as_read(db=db, user_id=user_id)
    
    return {"success": True, "count": count, "message": f"Marked {count} notifications as read"}


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a notification."""
    user_id = current_user.get("user_id")
    
    success = NotificationService.delete_notification(
        db=db,
        notification_id=notification_id,
        user_id=user_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return {"success": True, "message": "Notification deleted"}


@router.delete("/clear-all")
async def clear_all_notifications(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clear all notifications."""
    user_id = current_user.get("user_id")
    
    count = NotificationService.clear_all_notifications(db=db, user_id=user_id)
    
    return {"success": True, "count": count, "message": f"Cleared {count} notifications"}


@router.get("/preferences", response_model=NotificationPreferenceResponse)
async def get_preferences(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's notification preferences."""
    user_id = current_user.get("user_id")
    
    prefs = NotificationService.get_preferences(db=db, user_id=user_id)
    
    return NotificationPreferenceResponse(
        id=prefs.id,
        user_id=prefs.user_id,
        email_new_message=prefs.email_new_message,
        email_milestone_submitted=prefs.email_milestone_submitted,
        email_milestone_approved=prefs.email_milestone_approved,
        email_milestone_rejected=prefs.email_milestone_rejected,
        email_dispute_raised=prefs.email_dispute_raised,
        email_payment_processed=prefs.email_payment_processed,
        inapp_new_message=prefs.inapp_new_message,
        inapp_milestone_submitted=prefs.inapp_milestone_submitted,
        inapp_milestone_approved=prefs.inapp_milestone_approved,
        inapp_milestone_rejected=prefs.inapp_milestone_rejected,
        inapp_dispute_raised=prefs.inapp_dispute_raised,
        inapp_payment_processed=prefs.inapp_payment_processed
    )


@router.put("/preferences", response_model=NotificationPreferenceResponse)
async def update_preferences(
    preferences: NotificationPreferenceUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user's notification preferences."""
    user_id = current_user.get("user_id")
    
    # Convert to dict, excluding None values
    prefs_dict = {k: v for k, v in preferences.dict().items() if v is not None}
    
    updated_prefs = NotificationService.update_preferences(
        db=db,
        user_id=user_id,
        preferences=prefs_dict
    )
    
    return NotificationPreferenceResponse(
        id=updated_prefs.id,
        user_id=updated_prefs.user_id,
        email_new_message=updated_prefs.email_new_message,
        email_milestone_submitted=updated_prefs.email_milestone_submitted,
        email_milestone_approved=updated_prefs.email_milestone_approved,
        email_milestone_rejected=updated_prefs.email_milestone_rejected,
        email_dispute_raised=updated_prefs.email_dispute_raised,
        email_payment_processed=updated_prefs.email_payment_processed,
        inapp_new_message=updated_prefs.inapp_new_message,
        inapp_milestone_submitted=updated_prefs.inapp_milestone_submitted,
        inapp_milestone_approved=updated_prefs.inapp_milestone_approved,
        inapp_milestone_rejected=updated_prefs.inapp_milestone_rejected,
        inapp_dispute_raised=updated_prefs.inapp_dispute_raised,
        inapp_payment_processed=updated_prefs.inapp_payment_processed
    )
