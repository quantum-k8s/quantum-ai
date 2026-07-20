from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models import Notification
from schemas.notifications import NotificationCreate, NotificationUpdate
from typing import Optional, List
from common.exceptions import ResourceNotFoundException, ValidationException

class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def get_notification_by_id(self, notification_id: int) -> dict:
        """Get notification by ID"""
        notification = self.db.query(Notification).filter(Notification.id == notification_id).first()
        if not notification:
            raise ResourceNotFoundException("Notification", f"id {notification_id}")

        return {
            "id": notification.id,
            "user_id": notification.user_id,
            "title": notification.title,
            "message": notification.message,
            "type": notification.type,
            "is_read": notification.is_read,
            "created_at": notification.created_at,
            "related_id": notification.related_id,
            "related_type": notification.related_type
        }

    def get_notifications_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[dict]:
        """Get all notifications for a user with pagination"""
        notifications = self.db.query(Notification).filter(Notification.user_id == user_id) \
            .order_by(Notification.created_at.desc()) \
            .offset(skip).limit(limit).all()

        return [{
            "id": notif.id,
            "user_id": notif.user_id,
            "title": notif.title,
            "message": notif.message,
            "type": notif.type,
            "is_read": notif.is_read,
            "created_at": notif.created_at,
            "related_id": notif.related_id,
            "related_type": notif.related_type
        } for notif in notifications]

    def get_unread_count(self, user_id: int) -> int:
        """Get unread notification count for a user"""
        count = self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).count()
        return count

    def create_notification(self, notification_data: NotificationCreate) -> dict:
        """Create a new notification"""
        db_notification = Notification(**notification_data.dict())
        self.db.add(db_notification)
        self.db.commit()
        self.db.refresh(db_notification)

        return {
            "success": True,
            "message": "Notification created successfully",
            "id": db_notification.id
        }

    def update_notification(self, notification_id: int, data: NotificationUpdate) -> dict:
        """Update notification"""
        notification = self.db.query(Notification).filter(Notification.id == notification_id).first()
        if not notification:
            raise ResourceNotFoundException("Notification", f"id {notification_id}")

        # Update fields if provided
        if data.title is not None:
            notification.title = data.title
        if data.message is not None:
            notification.message = data.message
        if data.type is not None:
            notification.type = data.type
        if data.is_read is not None:
            notification.is_read = data.is_read
        if data.related_id is not None:
            notification.related_id = data.related_id
        if data.related_type is not None:
            notification.related_type = data.related_type

        self.db.commit()
        return {"success": True, "message": "Notification updated successfully"}

    def mark_as_read(self, notification_id: int) -> dict:
        """Mark notification as read"""
        notification = self.db.query(Notification).filter(Notification.id == notification_id).first()
        if not notification:
            raise ResourceNotFoundException("Notification", f"id {notification_id}")

        notification.is_read = True
        self.db.commit()
        return {"success": True, "message": "Notification marked as read"}

    def mark_all_as_read(self, user_id: int) -> dict:
        """Mark all notifications as read for a user"""
        self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({"is_read": True})
        self.db.commit()
        return {"success": True, "message": "All notifications marked as read"}

    def delete_notification(self, notification_id: int) -> dict:
        """Delete notification"""
        notification = self.db.query(Notification).filter(Notification.id == notification_id).first()
        if not notification:
            raise ResourceNotFoundException("Notification", f"id {notification_id}")

        self.db.delete(notification)
        self.db.commit()
        return {"success": True, "message": "Notification deleted successfully"}

    def delete_all_notifications(self, user_id: int) -> dict:
        """Delete all notifications for a user"""
        self.db.query(Notification).filter(Notification.user_id == user_id).delete()
        self.db.commit()
        return {"success": True, "message": "All notifications deleted successfully"}