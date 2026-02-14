"""Alerts and notification agent for centralized event-driven alerting."""

import logging
import asyncio
import json
import aiohttp
import re
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from anthropic import AsyncAnthropic

from agents.base_agent import BaseAgent
from agents.events import Event, EventType
from models.alerts import AlertRule, Notification, NotificationPreference
from models.user import User
from models.submission import Submission
from models.contract import Contract
from models.referral import Referral
from models.enums import SubmissionStatus, ContractStatus

logger = logging.getLogger(__name__)


class AlertsNotificationAgent(BaseAgent):
    """Centralized alerts and notifications for all platform events."""

    def __init__(self, anthropic_api_key: str, agent_version: str = "1.0.0"):
        """Initialize alerts and notification agent."""
        super().__init__(agent_name="AlertsNotificationAgent", agent_version=agent_version)
        self.client = AsyncAnthropic(api_key=anthropic_api_key)
        self.event_handlers = {
            EventType.SUBMISSION_CREATED: self._handle_submission_created,
            EventType.SUBMISSION_SENT: self._handle_submission_sent,
            EventType.OFFER_SENT: self._handle_offer_sent,
            EventType.OFFER_ACCEPTED: self._handle_offer_accepted,
            EventType.ONBOARDING_STARTED: self._handle_onboarding_started,
        }

    async def create_alert_rule(self, db: AsyncSession, rule_data: Dict[str, Any]) -> AlertRule:
        """Create configurable alert rule."""
        try:
            rule = AlertRule(
                name=rule_data.get("name"),
                description=rule_data.get("description"),
                event_type=rule_data.get("event_type"),
                conditions=rule_data.get("conditions", []),
                notification_channels=rule_data.get("notification_channels", []),
                recipients=rule_data.get("recipients", []),
                template_subject=rule_data.get("template_subject"),
                template_body=rule_data.get("template_body"),
                is_active=rule_data.get("is_active", True),
                priority=rule_data.get("priority", "medium"),
                cooldown_minutes=rule_data.get("cooldown_minutes", 0),
                created_by=rule_data.get("created_by", 1),
            )

            db.add(rule)
            await db.flush()

            logger.info(f"Created alert rule {rule.id}: {rule.name}")
            return rule

        except Exception as e:
            logger.error(f"Error creating alert rule: {str(e)}")
            raise

    async def process_event(self, db: AsyncSession, event: Event) -> None:
        """Process event and evaluate against all active rules."""
        try:
            # Get matching rules
            matching_rules = await self.evaluate_rules(db, event)

            for rule in matching_rules:
                # Generate notification
                notification_data = {
                    "alert_rule_id": rule.id,
                    "event_id": event.event_id,
                    "title": rule.template_subject or f"{event.event_type} Alert",
                    "message": rule.template_body or f"Event triggered: {event.event_type}",
                    "entity_type": event.entity_type,
                    "entity_id": event.entity_id,
                    "priority": rule.priority,
                    "metadata": {"event_payload": event.payload},
                }

                # Send to each channel
                for channel in rule.notification_channels:
                    for recipient in rule.recipients:
                        await self._send_to_channel(db, channel, recipient, rule, notification_data)

            logger.debug(f"Processed event {event.event_id}, matched {len(matching_rules)} rules")

        except Exception as e:
            logger.error(f"Error processing event: {str(e)}")
            await self.on_error(e)

    async def evaluate_rules(self, db: AsyncSession, event: Event) -> List[AlertRule]:
        """Check event against all active rules."""
        try:
            # Get rules for this event type
            stmt = select(AlertRule).where(
                and_(AlertRule.event_type == event.event_type.value, AlertRule.is_active is True)
            )
            result = await db.execute(stmt)
            rules = result.scalars().all()

            matching_rules = []

            for rule in rules:
                # Evaluate conditions
                if await self._evaluate_conditions(rule.conditions, event.payload):
                    # Check cooldown
                    stmt = select(Notification).where(
                        and_(
                            Notification.alert_rule_id == rule.id,
                            Notification.entity_id == event.entity_id,
                            Notification.created_at
                            > datetime.utcnow() - timedelta(minutes=rule.cooldown_minutes),
                        )
                    )
                    result = await db.execute(stmt)
                    recent_notification = result.scalars().first()

                    if not recent_notification:
                        matching_rules.append(rule)

            return matching_rules

        except Exception as e:
            logger.error(f"Error evaluating rules: {str(e)}")
            return []

    async def _evaluate_conditions(self, conditions: List[Dict[str, Any]], payload: Dict[str, Any]) -> bool:
        """Evaluate rule conditions against event payload."""
        if not conditions:
            return True

        for condition in conditions:
            field = condition.get("field")
            operator = condition.get("operator", "==")
            value = condition.get("value")

            if field not in payload:
                return False

            payload_value = payload[field]

            if operator == "==":
                if payload_value != value:
                    return False
            elif operator == "!=":
                if payload_value == value:
                    return False
            elif operator == ">":
                if not (payload_value > value):
                    return False
            elif operator == ">=":
                if not (payload_value >= value):
                    return False
            elif operator == "<":
                if not (payload_value < value):
                    return False
            elif operator == "<=":
                if not (payload_value <= value):
                    return False
            elif operator == "contains":
                if value not in str(payload_value):
                    return False
            elif operator == "in":
                if payload_value not in value:
                    return False

        return True

    async def send_notification(self, db: AsyncSession, notification: Dict[str, Any]) -> Notification:
        """Send notification via configured channel."""
        try:
            notification_obj = Notification(
                user_id=notification.get("user_id"),
                alert_rule_id=notification.get("alert_rule_id"),
                event_id=notification.get("event_id"),
                channel=notification.get("channel", "in_app"),
                recipient=notification.get("recipient"),
                title=notification.get("title"),
                message=notification.get("message"),
                link=notification.get("link"),
                entity_type=notification.get("entity_type"),
                entity_id=notification.get("entity_id"),
                priority=notification.get("priority", "medium"),
                status="pending",
                metadata=notification.get("metadata", {}),
            )

            db.add(notification_obj)
            await db.flush()

            logger.info(f"Created notification {notification_obj.id} via {notification.get('channel')}")
            return notification_obj

        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            raise

    async def _send_to_channel(
        self, db: AsyncSession, channel: str, recipient: Dict[str, Any], rule: AlertRule, notification_data: Dict[str, Any]
    ) -> bool:
        """Send notification via specific channel."""
        try:
            if channel == "email":
                return await self.send_email_notification(
                    recipient.get("value"),
                    notification_data.get("title"),
                    notification_data.get("message"),
                )
            elif channel == "sms":
                return await self.send_sms_notification(
                    recipient.get("value"),
                    notification_data.get("message"),
                )
            elif channel == "slack":
                return await self.send_slack_notification(
                    recipient.get("value"),
                    notification_data.get("message"),
                )
            elif channel == "webhook":
                return await self.send_webhook_notification(
                    recipient.get("value"),
                    notification_data,
                )
            elif channel == "in_app":
                user_id = None
                if recipient.get("type") == "user":
                    user_id = recipient.get("value")

                await self.create_in_app_notification(
                    db,
                    user_id or 1,
                    notification_data.get("title"),
                    notification_data.get("message"),
                    notification_data.get("link"),
                )
                return True

            return False

        except Exception as e:
            logger.error(f"Error sending to {channel}: {str(e)}")
            return False

    async def send_email_notification(self, recipient: str, subject: str, body: str) -> bool:
        """Send email notification via SendGrid."""
        try:
            # In production, use SendGrid API
            logger.info(f"Sending email to {recipient}: {subject}")

            # Validate email
            if not re.match(r"[^@]+@[^@]+\.[^@]+", recipient):
                logger.warning(f"Invalid email address: {recipient}")
                return False

            # Simulated SendGrid API call
            async with aiohttp.ClientSession() as session:
                # Replace with actual SendGrid API endpoint
                data = {
                    "personalizations": [{"to": [{"email": recipient}]}],
                    "from": {"email": "noreply@hrplatform.com"},
                    "subject": subject,
                    "content": [{"type": "text/html", "value": body}],
                }

                # In production: actual SendGrid API call
                logger.debug(f"Email notification sent to {recipient}")

            return True

        except Exception as e:
            logger.error(f"Error sending email notification: {str(e)}")
            return False

    async def send_sms_notification(self, phone: str, message: str) -> bool:
        """Send SMS notification via Twilio."""
        try:
            logger.info(f"Sending SMS to {phone}: {message[:50]}...")

            # In production, use Twilio API
            async with aiohttp.ClientSession() as session:
                # Replace with actual Twilio API endpoint
                pass

            return True

        except Exception as e:
            logger.error(f"Error sending SMS notification: {str(e)}")
            return False

    async def send_slack_notification(self, channel: str, message: str) -> bool:
        """Send Slack notification via webhook."""
        try:
            logger.info(f"Sending Slack message to {channel}")

            async with aiohttp.ClientSession() as session:
                # Slack webhook URL
                payload = {
                    "channel": channel,
                    "text": message,
                    "unfurl_links": False,
                }

                # In production: actual Slack webhook call
                logger.debug(f"Slack notification sent to {channel}")

            return True

        except Exception as e:
            logger.error(f"Error sending Slack notification: {str(e)}")
            return False

    async def send_webhook_notification(self, url: str, payload: Dict[str, Any]) -> bool:
        """Send custom webhook notification."""
        try:
            logger.info(f"Sending webhook to {url}")

            async with aiohttp.ClientSession() as session:
                # In production: actual webhook call with retries
                logger.debug(f"Webhook notification sent to {url}")

            return True

        except Exception as e:
            logger.error(f"Error sending webhook notification: {str(e)}")
            return False

    async def create_in_app_notification(
        self, db: AsyncSession, user_id: int, title: str, message: str, link: Optional[str] = None
    ) -> Notification:
        """Create in-app notification."""
        try:
            notification = Notification(
                user_id=user_id,
                channel="in_app",
                recipient=f"user_{user_id}",
                title=title,
                message=message,
                link=link,
                status="sent",
                sent_at=datetime.utcnow(),
            )

            db.add(notification)
            await db.flush()

            logger.info(f"Created in-app notification for user {user_id}")
            return notification

        except Exception as e:
            logger.error(f"Error creating in-app notification: {str(e)}")
            raise

    async def get_user_notifications(
        self, db: AsyncSession, user_id: int, unread_only: bool = False, limit: int = 20, offset: int = 0
    ) -> Dict[str, Any]:
        """Get user's notifications with pagination."""
        try:
            query = select(Notification).where(Notification.user_id == user_id)

            if unread_only:
                query = query.where(Notification.read_at.is_(None))

            # Get total count
            count_stmt = select(func.count(Notification.id)).where(Notification.user_id == user_id)
            if unread_only:
                count_stmt = count_stmt.where(Notification.read_at.is_(None))

            result = await db.execute(count_stmt)
            total_count = result.scalar() or 0

            # Get paginated results
            query = query.order_by(Notification.created_at.desc()).limit(limit).offset(offset)
            result = await db.execute(query)
            notifications = result.scalars().all()

            return {
                "notifications": notifications,
                "total": total_count,
                "limit": limit,
                "offset": offset,
            }

        except Exception as e:
            logger.error(f"Error getting user notifications: {str(e)}")
            raise

    async def mark_as_read(self, db: AsyncSession, notification_id: int) -> None:
        """Mark notification as read."""
        try:
            stmt = select(Notification).where(Notification.id == notification_id)
            result = await db.execute(stmt)
            notification = result.scalars().first()

            if notification:
                notification.read_at = datetime.utcnow()
                notification.status = "read"
                await db.flush()

                logger.debug(f"Marked notification {notification_id} as read")

        except Exception as e:
            logger.error(f"Error marking notification as read: {str(e)}")
            raise

    async def get_digest(self, db: AsyncSession, user_id: int, period: str = "daily") -> Dict[str, Any]:
        """Generate daily/weekly digest of notifications."""
        try:
            if period == "daily":
                time_delta = timedelta(days=1)
            elif period == "weekly":
                time_delta = timedelta(days=7)
            else:
                time_delta = timedelta(days=1)

            cutoff_time = datetime.utcnow() - time_delta

            stmt = (
                select(Notification)
                .where(
                    and_(
                        Notification.user_id == user_id,
                        Notification.created_at >= cutoff_time,
                    )
                )
                .order_by(Notification.priority.desc(), Notification.created_at.desc())
            )
            result = await db.execute(stmt)
            notifications = result.scalars().all()

            # Group by priority
            by_priority = {
                "critical": [n for n in notifications if n.priority == "critical"],
                "high": [n for n in notifications if n.priority == "high"],
                "medium": [n for n in notifications if n.priority == "medium"],
                "low": [n for n in notifications if n.priority == "low"],
            }

            digest = {
                "period": period,
                "user_id": user_id,
                "total_notifications": len(notifications),
                "by_priority": by_priority,
                "generated_at": datetime.utcnow().isoformat(),
            }

            return digest

        except Exception as e:
            logger.error(f"Error generating digest: {str(e)}")
            raise

    async def manage_preferences(
        self, db: AsyncSession, user_id: int, preferences: Dict[str, Any]
    ) -> NotificationPreference:
        """Manage user's notification preferences."""
        try:
            stmt = select(NotificationPreference).where(NotificationPreference.user_id == user_id)
            result = await db.execute(stmt)
            pref = result.scalars().first()

            if not pref:
                pref = NotificationPreference(user_id=user_id)
                db.add(pref)

            # Update preferences
            for key, value in preferences.items():
                if hasattr(pref, key):
                    setattr(pref, key, value)

            await db.flush()

            logger.info(f"Updated notification preferences for user {user_id}")
            return pref

        except Exception as e:
            logger.error(f"Error managing notification preferences: {str(e)}")
            raise

    async def get_alert_analytics(self, db: AsyncSession) -> Dict[str, Any]:
        """Alert analytics."""
        try:
            # Get notification stats
            stmt = select(func.count(Notification.id))
            result = await db.execute(stmt)
            total_notifications = result.scalar() or 0

            # By channel
            stmt = select(Notification.channel, func.count(Notification.id)).group_by(Notification.channel)
            result = await db.execute(stmt)
            by_channel = dict(result.all())

            # By status
            stmt = select(Notification.status, func.count(Notification.id)).group_by(Notification.status)
            result = await db.execute(stmt)
            by_status = dict(result.all())

            # By priority
            stmt = select(Notification.priority, func.count(Notification.id)).group_by(Notification.priority)
            result = await db.execute(stmt)
            by_priority = dict(result.all())

            # Get active rules
            stmt = select(func.count(AlertRule.id)).where(AlertRule.is_active is True)
            result = await db.execute(stmt)
            active_rules = result.scalar() or 0

            # Delivery success rate
            stmt = select(func.count(Notification.id)).where(Notification.status == "delivered")
            result = await db.execute(stmt)
            delivered = result.scalar() or 0

            delivery_success_rate = (delivered / total_notifications * 100) if total_notifications > 0 else 0

            # Read rate
            stmt = select(func.count(Notification.id)).where(Notification.status == "read")
            result = await db.execute(stmt)
            read = result.scalar() or 0

            read_rate = (read / total_notifications * 100) if total_notifications > 0 else 0

            analytics = {
                "total_rules": active_rules,
                "total_notifications": total_notifications,
                "notifications_by_channel": by_channel,
                "notifications_by_status": by_status,
                "notifications_by_priority": by_priority,
                "delivery_success_rate": round(delivery_success_rate, 2),
                "read_rate": round(read_rate, 2),
            }

            return analytics

        except Exception as e:
            logger.error(f"Error getting alert analytics: {str(e)}")
            raise

    # Built-in alert handlers for common events

    async def _handle_submission_created(self, db: AsyncSession, event: Event) -> None:
        """Handle submission created event."""
        logger.info(f"Submission created: {event.entity_id}")

    async def _handle_submission_sent(self, db: AsyncSession, event: Event) -> None:
        """Handle submission sent event."""
        logger.info(f"Submission sent: {event.entity_id}")

    async def _handle_offer_sent(self, db: AsyncSession, event: Event) -> None:
        """Handle offer sent event."""
        logger.info(f"Offer sent: {event.entity_id}")

    async def _handle_offer_accepted(self, db: AsyncSession, event: Event) -> None:
        """Handle offer accepted event."""
        logger.info(f"Offer accepted: {event.entity_id}")

    async def _handle_onboarding_started(self, db: AsyncSession, event: Event) -> None:
        """Handle onboarding started event."""
        logger.info(f"Onboarding started: {event.entity_id}")

    async def on_start(self) -> None:
        """Initialize alerts and notification agent."""
        logger.info("Alerts and Notification Agent started")

    async def on_stop(self) -> None:
        """Cleanup alerts and notification agent."""
        logger.info("Alerts and Notification Agent stopped")
