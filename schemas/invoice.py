"""Invoice schemas for request/response validation."""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class InvoiceLineItemCreate(BaseModel):
    """Create invoice line item request."""

    description: str
    quantity: float = Field(gt=0)
    unit_type: str = "hours"
    unit_price: float = Field(gt=0)
    is_taxable: bool = True
    line_type: str = "service"
    project_code: Optional[str] = None
    timesheet_id: Optional[int] = None
    placement_id: Optional[int] = None


class InvoiceLineItemUpdate(BaseModel):
    """Update invoice line item request."""

    description: Optional[str] = None
    quantity: Optional[float] = Field(default=None, gt=0)
    unit_type: Optional[str] = None
    unit_price: Optional[float] = Field(default=None, gt=0)
    is_taxable: Optional[bool] = None
    line_type: Optional[str] = None
    project_code: Optional[str] = None


class InvoiceLineItemResponse(BaseModel):
    """Invoice line item response."""

    id: int
    invoice_id: int
    description: str
    quantity: float
    unit_type: str
    unit_price: float
    amount: float
    is_taxable: bool
    line_type: str
    project_code: Optional[str] = None
    timesheet_id: Optional[int] = None
    placement_id: Optional[int] = None
    qb_item_id: Optional[str] = None
    qb_account_id: Optional[str] = None
    sort_order: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InvoicePaymentCreate(BaseModel):
    """Record payment request."""

    payment_date: date
    amount: float = Field(gt=0)
    payment_method: str
    reference_number: Optional[str] = None
    notes: Optional[str] = None
    recorded_by: Optional[int] = None


class InvoicePaymentResponse(BaseModel):
    """Invoice payment response."""

    id: int
    invoice_id: int
    payment_date: date
    amount: float
    payment_method: str
    reference_number: Optional[str] = None
    notes: Optional[str] = None
    qb_payment_id: Optional[str] = None
    recorded_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InvoiceCreate(BaseModel):
    """Create invoice request."""

    customer_id: int
    invoice_date: date
    due_date: date
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    payment_terms: str = "net_30"
    tax_rate: Optional[float] = None
    discount_percentage: Optional[float] = None
    notes: Optional[str] = None
    internal_notes: Optional[str] = None
    created_by: Optional[int] = None


class InvoiceUpdate(BaseModel):
    """Update invoice request."""

    due_date: Optional[date] = None
    tax_rate: Optional[float] = None
    discount_percentage: Optional[float] = None
    notes: Optional[str] = None
    internal_notes: Optional[str] = None
    status: Optional[str] = None


class InvoiceResponse(BaseModel):
    """Invoice response."""

    id: int
    invoice_number: str
    customer_id: int
    invoice_date: date
    due_date: date
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    subtotal: float
    tax_amount: float
    tax_rate: Optional[float] = None
    discount_amount: float
    discount_percentage: Optional[float] = None
    total_amount: float
    amount_paid: float
    amount_due: float
    currency: str
    status: str
    payment_terms: str
    pdf_path: Optional[str] = None
    qb_invoice_id: Optional[str] = None
    qb_sync_status: Optional[str] = None
    sent_at: Optional[datetime] = None
    sent_to: Optional[str] = None
    viewed_at: Optional[datetime] = None
    reminder_count: int
    notes: Optional[str] = None
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InvoiceDetailResponse(InvoiceResponse):
    """Invoice with line items and payments."""

    line_items: List[InvoiceLineItemResponse] = []
    payments: List[InvoicePaymentResponse] = []


class CreditMemoCreate(BaseModel):
    """Create credit memo request."""

    amount: float = Field(gt=0)
    reason: str


class CreditMemoResponse(BaseModel):
    """Credit memo response."""

    id: int
    invoice_id: int
    memo_number: str
    amount: float
    reason: str
    status: str
    applied_to_invoice_id: Optional[int] = None
    qb_credit_memo_id: Optional[str] = None
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InvoiceListFilter(BaseModel):
    """Filter for invoice list."""

    customer_id: Optional[int] = None
    status: Optional[str] = None
    invoice_date_start: Optional[date] = None
    invoice_date_end: Optional[date] = None
    due_date_start: Optional[date] = None
    due_date_end: Optional[date] = None
    skip: int = 0
    limit: int = 20


class InvoiceAgingReport(BaseModel):
    """Aging report entry."""

    bucket: str  # current, 30_days, 60_days, 90_days, 120_plus
    invoice_count: int
    total_amount: float
    customer_count: int
    details: List[Dict[str, Any]]


class InvoiceAgingResponse(BaseModel):
    """Accounts receivable aging report."""

    total_outstanding: float
    total_invoices: int
    current: InvoiceAgingReport
    days_30: InvoiceAgingReport
    days_60: InvoiceAgingReport
    days_90: InvoiceAgingReport
    days_120_plus: InvoiceAgingReport


class RevenueReport(BaseModel):
    """Revenue report."""

    period_start: date
    period_end: date
    total_invoiced: float
    total_collected: float
    total_outstanding: float
    by_customer: Dict[str, Dict[str, float]]
    by_month: Dict[str, Dict[str, float]]
    collection_rate: float


class SendInvoiceRequest(BaseModel):
    """Send invoice request."""

    delivery_method: str = "email"
    recipient_email: Optional[str] = None


class InvoiceAnalyticsResponse(BaseModel):
    """Invoicing analytics."""

    total_invoiced: float
    total_collected: float
    total_outstanding: float
    avg_days_to_pay: float
    collection_rate: float
    overdue_percentage: float
    total_invoices: int
    paid_invoices: int
    overdue_invoices: int
    revenue_by_customer: Dict[str, float]
    margin_by_placement: Dict[str, float]


class QuickBooksConnectRequest(BaseModel):
    """QuickBooks connection request."""

    auth_code: str
    realm_id: str


class QuickBooksConnectResponse(BaseModel):
    """QuickBooks connection response."""

    is_connected: bool
    company_name: Optional[str] = None
    realm_id: str
    connected_at: datetime


class QuickBooksSyncRequest(BaseModel):
    """QuickBooks sync request."""

    entity_type: str
    entity_id: Optional[int] = None
    force_sync: bool = False


class QuickBooksSyncResponse(BaseModel):
    """QuickBooks sync response."""

    sync_id: int
    sync_type: str
    status: str
    records_processed: int
    records_failed: int
    error_details: Optional[Dict[str, Any]] = None
    started_at: datetime
    completed_at: Optional[datetime] = None


class QuickBooksStatusResponse(BaseModel):
    """QuickBooks connection status."""

    is_connected: bool
    realm_id: Optional[str] = None
    company_name: Optional[str] = None
    last_sync_at: Optional[datetime] = None
    token_expires_at: Optional[datetime] = None
    sync_health: str


class QuickBooksAccountMapping(BaseModel):
    """Account mapping for QuickBooks."""

    income_account: Optional[str] = None
    expense_account: Optional[str] = None
    ar_account: Optional[str] = None
    ap_account: Optional[str] = None
    custom_mapping: Optional[Dict[str, str]] = None


class GenerateInvoiceFromTimesheetRequest(BaseModel):
    """Generate invoice from timesheet request."""

    timesheet_id: int
    customer_id: int
    apply_markup: bool = True
    markup_percentage: Optional[float] = None


class BulkGenerateInvoicesRequest(BaseModel):
    """Bulk generate invoices request."""

    period_start: date
    period_end: date
    customer_id: Optional[int] = None
    apply_markup: bool = True
    markup_percentage: Optional[float] = None
