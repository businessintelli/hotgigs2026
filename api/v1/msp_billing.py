"""MSP Tiered Billing, Cascading Invoicing & Fee Management API endpoints."""

import logging
import random
from datetime import datetime, date, timedelta
from typing import Optional, List
from fastapi import APIRouter, Query, Path, HTTPException

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/msp-billing")


# ── Mock Data Helpers ───────────────────────────────────────

def _mock_fee_tiers():
    return [
        {"id": 1, "tier_name": "Starter (0-1M)", "revenue_min": 0, "revenue_max": 1000000, "fee_type": "percentage_of_bill", "fee_percentage": 5.0, "fee_flat_amount": None, "effective_from": "2026-01-01", "effective_to": None, "status": "active", "client_org_id": None, "notes": "Default tier for new suppliers", "created_at": "2026-01-01T00:00:00Z"},
        {"id": 2, "tier_name": "Growth (1M-5M)", "revenue_min": 1000000, "revenue_max": 5000000, "fee_type": "percentage_of_bill", "fee_percentage": 4.0, "fee_flat_amount": None, "effective_from": "2026-01-01", "effective_to": None, "status": "active", "client_org_id": None, "notes": "Mid-volume suppliers", "created_at": "2026-01-01T00:00:00Z"},
        {"id": 3, "tier_name": "Enterprise (5M-10M)", "revenue_min": 5000000, "revenue_max": 10000000, "fee_type": "percentage_of_bill", "fee_percentage": 3.5, "fee_flat_amount": None, "effective_from": "2026-01-01", "effective_to": None, "status": "active", "client_org_id": None, "notes": "High-volume discount tier", "created_at": "2026-01-01T00:00:00Z"},
        {"id": 4, "tier_name": "Strategic (10M+)", "revenue_min": 10000000, "revenue_max": None, "fee_type": "percentage_of_bill", "fee_percentage": 3.0, "fee_flat_amount": None, "effective_from": "2026-01-01", "effective_to": None, "status": "active", "client_org_id": None, "notes": "Strategic partners — lowest rate", "created_at": "2026-01-01T00:00:00Z"},
    ]

suppliers = ["TechStaff Pro", "GlobalForce HR", "PrimeRecruit Inc", "NexGen Staffing", "ApexTalent Solutions", "BluWave Consulting"]

def _mock_supplier_revenue():
    tiers = _mock_fee_tiers()
    result = []
    revenues = [750000, 2800000, 6200000, 12500000, 450000, 3100000]
    for i, (name, rev) in enumerate(zip(suppliers, revenues)):
        tier = next((t for t in tiers if t["revenue_min"] <= rev and (t["revenue_max"] is None or rev < t["revenue_max"])), tiers[0])
        fee_pct = tier["fee_percentage"]
        msp_fees = rev * fee_pct / 100
        next_tier = next((t for t in tiers if t["revenue_min"] > rev), None)
        result.append({
            "supplier_org_id": 100 + i, "supplier_name": name,
            "current_revenue": rev, "current_tier": tier["tier_name"],
            "fee_percentage": fee_pct, "ytd_msp_fees": round(msp_fees, 2),
            "active_placements": random.randint(5, 40),
            "next_tier_at": next_tier["revenue_min"] if next_tier else None,
            "savings_at_next_tier": round((fee_pct - (next_tier["fee_percentage"] if next_tier else fee_pct)) * rev / 100, 2) if next_tier else None,
        })
    return result


def _mock_cascade_invoices():
    invoices = []
    statuses = ["approved", "generated", "sent", "paid", "pending"]
    for i in range(20):
        ts_id = 5000 + i
        period_start = date(2026, 2, 3) + timedelta(weeks=i % 4)
        period_end = period_start + timedelta(days=6)
        bill_rate = round(random.uniform(65, 150), 2)
        pay_rate = round(bill_rate * random.uniform(0.60, 0.75), 2)
        hours = round(random.uniform(30, 45), 1)
        gross = round(bill_rate * hours, 2)
        fee_pct = random.choice([3.0, 3.5, 4.0, 5.0])
        msp_fee = round(gross * fee_pct / 100, 2)
        net = round(pay_rate * hours, 2)
        status = random.choice(statuses)
        auto = status in ["approved", "generated", "sent", "paid"]
        # Client → MSP invoice
        inv_client = {
            "id": i * 3 + 1, "invoice_number": f"INV-C-{2026}{i+1:04d}",
            "invoice_type": "client_to_msp", "from_org_name": f"Client Corp {(i % 4) + 1}",
            "to_org_name": "HotGigs MSP", "period_start": str(period_start), "period_end": str(period_end),
            "gross_amount": gross, "msp_fee_amount": msp_fee, "net_amount": gross,
            "tax_amount": 0, "total_amount": gross, "bill_rate": bill_rate, "pay_rate": None,
            "total_hours": hours, "status": status, "auto_approved": False,
            "upstream_approved": True, "approved_at": str(datetime.now()), "due_date": str(period_end + timedelta(days=30)),
            "paid_at": str(datetime.now()) if status == "paid" else None,
            "parent_invoice_id": None, "created_at": str(datetime.now()),
        }
        # MSP → Supplier invoice
        inv_supplier = {
            "id": i * 3 + 2, "invoice_number": f"INV-S-{2026}{i+1:04d}",
            "invoice_type": "msp_to_supplier", "from_org_name": "HotGigs MSP",
            "to_org_name": suppliers[i % len(suppliers)], "period_start": str(period_start), "period_end": str(period_end),
            "gross_amount": net, "msp_fee_amount": 0, "net_amount": net,
            "tax_amount": 0, "total_amount": net, "bill_rate": None, "pay_rate": pay_rate,
            "total_hours": hours, "status": status if auto else "pending",
            "auto_approved": auto, "upstream_approved": auto,
            "approved_at": str(datetime.now()) if auto else None,
            "due_date": str(period_end + timedelta(days=30)),
            "paid_at": str(datetime.now()) if status == "paid" else None,
            "parent_invoice_id": i * 3 + 1, "created_at": str(datetime.now()),
        }
        invoices.append(inv_client)
        invoices.append(inv_supplier)
    return invoices


# ── Fee Tier Endpoints ──────────────────────────────────────

@router.get("/fee-tiers")
async def list_fee_tiers(status: Optional[str] = Query(None)):
    """List all MSP fee tier configurations."""
    tiers = _mock_fee_tiers()
    if status:
        tiers = [t for t in tiers if t["status"] == status]
    return {"fee_tiers": tiers, "total": len(tiers)}


@router.get("/fee-tiers/{tier_id}")
async def get_fee_tier(tier_id: int = Path(...)):
    """Get a specific fee tier by ID."""
    tiers = _mock_fee_tiers()
    tier = next((t for t in tiers if t["id"] == tier_id), None)
    if not tier:
        raise HTTPException(404, "Fee tier not found")
    return tier


@router.post("/fee-tiers")
async def create_fee_tier(body: dict):
    """Create a new MSP fee tier bracket."""
    return {
        "id": random.randint(10, 99),
        **body,
        "status": "active",
        "created_at": datetime.now().isoformat(),
        "message": "Fee tier created successfully",
    }


@router.put("/fee-tiers/{tier_id}")
async def update_fee_tier(tier_id: int, body: dict):
    """Update an existing fee tier."""
    return {"id": tier_id, **body, "updated_at": datetime.now().isoformat(), "message": "Fee tier updated"}


@router.delete("/fee-tiers/{tier_id}")
async def archive_fee_tier(tier_id: int):
    """Archive (soft-delete) a fee tier."""
    return {"id": tier_id, "status": "archived", "message": "Fee tier archived"}


# ── Supplier Revenue Tracking ───────────────────────────────

@router.get("/supplier-revenue")
async def list_supplier_revenue(period: Optional[str] = Query("ytd")):
    """Get supplier revenue brackets and applied fee tiers."""
    return {"suppliers": _mock_supplier_revenue(), "period": period, "total": len(suppliers)}


@router.get("/supplier-revenue/{supplier_org_id}")
async def get_supplier_revenue(supplier_org_id: int):
    """Get detailed revenue breakdown for a specific supplier."""
    all_suppliers = _mock_supplier_revenue()
    supplier = next((s for s in all_suppliers if s["supplier_org_id"] == supplier_org_id), None)
    if not supplier:
        raise HTTPException(404, "Supplier not found")
    # Add monthly breakdown
    monthly = []
    for m in range(1, 4):
        monthly.append({
            "month": f"2026-{m:02d}",
            "revenue": round(supplier["current_revenue"] / 3 * random.uniform(0.8, 1.2), 2),
            "hours": round(random.uniform(500, 2000), 1),
            "placements": random.randint(3, 15),
            "msp_fee": round(supplier["ytd_msp_fees"] / 3 * random.uniform(0.8, 1.2), 2),
        })
    return {**supplier, "monthly_breakdown": monthly}


@router.post("/supplier-revenue/recalculate")
async def recalculate_supplier_revenue():
    """Trigger recalculation of all supplier revenue brackets and fee tiers."""
    return {
        "message": "Revenue recalculation triggered",
        "suppliers_updated": len(suppliers),
        "tiers_applied": 4,
        "total_msp_fees_recalculated": sum(s["ytd_msp_fees"] for s in _mock_supplier_revenue()),
    }


# ── Cascade Invoice Endpoints ───────────────────────────────

@router.get("/cascade-invoices")
async def list_cascade_invoices(
    status: Optional[str] = Query(None),
    invoice_type: Optional[str] = Query(None),
    limit: int = Query(50),
    offset: int = Query(0),
):
    """List all cascading invoices with filtering."""
    invoices = _mock_cascade_invoices()
    if status:
        invoices = [i for i in invoices if i["status"] == status]
    if invoice_type:
        invoices = [i for i in invoices if i["invoice_type"] == invoice_type]
    return {"invoices": invoices[offset:offset + limit], "total": len(invoices)}


@router.get("/cascade-invoices/{invoice_id}")
async def get_cascade_invoice(invoice_id: int):
    """Get a specific cascade invoice with its chain."""
    invoices = _mock_cascade_invoices()
    inv = next((i for i in invoices if i["id"] == invoice_id), None)
    if not inv:
        raise HTTPException(404, "Invoice not found")
    # Find children
    children = [i for i in invoices if i.get("parent_invoice_id") == invoice_id]
    inv["children"] = children
    return inv


@router.get("/cascade-chains")
async def list_cascade_chains():
    """Get full cascade chains — shows Client→MSP→Supplier for each timesheet."""
    chains = []
    for i in range(10):
        chains.append({
            "timesheet_id": 5000 + i,
            "placement_id": 3000 + i,
            "candidate_name": f"Contractor {chr(65 + i)}",
            "period": f"2026-02-{3 + (i % 4) * 7:02d} to 2026-02-{9 + (i % 4) * 7:02d}",
            "total_hours": round(random.uniform(35, 45), 1),
            "bill_rate": round(random.uniform(75, 140), 2),
            "pay_rate": round(random.uniform(50, 95), 2),
            "msp_fee_pct": random.choice([3.0, 3.5, 4.0, 5.0]),
            "cascade_status": random.choice(["fully_cascaded", "partially_cascaded", "pending"]),
            "client_invoice_status": random.choice(["approved", "paid", "pending"]),
            "supplier_invoice_status": random.choice(["auto_approved", "generated", "paid", "pending"]),
        })
    return {"chains": chains, "total": len(chains)}


@router.post("/cascade-invoices/trigger")
async def trigger_cascade(body: dict):
    """
    Trigger cascading invoices from an approved timesheet.
    When upstream (client/MSP) approves, downstream invoices auto-generate.
    """
    timesheet_id = body.get("timesheet_id")
    approval_level = body.get("approval_level", "client")
    return {
        "message": f"Cascade triggered from {approval_level} approval",
        "timesheet_id": timesheet_id,
        "invoices_generated": [
            {"type": "client_to_msp", "invoice_number": f"INV-C-{timesheet_id}", "status": "generated", "auto_approved": True},
            {"type": "msp_to_supplier", "invoice_number": f"INV-S-{timesheet_id}", "status": "auto_approved", "auto_approved": True},
        ],
        "downstream_auto_approved": True,
        "msp_fee_applied": True,
    }


@router.post("/cascade-invoices/{invoice_id}/approve")
async def approve_cascade_invoice(invoice_id: int, body: dict):
    """Approve an invoice — triggers downstream auto-approval if configured."""
    return {
        "invoice_id": invoice_id,
        "status": "approved",
        "downstream_auto_approved": True,
        "downstream_invoices_generated": 1,
        "message": "Invoice approved. Downstream invoices auto-generated and auto-approved.",
    }


# ── Approval Rules ──────────────────────────────────────────

@router.get("/approval-rules")
async def list_approval_rules():
    """List cascade approval rules."""
    return {"rules": [
        {"id": 1, "rule_name": "Client Approval → Auto-Cascade", "trigger_level": "client", "auto_approve_downstream": True, "auto_generate_invoice": True, "billing_cycle": "weekly", "apply_msp_fee": True, "client_org_id": None, "supplier_org_id": None},
        {"id": 2, "rule_name": "MSP Review → Auto-Supplier Pay", "trigger_level": "msp", "auto_approve_downstream": True, "auto_generate_invoice": True, "billing_cycle": "biweekly", "apply_msp_fee": True, "client_org_id": None, "supplier_org_id": None},
        {"id": 3, "rule_name": "Enterprise Client Fast Track", "trigger_level": "client", "auto_approve_downstream": True, "auto_generate_invoice": True, "billing_cycle": "weekly", "apply_msp_fee": True, "client_org_id": 201, "supplier_org_id": None},
    ]}


@router.post("/approval-rules")
async def create_approval_rule(body: dict):
    """Create a new cascade approval rule."""
    return {"id": random.randint(10, 99), **body, "message": "Approval rule created"}


@router.put("/approval-rules/{rule_id}")
async def update_approval_rule(rule_id: int, body: dict):
    """Update a cascade approval rule."""
    return {"id": rule_id, **body, "message": "Approval rule updated"}


# ── Billing Configuration ───────────────────────────────────

@router.get("/config")
async def get_billing_config():
    """Get MSP billing configuration."""
    return {
        "id": 1, "organization_id": 1,
        "default_billing_cycle": "weekly", "auto_cascade_on_approval": True,
        "auto_apply_fee_tier": True, "default_payment_terms_days": 30,
        "tax_rate": 0.0, "invoice_prefix": "INV",
        "msp_fee_calculation_method": "percentage_of_bill",
        "include_expenses_in_revenue": False, "revenue_tracking_period": "annual",
    }


@router.put("/config")
async def update_billing_config(body: dict):
    """Update MSP billing configuration."""
    return {**body, "message": "Billing configuration updated"}


# ── Dashboard ───────────────────────────────────────────────

@router.get("/dashboard")
async def billing_dashboard():
    """Get billing dashboard with KPIs and summaries."""
    invoices = _mock_cascade_invoices()
    paid = [i for i in invoices if i["status"] == "paid"]
    pending = [i for i in invoices if i["status"] == "pending"]
    return {
        "total_invoices": len(invoices),
        "total_billed": round(sum(i["total_amount"] for i in invoices), 2),
        "total_paid": round(sum(i["total_amount"] for i in paid), 2),
        "total_outstanding": round(sum(i["total_amount"] for i in pending), 2),
        "total_msp_fees": round(sum(i["msp_fee_amount"] for i in invoices), 2),
        "cascade_completion_rate": 87.5,
        "avg_days_to_payment": 18.3,
        "invoices_by_status": {
            "pending": len([i for i in invoices if i["status"] == "pending"]),
            "approved": len([i for i in invoices if i["status"] == "approved"]),
            "generated": len([i for i in invoices if i["status"] == "generated"]),
            "sent": len([i for i in invoices if i["status"] == "sent"]),
            "paid": len(paid),
        },
        "fee_tiers": _mock_fee_tiers(),
        "supplier_revenue_summary": _mock_supplier_revenue(),
    }
