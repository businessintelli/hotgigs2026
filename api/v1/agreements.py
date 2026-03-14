"""Agreements API — MSA, NDA, SOW, PO management with template repository,
e-signature workflows, signatory authority, and change request handling.

Company-specific document templates with dynamic variable substitution,
auto-sign for sender, review/change request workflow for recipients.
"""
from datetime import datetime, date, timedelta
from fastapi import APIRouter, Query
from typing import Optional

router = APIRouter(prefix="/agreements")


# ══════════════════════════════════════════════════════════════
#  MOCK DATA — Signatory Authorities
# ══════════════════════════════════════════════════════════════

_mock_signatories = [
    {"id": 1, "org_id": 1, "name": "Robert Chen", "designation": "CEO & Managing Director", "email": "robert.chen@hotgigs.com", "phone": "+1-555-0101", "is_default": True, "can_sign_types": None, "max_contract_value": None, "is_active": True, "signature_image": "data:image/png;base64,R0bGVySignature..."},
    {"id": 2, "org_id": 1, "name": "Lisa Park", "designation": "VP of Operations", "email": "lisa.park@hotgigs.com", "phone": "+1-555-0102", "is_default": False, "can_sign_types": ["sow", "po", "staffing", "rate_card"], "max_contract_value": 500000, "is_active": True, "signature_image": "data:image/png;base64,TGlzYSignature..."},
    {"id": 3, "org_id": 1, "name": "David Martinez", "designation": "Legal Counsel", "email": "david.martinez@hotgigs.com", "phone": "+1-555-0103", "is_default": False, "can_sign_types": ["msa", "nda", "non_compete", "ip_assignment"], "max_contract_value": None, "is_active": True, "signature_image": "data:image/png;base64,RGF2aSignature..."},
]

# ══════════════════════════════════════════════════════════════
#  MOCK DATA — Agreement Templates
# ══════════════════════════════════════════════════════════════

_mock_templates = [
    {
        "id": 1, "org_id": 1, "name": "Master Service Agreement — Standard",
        "agreement_type": "msa", "category": "client",
        "description": "Standard MSA for staffing engagements with clients. Covers liability, IP, payment terms, and termination.",
        "version": "3.2", "is_active": True, "is_default": True,
        "auto_sign_sender": True, "default_signatory_id": 1,
        "requires_witness": False, "requires_notary": False,
        "variables": [
            {"key": "client_company_name", "label": "Client Company Name", "type": "text", "required": True},
            {"key": "client_address", "label": "Client Address", "type": "textarea", "required": True},
            {"key": "client_signatory_name", "label": "Client Signatory Name", "type": "text", "required": True},
            {"key": "client_signatory_designation", "label": "Client Signatory Title", "type": "text", "required": True},
            {"key": "client_email", "label": "Client Email", "type": "email", "required": True},
            {"key": "effective_date", "label": "Effective Date", "type": "date", "required": True},
            {"key": "term_months", "label": "Term (Months)", "type": "number", "required": True, "default": "12"},
            {"key": "payment_terms", "label": "Payment Terms", "type": "select", "required": True, "options": ["Net 30", "Net 45", "Net 60"]},
            {"key": "governing_law_state", "label": "Governing Law State", "type": "text", "required": True, "default": "California"},
        ],
        "tags": ["client", "staffing", "standard"], "usage_count": 24,
        "created_by": "Robert Chen", "updated_at": "2026-02-15",
    },
    {
        "id": 2, "org_id": 1, "name": "Non-Disclosure Agreement — Mutual",
        "agreement_type": "nda", "category": "general",
        "description": "Mutual NDA for protecting confidential information between parties.",
        "version": "2.1", "is_active": True, "is_default": True,
        "auto_sign_sender": True, "default_signatory_id": 3,
        "requires_witness": False, "requires_notary": False,
        "variables": [
            {"key": "party_name", "label": "Other Party Name", "type": "text", "required": True},
            {"key": "party_company", "label": "Other Party Company", "type": "text", "required": False},
            {"key": "party_address", "label": "Other Party Address", "type": "textarea", "required": True},
            {"key": "party_email", "label": "Other Party Email", "type": "email", "required": True},
            {"key": "effective_date", "label": "Effective Date", "type": "date", "required": True},
            {"key": "confidentiality_period_years", "label": "Confidentiality Period (Years)", "type": "number", "required": True, "default": "2"},
            {"key": "purpose", "label": "Purpose of Disclosure", "type": "textarea", "required": True},
        ],
        "tags": ["nda", "mutual", "confidentiality"], "usage_count": 38,
        "created_by": "David Martinez", "updated_at": "2026-01-20",
    },
    {
        "id": 3, "org_id": 1, "name": "Statement of Work — IT Staffing",
        "agreement_type": "sow", "category": "client",
        "description": "SOW for IT staffing projects. References parent MSA, defines scope, rates, and deliverables.",
        "version": "2.0", "is_active": True, "is_default": True,
        "auto_sign_sender": True, "default_signatory_id": 2,
        "requires_witness": False, "requires_notary": False,
        "variables": [
            {"key": "client_company_name", "label": "Client Company", "type": "text", "required": True},
            {"key": "client_signatory", "label": "Client Signatory", "type": "text", "required": True},
            {"key": "client_email", "label": "Client Email", "type": "email", "required": True},
            {"key": "parent_msa_number", "label": "Parent MSA Number", "type": "text", "required": True},
            {"key": "project_name", "label": "Project Name", "type": "text", "required": True},
            {"key": "scope_description", "label": "Scope of Work", "type": "textarea", "required": True},
            {"key": "start_date", "label": "Start Date", "type": "date", "required": True},
            {"key": "end_date", "label": "End Date", "type": "date", "required": True},
            {"key": "bill_rate", "label": "Bill Rate ($/hr)", "type": "number", "required": True},
            {"key": "estimated_hours", "label": "Estimated Hours", "type": "number", "required": True},
            {"key": "not_to_exceed", "label": "Not-to-Exceed Amount ($)", "type": "number", "required": False},
        ],
        "tags": ["sow", "it", "staffing", "client"], "usage_count": 15,
        "created_by": "Lisa Park", "updated_at": "2026-03-01",
    },
    {
        "id": 4, "org_id": 1, "name": "Purchase Order — Standard",
        "agreement_type": "po", "category": "supplier",
        "description": "Standard PO for procurement of staffing services from suppliers.",
        "version": "1.5", "is_active": True, "is_default": True,
        "auto_sign_sender": True, "default_signatory_id": 2,
        "requires_witness": False, "requires_notary": False,
        "variables": [
            {"key": "supplier_name", "label": "Supplier Company Name", "type": "text", "required": True},
            {"key": "supplier_contact", "label": "Supplier Contact Name", "type": "text", "required": True},
            {"key": "supplier_email", "label": "Supplier Email", "type": "email", "required": True},
            {"key": "supplier_address", "label": "Supplier Address", "type": "textarea", "required": True},
            {"key": "po_description", "label": "Description of Services", "type": "textarea", "required": True},
            {"key": "total_amount", "label": "Total PO Amount ($)", "type": "number", "required": True},
            {"key": "payment_terms", "label": "Payment Terms", "type": "select", "required": True, "options": ["Net 15", "Net 30", "Net 45"]},
            {"key": "delivery_date", "label": "Expected Delivery Date", "type": "date", "required": True},
        ],
        "tags": ["po", "supplier", "procurement"], "usage_count": 31,
        "created_by": "Lisa Park", "updated_at": "2026-02-28",
    },
    {
        "id": 5, "org_id": 1, "name": "Supplier Staffing Agreement",
        "agreement_type": "staffing", "category": "supplier",
        "description": "Agreement with staffing suppliers for providing contract resources.",
        "version": "2.3", "is_active": True, "is_default": False,
        "auto_sign_sender": True, "default_signatory_id": 1,
        "requires_witness": False, "requires_notary": False,
        "variables": [
            {"key": "supplier_name", "label": "Supplier Name", "type": "text", "required": True},
            {"key": "supplier_contact", "label": "Contact Person", "type": "text", "required": True},
            {"key": "supplier_email", "label": "Email", "type": "email", "required": True},
            {"key": "supplier_address", "label": "Address", "type": "textarea", "required": True},
            {"key": "effective_date", "label": "Effective Date", "type": "date", "required": True},
            {"key": "markup_structure", "label": "Markup Structure", "type": "textarea", "required": True},
            {"key": "payment_terms", "label": "Payment Terms", "type": "select", "required": True, "options": ["Net 30", "Net 45"]},
            {"key": "insurance_requirements", "label": "Insurance Requirements", "type": "textarea", "required": False},
        ],
        "tags": ["supplier", "staffing", "agreement"], "usage_count": 8,
        "created_by": "Robert Chen", "updated_at": "2026-01-10",
    },
    {
        "id": 6, "org_id": 1, "name": "Non-Compete Agreement — Associate",
        "agreement_type": "non_compete", "category": "associate",
        "description": "Non-compete and non-solicitation agreement for placed associates.",
        "version": "1.2", "is_active": True, "is_default": True,
        "auto_sign_sender": True, "default_signatory_id": 3,
        "requires_witness": True, "requires_notary": False,
        "variables": [
            {"key": "associate_name", "label": "Associate Full Name", "type": "text", "required": True},
            {"key": "associate_email", "label": "Associate Email", "type": "email", "required": True},
            {"key": "associate_address", "label": "Associate Address", "type": "textarea", "required": True},
            {"key": "client_name", "label": "Client Name", "type": "text", "required": True},
            {"key": "restriction_period_months", "label": "Restriction Period (Months)", "type": "number", "required": True, "default": "12"},
            {"key": "geographic_scope", "label": "Geographic Scope", "type": "text", "required": True, "default": "United States"},
        ],
        "tags": ["non-compete", "associate", "restriction"], "usage_count": 12,
        "created_by": "David Martinez", "updated_at": "2026-02-05",
    },
]

# ══════════════════════════════════════════════════════════════
#  MOCK DATA — Agreements (Sent)
# ══════════════════════════════════════════════════════════════

_mock_agreements = [
    {
        "id": 1, "agreement_number": "AGR-2026-0001", "template_id": 1, "agreement_type": "msa",
        "title": "Master Service Agreement — TechCorp Inc",
        "status": "fully_executed",
        "sender_org_name": "HotGigs MSP", "sender_name": "Robert Chen", "sender_email": "robert.chen@hotgigs.com", "sender_designation": "CEO",
        "recipient_org_name": "TechCorp Inc", "recipient_name": "Sarah Mitchell", "recipient_email": "sarah.m@techcorp.com", "recipient_designation": "VP Procurement",
        "effective_date": "2025-06-01", "expiry_date": "2026-05-31",
        "contract_value": 2400000, "currency": "USD",
        "sender_signed": True, "sender_signed_at": "2025-05-28T10:00:00Z",
        "recipient_signed": True, "recipient_signed_at": "2025-05-29T14:30:00Z",
        "sent_at": "2025-05-28T10:05:00Z", "completed_at": "2025-05-29T14:30:00Z",
    },
    {
        "id": 2, "agreement_number": "AGR-2026-0002", "template_id": 2, "agreement_type": "nda",
        "title": "Mutual NDA — MedFirst Health",
        "status": "fully_executed",
        "sender_org_name": "HotGigs MSP", "sender_name": "David Martinez", "sender_email": "david.martinez@hotgigs.com", "sender_designation": "Legal Counsel",
        "recipient_org_name": "MedFirst Health", "recipient_name": "Dr. James Wilson", "recipient_email": "jwilson@medfirst.com", "recipient_designation": "CTO",
        "effective_date": "2025-08-01", "expiry_date": "2027-07-31",
        "contract_value": None, "currency": "USD",
        "sender_signed": True, "sender_signed_at": "2025-07-28T09:00:00Z",
        "recipient_signed": True, "recipient_signed_at": "2025-07-29T16:45:00Z",
        "sent_at": "2025-07-28T09:05:00Z", "completed_at": "2025-07-29T16:45:00Z",
    },
    {
        "id": 3, "agreement_number": "AGR-2026-0015", "template_id": 3, "agreement_type": "sow",
        "title": "SOW — Cloud Migration Project (TechCorp)",
        "status": "pending_signature",
        "sender_org_name": "HotGigs MSP", "sender_name": "Lisa Park", "sender_email": "lisa.park@hotgigs.com", "sender_designation": "VP Operations",
        "recipient_org_name": "TechCorp Inc", "recipient_name": "Mike Johnson", "recipient_email": "mike.j@techcorp.com", "recipient_designation": "Project Director",
        "effective_date": "2026-04-01", "expiry_date": "2026-09-30",
        "contract_value": 485000, "currency": "USD",
        "sender_signed": True, "sender_signed_at": "2026-03-12T11:00:00Z",
        "recipient_signed": False, "recipient_signed_at": None,
        "sent_at": "2026-03-12T11:05:00Z", "completed_at": None,
    },
    {
        "id": 4, "agreement_number": "AGR-2026-0018", "template_id": 4, "agreement_type": "po",
        "title": "PO — StaffPro Q2 Staffing Services",
        "status": "changes_requested",
        "sender_org_name": "HotGigs MSP", "sender_name": "Lisa Park", "sender_email": "lisa.park@hotgigs.com", "sender_designation": "VP Operations",
        "recipient_org_name": "StaffPro Solutions", "recipient_name": "Karen White", "recipient_email": "karen.w@staffpro.com", "recipient_designation": "Account Manager",
        "effective_date": "2026-04-01", "expiry_date": "2026-06-30",
        "contract_value": 225000, "currency": "USD",
        "sender_signed": True, "sender_signed_at": "2026-03-10T14:00:00Z",
        "recipient_signed": False, "recipient_signed_at": None,
        "sent_at": "2026-03-10T14:05:00Z", "completed_at": None,
    },
    {
        "id": 5, "agreement_number": "AGR-2026-0020", "template_id": 5, "agreement_type": "staffing",
        "title": "Staffing Agreement — CodeForce Inc",
        "status": "pending_review",
        "sender_org_name": "HotGigs MSP", "sender_name": "Robert Chen", "sender_email": "robert.chen@hotgigs.com", "sender_designation": "CEO",
        "recipient_org_name": "CodeForce Inc", "recipient_name": "Alex Petrov", "recipient_email": "alex.p@codeforce.io", "recipient_designation": "Director",
        "effective_date": "2026-04-01", "expiry_date": "2027-03-31",
        "contract_value": 1200000, "currency": "USD",
        "sender_signed": False, "sender_signed_at": None,
        "recipient_signed": False, "recipient_signed_at": None,
        "sent_at": None, "completed_at": None,
    },
    {
        "id": 6, "agreement_number": "AGR-2026-0022", "template_id": 2, "agreement_type": "nda",
        "title": "Mutual NDA — BuildRight Construction",
        "status": "draft",
        "sender_org_name": "HotGigs MSP", "sender_name": "David Martinez", "sender_email": "david.martinez@hotgigs.com", "sender_designation": "Legal Counsel",
        "recipient_org_name": "BuildRight Construction", "recipient_name": "Tom Hayes", "recipient_email": "thayes@buildright.com", "recipient_designation": "CEO",
        "effective_date": None, "expiry_date": None,
        "contract_value": None, "currency": "USD",
        "sender_signed": False, "sender_signed_at": None,
        "recipient_signed": False, "recipient_signed_at": None,
        "sent_at": None, "completed_at": None,
    },
]

_mock_change_requests = [
    {
        "id": 1, "agreement_id": 4, "agreement_number": "AGR-2026-0018",
        "requested_by_name": "Karen White", "requested_by_email": "karen.w@staffpro.com",
        "section": "Section 4 — Payment Terms",
        "original_text": "Payment shall be made within 30 days of receipt of invoice.",
        "proposed_text": "Payment shall be made within 45 days of receipt of invoice.",
        "reason": "Our standard payment processing cycle requires 45 days for supplier invoices.",
        "status": "pending", "reviewed_by": None, "reviewed_at": None,
    },
    {
        "id": 2, "agreement_id": 4, "agreement_number": "AGR-2026-0018",
        "requested_by_name": "Karen White", "requested_by_email": "karen.w@staffpro.com",
        "section": "Section 7.2 — Termination Notice",
        "original_text": "Either party may terminate with 30 days written notice.",
        "proposed_text": "Either party may terminate with 60 days written notice.",
        "reason": "We need additional time to transition resources on active assignments.",
        "status": "pending", "reviewed_by": None, "reviewed_at": None,
    },
]

_mock_audit_trail = [
    {"agreement_id": 4, "action": "created", "actor_name": "Lisa Park", "actor_email": "lisa.park@hotgigs.com", "timestamp": "2026-03-10T13:50:00Z"},
    {"agreement_id": 4, "action": "sender_signed", "actor_name": "Lisa Park", "actor_email": "lisa.park@hotgigs.com", "timestamp": "2026-03-10T14:00:00Z", "details": {"auto_signed": True}},
    {"agreement_id": 4, "action": "sent", "actor_name": "System", "actor_email": "system@hotgigs.com", "timestamp": "2026-03-10T14:05:00Z", "details": {"to": "karen.w@staffpro.com"}},
    {"agreement_id": 4, "action": "viewed", "actor_name": "Karen White", "actor_email": "karen.w@staffpro.com", "timestamp": "2026-03-11T09:30:00Z"},
    {"agreement_id": 4, "action": "change_requested", "actor_name": "Karen White", "actor_email": "karen.w@staffpro.com", "timestamp": "2026-03-11T10:15:00Z", "details": {"changes": 2}},
]


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — Signatory Authorities
# ══════════════════════════════════════════════════════════════

@router.get("/signatories")
async def get_signatories():
    return {"items": _mock_signatories, "total": len(_mock_signatories)}

@router.get("/signatories/{signatory_id}")
async def get_signatory(signatory_id: int):
    item = next((s for s in _mock_signatories if s["id"] == signatory_id), None)
    return item or {"error": "Not found"}

@router.post("/signatories")
async def create_signatory(name: str, designation: str, email: str):
    return {"id": 4, "name": name, "designation": designation, "email": email, "created": True}

@router.put("/signatories/{signatory_id}")
async def update_signatory(signatory_id: int):
    return {"id": signatory_id, "updated": True}

@router.delete("/signatories/{signatory_id}")
async def deactivate_signatory(signatory_id: int):
    return {"id": signatory_id, "is_active": False}


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — Template Repository
# ══════════════════════════════════════════════════════════════

@router.get("/templates")
async def get_templates(
    agreement_type: Optional[str] = None,
    category: Optional[str] = None,
    is_active: Optional[bool] = True,
):
    results = _mock_templates
    if agreement_type:
        results = [t for t in results if t["agreement_type"] == agreement_type]
    if category:
        results = [t for t in results if t["category"] == category]
    return {"items": results, "total": len(results)}

@router.get("/templates/{template_id}")
async def get_template(template_id: int):
    item = next((t for t in _mock_templates if t["id"] == template_id), None)
    return item or {"error": "Not found"}

@router.post("/templates")
async def create_template(name: str, agreement_type: str, content_html: str = ""):
    return {"id": 7, "name": name, "agreement_type": agreement_type, "created": True}

@router.put("/templates/{template_id}")
async def update_template(template_id: int):
    return {"id": template_id, "updated": True}

@router.post("/templates/{template_id}/clone")
async def clone_template(template_id: int, new_name: str = ""):
    return {"id": 8, "cloned_from": template_id, "name": new_name or "Clone", "created": True}

@router.delete("/templates/{template_id}")
async def deactivate_template(template_id: int):
    return {"id": template_id, "is_active": False}


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — Agreements
# ══════════════════════════════════════════════════════════════

@router.get("")
async def get_agreements(
    agreement_type: Optional[str] = None,
    status: Optional[str] = None,
    recipient_org: Optional[str] = None,
):
    results = _mock_agreements
    if agreement_type:
        results = [a for a in results if a["agreement_type"] == agreement_type]
    if status:
        results = [a for a in results if a["status"] == status]
    if recipient_org:
        results = [a for a in results if recipient_org.lower() in a.get("recipient_org_name", "").lower()]
    return {"items": results, "total": len(results)}

@router.get("/{agreement_id}")
async def get_agreement(agreement_id: int):
    item = next((a for a in _mock_agreements if a["id"] == agreement_id), None)
    return item or {"error": "Not found"}

@router.post("")
async def create_agreement(template_id: int, title: str, recipient_name: str, recipient_email: str):
    return {"id": 7, "agreement_number": "AGR-2026-0025", "template_id": template_id, "title": title, "status": "draft", "created": True}

@router.post("/from-template")
async def create_from_template(template_id: int, variables: dict = {}):
    """Generate agreement from template with filled variables."""
    template = next((t for t in _mock_templates if t["id"] == template_id), None)
    if not template:
        return {"error": "Template not found"}
    return {
        "id": 8, "agreement_number": "AGR-2026-0026",
        "template_id": template_id, "template_name": template["name"],
        "agreement_type": template["agreement_type"],
        "status": "draft", "variables_applied": variables, "created": True,
    }

@router.put("/{agreement_id}")
async def update_agreement(agreement_id: int):
    return {"id": agreement_id, "updated": True}


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — Signing Workflow
# ══════════════════════════════════════════════════════════════

@router.post("/{agreement_id}/send")
async def send_agreement(agreement_id: int, signatory_id: Optional[int] = None, auto_sign_sender: bool = True):
    """Send agreement for signature. Auto-signs sender if configured."""
    agreement = next((a for a in _mock_agreements if a["id"] == agreement_id), None)
    if not agreement:
        return {"error": "Not found"}
    return {
        "id": agreement_id,
        "status": "pending_signature",
        "sender_auto_signed": auto_sign_sender,
        "signatory_used": signatory_id or "default",
        "sent_to": agreement["recipient_email"],
        "sent_at": datetime.utcnow().isoformat(),
    }

@router.post("/{agreement_id}/sign-sender")
async def sign_as_sender(agreement_id: int, signatory_id: int):
    """Manually sign as sender using specific signatory authority."""
    return {"id": agreement_id, "sender_signed": True, "signatory_id": signatory_id, "signed_at": datetime.utcnow().isoformat()}

@router.post("/{agreement_id}/sign-recipient")
async def sign_as_recipient(agreement_id: int, signatory_name: Optional[str] = None, signatory_designation: Optional[str] = None):
    """Recipient signs the agreement. Can use existing or provide new signatory details."""
    return {
        "id": agreement_id,
        "recipient_signed": True,
        "signatory_name": signatory_name or "Default Signatory",
        "signatory_designation": signatory_designation or "Authorized Signatory",
        "signed_at": datetime.utcnow().isoformat(),
        "status": "fully_executed",
    }

@router.post("/{agreement_id}/void")
async def void_agreement(agreement_id: int, reason: str = ""):
    return {"id": agreement_id, "status": "voided", "reason": reason}


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — Change Requests
# ══════════════════════════════════════════════════════════════

@router.get("/{agreement_id}/change-requests")
async def get_change_requests(agreement_id: int):
    results = [cr for cr in _mock_change_requests if cr["agreement_id"] == agreement_id]
    return {"items": results, "total": len(results)}

@router.post("/{agreement_id}/change-requests")
async def create_change_request(agreement_id: int, section: str = "", proposed_text: str = "", reason: str = ""):
    return {"id": 3, "agreement_id": agreement_id, "section": section, "status": "pending", "created": True}

@router.put("/change-requests/{request_id}/accept")
async def accept_change_request(request_id: int, notes: str = ""):
    return {"id": request_id, "status": "accepted", "reviewed_at": datetime.utcnow().isoformat()}

@router.put("/change-requests/{request_id}/reject")
async def reject_change_request(request_id: int, notes: str = ""):
    return {"id": request_id, "status": "rejected", "reviewed_at": datetime.utcnow().isoformat()}


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — Audit Trail
# ══════════════════════════════════════════════════════════════

@router.get("/{agreement_id}/audit-trail")
async def get_audit_trail(agreement_id: int):
    results = [a for a in _mock_audit_trail if a["agreement_id"] == agreement_id]
    return {"items": results, "total": len(results)}


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — Dashboard & Analytics
# ══════════════════════════════════════════════════════════════

@router.get("/stats/dashboard")
async def get_agreement_dashboard():
    return {
        "total_agreements": 22,
        "by_status": {
            "draft": 3, "pending_review": 2, "changes_requested": 1,
            "pending_signature": 4, "partially_signed": 1,
            "fully_executed": 8, "active": 2, "expired": 1,
        },
        "by_type": {
            "msa": 5, "nda": 6, "sow": 4, "po": 3,
            "staffing": 2, "non_compete": 1, "custom": 1,
        },
        "templates": {"total": 6, "active": 6, "most_used": "Mutual NDA (38 uses)"},
        "signatories": {"total": 3, "active": 3},
        "signing_metrics": {
            "avg_time_to_sign_hours": 28.5,
            "completion_rate": 87.5,
            "change_request_rate": 12.5,
        },
        "recent_activity": [
            {"action": "change_requested", "agreement": "AGR-2026-0018", "by": "Karen White", "at": "2026-03-11T10:15:00Z"},
            {"action": "sent", "agreement": "AGR-2026-0015", "by": "Lisa Park", "at": "2026-03-12T11:05:00Z"},
            {"action": "drafted", "agreement": "AGR-2026-0022", "by": "David Martinez", "at": "2026-03-13T09:00:00Z"},
        ],
        "expiring_soon": [
            {"agreement_number": "AGR-2026-0001", "title": "MSA — TechCorp Inc", "expiry_date": "2026-05-31", "days_remaining": 78},
        ],
    }
