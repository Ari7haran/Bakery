from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.repositories.base_repository import BaseRepository
from app.models.notification import Notification

class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, db: Session):
        super().__init__(Notification, db)

    def list_by_user(
        self,
        user_id: int,
        is_read: Optional[bool] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[Notification]:
        query = self.db.query(Notification).filter(Notification.user_id == user_id)
        if is_read is not None:
            query = query.filter(Notification.is_read == is_read)
        return query.order_by(Notification.created_at.desc(), Notification.id.desc()).offset(skip).limit(limit).all()

    def count_by_user(self, user_id: int, is_read: Optional[bool] = None) -> int:
        query = self.db.query(func.count(Notification.id)).filter(Notification.user_id == user_id)
        if is_read is not None:
            query = query.filter(Notification.is_read == is_read)
        return query.scalar() or 0

    def count_unread_by_user(self, user_id: int) -> int:
        return self.count_by_user(user_id, is_read=False)

    def get_user_notification(self, user_id: int, notification_id: int) -> Optional[Notification]:
        """
        Enforce strict ownership: only returns notification if it belongs to user_id.
        Prevents IDOR across users.
        """
        return (
            self.db.query(Notification)
            .filter(Notification.id == notification_id, Notification.user_id == user_id)
            .first()
        )

    def mark_as_read(self, user_id: int, notification_id: int) -> Optional[Notification]:
        notification = self.get_user_notification(user_id, notification_id)
        if not notification:
            return None
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(notification)
        return notification

    def mark_all_read(self, user_id: int) -> int:
        now = datetime.now(timezone.utc)
        count = (
            self.db.query(Notification)
            .filter(Notification.user_id == user_id, Notification.is_read == False)
            .update(
                {Notification.is_read: True, Notification.read_at: now},
                synchronize_session="fetch"
            )
        )
        self.db.commit()
        return count

    def delete_user_notification(self, user_id: int, notification_id: int) -> bool:
        notification = self.get_user_notification(user_id, notification_id)
        if not notification:
            return False
        self.db.delete(notification)
        self.db.commit()
        return True

    def create_notification(
        self,
        user_id: int,
        title: str,
        message: str,
        notification_type: str = "system",
        priority: str = "normal",
        link_url: Optional[str] = None,
        related_entity_type: Optional[str] = None,
        related_entity_id: Optional[int] = None,
        commit: bool = True
    ) -> Notification:
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            is_read=False,
            link_url=link_url,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
            created_at=datetime.now(timezone.utc)
        )
        self.db.add(notification)
        if commit:
            self.db.commit()
            self.db.refresh(notification)
        else:
            self.db.flush()
        return notification
