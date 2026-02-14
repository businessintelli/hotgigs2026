"""Timesheet schemas for request/response validation."""

from datetime import datetime, date, time
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class TimesheetEntryCreate(BaseModel):
    """Create time entry request."""

    entry_date: date
    hours_regular: float = Field(ge=0, le=24)
    hours_overtime: float = Field(default=0, ge=0, le=24)
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    break_minutes: int = Field(default=0, ge=0)
    project_code: Optional[str] = None
    task_description: Optional[str] = None
    is_billable: bool = True
    is_holiday: bool = False
    is_pto: bool = False
    is_sick_day: bool = False
    notes: Optional[str] = None

    @field_validator("hours_regular", "hours_overtime")
    @classmethod
    def validate_hours(cls, v: float) -> float:
        """Validate hours are reasonable."""
        if v < 0:
            raise ValueError("Hours cannot be negative")
        if v > 24:
            raise ValueError("Hours cannot exceed 24 per day")
        return v


class TimesheetEntryUpdate(BaseModel):
    """Update time entry request."""

    hours_regular: Optional[float] = Field(default=None, ge=0, le=24)
    hours_overtime: Optional[float] = Field(default=None, ge=0, le=24)
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    break_minutes: Optional[int] = Field(default=None, ge=0)
    project_code: Optional[str] = None
    task_description: Optional[str] = None
    is_billable: Optional[bool] = None
    is_holiday: Optional[bool] = None
    is_pto: Optional[bool] = None
    is_sick_day: Optional[bool] = None
    notes: Optional[str] = None


class TimesheetEntryResponse(BaseModel):
    """Time entry response."""

    id: int
    timesheet_id: int
    entry_date: date
    day_of_week: str
    hours_regular: float
    hours_overtime: float
    total_hours: float
    is_billable: bool
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    break_minutes: int
    project_code: Optional[str] = None
    task_description: Optional[str] = None
    is_holiday: bool
    is_pto: bool
    is_sick_day: bool
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TimesheetCreate(BaseModel):
    """Create timesheet request."""

    placement_id: int
    contractor_id: int
    customer_id: int
    requirement_id: Optional[int] = None
    period_start: date
    period_end: date
    billing_cycle: str = "weekly"
    regular_rate: float = Field(gt=0)
    overtime_rate: Optional[float] = None
    bill_rate: Optional[float] = None
    contractor_notes: Optional[str] = None


class TimesheetUpdate(BaseModel):
    """Update timesheet request."""

    regular_rate: Optional[float] = Field(default=None, gt=0)
    overtime_rate: Optional[float] = None
    bill_rate: Optional[float] = None
    contractor_notes: Optional[str] = None


class TimesheetResponse(BaseModel):
    """Timesheet response."""

    id: int
    placement_id: int
    contractor_id: int
    customer_id: int
    requirement_id: Optional[int] = None
    period_start: date
    period_end: date
    billing_cycle: str
    total_regular_hours: float
    total_overtime_hours: float
    total_hours: float
    total_billable_hours: float
    regular_rate: float
    overtime_rate: Optional[float] = None
    bill_rate: Optional[float] = None
    regular_amount: float
    overtime_amount: float
    total_pay_amount: float
    total_bill_amount: float
    margin_amount: float
    status: str
    submitted_at: Optional[datetime] = None
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    rejected_by: Optional[int] = None
    rejected_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    invoice_id: Optional[int] = None
    payment_id: Optional[int] = None
    contractor_notes: Optional[str] = None
    approver_notes: Optional[str] = None
    anomalies: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TimesheetDetailResponse(TimesheetResponse):
    """Timesheet with entries."""

    entries: List[TimesheetEntryResponse] = []


class TimesheetListFilter(BaseModel):
    """Filter for timesheet list."""

    contractor_id: Optional[int] = None
    customer_id: Optional[int] = None
    placement_id: Optional[int] = None
    status: Optional[str] = None
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    skip: int = 0
    limit: int = 20


class TimesheetApproveRequest(BaseModel):
    """Approve timesheet request."""

    approver_id: int
    notes: Optional[str] = None


class TimesheetRejectRequest(BaseModel):
    """Reject timesheet request."""

    approver_id: int
    reason: str


class TimesheetAnomalyDetection(BaseModel):
    """Anomaly detection result."""

    anomaly_type: str
    severity: str
    description: str
    entry_ids: Optional[List[int]] = None
    recommended_action: Optional[str] = None


class TimesheetAnomalyResponse(BaseModel):
    """Anomaly detection response."""

    timesheet_id: int
    anomalies: List[TimesheetAnomalyDetection]
    risk_score: float
    has_anomalies: bool


class TimesheetCalendarDay(BaseModel):
    """Calendar day representation."""

    date: date
    hours: float
    is_weekend: bool
    entries_count: int


class TimesheetCalendarResponse(BaseModel):
    """Calendar view response."""

    contractor_id: int
    month: int
    year: int
    days: List[TimesheetCalendarDay]
    total_hours: float
    total_billable_hours: float


class TimesheetAnalyticsResponse(BaseModel):
    """Timesheet analytics."""

    total_hours_billed: float
    utilization_rate: float
    avg_hours_per_contractor: float
    overtime_percentage: float
    on_time_submission_rate: float
    avg_approval_turnaround_hours: float
    total_contractors: int
    submitted_timesheets: int
    approved_timesheets: int
    pending_timesheets: int
    total_payroll_amount: float
    total_bill_amount: float


class TimesheetBulkApproveRequest(BaseModel):
    """Bulk approve timesheets request."""

    timesheet_ids: List[int]
    approver_id: int


class TimesheetBulkApproveResponse(BaseModel):
    """Bulk approve response."""

    total_requested: int
    approved_count: int
    failed_count: int
    failed_ids: List[int]
