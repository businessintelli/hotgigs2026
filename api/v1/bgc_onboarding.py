"""Background Check (BGC) Initiation & Tracking, Onboarding Document Collection & Task Workflows."""

import logging
import random
from datetime import datetime, date, timedelta
from typing import Optional
from fastapi import APIRouter, Query, Path, HTTPException

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/bgc-onboarding")


# ── Mock Data ───────────────────────────────────────────────

candidates = ["Alice Johnson", "Bob Martinez", "Carol Chen", "David Park", "Emma Williams", "Frank Lee", "Grace Kim", "Henry Brown"]
bgc_statuses = ["not_initiated", "initiated", "in_progress", "pending_review", "passed", "failed", "conditional"]
check_types = ["criminal", "employment", "education", "credit", "drug_screen", "reference", "identity"]
task_types = ["document_collection", "form_completion", "training", "system_access", "equipment_setup", "badge_issuance", "orientation", "policy_acknowledgment", "nda_signing"]
task_statuses = ["not_started", "in_progress", "pending_review", "completed", "blocked", "overdue"]
owner_roles = ["msp_coordinator", "supplier_coordinator", "client_hiring_manager", "client_it", "client_hr", "candidate", "system_admin_msp", "system_admin_supplier"]
doc_categories = ["identification", "work_authorization", "tax_forms", "insurance", "certification", "nda", "contract", "policy_acknowledgment"]


def _mock_bgc_packages():
    return [
        {"id": 1, "package_name": "Standard Background Check", "description": "Criminal + employment + education verification", "check_types": ["criminal", "employment", "education"], "is_default": True, "estimated_days": 5, "cost_estimate": 150.0, "vendor_name": "Sterling Check"},
        {"id": 2, "package_name": "Comprehensive Screening", "description": "Full 7-panel screening for sensitive roles", "check_types": ["criminal", "employment", "education", "credit", "drug_screen", "reference", "identity"], "is_default": False, "estimated_days": 10, "cost_estimate": 350.0, "vendor_name": "Sterling Check"},
        {"id": 3, "package_name": "Quick Drug Screen", "description": "Standard 5-panel drug screen only", "check_types": ["drug_screen"], "is_default": False, "estimated_days": 2, "cost_estimate": 45.0, "vendor_name": "Quest Diagnostics"},
    ]


def _mock_bgc_requests():
    requests = []
    for i in range(15):
        status = random.choice(bgc_statuses)
        requests.append({
            "id": i + 1, "candidate_id": 200 + i, "candidate_name": candidates[i % len(candidates)],
            "placement_id": 3000 + i, "package_id": random.choice([1, 2, 3]),
            "package_name": random.choice(["Standard Background Check", "Comprehensive Screening", "Quick Drug Screen"]),
            "status": status,
            "initiated_by_role": "msp_coordinator", "coordinated_by_role": "msp_coordinator",
            "executed_by_role": "supplier_coordinator",
            "initiated_at": str(datetime.now() - timedelta(days=random.randint(1, 30))),
            "due_date": str(date.today() + timedelta(days=random.randint(-5, 15))),
            "completed_at": str(datetime.now()) if status in ["passed", "failed", "conditional"] else None,
            "vendor_name": random.choice(["Sterling Check", "Quest Diagnostics", "HireRight"]),
            "overall_result": "pass" if status == "passed" else "fail" if status == "failed" else "conditional" if status == "conditional" else None,
            "risk_level": random.choice(["low", "medium", "high"]) if status in ["passed", "conditional"] else None,
            "supplier_name": random.choice(["TechStaff Pro", "GlobalForce HR", "PrimeRecruit Inc"]),
            "client_name": f"Client Corp {random.randint(1, 4)}",
            "check_items": [
                {"check_type": ct, "status": random.choice(["passed", "in_progress", "not_initiated"]),
                 "result": random.choice(["clear", "review", None])}
                for ct in random.sample(check_types, random.randint(2, 5))
            ],
        })
    return requests


def _mock_onboarding_tasks():
    tasks = []
    for i in range(25):
        status = random.choice(task_statuses)
        role = random.choice(owner_roles)
        tasks.append({
            "id": i + 1, "placement_id": 3000 + (i % 8), "candidate_id": 200 + (i % 8),
            "candidate_name": candidates[i % len(candidates)],
            "task_name": random.choice([
                "Collect W-4 Form", "Submit I-9 Documentation", "Complete NDA Signing",
                "Setup VPN Access", "Issue Building Badge", "Complete Safety Training",
                "Provide Direct Deposit Info", "Sign Employee Handbook Acknowledgment",
                "Complete Orientation Session", "Setup Email Account", "Provide Emergency Contacts",
                "Submit Insurance Enrollment", "Complete Security Clearance Form",
            ]),
            "task_type": random.choice(task_types),
            "status": status,
            "priority": random.choice([1, 2, 2, 3, 3, 4]),
            "owner_role": role,
            "owner_role_display": role.replace("_", " ").title(),
            "assigned_to_user": f"User {random.randint(1, 20)}",
            "assigned_to_org": random.choice(["HotGigs MSP", "TechStaff Pro", "Client Corp 1"]),
            "due_date": str(date.today() + timedelta(days=random.randint(-10, 20))),
            "started_at": str(datetime.now() - timedelta(days=random.randint(0, 10))) if status != "not_started" else None,
            "completed_at": str(datetime.now()) if status == "completed" else None,
            "follow_up_count": random.randint(0, 5),
            "last_follow_up_at": str(datetime.now() - timedelta(days=random.randint(0, 5))) if random.random() > 0.5 else None,
            "blocks_start_date": random.random() > 0.7,
            "is_overdue": status == "overdue" or (status not in ["completed", "skipped"] and random.random() > 0.7),
        })
    return tasks


def _mock_onboarding_documents():
    docs = []
    for i in range(20):
        received = random.random() > 0.3
        verified = received and random.random() > 0.4
        docs.append({
            "id": i + 1, "placement_id": 3000 + (i % 8), "candidate_id": 200 + (i % 8),
            "candidate_name": candidates[i % len(candidates)],
            "document_name": random.choice([
                "Passport Copy", "W-4 Tax Form", "I-9 Employment Eligibility",
                "Direct Deposit Form", "NDA Agreement", "Background Check Authorization",
                "Drug Screen Consent", "Employee Handbook Acknowledgment",
                "Emergency Contact Form", "Insurance Enrollment Form",
                "Professional Certification", "Driver's License Copy",
            ]),
            "category": random.choice(doc_categories),
            "is_received": received,
            "is_verified": verified,
            "received_at": str(datetime.now() - timedelta(days=random.randint(0, 15))) if received else None,
            "verified_at": str(datetime.now() - timedelta(days=random.randint(0, 5))) if verified else None,
            "required_by": str(date.today() + timedelta(days=random.randint(-5, 15))),
            "expires_at": str(date.today() + timedelta(days=random.randint(30, 365))) if random.random() > 0.5 else None,
            "collected_by_role": random.choice(["msp_coordinator", "supplier_coordinator", "candidate"]),
        })
    return docs


# ── BGC Package Endpoints ───────────────────────────────────

@router.get("/bgc/packages")
async def list_bgc_packages():
    """List all configured BGC packages."""
    return {"packages": _mock_bgc_packages(), "total": 3}


@router.get("/bgc/packages/{package_id}")
async def get_bgc_package(package_id: int):
    pkg = next((p for p in _mock_bgc_packages() if p["id"] == package_id), None)
    if not pkg: raise HTTPException(404, "Package not found")
    return pkg


@router.post("/bgc/packages")
async def create_bgc_package(body: dict):
    return {"id": random.randint(10, 99), **body, "message": "BGC package created"}


@router.put("/bgc/packages/{package_id}")
async def update_bgc_package(package_id: int, body: dict):
    return {"id": package_id, **body, "message": "BGC package updated"}


# ── BGC Request Endpoints ───────────────────────────────────

@router.get("/bgc/requests")
async def list_bgc_requests(
    status: Optional[str] = Query(None),
    candidate_id: Optional[int] = Query(None),
    limit: int = Query(50),
):
    """List all BGC requests with filtering."""
    reqs = _mock_bgc_requests()
    if status: reqs = [r for r in reqs if r["status"] == status]
    if candidate_id: reqs = [r for r in reqs if r["candidate_id"] == candidate_id]
    return {"requests": reqs[:limit], "total": len(reqs)}


@router.get("/bgc/requests/{request_id}")
async def get_bgc_request(request_id: int):
    reqs = _mock_bgc_requests()
    req = next((r for r in reqs if r["id"] == request_id), None)
    if not req: raise HTTPException(404, "BGC request not found")
    return req


@router.post("/bgc/requests")
async def initiate_bgc(body: dict):
    """
    Initiate a background check. MSP coordinates, supplier executes.
    Roles:
    - MSP Coordinator: initiates and tracks progress
    - Supplier Coordinator: schedules with vendor and collects results
    """
    return {
        "id": random.randint(100, 999),
        "candidate_id": body.get("candidate_id"),
        "package_id": body.get("package_id", 1),
        "status": "initiated",
        "initiated_by_role": "msp_coordinator",
        "coordinated_by_role": "msp_coordinator",
        "executed_by_role": "supplier_coordinator",
        "message": "BGC initiated. Supplier coordinator notified to schedule with vendor.",
        "check_items_created": len(body.get("check_types", ["criminal", "employment", "education"])),
    }


@router.put("/bgc/requests/{request_id}/status")
async def update_bgc_status(request_id: int, body: dict):
    """Update BGC request status — role-based (MSP updates coordination, supplier updates execution)."""
    return {
        "id": request_id, "status": body.get("status"), "updated_by_role": body.get("role"),
        "message": f"BGC status updated to {body.get('status')}",
    }


@router.post("/bgc/requests/{request_id}/check-items")
async def add_check_item(request_id: int, body: dict):
    """Add a check item result to a BGC request."""
    return {
        "bgc_request_id": request_id, "check_type": body.get("check_type"),
        "status": body.get("status", "in_progress"), "message": "Check item added",
    }


@router.get("/bgc/dashboard")
async def bgc_dashboard():
    """BGC tracking dashboard with KPIs."""
    reqs = _mock_bgc_requests()
    return {
        "total_requests": len(reqs),
        "by_status": {s: len([r for r in reqs if r["status"] == s]) for s in set(r["status"] for r in reqs)},
        "avg_completion_days": 6.2,
        "pass_rate": 82.5,
        "pending_review": len([r for r in reqs if r["status"] == "pending_review"]),
        "overdue": len([r for r in reqs if r.get("due_date") and r["due_date"] < str(date.today()) and r["status"] not in ["passed", "failed", "conditional", "cancelled"]]),
        "by_vendor": {"Sterling Check": 8, "Quest Diagnostics": 4, "HireRight": 3},
        "responsibility_breakdown": {
            "msp_coordinator": {"coordinating": 10, "description": "Initiates & tracks all BGC requests"},
            "supplier_coordinator": {"executing": 12, "description": "Schedules with vendor & collects results"},
        },
    }


# ── Onboarding Task Endpoints ───────────────────────────────

@router.get("/onboarding/templates")
async def list_onboarding_templates():
    """List onboarding task templates."""
    return {"templates": [
        {"id": 1, "template_name": "Standard Onboarding", "description": "Default onboarding for all placements", "is_default": True, "task_count": 12, "estimated_days": 7},
        {"id": 2, "template_name": "IT Contractor Onboarding", "description": "Extended onboarding with IT access setup", "is_default": False, "task_count": 15, "estimated_days": 10},
        {"id": 3, "template_name": "Remote Worker Onboarding", "description": "Simplified onboarding for remote contractors", "is_default": False, "task_count": 8, "estimated_days": 5},
    ]}


@router.post("/onboarding/templates")
async def create_onboarding_template(body: dict):
    return {"id": random.randint(10, 99), **body, "message": "Onboarding template created"}


@router.get("/onboarding/tasks")
async def list_onboarding_tasks(
    placement_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    owner_role: Optional[str] = Query(None),
    overdue_only: bool = Query(False),
    limit: int = Query(50),
):
    """List onboarding tasks with role-based filtering."""
    tasks = _mock_onboarding_tasks()
    if placement_id: tasks = [t for t in tasks if t["placement_id"] == placement_id]
    if status: tasks = [t for t in tasks if t["status"] == status]
    if owner_role: tasks = [t for t in tasks if t["owner_role"] == owner_role]
    if overdue_only: tasks = [t for t in tasks if t.get("is_overdue")]
    return {"tasks": tasks[:limit], "total": len(tasks)}


@router.get("/onboarding/tasks/{task_id}")
async def get_onboarding_task(task_id: int):
    tasks = _mock_onboarding_tasks()
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task: raise HTTPException(404, "Task not found")
    return task


@router.post("/onboarding/tasks")
async def create_onboarding_task(body: dict):
    """Create a new onboarding task with role assignment."""
    return {
        "id": random.randint(100, 999), **body, "status": "not_started",
        "message": f"Task created and assigned to {body.get('owner_role', 'msp_coordinator')}",
    }


@router.put("/onboarding/tasks/{task_id}/status")
async def update_task_status(task_id: int, body: dict):
    """Update onboarding task status."""
    return {
        "id": task_id, "status": body.get("status"),
        "message": f"Task updated to {body.get('status')}",
    }


@router.post("/onboarding/tasks/{task_id}/follow-up")
async def send_follow_up(task_id: int, body: dict):
    """Send a follow-up reminder for an onboarding task."""
    return {
        "task_id": task_id, "follow_up_sent": True,
        "follow_up_count": random.randint(1, 5),
        "sent_to_role": body.get("to_role", "assigned_user"),
        "message": "Follow-up reminder sent",
    }


@router.post("/onboarding/placement/{placement_id}/init")
async def initialize_onboarding(placement_id: int, body: dict):
    """
    Initialize onboarding for a placement — creates all tasks from template.
    Assigns tasks to appropriate roles (MSP coordinator, supplier, client IT, etc.)
    """
    template_id = body.get("template_id", 1)
    return {
        "placement_id": placement_id,
        "template_id": template_id,
        "tasks_created": random.randint(8, 15),
        "role_assignments": {
            "msp_coordinator": 3,
            "supplier_coordinator": 4,
            "client_it": 2,
            "client_hr": 2,
            "candidate": 3,
        },
        "bgc_auto_initiated": True,
        "message": "Onboarding initialized. Tasks assigned to roles. BGC auto-initiated.",
    }


# ── Onboarding Document Endpoints ───────────────────────────

@router.get("/onboarding/documents")
async def list_onboarding_documents(
    placement_id: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    received: Optional[bool] = Query(None),
):
    """List onboarding documents with filtering."""
    docs = _mock_onboarding_documents()
    if placement_id: docs = [d for d in docs if d["placement_id"] == placement_id]
    if category: docs = [d for d in docs if d["category"] == category]
    if received is not None: docs = [d for d in docs if d["is_received"] == received]
    return {"documents": docs, "total": len(docs)}


@router.post("/onboarding/documents")
async def upload_document(body: dict):
    return {"id": random.randint(100, 999), **body, "is_received": True, "message": "Document uploaded"}


@router.put("/onboarding/documents/{doc_id}/verify")
async def verify_document(doc_id: int, body: dict):
    return {"id": doc_id, "is_verified": True, "verified_by": body.get("verified_by"), "message": "Document verified"}


# ── Onboarding Dashboard ───────────────────────────────────

@router.get("/onboarding/dashboard")
async def onboarding_dashboard():
    """Onboarding overview with KPIs."""
    tasks = _mock_onboarding_tasks()
    docs = _mock_onboarding_documents()
    return {
        "total_tasks": len(tasks),
        "tasks_by_status": {s: len([t for t in tasks if t["status"] == s]) for s in set(t["status"] for t in tasks)},
        "tasks_by_role": {r: len([t for t in tasks if t["owner_role"] == r]) for r in set(t["owner_role"] for t in tasks)},
        "overdue_tasks": len([t for t in tasks if t.get("is_overdue")]),
        "avg_completion_days": 4.8,
        "document_collection_rate": round(len([d for d in docs if d["is_received"]]) / len(docs) * 100, 1),
        "document_verification_rate": round(len([d for d in docs if d["is_verified"]]) / len(docs) * 100, 1),
        "active_onboardings": 8,
        "blocking_tasks": len([t for t in tasks if t.get("blocks_start_date") and t["status"] not in ["completed", "skipped"]]),
    }
