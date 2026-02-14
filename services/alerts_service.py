"""Alerts and notifications service."""

import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import select, and_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from models.alerts import AlertRule, Notification, NotificationPreference

logger = logging.getLogger(__name__)


class AlertsService:
    """Service for alerts and notification operations."""

    def __init__(self, db: AsyncSession):
        """Initialize alerts service."""
        self.db = db

    async def get_rules(self, skip: int = 0, limit: int = 20) -> tuple[List[AlertRule], int]:
        """Get all alert rules with pagination."""
        try:
            stmt = select(func.count(AlertRule.id))
            result = await self.db.execute(stmt)
            total = result.scalar() or 0

            stmt = select(AlertRule).offset(skip).limit(limit).order_by(AlertRule.created_at.desc())
            result = await self.db.execute(stmt)
            rules = result.scalars().all()

            return rules, total

        except Exception as e:
            logger.error(f"Error getting alert rules: {str(e)}")
            raise

    async def get_rule_by_id(self, rule_id: int) -> Optional[AlertRule]:
        """Get alert rule by ID."""
        try:
            stmt = select(AlertRule).where(AlertRule.id == rule_id)
            result = await self.db.execute(stmt)
            return result.scalars().first()

        except Exception as e:
            logger.error(f"Error getting alert rule: {str(e)}")
            raise

    async def update_rule(self, rule_id: int, update_data: Dict[str, Any]) -> Optional[AlertRule]:
        """Update alert rule."""
        try:
            rule = await self.get_rule_by_id(rule_id)
            if not rule:
                return None

            for key, value in update_data.items():
                if hasattr(rule, key) and value is not None:
                    setattr(rule, key, value)

            await self.db.flush()
            logger.info(f"Updated alert rule {rule_id}")
            return rule

        except Exception as e:
            logger.error(f"Error updating alert rule: {str(e)}")
            raise

    async def deactivate_rule(self, rule_id: int) -> Optional[AlertRule]:
        """Deactivate an alert rule."""
        try:
            rule = await self.get_rule_by_id(rule_id)
            if rule:
                rule.is_active = False
                await self.db.flush()
                logger.info(f"Deactivated alert rule {rule_id}")
            return rule

        except Exception as e:
            logger.error(f"Error deactivating alert rule: {str(e)}")
            raise

    async def activate_rule(self, rule_id: int) -> Optional[AlertRule]:
        """Activate an alert rule."""
        try:
            rule = await self.get_rule_by_id(rule_id)
            if rule:
                rule.is_active = True
                await self.db.flush()
                logger.info(f"Activated alert rule {rule_id}")
            return rule

        except Exception as e:
            logger.error(f"Error activating alert rule: {str(e)}")
            raise

    async def get_notifications(
        self, user_id: int, skip: int = 0, limit: int = 20, unread_only: bool = False
    ) -> tuple[List[Notification], int]:
        """Get user notifications with pagination."""
        try:
            query = select(Notification).where(Notification.user_id == user_id)

            if unread_only:
                query = query.where(Notification.read_at.is_(None))

            stmt = select(func.count(Notification.id)).where(Notification.user_id == user_id)
            if unread_only:
                stmt = stmt.where(Notification.read_at.is_(None))

            result = await self.db.execute(stmt)
            total = result.scalar() or 0

            query = query.offset(skip).limit(limit).order_by(Notification.created_at.desc())
            result = await self.db.execute(query)
            notifications = result.scalars().all()

            return notifications, total

        except Exception as e:
            logger.error(f"Error getting notifications: {str(e)}")
            raise

    async def get_unread_count(self, user_id: int) -> int:
        """Get count of unread notifications for user."""
        try:
            stmt = select(func.count(Notification.id)).where(
                and_(
                    Notification.user_id == user_id,
                    Notification.read_at.is_(None),
                )
            )
            result = await self.db.execute(stmt)
            return result.scalar() or 0

        except Exception as e:
            logger.error(f"Error getting unread count: {str(e)}")
            raise

    async def get_notification_by_id(self, notification_id: int) -> Optional[Notification]:
        """Get notification by ID."""
        try:
            stmt = select(Notification).where(Notification.id == notification_id)
            result = await self.db.execute(stmt)
            return result.scalars().first()

        except Exception as e:
            logger.error(f"Error getting notification: {str(e)}")
            raise

    async def mark_read(self, notification_id: int) -> Optional[Notification]:
        """Mark notification as read."""
        try:
            notification = await self.get_notification_by_id(notification_id)
            if notification:
                notification.read_at = datetime.utcnow()
                notification.status = "read"
                await self.db.flush()
                logger.debug(f"Marked notification {notification_id} as read")
            return notification

        except Exception as e:
            logger.error(f"Error marking notification as read: {str(e)}")
            raise

    async def mark_all_read(self, user_id: int) -> int:
        """Mark all user notifications as read."""
        try:
            stmt = select(Notification).where(
                and_(
                    Notification.user_id == user_id,
                    Notification.read_at.is_(None),
                )
            )
            result = await self.db.execute(stmt)
            notifications = result.scalars().all()

            for notification in notifications:
                notification.read_at = datetime.utcnow()
                notification.status = "read"

            await self.db.flush()
            logger.info(f"Marked {len(notifications)} notifications as read for user {user_id}")
            return len(notifications)

        except Exception as e:
            logger.error(f"Error marking all as read: {str(e)}")
            raise

    async def get_preferences(self, user_id: int) -> Optional[NotificationPreference]:
        """Get notification preferences for user."""
        try:
            stmt = select(NotificationPreference).where(NotificationPreference.user_id == user_id)
            result = await self.db.execute(stmt)
            pref = result.scalars().first()

            if not pref:
                # Create default preferences
                pref = NotificationPreference(user_id=user_id)
                self.db.add(pref)
                await self.db.flush()

            return pref

        except Exception as e:
            logger.error(f"Error getting notification preferences: {str(e)}")
            raise

    async def update_preferences(self, user_id: int, update_data: Dict[str, Any]) -> Optional[NotificationPreference]:
        """Update notification preferences."""
        try:
            pref = await self.get_preferences(user_id)
            if pref:
                for key, value in update_data.items():
                    if hasattr(pref, key) and value is not None:
                        setattr(pref, key, value)
                await self.db.flush()
                logger.info(f"Updated notification preferences for user {user_id}")

            return pref

        except Exception as e:
            logger.error(f"Error updating notification preferences: {str(e)}")
            raise

    async def get_notification_by_entity(
        self, entity_type: str, entity_id: int, user_id: Optional[int] = None
    ) -> List[Notification]:
        """Get notifications for a specific entity."""
        try:
            query = select(Notification).where(
                and_(
                    Notification.entity_type == entity_type,
                    Notification.entity_id == entity_id,
                )
            )

            if user_id:
                query = query.where(Notification.user_id == user_id)

            result = await self.db.execute(query)
            return result.scalars().all()

        except Exception as e:
            logger.error(f"Error getting notifications by entity: {str(e)}")
            raise

    async def delete_old_notifications(self, days: int = 30) -> int:
        """Delete notifications older than specified days."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            stmt = select(Notification).where(Notification.created_at < cutoff_date)
            result = await self.db.execute(stmt)
            old_notifications = result.scalars().all()

            for notification in old_notifications:
                await self.db.delete(notification)

            await self.db.flush()
            logger.info(f"Deleted {len(old_notifications)} old notifications")
            return len(old_notifications)

        except Exception as e:
            logger.error(f"Error deleting old notifications: {str(e)}")
            raise

    async def get_notification_stats(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Get notification statistics."""
        try:
            query = select(Notification)
            if user_id:
                query = query.where(Notification.user_id == user_id)

            # By channel
            stmt = select(Notification.channel, func.count(Notification.id))
            if user_id:
                stmt = stmt.where(Notification.user_id == user_id)
            stmt = stmt.group_by(Notification.channel)
            result = await self.db.execute(stmt)
            by_channel = dict(result.all())

            # By status
            stmt = select(Notification.status, func.count(Notification.id))
            if user_id:
                stmt = stmt.where(Notification.user_id == user_id)
            stmt = stmt.group_by(Notification.status)
            result = await self.db.execute(stmt)
            by_status = dict(result.all())

            # Total
            stmt = select(func.count(Notification.id))
            if user_id:
                stmt = stmt.where(Notification.user_id == user_id)
            result = await self.db.execute(stmt)
            total = result.scalar() or 0

            return {
                "total": total,
                "by_channel": by_channel,
                "by_status": by_status,
            }

        except Exception as e:
            logger.error(f"Error getting notification stats: {str(e)}")
            raise
