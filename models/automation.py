"""Automation, search, and notification models."""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, Text, JSON, ForeignKey, Enum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import BaseModel, TenantBaseModel
from models.enums import SearchType, TriggerEvent, ActionType, NotificationType, NotificationCategory


class SavedSearch(TenantBaseModel):
    """Saved search templates for users."""

    __tablename__ = "saved_searches"

    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    search_type: Mapped[str] = mapped_column(
        Enum(SearchType),
        nullable=False,
        index=True,
        comment="CANDIDATE, REQUIREMENT, SUBMISSION, SUPPLIER"
    )
    filters: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        comment="Filter criteria as JSON object"
    )
    sort_by: Mapped[Optional[str]] = mapped_column(String(100))
    sort_order: Mapped[str] = mapped_column(String(10), default="desc", comment="asc or desc")
    is_default: Mapped[bool] = mapped_column(default=False, index=True)
    result_count: Mapped[int] = mapped_column(default=0, comment="Number of results in last run")
    last_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class AutomationRule(TenantBaseModel):
    """Workflow automation rules."""

    __tablename__ = "automation_rules"

    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    trigger_event: Mapped[str] = mapped_column(
        Enum(TriggerEvent),
        nullable=False,
        index=True,
        comment="Event that triggers the rule"
    )
    trigger_conditions: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        comment="Conditions that must be met (e.g., status changes)"
    )
    action_type: Mapped[str] = mapped_column(
        Enum(ActionType),
        nullable=False,
        comment="Type of action to perform"
    )
    action_config: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        comment="Configuration for the action (e.g., template, recipients)"
    )
    is_enabled: Mapped[bool] = mapped_column(default=True, index=True)
    execution_count: Mapped[int] = mapped_column(default=0, comment="Number of times executed")
    last_triggered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class Notification(TenantBaseModel):
    """In-app notification system."""

    __tablename__ = "notifications"

    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    notification_type: Mapped[str] = mapped_column(
        Enum(NotificationType),
        nullable=False,
        default=NotificationType.INFO,
        index=True
    )
    category: Mapped[str] = mapped_column(
        Enum(NotificationCategory),
        nullable=False,
        index=True,
        comment="SUBMISSION, INTERVIEW, OFFER, COMPLIANCE, SLA, TIMESHEET, SYSTEM"
    )
    reference_type: Mapped[Optional[str]] = mapped_column(
        String(100),
        comment="Type of referenced entity (submission, interview, etc.)"
    )
    reference_id: Mapped[Optional[int]] = mapped_column(
        comment="ID of the referenced entity"
    )
    is_read: Mapped[bool] = mapped_column(default=False, index=True)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    action_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        comment="URL to navigate to when clicking notification"
    )
