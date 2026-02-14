"""Payment processing models."""

from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Text, Integer, Float, Boolean, Date, DateTime, JSON, ForeignKey, Enum as SAEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import BaseModel


class Payment(BaseModel):
    """Payment record for all platform payments."""
    __tablename__ = "payments"

    payment_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # contractor_pay/referral_bonus/supplier_commission/expense_reimbursement
    placement_id: Mapped[Optional[int]] = mapped_column(ForeignKey("offers.id"))
    referral_bonus_id: Mapped[Optional[int]] = mapped_column(ForeignKey("referral_bonuses.id"))
    invoice_id: Mapped[Optional[int]] = mapped_column(ForeignKey("invoices.id"))
    timesheet_id: Mapped[Optional[int]] = mapped_column(ForeignKey("timesheets.id"))
    # Payee
    payee_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # candidate/supplier/referrer
    payee_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    payee_name: Mapped[str] = mapped_column(String(255), nullable=False)
    payee_email: Mapped[Optional[str]] = mapped_column(String(255))
    # Amounts
    gross_amount: Mapped[float] = mapped_column(Float, nullable=False)
    tax_withholding: Mapped[float] = mapped_column(Float, default=0.0)
    deductions: Mapped[float] = mapped_column(Float, default=0.0)
    net_amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    # Payment method
    payment_method_id: Mapped[Optional[int]] = mapped_column(ForeignKey("payment_methods.id"))
    payment_method_type: Mapped[Optional[str]] = mapped_column(String(50))  # ach/wire/stripe/paypal/check
    # Status
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    # External references
    external_transaction_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    gateway_response: Mapped[Optional[dict]] = mapped_column(JSON)
    # Dates
    scheduled_date: Mapped[Optional[date]] = mapped_column(Date, index=True)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    failed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    failure_reason: Mapped[Optional[str]] = mapped_column(Text)
    # Approval
    approved_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    metadata_extra: Mapped[dict] = mapped_column(JSON, default=dict)

    method = relationship("PaymentMethod")


class PaymentMethod(BaseModel):
    """Stored payment methods for payees (tokenized)."""
    __tablename__ = "payment_methods"

    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    method_type: Mapped[str] = mapped_column(String(50), nullable=False)  # bank_account/debit_card/paypal/wire
    # Tokenized data (never store raw account numbers)
    token: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    gateway: Mapped[Optional[str]] = mapped_column(String(50))  # stripe/plaid
    last_four: Mapped[Optional[str]] = mapped_column(String(4))
    bank_name: Mapped[Optional[str]] = mapped_column(String(255))
    account_holder_name: Mapped[Optional[str]] = mapped_column(String(255))
    routing_number_last_four: Mapped[Optional[str]] = mapped_column(String(4))
    paypal_email: Mapped[Optional[str]] = mapped_column(String(255))
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    payment_count: Mapped[int] = mapped_column(Integer, default=0)


class PaymentSchedule(BaseModel):
    """Recurring payment schedules."""
    __tablename__ = "payment_schedules"

    payee_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    payee_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    placement_id: Mapped[Optional[int]] = mapped_column(ForeignKey("offers.id"))
    frequency: Mapped[str] = mapped_column(String(50), nullable=False)  # weekly/bi_weekly/semi_monthly/monthly
    amount: Mapped[Optional[float]] = mapped_column(Float)  # Fixed amount or null if hourly
    rate: Mapped[Optional[float]] = mapped_column(Float)  # Hourly rate if timesheet-based
    rate_type: Mapped[str] = mapped_column(String(50), default="hourly")
    payment_method_id: Mapped[Optional[int]] = mapped_column(ForeignKey("payment_methods.id"))
    next_payment_date: Mapped[Optional[date]] = mapped_column(Date, index=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    auto_process: Mapped[bool] = mapped_column(Boolean, default=False)
    total_paid: Mapped[float] = mapped_column(Float, default=0.0)
    payments_count: Mapped[int] = mapped_column(Integer, default=0)
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))


class PaymentReconciliation(BaseModel):
    """Payment reconciliation records."""
    __tablename__ = "payment_reconciliations"

    period_start: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    period_end: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    total_invoiced: Mapped[float] = mapped_column(Float, default=0.0)
    total_collected: Mapped[float] = mapped_column(Float, default=0.0)
    total_paid_out: Mapped[float] = mapped_column(Float, default=0.0)
    gross_margin: Mapped[float] = mapped_column(Float, default=0.0)
    discrepancies: Mapped[Optional[dict]] = mapped_column(JSON)  # [{type, amount, description}]
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    reconciled_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    reconciled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    payment_count: Mapped[int] = mapped_column(Integer, default=0)
