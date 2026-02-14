"""Pydantic schemas for alerts and notifications."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class AlertRuleCreate(BaseModel):
    """Create alert rule request."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    event_type: str = Field(..., description="Event type to trigger alert")
    conditions: List[Dict[str, Any]] = Field(default_factory=list, description="Rule conditions")
    notification_channels: List[str] = Field(..., description="email/in_app/sms/slack/webhook")
    recipients: List[Dict[str, Any]] = Field(..., description="Recipients for alert")
    template_subject: Optional[str] = Field(None, max_length=500)
    template_body: Optional[str] = None
    priority: str = Field(default="medium", description="low/medium/high/critical")
    cooldown_minutes: int = Field(default=0, ge=0)


class AlertRuleUpdate(BaseModel):
    """Update alert rule request."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    conditions: Optional[List[Dict[str, Any]]] = None
    notification_channels: Optional[List[str]] = None
    recipients: Optional[List[Dict[str, Any]]] = None
    template_subject: Optional[str] = None
    template_body: Optional[str] = None
    priority: Optional[str] = None
    cooldown_minutes: Optional[int] = None
    is_active: Optional[bool] = None


class AlertRuleResponse(BaseModel):
    """Alert rule response."""

    id: int
    name: str
    description: Optional[str]
    event_type: str
    conditions: List[Dict[str, Any]]
    notification_channels: List[str]
    recipients: List[Dict[str, Any]]
    template_subject: Optional[str]
    is_active: bool
    priority: str
    cooldown_minutes: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationCreate(BaseModel):
    """Create notification request."""

    user_id: Optional[int] = None
    alert_rule_id: Optional[int] = None
    channel: str = Field(..., description="email/in_app/sms/slack/webhook")
    recipient: str = Field(...)
    title: str = Field(..., max_length=500)
    message: str = Field(...)
    link: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    priority: str = Field(default="medium")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class NotificationResponse(BaseModel):
    """Notification response."""

    id: int
    user_id: Optional[int]
    alert_rule_id: Optional[int]
    event_id: Optional[str]
    channel: str
    recipient: str
    title: str
    message: str
    link: Optional[str]
    entity_type: Optional[str]
    entity_id: Optional[int]
    priority: str
    status: str
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    read_at: Optional[datetime]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """User notification list response."""

    notifications: List[NotificationResponse]
    total: int
    unread_count: int


class NotificationPreferenceUpdate(BaseModel):
    """Update notification preference request."""

    email_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    slack_enabled: Optional[bool] = None
    in_app_enabled: Optional[bool] = None
    event_preferences: Optional[Dict[str, Any]] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    digest_frequency: Optional[str] = None
    digest_time: Optional[str] = None


class NotificationPreferenceResponse(BaseModel):
    """Notification preference response."""

    id: int
    user_id: int
    email_enabled: bool
    sms_enabled: bool
    slack_enabled: bool
    in_app_enabled: bool
    event_preferences: Dict[str, Any]
    quiet_hours_start: Optional[str]
    quiet_hours_end: Optional[str]
    digest_frequency: str
    digest_time: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DigestNotificationResponse(BaseModel):
    """Digest notification response."""

    digest_period: str
    notifications_count: int
    critical_notifications: List[NotificationResponse]
    high_notifications: List[NotificationResponse]
    medium_notifications: List[NotificationResponse]
    low_notifications: List[NotificationResponse]
    generated_at: datetime


class AlertAnalyticsResponse(BaseModel):
    """Alert analytics response."""

    total_rules: int
    active_rules: int
    total_notifications: int
    notifications_by_channel: Dict[str, int]
    notifications_by_status: Dict[str, int]
    notifications_by_priority: Dict[str, int]
    delivery_success_rate: float
    read_rate: float
    most_triggered_rules: List[Dict[str, Any]]
    average_delivery_time_seconds: float
