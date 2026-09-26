from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, Path, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.repositories.notification_repository import NotificationRepository
from app.repositories.user_repository import UserRepository
from app.services.notification_service import NotificationService
from app.schemas.notification import (
    NotificationOut,
    UnreadCountOut,
    NotificationListOut,
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])

def get_notification_service(db: Session = Depends(get_db)) -> NotificationService:
    return NotificationService(
        notification_repo=NotificationRepository(db),
        user_repo=UserRepository(db),
        db=db
    )

@router.get("/", response_model=NotificationListOut)
def list_notifications(
    is_read: Optional[bool] = Query(None, description="Filter by read state (true for read, false for unread)"),
    skip: int = Query(0, ge=0, description="Items to skip for pagination"),
    limit: int = Query(20, ge=1, le=100, description="Items to return (max 100)"),
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service)
):
    """
    Retrieve paginated notifications for the authenticated user, ordered newest first.
    Strictly isolated to current_user.
    """
    return service.get_user_notifications(
        current_user=current_user,
        is_read=is_read,
        skip=skip,
        limit=limit
    )

@router.get("/unread-count", response_model=UnreadCountOut)
def get_unread_count(
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service)
):
    """
    Lightweight, fast query to fetch only the unread count for navbar badges.
    """
    count = service.get_unread_count(current_user)
    return {"unread_count": count}

@router.put("/{notification_id}/read", response_model=NotificationOut)
def mark_notification_as_read(
    notification_id: int = Path(..., gt=0, description="Notification ID must be greater than zero"),
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service)
):
    """
    Mark a specific notification as read.
    Enforces ownership validation to prevent IDOR vulnerabilities.
    """
    return service.mark_notification_read(current_user, notification_id)

@router.put("/mark-all-read", response_model=Dict[str, Any])
def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service)
):
    """
    Bulk update: marks all unread notifications of the authenticated user as read.
    """
    updated_count = service.mark_all_read(current_user)
    return {
        "updated_count": updated_count,
        "message": f"Successfully marked {updated_count} notification(s) as read"
    }

@router.delete("/{notification_id}", response_model=Dict[str, str])
def delete_notification(
    notification_id: int = Path(..., gt=0, description="Notification ID must be greater than zero"),
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service)
):
    """
    Dismiss / delete a notification belonging to the authenticated user.
    """
    service.delete_notification(current_user, notification_id)
    return {"message": "Notification dismissed successfully"}
