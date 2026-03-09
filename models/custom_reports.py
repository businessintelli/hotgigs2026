"""Custom Report Builder and Report Scheduler models."""

from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, String, Integer, Text, JSON, Enum, Float, DateTime, ForeignKey, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column
from models.base import BaseModel
from models.enums import ReportType, DeliveryMethod, ExportFormat, ReportScheduleStatus


class SavedReport(BaseModel):
    """Stores custom report definitions created by users."""

    __tablename__ = "saved_reports"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)

    report_name: Mapped[str] = mapped_column(String(255), nullable=False, comment="Name of the report")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="Report description")

    report_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=ReportType.CUSTOM.value,
        comment="ReportType: custom, predefined"
    )

    # Report structure - stored as JSON
    dimensions: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        comment="JSON list of selected dimensions (e.g., ['client', 'job', 'recruiter'])"
    )
    metrics: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        comment="JSON list of selected metrics (e.g., ['placements', 'fill_rate'])"
    )
    filters: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        comment="JSON dict of filter criteria (e.g., {'date_range': 'last_90_days', 'priority': 'urgent'})"
    )
    group_by: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        comment="JSON list of fields to group by"
    )

    # Sorting
    sort_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="Column to sort by")
    sort_order: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="asc",
        comment="Sort order: asc or desc"
    )

    # Visualization
    visualization_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="table",
        comment="Visualization type: table, bar_chart, line_chart, pie_chart, heatmap"
    )

    # Sharing and favorites
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False, comment="Whether marked as favorite")
    is_shared: Mapped[bool] = mapped_column(Boolean, default=False, comment="Whether shared with organization")
    role_access: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="admin_only",
        comment="Role access level: admin_only, msp_admin_only, all_admins"
    )

    # Execution tracking
    last_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, comment="Last execution time")
    run_count: Mapped[int] = mapped_column(Integer, default=0, comment="Total number of executions")

    def __repr__(self):
        return f"<SavedReport(id={self.id}, name={self.report_name}, org_id={self.organization_id})>"


class ReportSchedule(BaseModel):
    """Stores scheduled report jobs for automated delivery."""

    __tablename__ = "report_schedules"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    saved_report_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("saved_reports.id"),
        nullable=True,
        index=True,
        comment="FK to SavedReport; nullable for predefined reports"
    )

    predefined_report_key: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Key for predefined report (e.g., 'by-client', 'conversion-funnel')"
    )

    schedule_name: Mapped[str] = mapped_column(String(255), nullable=False, comment="Name of the schedule")

    # Scheduling
    cron_expression: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Cron expression (e.g., '0 8 * * 1' for Monday 8am)"
    )
    frequency_label: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Human-readable frequency (e.g., 'Weekly on Monday at 8:00 AM')"
    )

    # Delivery configuration
    delivery_method: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=DeliveryMethod.EMAIL.value,
        comment="DeliveryMethod: email, in_app, both"
    )
    delivery_recipients: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        comment="JSON list of email addresses for delivery"
    )
    export_format: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=ExportFormat.PDF.value,
        comment="ExportFormat: pdf, xlsx, csv"
    )

    # Status and scheduling
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, comment="Whether schedule is active")

    # Execution tracking
    last_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, comment="Last execution time")
    next_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, comment="Next scheduled execution")
    run_count: Mapped[int] = mapped_column(Integer, default=0, comment="Total number of executions")

    last_run_status: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Status of last run: success, failed, partial"
    )
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="Error message from last failed run")

    def __repr__(self):
        return f"<ReportSchedule(id={self.id}, name={self.schedule_name}, org_id={self.organization_id})>"
