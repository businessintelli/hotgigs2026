"""Invoicing and payment models."""

from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Text, Integer, Float, Boolean, Date, DateTime, JSON, ForeignKey, UniqueConstraint, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import BaseModel


class Invoice(BaseModel):
    """Customer invoice."""

    __tablename__ = "invoices"

    invoice_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False, index=True)

    # Dates
    invoice_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    period_start: Mapped[Optional[date]] = mapped_column(Date)
    period_end: Mapped[Optional[date]] = mapped_column(Date)

    # Amounts
    subtotal: Mapped[float] = mapped_column(Float, default=0.0)
    tax_amount: Mapped[float] = mapped_column(Float, default=0.0)
    tax_rate: Mapped[Optional[float]] = mapped_column(Float)
    discount_amount: Mapped[float] = mapped_column(Float, default=0.0)
    discount_percentage: Mapped[Optional[float]] = mapped_column(Float)
    total_amount: Mapped[float] = mapped_column(Float, default=0.0)
    amount_paid: Mapped[float] = mapped_column(Float, default=0.0)
    amount_due: Mapped[float] = mapped_column(Float, default=0.0)
    currency: Mapped[str] = mapped_column(String(3), default="USD")

    # Status
    status: Mapped[str] = mapped_column(String(50), default="draft", index=True)

    # Payment terms
    payment_terms: Mapped[str] = mapped_column(String(50), default="net_30")

    # File
    pdf_path: Mapped[Optional[str]] = mapped_column(String(500))

    # QuickBooks
    qb_invoice_id: Mapped[Optional[str]] = mapped_column(String(255))
    qb_sync_status: Mapped[Optional[str]] = mapped_column(String(50))
    qb_last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    qb_sync_error: Mapped[Optional[str]] = mapped_column(Text)

    # Delivery
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    sent_to: Mapped[Optional[str]] = mapped_column(String(255))
    viewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Reminders
    reminder_count: Mapped[int] = mapped_column(Integer, default=0)
    last_reminder_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    internal_notes: Mapped[Optional[str]] = mapped_column(Text)
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))

    __table_args__ = (
        Index("idx_invoice_status_customer", "status", "customer_id"),
        Index("idx_invoice_date_due", "invoice_date", "due_date"),
    )

    line_items = relationship("InvoiceLineItem", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("InvoicePayment", back_populates="invoice", cascade="all, delete-orphan")


class InvoiceLineItem(BaseModel):
    """Individual line item on an invoice."""

    __tablename__ = "invoice_line_items"

    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id"), nullable=False, index=True)
    timesheet_id: Mapped[Optional[int]] = mapped_column(ForeignKey("timesheets.id"))
    placement_id: Mapped[Optional[int]] = mapped_column(ForeignKey("offers.id"))

    # Line item details
    description: Mapped[str] = mapped_column(Text, nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit_type: Mapped[str] = mapped_column(String(50), default="hours")
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    is_taxable: Mapped[bool] = mapped_column(Boolean, default=True)

    # Categorization
    line_type: Mapped[str] = mapped_column(String(50), default="service")
    project_code: Mapped[Optional[str]] = mapped_column(String(100))

    # QuickBooks mapping
    qb_item_id: Mapped[Optional[str]] = mapped_column(String(255))
    qb_account_id: Mapped[Optional[str]] = mapped_column(String(255))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    invoice = relationship("Invoice", back_populates="line_items")


class InvoicePayment(BaseModel):
    """Payment received against an invoice."""

    __tablename__ = "invoice_payments"

    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id"), nullable=False, index=True)
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    payment_method: Mapped[str] = mapped_column(String(50))
    reference_number: Mapped[Optional[str]] = mapped_column(String(255))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    qb_payment_id: Mapped[Optional[str]] = mapped_column(String(255))
    recorded_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))

    invoice = relationship("Invoice", back_populates="payments")


class CreditMemo(BaseModel):
    """Credit memo / refund against an invoice."""

    __tablename__ = "credit_memos"

    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id"), nullable=False, index=True)
    memo_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="issued")
    applied_to_invoice_id: Mapped[Optional[int]] = mapped_column(ForeignKey("invoices.id"))
    qb_credit_memo_id: Mapped[Optional[str]] = mapped_column(String(255))
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))


class QuickBooksConfig(BaseModel):
    """QuickBooks integration configuration."""

    __tablename__ = "quickbooks_config"

    realm_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    company_name: Mapped[Optional[str]] = mapped_column(String(255))
    access_token_encrypted: Mapped[Optional[str]] = mapped_column(Text)
    refresh_token_encrypted: Mapped[Optional[str]] = mapped_column(Text)
    token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    is_connected: Mapped[bool] = mapped_column(Boolean, default=False)
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    sync_config: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    account_mapping: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    connected_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))


class QuickBooksSyncLog(BaseModel):
    """Log of QuickBooks sync operations."""

    __tablename__ = "quickbooks_sync_log"

    sync_type: Mapped[str] = mapped_column(String(50))
    direction: Mapped[str] = mapped_column(String(20))
    entity_type: Mapped[Optional[str]] = mapped_column(String(50))
    entity_id: Mapped[Optional[int]] = mapped_column(Integer)
    qb_entity_id: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50))
    records_processed: Mapped[int] = mapped_column(Integer, default=0)
    records_failed: Mapped[int] = mapped_column(Integer, default=0)
    error_details: Mapped[Optional[dict]] = mapped_column(JSON)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    triggered_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))

    __table_args__ = (
        Index("idx_sync_log_status_type", "status", "sync_type"),
    )
