"""Schemas for MSP tiered billing, cascading invoicing, and fee structures."""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field


# ── Fee Tier Schemas ────────────────────────────────────────

class FeeTierCreate(BaseModel):
    tier_name: str
    revenue_min: float = 0
    revenue_max: Optional[float] = None
    fee_type: str = "percentage_of_bill"
    fee_percentage: float
    fee_flat_amount: Optional[float] = None
    effective_from: date
    effective_to: Optional[date] = None
    client_org_id: Optional[int] = None
    notes: Optional[str] = None

class FeeTierResponse(BaseModel):
    id: int
    tier_name: str
    revenue_min: float
    revenue_max: Optional[float]
    fee_type: str
    fee_percentage: float
    fee_flat_amount: Optional[float]
    effective_from: date
    effective_to: Optional[date]
    status: str
    client_org_id: Optional[int]
    notes: Optional[str]
    created_at: datetime

class FeeTierUpdate(BaseModel):
    tier_name: Optional[str] = None
    revenue_min: Optional[float] = None
    revenue_max: Optional[float] = None
    fee_percentage: Optional[float] = None
    effective_to: Optional[date] = None
    status: Optional[str] = None
    notes: Optional[str] = None


# ── Supplier Revenue Schemas ────────────────────────────────

class SupplierRevenueResponse(BaseModel):
    id: int
    supplier_org_id: int
    supplier_name: str
    period_start: date
    period_end: date
    total_revenue: float
    total_hours: float
    total_placements: int
    applied_fee_tier: Optional[str]
    applied_fee_percentage: Optional[float]
    msp_fee_amount: float

class SupplierRevenueSummary(BaseModel):
    supplier_org_id: int
    supplier_name: str
    current_revenue: float
    current_tier: str
    fee_percentage: float
    ytd_msp_fees: float
    active_placements: int
    next_tier_at: Optional[float]
    savings_at_next_tier: Optional[float]


# ── Cascade Invoice Schemas ─────────────────────────────────

class CascadeInvoiceResponse(BaseModel):
    id: int
    invoice_number: str
    invoice_type: str
    from_org_name: str
    to_org_name: str
    period_start: date
    period_end: date
    gross_amount: float
    msp_fee_amount: float
    net_amount: float
    tax_amount: float
    total_amount: float
    bill_rate: Optional[float]
    pay_rate: Optional[float]
    total_hours: Optional[float]
    status: str
    auto_approved: bool
    upstream_approved: bool
    approved_at: Optional[datetime]
    due_date: Optional[date]
    paid_at: Optional[datetime]
    parent_invoice_id: Optional[int]
    children: Optional[List["CascadeInvoiceResponse"]] = None
    created_at: datetime

class CascadeChainResponse(BaseModel):
    """Full cascade chain: Client→MSP→Supplier invoices for one timesheet."""
    timesheet_id: int
    placement_id: int
    candidate_name: str
    period: str
    total_hours: float
    client_invoice: Optional[CascadeInvoiceResponse]
    msp_invoice: Optional[CascadeInvoiceResponse]
    supplier_invoice: Optional[CascadeInvoiceResponse]
    cascade_status: str  # fully_cascaded, partially_cascaded, pending

class TimesheetApprovalCascadeRequest(BaseModel):
    timesheet_id: int
    approval_level: str  # "client" or "msp"
    approved_by_user_id: int
    notes: Optional[str] = None


# ── Approval Rules ──────────────────────────────────────────

class ApprovalRuleCreate(BaseModel):
    rule_name: str
    trigger_level: str
    auto_approve_downstream: bool = True
    auto_generate_invoice: bool = True
    billing_cycle: str = "weekly"
    apply_msp_fee: bool = True
    client_org_id: Optional[int] = None
    supplier_org_id: Optional[int] = None
    notes: Optional[str] = None

class ApprovalRuleResponse(BaseModel):
    id: int
    rule_name: str
    trigger_level: str
    auto_approve_downstream: bool
    auto_generate_invoice: bool
    billing_cycle: str
    apply_msp_fee: bool
    client_org_id: Optional[int]
    supplier_org_id: Optional[int]
    notes: Optional[str]


# ── Billing Config ──────────────────────────────────────────

class BillingConfigResponse(BaseModel):
    id: int
    organization_id: int
    default_billing_cycle: str
    auto_cascade_on_approval: bool
    auto_apply_fee_tier: bool
    default_payment_terms_days: int
    tax_rate: float
    invoice_prefix: str
    msp_fee_calculation_method: str
    include_expenses_in_revenue: bool
    revenue_tracking_period: str

class BillingConfigUpdate(BaseModel):
    default_billing_cycle: Optional[str] = None
    auto_cascade_on_approval: Optional[bool] = None
    auto_apply_fee_tier: Optional[bool] = None
    default_payment_terms_days: Optional[int] = None
    tax_rate: Optional[float] = None
    invoice_prefix: Optional[str] = None
    msp_fee_calculation_method: Optional[str] = None
    include_expenses_in_revenue: Optional[bool] = None
    revenue_tracking_period: Optional[str] = None


# ── Dashboard ───────────────────────────────────────────────

class BillingDashboardResponse(BaseModel):
    total_invoices: int
    total_billed: float
    total_paid: float
    total_outstanding: float
    total_msp_fees: float
    cascade_completion_rate: float
    avg_days_to_payment: float
    invoices_by_status: dict
    fee_tiers: List[FeeTierResponse]
    supplier_revenue_summary: List[SupplierRevenueSummary]
