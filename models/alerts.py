"""Alerts and notification data models."""

from datetime import datetime, time
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Integer, DateTime, Boolean, Float, Text, JSON, ForeignKey, Index, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import BaseModel


class AlertRule(BaseModel):
    """Configurable alert rule for platform events."""

    __tablename__ = "alert_rules"
    __table_args__ = (
        Index("ix_alert_rules_event_type", "event_type"),
        Index("ix_alert_rules_is_active", "is_active"),
        Index("ix_alert_rules_priority", "priority"),
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    conditions: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=[], nullable=False)
    notification_channels: Mapped[List[str]] = mapped_column(JSON, default=[], nullable=False)
    recipients: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=[], nullable=False)
    template_subject: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    template_body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    priority: Mapped[str] = mapped_column(String(20), default="medium")  # low/medium/high/critical
    cooldown_minutes: Mapped[int] = mapped_column(Integer, default=0)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Relationships
    notifications: Mapped[List["Notification"]] = relationship("Notification", back_populates="rule")


class Notification(BaseModel):
    """Individual notification record."""

    __tablename__ = "notifications"
    __table_args__ = (
        Index("ix_notifications_user_id", "user_id"),
        Index("ix_notifications_alert_rule_id", "alert_rule_id"),
        Index("ix_notifications_channel", "channel"),
        Index("ix_notifications_status", "status"),
        Index("ix_notifications_entity_type_id", "entity_type", "entity_id"),
    )

    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    alert_rule_id: Mapped[Optional[int]] = mapped_column(ForeignKey("alert_rules.id"), nullable=True)
    event_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    channel: Mapped[str] = mapped_column(String(50), nullable=False)  # email/in_app/sms/slack/webhook
    recipient: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    link: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    entity_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    entity_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending/sent/delivered/failed/read
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extra_metadata: Mapped[Dict[str, Any]] = mapped_column("metadata", JSON, default={}, nullable=False)

    # Relationships
    rule: Mapped[Optional["AlertRule"]] = relationship("AlertRule", back_populates="notifications")


class NotificationPreference(BaseModel):
    """User notification preferences."""

    __tablename__ = "notification_preferences"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_user_notification_preferences"),
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    email_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    sms_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    slack_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    in_app_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    event_preferences: Mapped[Dict[str, Any]] = mapped_column(JSON, default={}, nullable=False)
    quiet_hours_start: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)  # "22:00"
    quiet_hours_end: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)  # "08:00"
    digest_frequency: Mapped[str] = mapped_column(String(20), default="daily")  # none/daily/weekly
    digest_time: Mapped[str] = mapped_column(String(5), default="09:00")
