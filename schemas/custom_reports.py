"""Pydantic schemas for Custom Reports and Report Scheduling."""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


# ─────────────────────────────────────────────────────────────────────────
# Saved Report Schemas
# ─────────────────────────────────────────────────────────────────────────

class SavedReportCreate(BaseModel):
    """Schema for creating a new saved report."""

    report_name: str = Field(..., min_length=1, max_length=255, description="Name of the report")
    description: Optional[str] = Field(None, max_length=1000, description="Report description")
    report_type: str = Field(default="custom", description="ReportType: custom, predefined")

    dimensions: List[str] = Field(default_factory=list, description="Selected dimensions")
    metrics: List[str] = Field(default_factory=list, description="Selected metrics")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Filter criteria")
    group_by: List[str] = Field(default_factory=list, description="Fields to group by")

    sort_by: Optional[str] = Field(None, max_length=100, description="Column to sort by")
    sort_order: str = Field(default="asc", pattern="^(asc|desc)$", description="Sort order")

    visualization_type: str = Field(default="table", description="Visualization type")
    role_access: str = Field(default="admin_only", description="Role access: admin_only, msp_admin_only, all_admins")

    model_config = ConfigDict(from_attributes=True)


class SavedReportUpdate(BaseModel):
    """Schema for updating a saved report."""

    report_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)

    dimensions: Optional[List[str]] = None
    metrics: Optional[List[str]] = None
    filters: Optional[Dict[str, Any]] = None
    group_by: Optional[List[str]] = None

    sort_by: Optional[str] = None
    sort_order: Optional[str] = Field(None, pattern="^(asc|desc)$")

    visualization_type: Optional[str] = None
    role_access: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class SavedReportResponse(BaseModel):
    """Schema for returning a saved report."""

    id: int
    user_id: int
    organization_id: int
    report_name: str
    description: Optional[str]
    report_type: str

    dimensions: List[str]
    metrics: List[str]
    filters: Dict[str, Any]
    group_by: List[str]

    sort_by: Optional[str]
    sort_order: str

    visualization_type: str
    is_favorite: bool
    is_shared: bool
    role_access: str

    last_run_at: Optional[datetime]
    run_count: int

    created_at: datetime
    updated_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class SavedReportListResponse(BaseModel):
    """Schema for listing saved reports."""

    total: int
    page: int
    page_size: int
    items: List[SavedReportResponse]

    model_config = ConfigDict(from_attributes=True)


# ─────────────────────────────────────────────────────────────────────────
# Report Schedule Schemas
# ─────────────────────────────────────────────────────────────────────────

class ReportScheduleCreate(BaseModel):
    """Schema for creating a report schedule."""

    schedule_name: str = Field(..., min_length=1, max_length=255, description="Name of the schedule")
    saved_report_id: Optional[int] = Field(None, description="FK to SavedReport; optional for predefined reports")
    predefined_report_key: Optional[str] = Field(None, max_length=100, description="Key for predefined report")

    cron_expression: str = Field(..., max_length=100, description="Cron expression")
    frequency_label: str = Field(..., max_length=255, description="Human-readable frequency")

    delivery_method: str = Field(default="email", description="DeliveryMethod: email, in_app, both")
    delivery_recipients: List[str] = Field(default_factory=list, description="Email addresses for delivery")
    export_format: str = Field(default="pdf", description="ExportFormat: pdf, xlsx, csv")

    is_enabled: bool = Field(default=True, description="Whether schedule is active")

    model_config = ConfigDict(from_attributes=True)


class ReportScheduleUpdate(BaseModel):
    """Schema for updating a report schedule."""

    schedule_name: Optional[str] = Field(None, min_length=1, max_length=255)
    cron_expression: Optional[str] = Field(None, max_length=100)
    frequency_label: Optional[str] = Field(None, max_length=255)

    delivery_method: Optional[str] = None
    delivery_recipients: Optional[List[str]] = None
    export_format: Optional[str] = None

    is_enabled: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


class ReportScheduleResponse(BaseModel):
    """Schema for returning a report schedule."""

    id: int
    user_id: int
    organization_id: int
    saved_report_id: Optional[int]
    predefined_report_key: Optional[str]

    schedule_name: str
    cron_expression: str
    frequency_label: str

    delivery_method: str
    delivery_recipients: List[str]
    export_format: str

    is_enabled: bool

    last_run_at: Optional[datetime]
    next_run_at: Optional[datetime]
    run_count: int

    last_run_status: Optional[str]
    last_error: Optional[str]

    created_at: datetime
    updated_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class ReportScheduleListResponse(BaseModel):
    """Schema for listing report schedules."""

    total: int
    page: int
    page_size: int
    items: List[ReportScheduleResponse]

    model_config = ConfigDict(from_attributes=True)


# ─────────────────────────────────────────────────────────────────────────
# Report Execution and Result Schemas
# ─────────────────────────────────────────────────────────────────────────

class ReportExecutionResult(BaseModel):
    """Schema for report execution result."""

    report_id: Optional[int] = Field(None, description="ID of saved report, if executed from saved report")
    report_name: str = Field(..., description="Name of the report")
    data: Dict[str, Any] = Field(..., description="Report data as dict")
    row_count: int = Field(..., description="Number of rows in report")
    execution_time_ms: int = Field(..., description="Execution time in milliseconds")
    generated_at: datetime = Field(..., description="Timestamp when report was generated")

    model_config = ConfigDict(from_attributes=True)


# ─────────────────────────────────────────────────────────────────────────
# Report Builder Config Schemas
# ─────────────────────────────────────────────────────────────────────────

class AvailableDimension(BaseModel):
    """Schema for available report dimension."""

    key: str = Field(..., description="Dimension key")
    label: str = Field(..., description="Display label")
    description: str = Field(..., description="Description of the dimension")
    category: str = Field(..., description="Category (e.g., 'Entity', 'Time', 'Status')")

    model_config = ConfigDict(from_attributes=True)


class AvailableMetric(BaseModel):
    """Schema for available report metric."""

    key: str = Field(..., description="Metric key")
    label: str = Field(..., description="Display label")
    description: str = Field(..., description="Description of the metric")
    format_type: str = Field(..., description="Format: number, percent, currency, days")

    model_config = ConfigDict(from_attributes=True)


class AvailableFilter(BaseModel):
    """Schema for available filter."""

    key: str = Field(..., description="Filter key")
    label: str = Field(..., description="Display label")
    type: str = Field(..., description="Filter type: date_range, select, multi_select, number")
    options: Optional[List[Dict[str, Any]]] = Field(None, description="Options for select/multi_select filters")

    model_config = ConfigDict(from_attributes=True)


class ReportBuilderConfig(BaseModel):
    """Schema for report builder configuration."""

    available_dimensions: List[AvailableDimension] = Field(..., description="Available dimensions")
    available_metrics: List[AvailableMetric] = Field(..., description="Available metrics")
    available_filters: List[AvailableFilter] = Field(..., description="Available filters")
    available_visualizations: List[str] = Field(..., description="Available visualization types")

    model_config = ConfigDict(from_attributes=True)


# ─────────────────────────────────────────────────────────────────────────
# Report Templates Schema
# ─────────────────────────────────────────────────────────────────────────

class ReportTemplate(BaseModel):
    """Schema for a predefined report template."""

    key: str = Field(..., description="Unique template key")
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    category: str = Field(..., description="Template category (e.g., 'Recruitment', 'Performance')")

    dimensions: List[str] = Field(..., description="Default dimensions")
    metrics: List[str] = Field(..., description="Default metrics")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Default filters")
    visualization_type: str = Field(..., description="Default visualization type")

    model_config = ConfigDict(from_attributes=True)


class ReportTemplateListResponse(BaseModel):
    """Schema for listing report templates."""

    total: int
    items: List[ReportTemplate]

    model_config = ConfigDict(from_attributes=True)


# ─────────────────────────────────────────────────────────────────────────
# Schedule History Schema
# ─────────────────────────────────────────────────────────────────────────

class ScheduleRunHistory(BaseModel):
    """Schema for a single schedule run history entry."""

    run_id: int = Field(..., description="Run ID")
    scheduled_time: datetime = Field(..., description="Scheduled execution time")
    actual_time: Optional[datetime] = Field(None, description="Actual execution time")
    status: str = Field(..., description="Status: success, failed, partial")
    row_count: Optional[int] = Field(None, description="Rows in report")
    execution_time_ms: Optional[int] = Field(None, description="Execution time in ms")
    error_message: Optional[str] = Field(None, description="Error message if failed")

    model_config = ConfigDict(from_attributes=True)


class ScheduleRunHistoryList(BaseModel):
    """Schema for listing schedule run history."""

    schedule_id: int
    total_runs: int
    runs: List[ScheduleRunHistory]

    model_config = ConfigDict(from_attributes=True)
