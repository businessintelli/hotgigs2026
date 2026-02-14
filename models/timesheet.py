"""Timesheet tracking models."""

from datetime import datetime, date, time
from typing import Optional
from sqlalchemy import String, Text, Integer, Float, Boolean, Date, DateTime, Time, JSON, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import BaseModel


class Timesheet(BaseModel):
    """Timesheet for a contractor placement."""

    __tablename__ = "timesheets"

    placement_id: Mapped[int] = mapped_column(ForeignKey("offers.id"), nullable=False, index=True)
    contractor_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), nullable=False, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False, index=True)
    requirement_id: Mapped[Optional[int]] = mapped_column(ForeignKey("requirements.id"))

    # Period
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    billing_cycle: Mapped[str] = mapped_column(String(50), default="weekly")

    # Totals (calculated)
    total_regular_hours: Mapped[float] = mapped_column(Float, default=0.0)
    total_overtime_hours: Mapped[float] = mapped_column(Float, default=0.0)
    total_hours: Mapped[float] = mapped_column(Float, default=0.0)
    total_billable_hours: Mapped[float] = mapped_column(Float, default=0.0)

    # Rates
    regular_rate: Mapped[float] = mapped_column(Float, nullable=False)
    overtime_rate: Mapped[Optional[float]] = mapped_column(Float)
    bill_rate: Mapped[Optional[float]] = mapped_column(Float)

    # Amounts (calculated)
    regular_amount: Mapped[float] = mapped_column(Float, default=0.0)
    overtime_amount: Mapped[float] = mapped_column(Float, default=0.0)
    total_pay_amount: Mapped[float] = mapped_column(Float, default=0.0)
    total_bill_amount: Mapped[float] = mapped_column(Float, default=0.0)
    margin_amount: Mapped[float] = mapped_column(Float, default=0.0)

    # Status
    status: Mapped[str] = mapped_column(String(50), default="draft", index=True)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    approved_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    rejected_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    rejected_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text)

    # Invoice link
    invoice_id: Mapped[Optional[int]] = mapped_column(ForeignKey("invoices.id"))
    payment_id: Mapped[Optional[int]] = mapped_column(ForeignKey("payments.id"))

    # Notes
    contractor_notes: Mapped[Optional[str]] = mapped_column(Text)
    approver_notes: Mapped[Optional[str]] = mapped_column(Text)
    anomalies: Mapped[Optional[dict]] = mapped_column(JSON)

    # Unique constraint
    __table_args__ = (
        UniqueConstraint("contractor_id", "period_start", "period_end", name="uq_timesheet_contractor_period"),
        Index("idx_timesheet_status_period", "status", "period_start"),
    )

    entries = relationship("TimesheetEntry", back_populates="timesheet", cascade="all, delete-orphan")


class TimesheetEntry(BaseModel):
    """Individual time entry within a timesheet."""

    __tablename__ = "timesheet_entries"

    timesheet_id: Mapped[int] = mapped_column(ForeignKey("timesheets.id"), nullable=False, index=True)
    entry_date: Mapped[date] = mapped_column(Date, nullable=False)
    day_of_week: Mapped[str] = mapped_column(String(10))

    # Hours
    hours_regular: Mapped[float] = mapped_column(Float, default=0.0)
    hours_overtime: Mapped[float] = mapped_column(Float, default=0.0)
    total_hours: Mapped[float] = mapped_column(Float, default=0.0)
    is_billable: Mapped[bool] = mapped_column(Boolean, default=True)

    # Details
    start_time: Mapped[Optional[time]] = mapped_column(Time)
    end_time: Mapped[Optional[time]] = mapped_column(Time)
    break_minutes: Mapped[int] = mapped_column(Integer, default=0)
    project_code: Mapped[Optional[str]] = mapped_column(String(100))
    task_description: Mapped[Optional[str]] = mapped_column(Text)

    # Flags
    is_holiday: Mapped[bool] = mapped_column(Boolean, default=False)
    is_pto: Mapped[bool] = mapped_column(Boolean, default=False)
    is_sick_day: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Unique constraint
    __table_args__ = (
        UniqueConstraint("timesheet_id", "entry_date", name="uq_entry_timesheet_date"),
        Index("idx_entry_date_billable", "entry_date", "is_billable"),
    )

    timesheet = relationship("Timesheet", back_populates="entries")
