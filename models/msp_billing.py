"""MSP tiered billing, cascading invoicing, and fee structure models."""
from datetime import datetime, date
from typing import Optional
from sqlalchemy import (
    String, DateTime, Date, Enum, JSON, ForeignKey, Text, Float, Integer,
    Boolean, Index, func, Numeric
)
from sqlalchemy.orm import Mapped, mapped_column
from models.base import BaseModel
import enum


# ── Enums ──────────────────────────────────────────────────

class FeeTierType(str, enum.Enum):
    PERCENTAGE_OF_BILL = "percentage_of_bill"
    FLAT_FEE_PER_HOUR = "flat_fee_per_hour"
    FLAT_FEE_PER_PLACEMENT = "flat_fee_per_placement"
    PERCENTAGE_OF_MARGIN = "percentage_of_margin"


class RevenueBracketStatus(str, enum.Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DRAFT = "draft"


class CascadeInvoiceStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    GENERATED = "generated"
    SENT = "sent"
    PAID = "paid"
    DISPUTED = "disputed"
    VOIDED = "voided"


class ApprovalLevel(str, enum.Enum):
    CLIENT = "client"
    MSP = "msp"
    SUPPLIER = "supplier"
    AUTO = "auto"


class BillingCycleType(str, enum.Enum):
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    SEMIMONTHLY = "semimonthly"
    MONTHLY = "monthly"


# ── Models ─────────────────────────────────────────────────

class MSPFeeTier(BaseModel):
    """
    Defines MSP fee percentage brackets based on supplier revenue.
    E.g., 0-1M = 5%, 1-5M = 4%, 5-10M = 3.5%, 10M+ = 3%.
    """
    __tablename__ = "msp_fee_tiers"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    tier_name: Mapped[str] = mapped_column(String(100), nullable=False)
    revenue_min: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    revenue_max: Mapped[Optional[float]] = mapped_column(Numeric(15, 2), nullable=True)  # NULL = unlimited
    fee_type: Mapped[str] = mapped_column(
        Enum(FeeTierType), default=FeeTierType.PERCENTAGE_OF_BILL, nullable=False
    )
    fee_percentage: Mapped[float] = mapped_column(Numeric(5, 3), nullable=False)  # e.g., 5.000 = 5%
    fee_flat_amount: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(
        Enum(RevenueBracketStatus), default=RevenueBracketStatus.ACTIVE, index=True
    )
    client_org_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("organizations.id"), nullable=True, index=True
    )  # NULL = applies to all clients
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))

    __table_args__ = (
        Index("ix_msp_fee_org_status", "organization_id", "status"),
        Index("ix_msp_fee_revenue_range", "revenue_min", "revenue_max"),
    )


class SupplierRevenueBracket(BaseModel):
    """
    Tracks cumulative supplier revenue per period to determine applicable fee tier.
    """
    __tablename__ = "supplier_revenue_brackets"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    supplier_org_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    total_revenue: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    total_hours: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    total_placements: Mapped[int] = mapped_column(Integer, default=0)
    applied_fee_tier_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("msp_fee_tiers.id"), nullable=True
    )
    applied_fee_percentage: Mapped[Optional[float]] = mapped_column(Numeric(5, 3))
    msp_fee_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    last_calculated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        Index("ix_supp_rev_org_supplier", "organization_id", "supplier_org_id"),
        Index("ix_supp_rev_period", "period_start", "period_end"),
    )


class CascadeInvoice(BaseModel):
    """
    Cascading invoice: when client/MSP approves time, downstream invoices are
    auto-generated. Upstream approval = no downstream approval needed.
    """
    __tablename__ = "cascade_invoices"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    # Link to upstream
    parent_invoice_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("cascade_invoices.id"), nullable=True, index=True
    )
    # Parties
    from_org_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"), nullable=False
    )
    to_org_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"), nullable=False
    )
    # Invoice details
    invoice_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    invoice_type: Mapped[str] = mapped_column(String(50), nullable=False)  # client_to_msp, msp_to_supplier, etc.
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    # Amounts
    gross_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    msp_fee_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    net_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    tax_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    total_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    # Rate details
    bill_rate: Mapped[Optional[float]] = mapped_column(Numeric(8, 2))
    pay_rate: Mapped[Optional[float]] = mapped_column(Numeric(8, 2))
    total_hours: Mapped[Optional[float]] = mapped_column(Numeric(8, 2))
    # Status and approval
    status: Mapped[str] = mapped_column(
        Enum(CascadeInvoiceStatus), default=CascadeInvoiceStatus.PENDING, index=True
    )
    approved_by_level: Mapped[Optional[str]] = mapped_column(Enum(ApprovalLevel))
    approved_by_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    auto_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    upstream_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    # Timesheet link
    timesheet_id: Mapped[Optional[int]] = mapped_column(index=True)
    placement_id: Mapped[Optional[int]] = mapped_column(index=True)
    # Payment
    due_date: Mapped[Optional[date]] = mapped_column(Date)
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    payment_reference: Mapped[Optional[str]] = mapped_column(String(100))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    __table_args__ = (
        Index("ix_cascade_inv_org_status", "organization_id", "status"),
        Index("ix_cascade_inv_parent", "parent_invoice_id"),
        Index("ix_cascade_inv_period", "period_start", "period_end"),
    )


class CascadeApprovalRule(BaseModel):
    """
    Rules governing cascading approvals: e.g., if client approves timesheet,
    MSP-to-supplier invoice is auto-generated and auto-approved.
    """
    __tablename__ = "cascade_approval_rules"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    rule_name: Mapped[str] = mapped_column(String(200), nullable=False)
    trigger_level: Mapped[str] = mapped_column(Enum(ApprovalLevel), nullable=False)  # e.g., "client"
    auto_approve_downstream: Mapped[bool] = mapped_column(Boolean, default=True)
    auto_generate_invoice: Mapped[bool] = mapped_column(Boolean, default=True)
    billing_cycle: Mapped[str] = mapped_column(
        Enum(BillingCycleType), default=BillingCycleType.WEEKLY
    )
    apply_msp_fee: Mapped[bool] = mapped_column(Boolean, default=True)
    client_org_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("organizations.id"), nullable=True
    )  # NULL = applies to all clients
    supplier_org_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("organizations.id"), nullable=True
    )  # NULL = applies to all suppliers
    notes: Mapped[Optional[str]] = mapped_column(Text)


class MSPBillingConfig(BaseModel):
    """
    Master billing configuration for MSP organization.
    """
    __tablename__ = "msp_billing_configs"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, unique=True
    )
    default_billing_cycle: Mapped[str] = mapped_column(
        Enum(BillingCycleType), default=BillingCycleType.WEEKLY
    )
    auto_cascade_on_approval: Mapped[bool] = mapped_column(Boolean, default=True)
    auto_apply_fee_tier: Mapped[bool] = mapped_column(Boolean, default=True)
    default_payment_terms_days: Mapped[int] = mapped_column(Integer, default=30)
    tax_rate: Mapped[float] = mapped_column(Numeric(5, 3), default=0)
    invoice_prefix: Mapped[str] = mapped_column(String(20), default="INV")
    msp_fee_calculation_method: Mapped[str] = mapped_column(String(50), default="percentage_of_bill")
    include_expenses_in_revenue: Mapped[bool] = mapped_column(Boolean, default=False)
    revenue_tracking_period: Mapped[str] = mapped_column(String(20), default="annual")  # annual, quarterly
