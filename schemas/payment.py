"""Pydantic schemas for payment processing."""

from pydantic import BaseModel, Field, EmailStr
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from schemas.common import BaseResponse


# Payment Schemas

class PaymentCreate(BaseModel):
    """Create payment."""

    payment_type: str = Field(..., pattern="^(contractor_pay|referral_bonus|supplier_commission|expense_reimbursement)$")
    payee_type: str = Field(..., pattern="^(candidate|supplier|referrer)$")
    payee_id: int
    payee_name: str = Field(..., max_length=255)
    payee_email: Optional[EmailStr] = None
    gross_amount: float = Field(..., gt=0)
    tax_withholding: float = Field(default=0.0, ge=0)
    deductions: float = Field(default=0.0, ge=0)
    currency: str = Field(default="USD", max_length=3)
    payment_method_id: Optional[int] = None
    scheduled_date: Optional[date] = None
    placement_id: Optional[int] = None
    referral_bonus_id: Optional[int] = None
    invoice_id: Optional[int] = None
    timesheet_id: Optional[int] = None
    notes: Optional[str] = None
    metadata_extra: Optional[Dict[str, Any]] = Field(default_factory=dict)


class PaymentUpdate(BaseModel):
    """Update payment."""

    scheduled_date: Optional[date] = None
    notes: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(pending|processing|completed|failed|cancelled|refunded)$")
    metadata_extra: Optional[Dict[str, Any]] = None


class PaymentResponse(BaseResponse):
    """Payment response."""

    id: int
    payment_type: str
    payee_type: str
    payee_id: int
    payee_name: str
    payee_email: Optional[str]
    gross_amount: float
    tax_withholding: float
    deductions: float
    net_amount: float
    currency: str
    status: str
    external_transaction_id: Optional[str]
    scheduled_date: Optional[date]
    processed_at: Optional[datetime]
    completed_at: Optional[datetime]
    failed_at: Optional[datetime]
    notes: Optional[str]

    class Config:
        from_attributes = True


# Payment Method Schemas

class PaymentMethodCreate(BaseModel):
    """Create payment method."""

    entity_type: str = Field(..., pattern="^(candidate|supplier|referrer)$")
    entity_id: int
    method_type: str = Field(..., pattern="^(bank_account|debit_card|paypal|wire)$")
    gateway: str = Field(default="stripe")
    last_four: Optional[str] = Field(None, max_length=4)
    bank_name: Optional[str] = Field(None, max_length=255)
    account_holder_name: Optional[str] = Field(None, max_length=255)
    routing_number_last_four: Optional[str] = Field(None, max_length=4)
    paypal_email: Optional[EmailStr] = None
    is_default: bool = False


class PaymentMethodUpdate(BaseModel):
    """Update payment method."""

    is_default: Optional[bool] = None
    is_verified: Optional[bool] = None


class PaymentMethodResponse(BaseResponse):
    """Payment method response."""

    id: int
    entity_type: str
    entity_id: int
    method_type: str
    gateway: str
    last_four: Optional[str]
    bank_name: Optional[str]
    is_default: bool
    is_verified: bool
    verified_at: Optional[datetime]
    payment_count: int

    class Config:
        from_attributes = True


# Payment Schedule Schemas

class PaymentScheduleCreate(BaseModel):
    """Create payment schedule."""

    payee_type: str = Field(..., pattern="^(candidate|supplier|referrer)$")
    payee_id: int
    frequency: str = Field(..., pattern="^(weekly|bi_weekly|semi_monthly|monthly)$")
    amount: Optional[float] = Field(None, gt=0)
    rate: Optional[float] = Field(None, gt=0)
    rate_type: str = Field(default="hourly")
    payment_method_id: Optional[int] = None
    start_date: date
    end_date: Optional[date] = None
    placement_id: Optional[int] = None
    auto_process: bool = False


class PaymentScheduleUpdate(BaseModel):
    """Update payment schedule."""

    frequency: Optional[str] = Field(None, pattern="^(weekly|bi_weekly|semi_monthly|monthly)$")
    amount: Optional[float] = Field(None, gt=0)
    rate: Optional[float] = Field(None, gt=0)
    end_date: Optional[date] = None
    is_active: Optional[bool] = None
    auto_process: Optional[bool] = None


class PaymentScheduleResponse(BaseResponse):
    """Payment schedule response."""

    id: int
    payee_type: str
    payee_id: int
    frequency: str
    amount: Optional[float]
    rate: Optional[float]
    rate_type: str
    next_payment_date: Optional[date]
    start_date: date
    end_date: Optional[date]
    is_active: bool
    auto_process: bool
    total_paid: float
    payments_count: int

    class Config:
        from_attributes = True


# Reconciliation Schemas

class PaymentReconciliationCreate(BaseModel):
    """Create payment reconciliation."""

    period_start: date
    period_end: date


class PaymentReconciliationUpdate(BaseModel):
    """Update payment reconciliation."""

    status: Optional[str] = Field(None, pattern="^(pending|reviewed|resolved)$")
    notes: Optional[str] = None


class PaymentReconciliationResponse(BaseResponse):
    """Payment reconciliation response."""

    id: int
    period_start: date
    period_end: date
    total_invoiced: float
    total_collected: float
    total_paid_out: float
    gross_margin: float
    discrepancies: Optional[List[Dict[str, Any]]]
    status: str
    reconciled_at: Optional[datetime]
    notes: Optional[str]

    class Config:
        from_attributes = True


# Batch Processing Schemas

class PaymentBatchProcess(BaseModel):
    """Process batch of payments."""

    payment_ids: List[int]


class PaymentBatchResult(BaseModel):
    """Batch processing result."""

    success: bool
    processed: int
    failed: int
    total_amount: float
    timestamp: datetime


# Report & Analytics Schemas

class PaymentReport(BaseModel):
    """Payment report."""

    period_start: date
    period_end: date
    total_amount: float
    payment_count: int
    by_type: Dict[str, Dict[str, Any]]
    by_method: Dict[str, Dict[str, Any]]
    by_status: Dict[str, Dict[str, Any]]
    timestamp: datetime


class PaymentAnalytics(BaseModel):
    """Payment analytics."""

    period: str
    total_processed: int
    total_failed: int
    failure_rate: float
    total_amount: float
    avg_processing_time_hours: float
    payment_count: int
    timestamp: datetime


class TaxDocumentation(BaseModel):
    """1099 tax documentation."""

    contractor_id: int
    contractor_name: str
    contractor_email: str
    tax_year: int
    total_amount: float
    payment_count: int
    payments: List[Dict[str, Any]]


# Referral Bonus Payout Schemas

class ReferralBonusPayoutCreate(BaseModel):
    """Process referral bonus payout."""

    bonus_id: int


class ReferralBonusPayoutResponse(BaseModel):
    """Referral bonus payout response."""

    success: bool
    bonus_id: int
    amount: float
    status: str
    timestamp: datetime


# Supplier Commission Schemas

class SupplierCommissionProcess(BaseModel):
    """Process supplier commission."""

    placement_id: int


class SupplierCommissionResponse(BaseModel):
    """Supplier commission response."""

    success: bool
    placement_id: int
    supplier_id: int
    commission: float
    timestamp: datetime


# Integration Status Schemas

class IntegrationStatus(BaseModel):
    """Payment integration status."""

    stripe_connected: bool
    paypal_connected: bool
    ach_enabled: bool
    last_check: datetime


class PaymentHealth(BaseModel):
    """Payment system health check."""

    status: str
    total_pending: int
    total_failed: int
    oldest_pending_date: Optional[date]
    success_rate: float
    average_processing_time: float
