"""Financial Reports API — P&L, Balance Sheet, Revenue/Expense breakdowns,
AR/AP aging, Associate 360° financials, and revenue analytics.

All endpoints return mock data for demo purposes.
"""
from datetime import datetime, date, timedelta
from fastapi import APIRouter, Query
from typing import Optional

router = APIRouter(prefix="/financial-reports")


# ══════════════════════════════════════════════════════════════
#  MOCK DATA — P&L
# ══════════════════════════════════════════════════════════════

_mock_pl_monthly = [
    {"period": "2026-01", "revenue": 485000, "cogs": 312000, "gross_profit": 173000, "gross_margin": 35.7, "operating_expenses": 98000, "operating_income": 75000, "other_income": 3200, "other_expenses": 1800, "net_income": 76400, "net_margin": 15.8},
    {"period": "2026-02", "revenue": 512000, "cogs": 325000, "gross_profit": 187000, "gross_margin": 36.5, "operating_expenses": 102000, "operating_income": 85000, "other_income": 2800, "other_expenses": 2100, "net_income": 85700, "net_margin": 16.7},
    {"period": "2026-03", "revenue": 548000, "cogs": 341000, "gross_profit": 207000, "gross_margin": 37.8, "operating_expenses": 105000, "operating_income": 102000, "other_income": 3500, "other_expenses": 1500, "net_income": 104000, "net_margin": 19.0},
]

_mock_pl_breakdown = {
    "revenue_lines": [
        {"account": "Staffing Revenue — IT", "amount": 285000, "percent": 52.0},
        {"account": "Staffing Revenue — Engineering", "amount": 142000, "percent": 25.9},
        {"account": "Staffing Revenue — Healthcare", "amount": 78000, "percent": 14.2},
        {"account": "Staffing Revenue — Finance", "amount": 33000, "percent": 6.0},
        {"account": "Placement Fees", "amount": 10000, "percent": 1.8},
    ],
    "cogs_lines": [
        {"account": "Associate Payroll", "amount": 268000, "percent": 78.6},
        {"account": "Payroll Taxes & Benefits", "amount": 42000, "percent": 12.3},
        {"account": "Workers Compensation", "amount": 18000, "percent": 5.3},
        {"account": "Background Checks", "amount": 8000, "percent": 2.3},
        {"account": "Drug Testing", "amount": 5000, "percent": 1.5},
    ],
    "opex_lines": [
        {"account": "Salaries — Internal Staff", "amount": 52000, "percent": 49.5},
        {"account": "Office & Facilities", "amount": 15000, "percent": 14.3},
        {"account": "Technology & Software", "amount": 12000, "percent": 11.4},
        {"account": "Marketing & Sales", "amount": 9000, "percent": 8.6},
        {"account": "Insurance — General", "amount": 8000, "percent": 7.6},
        {"account": "Professional Services", "amount": 5000, "percent": 4.8},
        {"account": "Travel & Entertainment", "amount": 4000, "percent": 3.8},
    ],
}


# ══════════════════════════════════════════════════════════════
#  MOCK DATA — Balance Sheet
# ══════════════════════════════════════════════════════════════

_mock_balance_sheet = {
    "snapshot_date": "2026-03-13",
    "assets": {
        "current_assets": {
            "cash_and_equivalents": 342000,
            "accounts_receivable": 628000,
            "unbilled_revenue": 85000,
            "prepaid_expenses": 24000,
            "total": 1079000,
        },
        "non_current_assets": {
            "property_equipment": 45000,
            "intangible_assets": 12000,
            "deposits": 8000,
            "total": 65000,
        },
        "total_assets": 1144000,
    },
    "liabilities": {
        "current_liabilities": {
            "accounts_payable": 412000,
            "accrued_payroll": 168000,
            "payroll_taxes_payable": 32000,
            "accrued_expenses": 18000,
            "current_portion_debt": 25000,
            "total": 655000,
        },
        "non_current_liabilities": {
            "long_term_debt": 75000,
            "deferred_revenue": 15000,
            "total": 90000,
        },
        "total_liabilities": 745000,
    },
    "equity": {
        "common_stock": 100000,
        "retained_earnings": 299000,
        "total_equity": 399000,
    },
    "total_liabilities_and_equity": 1144000,
}


# ══════════════════════════════════════════════════════════════
#  MOCK DATA — Revenue by Customer
# ══════════════════════════════════════════════════════════════

_mock_revenue_by_customer = [
    {"client_id": 1, "client_name": "TechCorp Inc", "industry": "Technology", "ytd_revenue": 425000, "mtd_revenue": 148000, "last_month": 142000, "growth_percent": 4.2, "active_associates": 12, "avg_bill_rate": 125.00, "total_hours": 3400, "invoices_outstanding": 186000, "payment_terms": "net_30"},
    {"client_id": 2, "client_name": "MedFirst Health", "industry": "Healthcare", "ytd_revenue": 312000, "mtd_revenue": 108000, "last_month": 102000, "growth_percent": 5.9, "active_associates": 8, "avg_bill_rate": 95.00, "total_hours": 2560, "invoices_outstanding": 95000, "payment_terms": "net_45"},
    {"client_id": 3, "client_name": "FinanceGroup LLC", "industry": "Financial Services", "ytd_revenue": 268000, "mtd_revenue": 92000, "last_month": 88000, "growth_percent": 4.5, "active_associates": 6, "avg_bill_rate": 145.00, "total_hours": 1920, "invoices_outstanding": 132000, "payment_terms": "net_30"},
    {"client_id": 4, "client_name": "BuildRight Construction", "industry": "Construction", "ytd_revenue": 198000, "mtd_revenue": 72000, "last_month": 65000, "growth_percent": 10.8, "active_associates": 9, "avg_bill_rate": 68.00, "total_hours": 2880, "invoices_outstanding": 72000, "payment_terms": "net_60"},
    {"client_id": 5, "client_name": "RetailMax Corp", "industry": "Retail", "ytd_revenue": 156000, "mtd_revenue": 54000, "last_month": 52000, "growth_percent": 3.8, "active_associates": 5, "avg_bill_rate": 82.00, "total_hours": 1600, "invoices_outstanding": 54000, "payment_terms": "net_30"},
    {"client_id": 6, "client_name": "AutoDrive Systems", "industry": "Automotive", "ytd_revenue": 124000, "mtd_revenue": 42000, "last_month": 40000, "growth_percent": 5.0, "active_associates": 3, "avg_bill_rate": 135.00, "total_hours": 960, "invoices_outstanding": 42000, "payment_terms": "net_45"},
    {"client_id": 7, "client_name": "EduTech Academy", "industry": "Education", "ytd_revenue": 62000, "mtd_revenue": 32000, "last_month": 23000, "growth_percent": 39.1, "active_associates": 2, "avg_bill_rate": 78.00, "total_hours": 640, "invoices_outstanding": 32000, "payment_terms": "net_30"},
]


# ══════════════════════════════════════════════════════════════
#  MOCK DATA — Expenses by Supplier
# ══════════════════════════════════════════════════════════════

_mock_expenses_by_supplier = [
    {"supplier_id": 1, "supplier_name": "StaffPro Solutions", "category": "Staffing", "ytd_expenses": 385000, "mtd_expenses": 138000, "last_month": 132000, "active_associates": 18, "avg_pay_rate": 72.00, "bills_outstanding": 142000, "payment_terms": "net_30", "on_time_payment_rate": 96.5},
    {"supplier_id": 2, "supplier_name": "TalentBridge Agency", "category": "Staffing", "ytd_expenses": 248000, "mtd_expenses": 88000, "last_month": 82000, "active_associates": 10, "avg_pay_rate": 65.00, "bills_outstanding": 88000, "payment_terms": "net_30", "on_time_payment_rate": 98.2},
    {"supplier_id": 3, "supplier_name": "CodeForce Inc", "category": "Staffing — IT", "ytd_expenses": 192000, "mtd_expenses": 68000, "last_month": 64000, "active_associates": 6, "avg_pay_rate": 95.00, "bills_outstanding": 68000, "payment_terms": "net_45", "on_time_payment_rate": 94.8},
    {"supplier_id": 4, "supplier_name": "HireRight Inc", "category": "Background Checks", "ytd_expenses": 24000, "mtd_expenses": 8000, "last_month": 7500, "active_associates": 0, "avg_pay_rate": 0, "bills_outstanding": 8000, "payment_terms": "net_30", "on_time_payment_rate": 100.0},
    {"supplier_id": 5, "supplier_name": "ADP Payroll Services", "category": "Payroll Processing", "ytd_expenses": 18000, "mtd_expenses": 6000, "last_month": 6000, "active_associates": 0, "avg_pay_rate": 0, "bills_outstanding": 6000, "payment_terms": "net_15", "on_time_payment_rate": 100.0},
    {"supplier_id": 6, "supplier_name": "SecureInsure Corp", "category": "Insurance", "ytd_expenses": 36000, "mtd_expenses": 12000, "last_month": 12000, "active_associates": 0, "avg_pay_rate": 0, "bills_outstanding": 0, "payment_terms": "net_60", "on_time_payment_rate": 100.0},
]


# ══════════════════════════════════════════════════════════════
#  MOCK DATA — Receivables Aging (AR)
# ══════════════════════════════════════════════════════════════

_mock_receivables = [
    {"invoice_id": "INV-2026-0042", "client_name": "TechCorp Inc", "issue_date": "2026-03-01", "due_date": "2026-03-31", "amount": 68000, "paid": 0, "balance": 68000, "status": "sent", "aging_bucket": "current", "days_outstanding": 12},
    {"invoice_id": "INV-2026-0041", "client_name": "TechCorp Inc", "issue_date": "2026-02-15", "due_date": "2026-03-17", "amount": 72000, "paid": 0, "balance": 72000, "status": "sent", "aging_bucket": "current", "days_outstanding": 26},
    {"invoice_id": "INV-2026-0039", "client_name": "MedFirst Health", "issue_date": "2026-02-01", "due_date": "2026-03-17", "amount": 54000, "paid": 0, "balance": 54000, "status": "sent", "aging_bucket": "current", "days_outstanding": 40},
    {"invoice_id": "INV-2026-0038", "client_name": "FinanceGroup LLC", "issue_date": "2026-01-25", "due_date": "2026-02-24", "amount": 48000, "paid": 0, "balance": 48000, "status": "overdue", "aging_bucket": "31_45", "days_outstanding": 47},
    {"invoice_id": "INV-2026-0035", "client_name": "MedFirst Health", "issue_date": "2026-01-15", "due_date": "2026-03-01", "amount": 41000, "paid": 0, "balance": 41000, "status": "overdue", "aging_bucket": "31_45", "days_outstanding": 57},
    {"invoice_id": "INV-2026-0032", "client_name": "BuildRight Construction", "issue_date": "2026-01-05", "due_date": "2026-03-06", "amount": 72000, "paid": 0, "balance": 72000, "status": "sent", "aging_bucket": "current", "days_outstanding": 67},
    {"invoice_id": "INV-2025-0128", "client_name": "FinanceGroup LLC", "issue_date": "2025-12-20", "due_date": "2026-01-19", "amount": 52000, "paid": 0, "balance": 52000, "status": "overdue", "aging_bucket": "46_60", "days_outstanding": 83},
    {"invoice_id": "INV-2025-0122", "client_name": "RetailMax Corp", "issue_date": "2025-12-10", "due_date": "2026-01-09", "amount": 38000, "paid": 0, "balance": 38000, "status": "overdue", "aging_bucket": "61_90", "days_outstanding": 93},
    {"invoice_id": "INV-2025-0115", "client_name": "AutoDrive Systems", "issue_date": "2025-11-15", "due_date": "2025-12-30", "amount": 42000, "paid": 0, "balance": 42000, "status": "overdue", "aging_bucket": "over_90", "days_outstanding": 118},
    {"invoice_id": "INV-2025-0108", "client_name": "BuildRight Construction", "issue_date": "2025-11-01", "due_date": "2025-12-31", "amount": 35000, "paid": 12000, "balance": 23000, "status": "partial", "aging_bucket": "over_90", "days_outstanding": 132},
]

_mock_ar_aging_summary = {
    "current": {"count": 4, "total": 266000, "percent": 47.2},
    "31_45": {"count": 2, "total": 89000, "percent": 15.8},
    "46_60": {"count": 1, "total": 52000, "percent": 9.2},
    "61_90": {"count": 1, "total": 38000, "percent": 6.7},
    "over_90": {"count": 2, "total": 65000, "percent": 11.5},
    "total_outstanding": 628000,
    "total_overdue": 244000,
    "dso": 42,  # Days Sales Outstanding
}


# ══════════════════════════════════════════════════════════════
#  MOCK DATA — Payables Aging (AP)
# ══════════════════════════════════════════════════════════════

_mock_payables = [
    {"bill_id": "BILL-2026-0089", "supplier_name": "StaffPro Solutions", "issue_date": "2026-03-01", "due_date": "2026-03-31", "amount": 72000, "paid": 0, "balance": 72000, "status": "sent", "aging_bucket": "current", "days_outstanding": 12, "category": "Staffing"},
    {"bill_id": "BILL-2026-0088", "supplier_name": "TalentBridge Agency", "issue_date": "2026-03-01", "due_date": "2026-03-31", "amount": 44000, "paid": 0, "balance": 44000, "status": "sent", "aging_bucket": "current", "days_outstanding": 12, "category": "Staffing"},
    {"bill_id": "BILL-2026-0085", "supplier_name": "StaffPro Solutions", "issue_date": "2026-02-15", "due_date": "2026-03-17", "amount": 66000, "paid": 0, "balance": 66000, "status": "sent", "aging_bucket": "current", "days_outstanding": 26, "category": "Staffing"},
    {"bill_id": "BILL-2026-0082", "supplier_name": "CodeForce Inc", "issue_date": "2026-02-01", "due_date": "2026-03-17", "amount": 34000, "paid": 0, "balance": 34000, "status": "sent", "aging_bucket": "current", "days_outstanding": 40, "category": "Staffing — IT"},
    {"bill_id": "BILL-2026-0078", "supplier_name": "StaffPro Solutions", "issue_date": "2026-01-15", "due_date": "2026-02-14", "amount": 68000, "paid": 0, "balance": 68000, "status": "overdue", "aging_bucket": "31_45", "days_outstanding": 57, "category": "Staffing"},
    {"bill_id": "BILL-2026-0075", "supplier_name": "CodeForce Inc", "issue_date": "2026-01-01", "due_date": "2026-02-15", "amount": 34000, "paid": 0, "balance": 34000, "status": "overdue", "aging_bucket": "31_45", "days_outstanding": 71, "category": "Staffing — IT"},
    {"bill_id": "BILL-2025-0215", "supplier_name": "HireRight Inc", "issue_date": "2025-12-15", "due_date": "2026-01-14", "amount": 8000, "paid": 0, "balance": 8000, "status": "overdue", "aging_bucket": "46_60", "days_outstanding": 88, "category": "Background Checks"},
    {"bill_id": "BILL-2025-0210", "supplier_name": "SecureInsure Corp", "issue_date": "2025-12-01", "due_date": "2026-01-30", "amount": 12000, "paid": 0, "balance": 12000, "status": "overdue", "aging_bucket": "46_60", "days_outstanding": 102, "category": "Insurance"},
]

_mock_ap_aging_summary = {
    "current": {"count": 4, "total": 216000, "percent": 52.4},
    "31_45": {"count": 2, "total": 102000, "percent": 24.8},
    "46_60": {"count": 2, "total": 20000, "percent": 4.9},
    "61_90": {"count": 0, "total": 0, "percent": 0},
    "over_90": {"count": 0, "total": 0, "percent": 0},
    "total_outstanding": 412000,
    "total_overdue": 122000,
    "dpo": 38,  # Days Payable Outstanding
}


# ══════════════════════════════════════════════════════════════
#  MOCK DATA — Associate 360° Financials
# ══════════════════════════════════════════════════════════════

_mock_associates = [
    {
        "associate_id": 1, "name": "James Rodriguez", "title": "Sr. Software Engineer",
        "client_name": "TechCorp Inc", "supplier_name": "StaffPro Solutions",
        "bill_rate": 135.00, "pay_rate": 85.00, "markup_percent": 58.8, "margin_per_hour": 50.00,
        "status": "active", "start_date": "2025-06-15", "hours_ytd": 440, "hours_mtd": 168,
        "revenue": {"ytd": 59400, "mtd": 22680, "last_month": 21600},
        "costs": {
            "payroll": {"ytd": 37400, "mtd": 14280},
            "benefits": {"ytd": 4800, "mtd": 1600},
            "insurance": {"ytd": 2400, "mtd": 800},
            "payroll_taxes": {"ytd": 5610, "mtd": 2142},
            "bgc_drug_test": {"ytd": 350, "mtd": 0},
            "reimbursements": {"ytd": 1200, "mtd": 400},
            "total": {"ytd": 51760, "mtd": 19222},
        },
        "profit": {"ytd": 7640, "mtd": 3458},
        "effective_margin": 12.9,
        "monthly_trend": [
            {"month": "2026-01", "revenue": 21600, "costs": 16250, "profit": 5350},
            {"month": "2026-02", "revenue": 21600, "costs": 16288, "profit": 5312},
            {"month": "2026-03", "revenue": 22680, "costs": 19222, "profit": 3458},
        ],
    },
    {
        "associate_id": 2, "name": "Priya Sharma", "title": "Data Analyst",
        "client_name": "FinanceGroup LLC", "supplier_name": "TalentBridge Agency",
        "bill_rate": 105.00, "pay_rate": 62.00, "markup_percent": 69.4, "margin_per_hour": 43.00,
        "status": "active", "start_date": "2025-09-01", "hours_ytd": 400, "hours_mtd": 160,
        "revenue": {"ytd": 42000, "mtd": 16800, "last_month": 16800},
        "costs": {
            "payroll": {"ytd": 24800, "mtd": 9920},
            "benefits": {"ytd": 3600, "mtd": 1200},
            "insurance": {"ytd": 1800, "mtd": 600},
            "payroll_taxes": {"ytd": 3720, "mtd": 1488},
            "bgc_drug_test": {"ytd": 250, "mtd": 0},
            "reimbursements": {"ytd": 600, "mtd": 200},
            "total": {"ytd": 34770, "mtd": 13408},
        },
        "profit": {"ytd": 7230, "mtd": 3392},
        "effective_margin": 17.2,
        "monthly_trend": [
            {"month": "2026-01", "revenue": 16800, "costs": 10654, "profit": 6146},
            {"month": "2026-02", "revenue": 16800, "costs": 10708, "profit": 6092},
            {"month": "2026-03", "revenue": 16800, "costs": 13408, "profit": 3392},
        ],
    },
    {
        "associate_id": 3, "name": "Marcus Johnson", "title": "Registered Nurse",
        "client_name": "MedFirst Health", "supplier_name": "StaffPro Solutions",
        "bill_rate": 92.00, "pay_rate": 58.00, "markup_percent": 58.6, "margin_per_hour": 34.00,
        "status": "active", "start_date": "2025-04-01", "hours_ytd": 480, "hours_mtd": 176,
        "revenue": {"ytd": 44160, "mtd": 16192, "last_month": 14720},
        "costs": {
            "payroll": {"ytd": 27840, "mtd": 10208},
            "benefits": {"ytd": 4200, "mtd": 1400},
            "insurance": {"ytd": 3600, "mtd": 1200},
            "payroll_taxes": {"ytd": 4176, "mtd": 1531},
            "bgc_drug_test": {"ytd": 450, "mtd": 0},
            "reimbursements": {"ytd": 800, "mtd": 150},
            "total": {"ytd": 41066, "mtd": 14489},
        },
        "profit": {"ytd": 3094, "mtd": 1703},
        "effective_margin": 7.0,
        "monthly_trend": [
            {"month": "2026-01", "revenue": 14720, "costs": 12928, "profit": 1792},
            {"month": "2026-02", "revenue": 14720, "costs": 13649, "profit": 1071},
            {"month": "2026-03", "revenue": 16192, "costs": 14489, "profit": 1703},
        ],
    },
    {
        "associate_id": 4, "name": "Emily Chen", "title": "DevOps Engineer",
        "client_name": "TechCorp Inc", "supplier_name": "CodeForce Inc",
        "bill_rate": 155.00, "pay_rate": 105.00, "markup_percent": 47.6, "margin_per_hour": 50.00,
        "status": "active", "start_date": "2025-11-01", "hours_ytd": 400, "hours_mtd": 168,
        "revenue": {"ytd": 62000, "mtd": 26040, "last_month": 24800},
        "costs": {
            "payroll": {"ytd": 42000, "mtd": 17640},
            "benefits": {"ytd": 4800, "mtd": 1600},
            "insurance": {"ytd": 2400, "mtd": 800},
            "payroll_taxes": {"ytd": 6300, "mtd": 2646},
            "bgc_drug_test": {"ytd": 350, "mtd": 0},
            "reimbursements": {"ytd": 1500, "mtd": 500},
            "total": {"ytd": 57350, "mtd": 23186},
        },
        "profit": {"ytd": 4650, "mtd": 2854},
        "effective_margin": 7.5,
        "monthly_trend": [
            {"month": "2026-01", "revenue": 24800, "costs": 17082, "profit": 7718},
            {"month": "2026-02", "revenue": 24800, "costs": 17082, "profit": 7718},
            {"month": "2026-03", "revenue": 26040, "costs": 23186, "profit": 2854},
        ],
    },
    {
        "associate_id": 5, "name": "David Wilson", "title": "Project Manager",
        "client_name": "BuildRight Construction", "supplier_name": "TalentBridge Agency",
        "bill_rate": 88.00, "pay_rate": 55.00, "markup_percent": 60.0, "margin_per_hour": 33.00,
        "status": "active", "start_date": "2025-08-15", "hours_ytd": 420, "hours_mtd": 160,
        "revenue": {"ytd": 36960, "mtd": 14080, "last_month": 14080},
        "costs": {
            "payroll": {"ytd": 23100, "mtd": 8800},
            "benefits": {"ytd": 3600, "mtd": 1200},
            "insurance": {"ytd": 1800, "mtd": 600},
            "payroll_taxes": {"ytd": 3465, "mtd": 1320},
            "bgc_drug_test": {"ytd": 250, "mtd": 0},
            "reimbursements": {"ytd": 2200, "mtd": 800},
            "total": {"ytd": 34415, "mtd": 12720},
        },
        "profit": {"ytd": 2545, "mtd": 1360},
        "effective_margin": 6.9,
        "monthly_trend": [
            {"month": "2026-01", "revenue": 14080, "costs": 10848, "profit": 3232},
            {"month": "2026-02", "revenue": 14080, "costs": 10847, "profit": 3233},
            {"month": "2026-03", "revenue": 14080, "costs": 12720, "profit": 1360},
        ],
    },
    {
        "associate_id": 6, "name": "Sarah Thompson", "title": "UX Designer",
        "client_name": "RetailMax Corp", "supplier_name": "StaffPro Solutions",
        "bill_rate": 110.00, "pay_rate": 68.00, "markup_percent": 61.8, "margin_per_hour": 42.00,
        "status": "active", "start_date": "2026-01-06", "hours_ytd": 360, "hours_mtd": 152,
        "revenue": {"ytd": 39600, "mtd": 16720, "last_month": 17600},
        "costs": {
            "payroll": {"ytd": 24480, "mtd": 10336},
            "benefits": {"ytd": 3600, "mtd": 1200},
            "insurance": {"ytd": 1800, "mtd": 600},
            "payroll_taxes": {"ytd": 3672, "mtd": 1550},
            "bgc_drug_test": {"ytd": 350, "mtd": 0},
            "reimbursements": {"ytd": 450, "mtd": 150},
            "total": {"ytd": 34352, "mtd": 13836},
        },
        "profit": {"ytd": 5248, "mtd": 2884},
        "effective_margin": 13.3,
        "monthly_trend": [
            {"month": "2026-01", "revenue": 17600, "costs": 10258, "profit": 7342},
            {"month": "2026-02", "revenue": 17600, "costs": 10258, "profit": 7342},
            {"month": "2026-03", "revenue": 16720, "costs": 13836, "profit": 2884},
        ],
    },
]


# ══════════════════════════════════════════════════════════════
#  MOCK DATA — Revenue Analytics
# ══════════════════════════════════════════════════════════════

_mock_revenue_analytics = {
    "summary": {
        "ytd_revenue": 1545000,
        "ytd_expenses": 978000,
        "ytd_gross_profit": 567000,
        "ytd_net_income": 266100,
        "avg_monthly_revenue": 515000,
        "revenue_growth_yoy": 18.4,
        "gross_margin": 36.7,
        "net_margin": 17.2,
        "revenue_per_associate": 35340,
        "avg_bill_rate": 108.50,
        "avg_pay_rate": 68.20,
        "avg_markup": 59.1,
    },
    "monthly_revenue_trend": [
        {"month": "2025-04", "revenue": 320000, "expenses": 218000, "profit": 102000},
        {"month": "2025-05", "revenue": 345000, "expenses": 232000, "profit": 113000},
        {"month": "2025-06", "revenue": 368000, "expenses": 245000, "profit": 123000},
        {"month": "2025-07", "revenue": 382000, "expenses": 252000, "profit": 130000},
        {"month": "2025-08", "revenue": 395000, "expenses": 260000, "profit": 135000},
        {"month": "2025-09", "revenue": 412000, "expenses": 271000, "profit": 141000},
        {"month": "2025-10", "revenue": 428000, "expenses": 280000, "profit": 148000},
        {"month": "2025-11", "revenue": 445000, "expenses": 290000, "profit": 155000},
        {"month": "2025-12", "revenue": 462000, "expenses": 298000, "profit": 164000},
        {"month": "2026-01", "revenue": 485000, "expenses": 312000, "profit": 173000},
        {"month": "2026-02", "revenue": 512000, "expenses": 325000, "profit": 187000},
        {"month": "2026-03", "revenue": 548000, "expenses": 341000, "profit": 207000},
    ],
    "revenue_by_industry": [
        {"industry": "Technology", "revenue": 549000, "percent": 35.5},
        {"industry": "Healthcare", "revenue": 312000, "percent": 20.2},
        {"industry": "Financial Services", "revenue": 268000, "percent": 17.3},
        {"industry": "Construction", "revenue": 198000, "percent": 12.8},
        {"industry": "Retail", "revenue": 156000, "percent": 10.1},
        {"industry": "Automotive", "revenue": 62000, "percent": 4.0},
    ],
    "top_performing_associates": [
        {"name": "Emily Chen", "revenue": 62000, "margin": 7.5, "hours": 400},
        {"name": "James Rodriguez", "revenue": 59400, "margin": 12.9, "hours": 440},
        {"name": "Marcus Johnson", "revenue": 44160, "margin": 7.0, "hours": 480},
        {"name": "Priya Sharma", "revenue": 42000, "margin": 17.2, "hours": 400},
        {"name": "Sarah Thompson", "revenue": 39600, "margin": 13.3, "hours": 360},
    ],
}


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — P&L
# ══════════════════════════════════════════════════════════════

@router.get("/pl")
async def get_profit_and_loss(
    period_type: str = Query("monthly", description="monthly|quarterly|yearly"),
    year: int = Query(2026),
):
    """Get Profit & Loss statement."""
    return {
        "period_type": period_type,
        "year": year,
        "periods": _mock_pl_monthly,
        "ytd_summary": {
            "revenue": 1545000, "cogs": 978000, "gross_profit": 567000,
            "gross_margin": 36.7, "operating_expenses": 305000,
            "operating_income": 262000, "net_income": 266100, "net_margin": 17.2,
        },
        "breakdown": _mock_pl_breakdown,
    }


@router.get("/pl/trend")
async def get_pl_trend(months: int = Query(12)):
    """Get P&L trend over time."""
    return {"months": months, "trend": _mock_revenue_analytics["monthly_revenue_trend"][-months:]}


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — Balance Sheet
# ══════════════════════════════════════════════════════════════

@router.get("/balance-sheet")
async def get_balance_sheet(as_of_date: Optional[str] = None):
    """Get Balance Sheet as of a specific date."""
    return _mock_balance_sheet


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — Revenue by Customer
# ══════════════════════════════════════════════════════════════

@router.get("/revenue-by-customer")
async def get_revenue_by_customer(
    sort_by: str = Query("ytd_revenue", description="Sort field"),
    sort_dir: str = Query("desc"),
    industry: Optional[str] = None,
):
    """Get revenue breakdown by customer."""
    results = _mock_revenue_by_customer
    if industry:
        results = [r for r in results if r["industry"].lower() == industry.lower()]
    reverse = sort_dir == "desc"
    results = sorted(results, key=lambda x: x.get(sort_by, 0), reverse=reverse)
    total = sum(r["ytd_revenue"] for r in results)
    return {"items": results, "total": len(results), "total_ytd_revenue": total}


@router.get("/revenue-by-customer/{client_id}")
async def get_customer_revenue_detail(client_id: int):
    """Get detailed revenue for a specific customer."""
    item = next((r for r in _mock_revenue_by_customer if r["client_id"] == client_id), None)
    return item or {"error": "Not found"}


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — Expenses by Supplier
# ══════════════════════════════════════════════════════════════

@router.get("/expenses-by-supplier")
async def get_expenses_by_supplier(
    sort_by: str = Query("ytd_expenses", description="Sort field"),
    sort_dir: str = Query("desc"),
    category: Optional[str] = None,
):
    """Get expense breakdown by supplier."""
    results = _mock_expenses_by_supplier
    if category:
        results = [r for r in results if category.lower() in r["category"].lower()]
    reverse = sort_dir == "desc"
    results = sorted(results, key=lambda x: x.get(sort_by, 0), reverse=reverse)
    total = sum(r["ytd_expenses"] for r in results)
    return {"items": results, "total": len(results), "total_ytd_expenses": total}


@router.get("/expenses-by-supplier/{supplier_id}")
async def get_supplier_expense_detail(supplier_id: int):
    """Get detailed expenses for a specific supplier."""
    item = next((r for r in _mock_expenses_by_supplier if r["supplier_id"] == supplier_id), None)
    return item or {"error": "Not found"}


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — Receivables (AR Aging)
# ══════════════════════════════════════════════════════════════

@router.get("/receivables")
async def get_receivables(
    aging_bucket: Optional[str] = None,
    client_name: Optional[str] = None,
    status: Optional[str] = None,
):
    """Get accounts receivable with aging."""
    results = _mock_receivables
    if aging_bucket:
        results = [r for r in results if r["aging_bucket"] == aging_bucket]
    if client_name:
        results = [r for r in results if client_name.lower() in r["client_name"].lower()]
    if status:
        results = [r for r in results if r["status"] == status]
    return {"items": results, "total": len(results), "aging_summary": _mock_ar_aging_summary}


@router.get("/receivables/aging-summary")
async def get_ar_aging_summary():
    """Get AR aging summary buckets."""
    return _mock_ar_aging_summary


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — Payables (AP Aging)
# ══════════════════════════════════════════════════════════════

@router.get("/payables")
async def get_payables(
    aging_bucket: Optional[str] = None,
    supplier_name: Optional[str] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
):
    """Get accounts payable with aging."""
    results = _mock_payables
    if aging_bucket:
        results = [r for r in results if r["aging_bucket"] == aging_bucket]
    if supplier_name:
        results = [r for r in results if supplier_name.lower() in r["supplier_name"].lower()]
    if status:
        results = [r for r in results if r["status"] == status]
    if category:
        results = [r for r in results if category.lower() in r["category"].lower()]
    return {"items": results, "total": len(results), "aging_summary": _mock_ap_aging_summary}


@router.get("/payables/aging-summary")
async def get_ap_aging_summary():
    """Get AP aging summary buckets."""
    return _mock_ap_aging_summary


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — Associate 360° Financials
# ══════════════════════════════════════════════════════════════

@router.get("/associate-financials")
async def get_associate_financials(
    sort_by: str = Query("revenue.ytd", description="Sort field"),
    sort_dir: str = Query("desc"),
    client_name: Optional[str] = None,
    supplier_name: Optional[str] = None,
):
    """Get financial overview for all associates."""
    results = _mock_associates
    if client_name:
        results = [a for a in results if client_name.lower() in a["client_name"].lower()]
    if supplier_name:
        results = [a for a in results if supplier_name.lower() in a["supplier_name"].lower()]

    # Sort by nested field
    parts = sort_by.split(".")
    def sort_key(a):
        val = a
        for p in parts:
            if isinstance(val, dict):
                val = val.get(p, 0)
            else:
                val = 0
        return val if isinstance(val, (int, float)) else 0
    results = sorted(results, key=sort_key, reverse=(sort_dir == "desc"))

    totals = {
        "total_revenue_ytd": sum(a["revenue"]["ytd"] for a in results),
        "total_costs_ytd": sum(a["costs"]["total"]["ytd"] for a in results),
        "total_profit_ytd": sum(a["profit"]["ytd"] for a in results),
        "avg_effective_margin": round(sum(a["effective_margin"] for a in results) / len(results), 1) if results else 0,
    }
    return {"items": results, "total": len(results), "totals": totals}


@router.get("/associate-financials/{associate_id}")
async def get_associate_financial_detail(associate_id: int):
    """Get 360° financial view for a specific associate."""
    item = next((a for a in _mock_associates if a["associate_id"] == associate_id), None)
    return item or {"error": "Not found"}


@router.get("/associate-financials/{associate_id}/transactions")
async def get_associate_transactions(
    associate_id: int,
    transaction_type: Optional[str] = None,
    month: Optional[str] = None,
):
    """Get transaction history for a specific associate."""
    # Mock transactions for demo
    transactions = [
        {"date": "2026-03-07", "type": "payroll", "category": "Bi-weekly Pay", "description": "Pay period 03/01–03/07", "hours": 40, "rate": 85.00, "amount": -3400.00},
        {"date": "2026-03-07", "type": "revenue", "category": "Client Billing", "description": "TechCorp — week of 03/01", "hours": 40, "rate": 135.00, "amount": 5400.00},
        {"date": "2026-03-01", "type": "benefits", "category": "Health Insurance", "description": "March health coverage", "hours": None, "rate": None, "amount": -400.00},
        {"date": "2026-03-01", "type": "insurance", "category": "Workers Comp", "description": "March WC premium", "hours": None, "rate": None, "amount": -200.00},
        {"date": "2026-03-01", "type": "tax", "category": "Payroll Tax", "description": "March employer FICA", "hours": None, "rate": None, "amount": -535.50},
        {"date": "2026-02-28", "type": "reimbursement", "category": "Travel", "description": "Client site travel", "hours": None, "rate": None, "amount": -400.00},
    ]
    if transaction_type:
        transactions = [t for t in transactions if t["type"] == transaction_type]
    return {"associate_id": associate_id, "transactions": transactions}


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — Revenue Analytics
# ══════════════════════════════════════════════════════════════

@router.get("/revenue-analytics")
async def get_revenue_analytics():
    """Get comprehensive revenue analytics dashboard data."""
    return _mock_revenue_analytics


@router.get("/revenue-analytics/trend")
async def get_revenue_trend(months: int = Query(12)):
    """Get revenue trend over N months."""
    return {"months": months, "trend": _mock_revenue_analytics["monthly_revenue_trend"][-months:]}


@router.get("/revenue-analytics/by-industry")
async def get_revenue_by_industry():
    """Get revenue breakdown by industry."""
    return {"items": _mock_revenue_analytics["revenue_by_industry"]}


@router.get("/revenue-analytics/top-associates")
async def get_top_associates():
    """Get top performing associates by revenue."""
    return {"items": _mock_revenue_analytics["top_performing_associates"]}


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — Financial Dashboard
# ══════════════════════════════════════════════════════════════

@router.get("/dashboard")
async def get_financial_dashboard():
    """Get high-level financial dashboard data."""
    return {
        "kpis": {
            "ytd_revenue": 1545000,
            "ytd_net_income": 266100,
            "gross_margin": 36.7,
            "net_margin": 17.2,
            "ar_outstanding": 628000,
            "ap_outstanding": 412000,
            "cash_position": 342000,
            "dso": 42,
            "dpo": 38,
            "active_associates": 45,
            "revenue_per_associate": 35340,
        },
        "ar_aging": _mock_ar_aging_summary,
        "ap_aging": _mock_ap_aging_summary,
        "pl_summary": _mock_pl_monthly[-1],
        "top_customers": _mock_revenue_by_customer[:3],
        "top_suppliers": _mock_expenses_by_supplier[:3],
    }
