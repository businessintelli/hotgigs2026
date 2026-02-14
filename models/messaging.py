"""Messaging integration models."""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, Float, Boolean, DateTime, JSON, ForeignKey, Enum as SAEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import BaseModel


class MessagingIntegration(BaseModel):
    """Configuration for messaging platform integrations."""
    __tablename__ = "messaging_integrations"

    platform: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # slack/teams
    workspace_name: Mapped[Optional[str]] = mapped_column(String(255))
    workspace_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    bot_token_encrypted: Mapped[Optional[str]] = mapped_column(Text)  # Encrypted token
    webhook_url: Mapped[Optional[str]] = mapped_column(String(500))
    app_id: Mapped[Optional[str]] = mapped_column(String(255))
    client_id: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50), default="active", index=True)  # active/inactive/error
    last_connected_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_error: Mapped[Optional[str]] = mapped_column(Text)
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    setup_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))

    channels = relationship("MessagingChannel", back_populates="integration", cascade="all, delete-orphan")
    logs = relationship("MessagingLog", back_populates="integration", cascade="all, delete-orphan")


class MessagingChannel(BaseModel):
    """Mapped messaging channels for notifications."""
    __tablename__ = "messaging_channels"

    integration_id: Mapped[int] = mapped_column(ForeignKey("messaging_integrations.id"), index=True)
    channel_id: Mapped[str] = mapped_column(String(255), nullable=False)
    channel_name: Mapped[str] = mapped_column(String(255), nullable=False)
    channel_type: Mapped[str] = mapped_column(String(50), default="channel")  # channel/dm/group
    purpose: Mapped[Optional[str]] = mapped_column(String(100))  # general/requirements/submissions/interviews/offers/alerts
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    linked_requirement_id: Mapped[Optional[int]] = mapped_column(ForeignKey("requirements.id"))
    linked_customer_id: Mapped[Optional[int]] = mapped_column(ForeignKey("customers.id"))
    member_count: Mapped[int] = mapped_column(Integer, default=0)
    last_message_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    integration = relationship("MessagingIntegration", back_populates="channels")
    routes = relationship("NotificationRoute", back_populates="channel", cascade="all, delete-orphan")


class NotificationRoute(BaseModel):
    """Configuration for routing platform events to messaging channels."""
    __tablename__ = "notification_routes"

    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    channel_id: Mapped[int] = mapped_column(ForeignKey("messaging_channels.id"), index=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    template: Mapped[Optional[str]] = mapped_column(Text)  # Custom message template
    filters: Mapped[dict] = mapped_column(JSON, default=dict)  # {priority: ["high"], customer_id: [1,2]}
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    routes_count: Mapped[int] = mapped_column(Integer, default=0)  # Tracking count

    channel = relationship("MessagingChannel", back_populates="routes")


class MessagingLog(BaseModel):
    """Log of all messages sent via integrations."""
    __tablename__ = "messaging_logs"

    integration_id: Mapped[int] = mapped_column(ForeignKey("messaging_integrations.id"), index=True)
    channel_id: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    recipient: Mapped[Optional[str]] = mapped_column(String(255))
    message_type: Mapped[str] = mapped_column(String(50), index=True)  # notification/command_response/interaction/dm
    event_type: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    content_preview: Mapped[Optional[str]] = mapped_column(String(500))
    external_message_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    status: Mapped[str] = mapped_column(String(50), default="sent", index=True)  # sent/delivered/failed/pending
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    response_data: Mapped[Optional[dict]] = mapped_column(JSON)

    integration = relationship("MessagingIntegration", back_populates="logs")
