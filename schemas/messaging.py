"""Pydantic schemas for messaging integration."""

from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Optional, List, Dict, Any
from schemas.common import BaseResponse


# Messaging Integration Schemas

class MessagingIntegrationCreate(BaseModel):
    """Create messaging integration."""

    platform: str = Field(..., description="slack or teams")
    workspace_name: Optional[str] = Field(None, max_length=255)
    workspace_id: Optional[str] = Field(None, max_length=255)
    bot_token_encrypted: Optional[str] = Field(None, description="Encrypted bot token")
    webhook_url: Optional[str] = Field(None, max_length=500)
    app_id: Optional[str] = Field(None, max_length=255)
    client_id: Optional[str] = Field(None, max_length=255)
    config: Dict[str, Any] = Field(default_factory=dict)


class MessagingIntegrationUpdate(BaseModel):
    """Update messaging integration."""

    workspace_name: Optional[str] = Field(None, max_length=255)
    bot_token_encrypted: Optional[str] = None
    webhook_url: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = Field(None, pattern="^(active|inactive|error)$")
    config: Optional[Dict[str, Any]] = None


class MessagingIntegrationResponse(BaseResponse):
    """Messaging integration response."""

    id: int
    platform: str
    workspace_name: Optional[str]
    workspace_id: Optional[str]
    status: str
    last_connected_at: Optional[datetime]
    config: Dict[str, Any]

    class Config:
        from_attributes = True


# Messaging Channel Schemas

class MessagingChannelCreate(BaseModel):
    """Create messaging channel."""

    integration_id: int
    channel_id: str = Field(..., max_length=255)
    channel_name: str = Field(..., max_length=255)
    channel_type: str = Field(default="channel", pattern="^(channel|dm|group)$")
    purpose: Optional[str] = Field(None, max_length=100)
    is_default: bool = False
    linked_requirement_id: Optional[int] = None
    linked_customer_id: Optional[int] = None


class MessagingChannelUpdate(BaseModel):
    """Update messaging channel."""

    channel_name: Optional[str] = Field(None, max_length=255)
    purpose: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


class MessagingChannelResponse(BaseResponse):
    """Messaging channel response."""

    id: int
    integration_id: int
    channel_id: str
    channel_name: str
    channel_type: str
    purpose: Optional[str]
    is_default: bool
    is_active: bool
    member_count: int
    last_message_at: Optional[datetime]

    class Config:
        from_attributes = True


# Notification Route Schemas

class NotificationRouteCreate(BaseModel):
    """Create notification route."""

    event_type: str = Field(..., max_length=100)
    channel_id: int
    is_enabled: bool = True
    template: Optional[str] = None
    filters: Dict[str, Any] = Field(default_factory=dict)


class NotificationRouteUpdate(BaseModel):
    """Update notification route."""

    event_type: Optional[str] = Field(None, max_length=100)
    channel_id: Optional[int] = None
    is_enabled: Optional[bool] = None
    template: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None


class NotificationRouteResponse(BaseResponse):
    """Notification route response."""

    id: int
    event_type: str
    channel_id: int
    is_enabled: bool
    template: Optional[str]
    filters: Dict[str, Any]

    class Config:
        from_attributes = True


# Messaging Log Schemas

class MessagingLogCreate(BaseModel):
    """Create messaging log entry."""

    integration_id: int
    channel_id: Optional[str] = Field(None, max_length=255)
    recipient: Optional[str] = Field(None, max_length=255)
    message_type: str = Field(..., max_length=50)
    event_type: Optional[str] = Field(None, max_length=100)
    content_preview: Optional[str] = Field(None, max_length=500)


class MessagingLogResponse(BaseResponse):
    """Messaging log response."""

    id: int
    integration_id: int
    channel_id: Optional[str]
    recipient: Optional[str]
    message_type: str
    event_type: Optional[str]
    content_preview: Optional[str]
    external_message_id: Optional[str]
    status: str
    sent_at: datetime
    delivered_at: Optional[datetime]

    class Config:
        from_attributes = True


# Message Sending Schemas

class SlackMessageCreate(BaseModel):
    """Create Slack message."""

    channel: str = Field(..., description="Channel ID or name")
    message: str
    blocks: Optional[List[Dict[str, Any]]] = None
    thread_ts: Optional[str] = None


class TeamsMessageCreate(BaseModel):
    """Create Teams message."""

    channel_id: str
    message: str
    card: Optional[Dict[str, Any]] = None


class MessageResponse(BaseModel):
    """Message send response."""

    success: bool
    message_id: Optional[str]
    channel: str
    timestamp: datetime


# Slack Command Schemas

class SlackSlashCommandPayload(BaseModel):
    """Slack slash command payload."""

    command: str
    text: str
    user_id: str
    channel_id: str
    team_id: str
    response_url: str


class SlackCommandResponse(BaseModel):
    """Slack command response."""

    response_type: str = "in_channel"
    text: Optional[str] = None
    blocks: Optional[List[Dict[str, Any]]] = None


# Slack Interaction Schemas

class SlackInteractionPayload(BaseModel):
    """Slack interaction payload."""

    type: str
    user: Dict[str, Any]
    actions: List[Dict[str, Any]]
    channel: Dict[str, Any]
    response_url: str
    trigger_id: str


# Configuration Schemas

class NotificationConfig(BaseModel):
    """Notification routing configuration."""

    event_type: str
    slack_channel: Optional[str] = None
    teams_channel: Optional[str] = None
    is_enabled: bool = True
    filters: Optional[Dict[str, Any]] = None


class IntegrationStatus(BaseModel):
    """Integration status check result."""

    platform: str
    is_connected: bool
    last_connected: Optional[datetime]
    error_message: Optional[str]
    workspace_name: Optional[str]


class MessagingAnalytics(BaseModel):
    """Messaging analytics."""

    total_messages: int
    messages_by_type: Dict[str, int]
    messages_by_channel: Dict[str, int]
    delivery_rate: float
    average_response_time: float
    most_active_channels: List[str]
    period: str
