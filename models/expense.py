"""Expense tracking for placements."""
from datetime import date, datetime
from typing import Optional
from sqlalchemy import String, Float, Date, DateTime, ForeignKey, Index, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column
from models.base import BaseModel
from models.enums import ExpenseStatus, ExpenseCategory


class ExpenseEntry(BaseModel):
    __tablename__ = "expense_entries"

    placement_id: Mapped[int] = mapped_column(ForeignKey("placement_records.id"), nullable=False, index=True)
    timesheet_id: Mapped[Optional[int]] = mapped_column(ForeignKey("timesheets.id"))
    submitted_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    category: Mapped[str] = mapped_column(Enum(ExpenseCategory), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    receipt_url: Mapped[Optional[str]] = mapped_column(String(500))
    expense_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    status: Mapped[str] = mapped_column(Enum(ExpenseStatus), default=ExpenseStatus.DRAFT, index=True)
    approved_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text)

    __table_args__ = (
        Index("ix_expense_placement_status", "placement_id", "status"),
        Index("ix_expense_date_status", "expense_date", "status"),
    )
