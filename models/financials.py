"""Financial Models — P&L, Balance Sheet, Receivables, Payables, Associate Financials.

Supports multi-tenant financial reporting with aging schedules,
associate-level 360° views, and revenue/expense breakdowns.
"""
import enum
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import (
    Column, Integer, String, DateTime, Date, Numeric, Boolean,
    ForeignKey, Text, Enum as SAEnum, JSON,
)
from sqlalchemy.orm import relationship
from models.base import BaseModel


# ═══════════════════════════════════════════════════════════════
#  ENUMS
# ═══════════════════════════════════════════════════════════════

class TransactionType(str, enum.Enum):
    revenue = "revenue"
    expense = "expense"
    payroll = "payroll"
    reimbursement = "reimbursement"
    tax = "tax"
    insurance = "insurance"
    benefits = "benefits"
    markup = "markup"
    discount = "discount"
    adjustment = "adjustment"


class InvoiceStatus(str, enum.Enum):
    draft = "draft"
    sent = "sent"
    partial = "partial"
    paid = "paid"
    overdue = "overdue"
    disputed = "disputed"
    written_off = "written_off"
    cancelled = "cancelled"


class PaymentTerms(str, enum.Enum):
    net_15 = "net_15"
    net_30 = "net_30"
    net_45 = "net_45"
    net_60 = "net_60"
    net_90 = "net_90"
    due_on_receipt = "due_on_receipt"
    custom = "custom"


class AccountCategory(str, enum.Enum):
    asset = "asset"
    liability = "liability"
    equity = "equity"
    revenue = "revenue"
    cogs = "cogs"
    operating_expense = "operating_expense"
    other_income = "other_income"
    other_expense = "other_expense"


class PeriodType(str, enum.Enum):
    monthly = "monthly"
    quarterly = "quarterly"
    yearly = "yearly"
    custom = "custom"


# ═══════════════════════════════════════════════════════════════
#  CHART OF ACCOUNTS
# ═══════════════════════════════════════════════════════════════

class ChartOfAccounts(BaseModel):
    __tablename__ = "chart_of_accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    account_code = Column(String(20), nullable=False)
    account_name = Column(String(200), nullable=False)
    category = Column(SAEnum(AccountCategory), nullable=False)
    parent_account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    description = Column(Text, nullable=True)


# ═══════════════════════════════════════════════════════════════
#  FINANCIAL TRANSACTIONS (Journal Entries)
# ═══════════════════════════════════════════════════════════════

class FinancialTransaction(BaseModel):
    __tablename__ = "financial_transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    transaction_date = Column(Date, nullable=False)
    transaction_type = Column(SAEnum(TransactionType), nullable=False)
    account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=False)
    description = Column(Text, nullable=True)
    debit_amount = Column(Numeric(14, 2), default=0)
    credit_amount = Column(Numeric(14, 2), default=0)
    reference_type = Column(String(50), nullable=True)  # invoice, payroll, bill, etc.
    reference_id = Column(Integer, nullable=True)
    associate_id = Column(Integer, nullable=True)
    client_id = Column(Integer, nullable=True)
    supplier_id = Column(Integer, nullable=True)
    period_year = Column(Integer, nullable=False)
    period_month = Column(Integer, nullable=False)
    is_posted = Column(Boolean, default=True)
    posted_by = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)


# ═══════════════════════════════════════════════════════════════
#  INVOICES (Receivables)
# ═══════════════════════════════════════════════════════════════

class Invoice(BaseModel):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    invoice_number = Column(String(50), nullable=False, unique=True)
    client_id = Column(Integer, nullable=False)
    client_name = Column(String(200), nullable=False)
    issue_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    payment_terms = Column(SAEnum(PaymentTerms), default=PaymentTerms.net_30)
    custom_days = Column(Integer, nullable=True)
    subtotal = Column(Numeric(14, 2), nullable=False)
    tax_amount = Column(Numeric(14, 2), default=0)
    discount_amount = Column(Numeric(14, 2), default=0)
    total_amount = Column(Numeric(14, 2), nullable=False)
    paid_amount = Column(Numeric(14, 2), default=0)
    balance_due = Column(Numeric(14, 2), nullable=False)
    status = Column(SAEnum(InvoiceStatus), default=InvoiceStatus.draft)
    currency = Column(String(3), default="USD")
    notes = Column(Text, nullable=True)
    line_items = Column(JSON, nullable=True)  # [{associate_id, description, hours, rate, amount}]
    paid_date = Column(Date, nullable=True)


# ═══════════════════════════════════════════════════════════════
#  BILLS (Payables)
# ═══════════════════════════════════════════════════════════════

class Bill(BaseModel):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    bill_number = Column(String(50), nullable=False)
    supplier_id = Column(Integer, nullable=False)
    supplier_name = Column(String(200), nullable=False)
    issue_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    payment_terms = Column(SAEnum(PaymentTerms), default=PaymentTerms.net_30)
    custom_days = Column(Integer, nullable=True)
    subtotal = Column(Numeric(14, 2), nullable=False)
    tax_amount = Column(Numeric(14, 2), default=0)
    total_amount = Column(Numeric(14, 2), nullable=False)
    paid_amount = Column(Numeric(14, 2), default=0)
    balance_due = Column(Numeric(14, 2), nullable=False)
    status = Column(SAEnum(InvoiceStatus), default=InvoiceStatus.draft)
    currency = Column(String(3), default="USD")
    notes = Column(Text, nullable=True)
    line_items = Column(JSON, nullable=True)  # [{associate_id, description, hours, rate, amount}]
    paid_date = Column(Date, nullable=True)
    category = Column(String(100), nullable=True)  # staffing, tools, benefits, etc.


# ═══════════════════════════════════════════════════════════════
#  ASSOCIATE FINANCIALS (360° View)
# ═══════════════════════════════════════════════════════════════

class AssociateFinancialProfile(BaseModel):
    __tablename__ = "associate_financial_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    associate_id = Column(Integer, nullable=False)
    associate_name = Column(String(200), nullable=False)
    client_id = Column(Integer, nullable=True)
    client_name = Column(String(200), nullable=True)
    supplier_id = Column(Integer, nullable=True)
    supplier_name = Column(String(200), nullable=True)
    placement_id = Column(Integer, nullable=True)
    bill_rate = Column(Numeric(10, 2), nullable=True)
    pay_rate = Column(Numeric(10, 2), nullable=True)
    markup_percent = Column(Numeric(5, 2), nullable=True)
    margin_amount = Column(Numeric(10, 2), nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)


class AssociateTransaction(BaseModel):
    __tablename__ = "associate_transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    associate_id = Column(Integer, nullable=False)
    transaction_date = Column(Date, nullable=False)
    transaction_type = Column(SAEnum(TransactionType), nullable=False)
    category = Column(String(100), nullable=False)  # payroll, benefits, insurance, reimbursement, bill_revenue
    description = Column(Text, nullable=True)
    amount = Column(Numeric(14, 2), nullable=False)
    hours = Column(Numeric(8, 2), nullable=True)
    rate = Column(Numeric(10, 2), nullable=True)
    reference_type = Column(String(50), nullable=True)
    reference_id = Column(Integer, nullable=True)
    period_year = Column(Integer, nullable=False)
    period_month = Column(Integer, nullable=False)


# ═══════════════════════════════════════════════════════════════
#  P&L SNAPSHOT (Cached Period Summaries)
# ═══════════════════════════════════════════════════════════════

class PLSnapshot(BaseModel):
    __tablename__ = "pl_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    period_type = Column(SAEnum(PeriodType), nullable=False)
    period_year = Column(Integer, nullable=False)
    period_month = Column(Integer, nullable=True)
    period_quarter = Column(Integer, nullable=True)
    total_revenue = Column(Numeric(14, 2), default=0)
    total_cogs = Column(Numeric(14, 2), default=0)
    gross_profit = Column(Numeric(14, 2), default=0)
    gross_margin_percent = Column(Numeric(5, 2), default=0)
    operating_expenses = Column(Numeric(14, 2), default=0)
    operating_income = Column(Numeric(14, 2), default=0)
    other_income = Column(Numeric(14, 2), default=0)
    other_expenses = Column(Numeric(14, 2), default=0)
    net_income = Column(Numeric(14, 2), default=0)
    net_margin_percent = Column(Numeric(5, 2), default=0)
    breakdown = Column(JSON, nullable=True)  # Detailed line items
    generated_at = Column(DateTime, default=datetime.utcnow)


class BalanceSheetSnapshot(BaseModel):
    __tablename__ = "balance_sheet_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    snapshot_date = Column(Date, nullable=False)
    total_assets = Column(Numeric(14, 2), default=0)
    current_assets = Column(Numeric(14, 2), default=0)
    non_current_assets = Column(Numeric(14, 2), default=0)
    total_liabilities = Column(Numeric(14, 2), default=0)
    current_liabilities = Column(Numeric(14, 2), default=0)
    non_current_liabilities = Column(Numeric(14, 2), default=0)
    total_equity = Column(Numeric(14, 2), default=0)
    retained_earnings = Column(Numeric(14, 2), default=0)
    breakdown = Column(JSON, nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow)
