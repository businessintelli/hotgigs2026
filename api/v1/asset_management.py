"""Asset Allocation & Management — hardware, software, badges, access tracking."""

import logging
import random
from datetime import datetime, date, timedelta
from typing import Optional
from fastapi import APIRouter, Query, Path, HTTPException

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/asset-management")


# ── Mock Data ───────────────────────────────────────────────

asset_types = ["laptop", "monitor", "phone", "badge", "access_card", "vpn_access", "email_account", "software_license", "headset", "parking_pass"]
providers = ["msp", "supplier", "client", "contractor_owned"]
managed_by_roles = ["system_admin_msp", "system_admin_supplier", "system_admin_client", "client_it", "client_facilities"]
alloc_statuses = ["requested", "approved", "ordered", "allocated", "delivered", "return_initiated", "return_completed"]
candidates = ["Alice Johnson", "Bob Martinez", "Carol Chen", "David Park", "Emma Williams", "Frank Lee"]


def _mock_asset_catalog():
    assets = []
    items = [
        ("Dell Latitude 5540", "laptop", "Dell", "Latitude 5540", 1200),
        ("Dell UltraSharp 27\"", "monitor", "Dell", "U2722D", 450),
        ("iPhone 15 Pro", "phone", "Apple", "iPhone 15 Pro", 999),
        ("Jabra Evolve2 75", "headset", "Jabra", "Evolve2 75", 250),
        ("HID ProxCard II", "badge", "HID Global", "ProxCard II", 15),
        ("Cisco AnyConnect VPN", "vpn_access", "Cisco", "AnyConnect", 0),
        ("Microsoft 365 E5", "software_license", "Microsoft", "365 E5", 57),
        ("Office 365 Email", "email_account", "Microsoft", "Exchange Online", 0),
        ("Parking Level B2", "parking_pass", None, None, 150),
        ("HID iCLASS Card", "access_card", "HID Global", "iCLASS", 25),
    ]
    for i, (name, atype, make, model, cost) in enumerate(items):
        status = random.choice(["available", "available", "available", "allocated", "allocated", "in_use"])
        prov = "client" if atype in ["badge", "access_card", "vpn_access", "parking_pass"] else random.choice(["client", "msp", "supplier"])
        mgr = "client_it" if prov == "client" else f"system_admin_{prov}"
        assets.append({
            "id": i + 1, "asset_type": atype, "asset_name": name, "make": make, "model": model,
            "serial_number": f"SN-{random.randint(100000, 999999)}" if cost > 100 else None,
            "asset_tag": f"TAG-{1000 + i}", "status": status,
            "provider": prov, "managed_by": mgr,
            "purchase_cost": cost, "monthly_cost": round(cost / 36, 2) if cost > 0 else 0,
            "location": random.choice(["Building A, Floor 3", "Building B, Floor 1", "Remote - Ship to Home"]),
            "assigned_to_candidate": candidates[i % len(candidates)] if status in ["allocated", "in_use"] else None,
            "assigned_to_placement_id": 3000 + i if status in ["allocated", "in_use"] else None,
        })
    return assets


def _mock_allocation_requests():
    requests = []
    for i in range(18):
        status = random.choice(alloc_statuses)
        prov = random.choice(providers[:3])
        requests.append({
            "id": i + 1, "placement_id": 3000 + (i % 8), "candidate_id": 200 + (i % 6),
            "candidate_name": candidates[i % len(candidates)],
            "asset_type": random.choice(asset_types),
            "asset_description": random.choice(["Dell Laptop + Charger", "Building Badge", "VPN Access Setup", "Monitor 27\"", "Parking Pass L-B2", "Jabra Headset"]),
            "quantity": 1,
            "provider": prov,
            "provider_display": prov.replace("_", " ").title(),
            "managed_by": random.choice(managed_by_roles),
            "managed_by_org": random.choice(["HotGigs MSP", "TechStaff Pro", "Client Corp 1"]),
            "status": status,
            "requested_by": f"User {random.randint(1, 10)}",
            "needed_by": str(date.today() + timedelta(days=random.randint(-5, 15))),
            "approved_at": str(datetime.now() - timedelta(days=random.randint(0, 10))) if status not in ["requested"] else None,
            "delivered_at": str(datetime.now() - timedelta(days=random.randint(0, 5))) if status == "delivered" else None,
            "return_due_date": str(date.today() + timedelta(days=random.randint(30, 180))) if status in ["delivered", "return_initiated"] else None,
            "tracking_number": f"TRK-{random.randint(10000, 99999)}" if status in ["ordered", "allocated", "delivered"] else None,
        })
    return requests


def _mock_allocation_rules():
    return [
        {"id": 1, "rule_name": "Standard IT Setup — Client Corp 1", "client_org_id": 201, "job_category": None, "asset_types": [{"type": "laptop", "provider": "client"}, {"type": "badge", "provider": "client"}, {"type": "vpn_access", "provider": "client"}, {"type": "email_account", "provider": "client"}], "default_provider": "client", "default_managed_by": "client_it", "auto_request": True, "lead_days": 5},
        {"id": 2, "rule_name": "Remote Worker Kit — MSP Provided", "client_org_id": None, "job_category": "remote", "asset_types": [{"type": "laptop", "provider": "msp"}, {"type": "headset", "provider": "msp"}, {"type": "vpn_access", "provider": "client"}], "default_provider": "msp", "default_managed_by": "system_admin_msp", "auto_request": True, "lead_days": 7},
        {"id": 3, "rule_name": "Supplier-Provided Equipment", "client_org_id": None, "job_category": None, "asset_types": [{"type": "laptop", "provider": "supplier"}, {"type": "phone", "provider": "supplier"}], "default_provider": "supplier", "default_managed_by": "system_admin_supplier", "auto_request": False, "lead_days": 3},
    ]


# ── Asset Catalog Endpoints ─────────────────────────────────

@router.get("/catalog")
async def list_assets(
    asset_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    provider: Optional[str] = Query(None),
    limit: int = Query(50),
):
    """List all assets in the catalog."""
    assets = _mock_asset_catalog()
    if asset_type: assets = [a for a in assets if a["asset_type"] == asset_type]
    if status: assets = [a for a in assets if a["status"] == status]
    if provider: assets = [a for a in assets if a["provider"] == provider]
    return {"assets": assets[:limit], "total": len(assets)}


@router.get("/catalog/{asset_id}")
async def get_asset(asset_id: int):
    assets = _mock_asset_catalog()
    asset = next((a for a in assets if a["id"] == asset_id), None)
    if not asset: raise HTTPException(404, "Asset not found")
    return asset


@router.post("/catalog")
async def create_asset(body: dict):
    return {"id": random.randint(100, 999), **body, "status": "available", "message": "Asset added to catalog"}


@router.put("/catalog/{asset_id}")
async def update_asset(asset_id: int, body: dict):
    return {"id": asset_id, **body, "message": "Asset updated"}


# ── Allocation Request Endpoints ────────────────────────────

@router.get("/requests")
async def list_allocation_requests(
    placement_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    provider: Optional[str] = Query(None),
    managed_by: Optional[str] = Query(None),
    limit: int = Query(50),
):
    """List asset allocation requests with filtering."""
    reqs = _mock_allocation_requests()
    if placement_id: reqs = [r for r in reqs if r["placement_id"] == placement_id]
    if status: reqs = [r for r in reqs if r["status"] == status]
    if provider: reqs = [r for r in reqs if r["provider"] == provider]
    if managed_by: reqs = [r for r in reqs if r["managed_by"] == managed_by]
    return {"requests": reqs[:limit], "total": len(reqs)}


@router.get("/requests/{request_id}")
async def get_allocation_request(request_id: int):
    reqs = _mock_allocation_requests()
    req = next((r for r in reqs if r["id"] == request_id), None)
    if not req: raise HTTPException(404, "Request not found")
    return req


@router.post("/requests")
async def create_allocation_request(body: dict):
    """
    Request asset allocation. Provider determines who provides:
    - client: Client IT / facilities handles
    - msp: MSP system admin handles
    - supplier: Supplier system admin handles
    """
    return {
        "id": random.randint(100, 999), **body, "status": "requested",
        "message": f"Asset request created. {body.get('managed_by', 'system_admin_client')} notified.",
    }


@router.put("/requests/{request_id}/status")
async def update_allocation_status(request_id: int, body: dict):
    """Update allocation request status (approve, order, deliver, return)."""
    return {
        "id": request_id, "status": body.get("status"),
        "message": f"Request updated to {body.get('status')}",
    }


@router.post("/requests/{request_id}/approve")
async def approve_allocation(request_id: int, body: dict):
    return {"id": request_id, "status": "approved", "approved_by": body.get("approved_by"), "message": "Allocation approved"}


@router.post("/requests/{request_id}/return")
async def initiate_return(request_id: int, body: dict):
    """Initiate asset return — typically at end of placement."""
    return {
        "id": request_id, "status": "return_initiated",
        "return_due_date": str(date.today() + timedelta(days=14)),
        "message": "Asset return initiated. Return instructions sent.",
    }


@router.post("/requests/{request_id}/return-complete")
async def complete_return(request_id: int, body: dict):
    return {
        "id": request_id, "status": "return_completed",
        "return_condition": body.get("condition", "good"),
        "message": "Asset return completed and logged.",
    }


# ── Allocation Rules ───────────────────────────────────────

@router.get("/rules")
async def list_allocation_rules():
    """List auto-allocation rules."""
    return {"rules": _mock_allocation_rules(), "total": 3}


@router.post("/rules")
async def create_allocation_rule(body: dict):
    return {"id": random.randint(10, 99), **body, "message": "Allocation rule created"}


@router.put("/rules/{rule_id}")
async def update_allocation_rule(rule_id: int, body: dict):
    return {"id": rule_id, **body, "message": "Allocation rule updated"}


@router.post("/placement/{placement_id}/auto-allocate")
async def auto_allocate_for_placement(placement_id: int, body: dict):
    """
    Auto-allocate assets for a new placement based on matching rules.
    Determines provider (MSP/supplier/client) and assigns to correct system admin.
    """
    return {
        "placement_id": placement_id,
        "rules_matched": 2,
        "requests_created": [
            {"asset_type": "laptop", "provider": "client", "managed_by": "client_it", "status": "requested"},
            {"asset_type": "badge", "provider": "client", "managed_by": "client_facilities", "status": "requested"},
            {"asset_type": "vpn_access", "provider": "client", "managed_by": "client_it", "status": "requested"},
            {"asset_type": "email_account", "provider": "client", "managed_by": "client_it", "status": "requested"},
        ],
        "message": "4 asset allocation requests auto-created based on rules.",
    }


# ── Dashboard ───────────────────────────────────────────────

@router.get("/dashboard")
async def asset_dashboard():
    """Asset management dashboard."""
    assets = _mock_asset_catalog()
    reqs = _mock_allocation_requests()
    return {
        "total_assets": len(assets),
        "assets_by_status": {s: len([a for a in assets if a["status"] == s]) for s in set(a["status"] for a in assets)},
        "assets_by_type": {t: len([a for a in assets if a["asset_type"] == t]) for t in set(a["asset_type"] for a in assets)},
        "assets_by_provider": {
            "client": len([a for a in assets if a["provider"] == "client"]),
            "msp": len([a for a in assets if a["provider"] == "msp"]),
            "supplier": len([a for a in assets if a["provider"] == "supplier"]),
        },
        "total_requests": len(reqs),
        "pending_requests": len([r for r in reqs if r["status"] in ["requested", "approved", "ordered"]]),
        "pending_returns": len([r for r in reqs if r["status"] == "return_initiated"]),
        "overdue_returns": 2,
        "total_asset_value": sum(a.get("purchase_cost", 0) for a in assets),
        "monthly_cost": sum(a.get("monthly_cost", 0) for a in assets),
    }
