"""Email Agent API — classification, drafting, summarization, and inbox management."""
from datetime import datetime, date, timedelta
from fastapi import APIRouter, Query
from typing import Optional

router = APIRouter(prefix="/email-agent")


# ══════════════════════════════════════════════════════════════
#  MOCK DATA
# ══════════════════════════════════════════════════════════════

_mock_emails = [
    {
        "id": 1, "from_address": "sarah.johnson@techcorp.com", "from_name": "Sarah Johnson",
        "to_addresses": [{"email": "recruiter@hotgigs.com", "name": "Jane Recruiter"}],
        "cc_addresses": [], "subject": "URGENT: Need Java Developer by Friday - SLA at risk",
        "body_text": "Hi Jane, we urgently need a senior Java developer. Our SLA deadline is this Friday. Please escalate this requirement immediately.",
        "received_at": "2026-03-13T08:15:00Z", "is_read": False, "has_attachments": False,
        "attachment_count": 0, "classification": "escalation_urgent", "priority": "critical",
        "confidence_score": 0.96, "ai_summary": "TechCorp client urgently needs a senior Java developer by Friday due to SLA risk. Immediate escalation and action required.",
        "requires_response": True, "is_user_in_cc_only": False, "sentiment": "urgent",
        "classification_tags": ["escalation", "requirement", "SLA"], "draft_generated": True,
        "alert_sent": True, "resume_processed": False, "action_items_extracted": True,
    },
    {
        "id": 2, "from_address": "apply+candidate@jobs.linkedin.com", "from_name": "LinkedIn Jobs",
        "to_addresses": [{"email": "recruiting@hotgigs.com", "name": "HotGigs Recruiting"}],
        "cc_addresses": [], "subject": "New application: Priya Sharma applied for Senior Python Developer",
        "body_text": "Priya Sharma has applied for your Senior Python Developer position. View profile and resume attached.",
        "received_at": "2026-03-13T07:30:00Z", "is_read": False, "has_attachments": True,
        "attachment_count": 1, "attachments_meta": [{"filename": "PriyaSharma_Resume.pdf", "size": 245000, "mime": "application/pdf"}],
        "classification": "candidate_application", "priority": "high",
        "confidence_score": 0.98, "ai_summary": "Priya Sharma applied for Senior Python Developer via LinkedIn. Resume attached — 8 years experience with Python, Django, AWS. Strong match potential.",
        "requires_response": False, "is_user_in_cc_only": False, "sentiment": "positive",
        "classification_tags": ["recruitment", "candidate", "resume"], "draft_generated": False,
        "alert_sent": False, "resume_processed": True, "action_items_extracted": False,
    },
    {
        "id": 3, "from_address": "michael.chen@staffpro.com", "from_name": "Michael Chen",
        "to_addresses": [{"email": "recruiter@hotgigs.com", "name": "Jane Recruiter"}],
        "cc_addresses": [{"email": "admin@hotgigs.com", "name": "Admin"}],
        "subject": "Re: Interview Schedule for Amit Patel - Data Engineer Position",
        "body_text": "Hi Jane, Amit is available for the technical interview on Tuesday 3pm or Wednesday 10am. Please confirm with the client hiring manager.",
        "received_at": "2026-03-13T06:45:00Z", "is_read": True, "has_attachments": False,
        "attachment_count": 0, "classification": "interview_request", "priority": "medium",
        "confidence_score": 0.92, "ai_summary": "StaffPro supplier confirming candidate Amit Patel availability for Data Engineer interview — Tuesday 3pm or Wednesday 10am. Client confirmation needed.",
        "requires_response": True, "is_user_in_cc_only": False, "sentiment": "neutral",
        "classification_tags": ["interview", "scheduling"], "draft_generated": True,
        "alert_sent": False, "resume_processed": False, "action_items_extracted": True,
    },
    {
        "id": 4, "from_address": "noreply@techcorp.com", "from_name": "TechCorp HR",
        "to_addresses": [{"email": "hr-team@hotgigs.com", "name": "HotGigs HR Team"}],
        "cc_addresses": [{"email": "recruiter@hotgigs.com", "name": "Jane Recruiter"}],
        "subject": "Meeting Notes: Q1 Workforce Planning Review - Action Items Inside",
        "body_text": "Attached are the minutes from yesterday's Q1 Workforce Planning Review.\n\nKey Action Items:\n1. [Jane/MSP] Submit 5 additional .NET developers by March 20 - ESCALATED\n2. [Michael/StaffPro] Complete BGC for Vikram Singh by March 15\n3. [Sarah/TechCorp] Approve revised rate card for Data Engineering roles by March 18\n4. [All] Update placement forecasts in the system by EOW\n\nNext meeting: March 20, 2026 at 2pm EST.",
        "received_at": "2026-03-12T17:00:00Z", "is_read": True, "has_attachments": True,
        "attachment_count": 1, "classification": "meeting_minutes", "priority": "high",
        "confidence_score": 0.95, "ai_summary": "Q1 Workforce Planning MOM with 4 action items. Escalated: submit 5 .NET devs by March 20. Other items: BGC completion, rate card approval, forecast updates.",
        "requires_response": False, "is_user_in_cc_only": True, "sentiment": "neutral",
        "classification_tags": ["mom", "action_items", "escalation"], "draft_generated": False,
        "alert_sent": True, "resume_processed": False, "action_items_extracted": True,
    },
    {
        "id": 5, "from_address": "amit.patel@gmail.com", "from_name": "Amit Patel",
        "to_addresses": [{"email": "recruiting@hotgigs.com", "name": "HotGigs Recruiting"}],
        "cc_addresses": [], "subject": "Application for React Native Developer Position",
        "body_text": "Dear Hiring Team, I am writing to express my interest in the React Native Developer position. Please find my resume attached. I have 5+ years of experience in mobile development.",
        "received_at": "2026-03-13T05:20:00Z", "is_read": False, "has_attachments": True,
        "attachment_count": 1, "attachments_meta": [{"filename": "AmitPatel_CV.pdf", "size": 198000, "mime": "application/pdf"}],
        "classification": "candidate_application", "priority": "medium",
        "confidence_score": 0.97, "ai_summary": "Direct application from Amit Patel for React Native Developer. 5+ years mobile experience. Resume attached for parsing.",
        "requires_response": True, "is_user_in_cc_only": False, "sentiment": "positive",
        "classification_tags": ["recruitment", "candidate", "resume", "direct_application"],
        "draft_generated": True, "alert_sent": False, "resume_processed": True, "action_items_extracted": False,
    },
    {
        "id": 6, "from_address": "sarah.johnson@techcorp.com", "from_name": "Sarah Johnson",
        "to_addresses": [{"email": "recruiter@hotgigs.com", "name": "Jane Recruiter"}, {"email": "michael@staffpro.com", "name": "Michael Chen"}],
        "cc_addresses": [{"email": "admin@hotgigs.com", "name": "Admin"}],
        "subject": "Re: Onboarding Checklist for Rajesh Kumar - Start Date March 17",
        "body_text": "Team, please ensure all onboarding items are completed before Rajesh's start date on March 17:\n- Laptop and badge ready (Client IT)\n- VPN access provisioned (Client IT)\n- BGC cleared (StaffPro to confirm)\n- NDA signed (MSP to coordinate)\n- First week schedule sent to candidate",
        "received_at": "2026-03-12T14:30:00Z", "is_read": True, "has_attachments": False,
        "attachment_count": 0, "classification": "onboarding_related", "priority": "high",
        "confidence_score": 0.93, "ai_summary": "Onboarding checklist for Rajesh Kumar starting March 17. Multiple action items across Client IT, StaffPro (BGC), and MSP (NDA). Deadline in 4 days.",
        "requires_response": True, "is_user_in_cc_only": False, "sentiment": "neutral",
        "classification_tags": ["onboarding", "action_items", "deadline"], "draft_generated": True,
        "alert_sent": False, "resume_processed": False, "action_items_extracted": True,
    },
    {
        "id": 7, "from_address": "hr-newsletter@techcorp.com", "from_name": "TechCorp Newsletter",
        "to_addresses": [{"email": "partners@techcorp.com", "name": "TechCorp Partners"}],
        "cc_addresses": [{"email": "recruiter@hotgigs.com", "name": "Jane Recruiter"}],
        "subject": "TechCorp Q1 2026 Hiring Update & Technology Roadmap",
        "body_text": "Quarterly update on TechCorp's hiring plans and technology initiatives for Q1 2026...",
        "received_at": "2026-03-11T10:00:00Z", "is_read": True, "has_attachments": False,
        "attachment_count": 0, "classification": "fyi_cc", "priority": "low",
        "confidence_score": 0.89, "ai_summary": "TechCorp quarterly newsletter with hiring plans and tech roadmap. FYI only — no immediate action needed. Key insight: expanding cloud engineering team in Q2.",
        "requires_response": False, "is_user_in_cc_only": True, "sentiment": "positive",
        "classification_tags": ["newsletter", "fyi", "hiring_forecast"], "draft_generated": False,
        "alert_sent": False, "resume_processed": False, "action_items_extracted": False,
    },
    {
        "id": 8, "from_address": "michael.chen@staffpro.com", "from_name": "Michael Chen",
        "to_addresses": [{"email": "recruiter@hotgigs.com", "name": "Jane Recruiter"}],
        "cc_addresses": [], "subject": "Interview Reschedule Request - Vikram Singh",
        "body_text": "Hi Jane, Vikram Singh needs to reschedule his Wednesday interview due to a family emergency. Can we move it to Thursday or Friday same time?",
        "received_at": "2026-03-13T09:00:00Z", "is_read": False, "has_attachments": False,
        "attachment_count": 0, "classification": "interview_reschedule", "priority": "high",
        "confidence_score": 0.94, "ai_summary": "StaffPro supplier requesting interview reschedule for Vikram Singh from Wednesday to Thursday/Friday due to family emergency. Prompt response needed.",
        "requires_response": True, "is_user_in_cc_only": False, "sentiment": "neutral",
        "classification_tags": ["interview", "reschedule", "time_sensitive"],
        "draft_generated": True, "alert_sent": False, "resume_processed": False, "action_items_extracted": True,
    },
]

_mock_drafts = [
    {
        "id": 1, "email_message_id": 1, "draft_subject": "Re: URGENT: Need Java Developer by Friday - SLA at risk",
        "draft_body": "Hi Sarah,\n\nThank you for flagging this urgently. I've escalated this requirement to our senior recruitment team and we're prioritizing it immediately.\n\nHere's our action plan:\n1. Screening our existing talent pool for qualified Java developers (Senior level)\n2. Distributing to our top-tier supplier network within the hour\n3. Targeting first submissions by tomorrow EOD\n\nI'll provide a status update by tomorrow morning. Please let me know if there are any specific certifications or technical requirements beyond what's in the original JD.\n\nBest regards,\nJane",
        "draft_tone": "urgent", "status": "generated",
        "ai_reasoning": "Client escalation with SLA risk — tone set to urgent with concrete action plan to demonstrate responsiveness and commitment.",
        "confidence_score": 0.91, "created_at": "2026-03-13T08:16:00Z",
    },
    {
        "id": 2, "email_message_id": 3, "draft_subject": "Re: Interview Schedule for Amit Patel - Data Engineer Position",
        "draft_body": "Hi Michael,\n\nThank you for confirming Amit's availability. I'll coordinate with the TechCorp hiring manager and confirm the slot.\n\nProposed options:\n- Tuesday, March 17 at 3:00 PM EST\n- Wednesday, March 18 at 10:00 AM EST\n\nI'll send the calendar invite once confirmed. Please ensure Amit has the video conferencing link and interview prep materials.\n\nBest,\nJane",
        "draft_tone": "professional", "status": "generated",
        "ai_reasoning": "Scheduling coordination email — professional tone, reaffirmed options, and added helpful reminder about prep materials.",
        "confidence_score": 0.88, "created_at": "2026-03-13T06:46:00Z",
    },
    {
        "id": 3, "email_message_id": 5, "draft_subject": "Re: Application for React Native Developer Position",
        "draft_body": "Dear Amit,\n\nThank you for your interest in the React Native Developer position and for sharing your resume.\n\nWe've received your application and our recruitment team is reviewing your profile. Given your 5+ years of mobile development experience, we'd like to learn more about your background.\n\nA member of our team will reach out within 2 business days to discuss next steps.\n\nBest regards,\nHotGigs Recruiting Team",
        "draft_tone": "friendly", "status": "generated",
        "ai_reasoning": "Candidate application acknowledgment — warm, encouraging tone. Mentioned their experience to show personalization. Set clear timeline expectation.",
        "confidence_score": 0.93, "created_at": "2026-03-13T05:21:00Z",
    },
    {
        "id": 4, "email_message_id": 6, "draft_subject": "Re: Onboarding Checklist for Rajesh Kumar - Start Date March 17",
        "draft_body": "Hi Sarah,\n\nThank you for the onboarding checklist. Here's the MSP status update:\n\n- NDA: Will be sent to Rajesh today for signature (targeting completion by March 14)\n- BGC: Coordinating with StaffPro — Michael, can you confirm BGC clearance status?\n- Laptop/Badge/VPN: Please confirm Client IT has these in progress\n- First week schedule: We'll send this to Rajesh once all items are confirmed\n\nI'll track all items and provide a final status update on March 15.\n\nBest,\nJane",
        "draft_tone": "professional", "status": "generated",
        "ai_reasoning": "Onboarding coordination response — addressed each checklist item with status, delegated to appropriate parties, and set follow-up date.",
        "confidence_score": 0.90, "created_at": "2026-03-12T14:31:00Z",
    },
    {
        "id": 5, "email_message_id": 8, "draft_subject": "Re: Interview Reschedule Request - Vikram Singh",
        "draft_body": "Hi Michael,\n\nUnderstood, I hope everything is okay with Vikram's family. I'll reach out to the TechCorp hiring manager to reschedule.\n\nI'll aim for:\n- Thursday, March 19 at the same time\n- Friday, March 20 as backup\n\nWill confirm the new slot by end of today.\n\nBest,\nJane",
        "draft_tone": "empathetic", "status": "generated",
        "ai_reasoning": "Reschedule due to family emergency — empathetic tone, quick acknowledgment, proactive rescheduling with clear timeline.",
        "confidence_score": 0.92, "created_at": "2026-03-13T09:01:00Z",
    },
]

_mock_summaries = [
    {
        "id": 1, "summary_date": "2026-03-13", "summary_type": "daily",
        "total_emails": 8, "action_required_count": 4, "fyi_count": 2,
        "escalation_count": 1, "recruitment_count": 2,
        "summary_text": "Today's inbox: 8 emails — 1 critical escalation (Java developer SLA risk from TechCorp), 2 candidate applications (Priya Sharma via LinkedIn, Amit Patel direct), 1 interview reschedule (Vikram Singh), 1 onboarding coordination (Rajesh Kumar), 1 MOM with 4 action items. 2 FYI/newsletter emails summarized.",
        "topic_clusters": {"recruitment": 2, "scheduling": 2, "escalation": 1, "onboarding": 1, "newsletter": 1, "mom": 1},
    }
]


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — Email Inbox & Classification
# ══════════════════════════════════════════════════════════════

@router.get("/inbox")
async def get_inbox(
    classification: Optional[str] = None,
    priority: Optional[str] = None,
    requires_response: Optional[bool] = None,
    is_read: Optional[bool] = None,
    date_from: Optional[str] = None,
    limit: int = Query(default=50, le=200),
    offset: int = 0,
):
    """Get email inbox with AI classification and filtering."""
    results = _mock_emails
    if classification:
        results = [e for e in results if e["classification"] == classification]
    if priority:
        results = [e for e in results if e["priority"] == priority]
    if requires_response is not None:
        results = [e for e in results if e["requires_response"] == requires_response]
    if is_read is not None:
        results = [e for e in results if e["is_read"] == is_read]
    return {"items": results[offset:offset+limit], "total": len(results)}


@router.get("/inbox/{email_id}")
async def get_email_detail(email_id: int):
    """Get full email detail with classification, summary, and related items."""
    email = next((e for e in _mock_emails if e["id"] == email_id), None)
    if not email:
        return {"error": "Email not found"}
    drafts = [d for d in _mock_drafts if d["email_message_id"] == email_id]
    return {**email, "drafts": drafts, "action_items_count": 1 if email.get("action_items_extracted") else 0}


@router.post("/classify")
async def classify_emails(email_ids: list[int] = []):
    """Run AI classification on specified emails (or all unclassified)."""
    classified = []
    for eid in (email_ids or [e["id"] for e in _mock_emails]):
        email = next((e for e in _mock_emails if e["id"] == eid), None)
        if email:
            classified.append({
                "email_id": eid, "classification": email.get("classification", "general"),
                "priority": email.get("priority", "medium"), "confidence": email.get("confidence_score", 0.85),
                "summary": email.get("ai_summary", ""), "requires_response": email.get("requires_response", False),
            })
    return {"classified": classified, "total": len(classified)}


@router.post("/classify/{email_id}/override")
async def override_classification(email_id: int, classification: str, priority: Optional[str] = None):
    """Manually override AI classification for an email."""
    return {"email_id": email_id, "classification": classification, "priority": priority, "overridden": True}


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — Draft Responses
# ══════════════════════════════════════════════════════════════

@router.get("/drafts")
async def get_drafts(status: Optional[str] = None, limit: int = 50):
    """Get all AI-generated draft responses."""
    results = _mock_drafts
    if status:
        results = [d for d in results if d["status"] == status]
    return {"items": results[:limit], "total": len(results)}


@router.get("/drafts/{draft_id}")
async def get_draft(draft_id: int):
    """Get a specific draft with AI reasoning."""
    draft = next((d for d in _mock_drafts if d["id"] == draft_id), None)
    if not draft:
        return {"error": "Draft not found"}
    email = next((e for e in _mock_emails if e["id"] == draft["email_message_id"]), None)
    return {**draft, "original_email": email}


@router.post("/drafts/generate/{email_id}")
async def generate_draft(email_id: int, tone: str = "professional"):
    """Generate an AI draft response for a specific email."""
    email = next((e for e in _mock_emails if e["id"] == email_id), None)
    if not email:
        return {"error": "Email not found"}
    return {
        "id": 100, "email_message_id": email_id,
        "draft_subject": f"Re: {email['subject']}",
        "draft_body": f"Thank you for your email regarding '{email['subject']}'. I'll review and respond promptly.",
        "draft_tone": tone, "status": "generated",
        "ai_reasoning": f"Auto-generated {tone} response for {email['classification']} email.",
        "confidence_score": 0.85,
    }


@router.put("/drafts/{draft_id}")
async def update_draft(draft_id: int, edited_body: Optional[str] = None, status: Optional[str] = None):
    """Update/edit a draft before sending."""
    return {"id": draft_id, "status": status or "edited", "updated": True}


@router.post("/drafts/{draft_id}/send")
async def send_draft(draft_id: int):
    """Send an approved draft as an email reply."""
    return {"id": draft_id, "status": "sent", "sent_at": datetime.utcnow().isoformat()}


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — Email Summaries
# ══════════════════════════════════════════════════════════════

@router.get("/summaries")
async def get_summaries(summary_type: str = "daily", limit: int = 7):
    """Get daily/weekly email summaries."""
    return {"items": _mock_summaries[:limit], "total": len(_mock_summaries)}


@router.post("/summaries/generate")
async def generate_summary(summary_type: str = "daily", target_date: Optional[str] = None):
    """Generate a new email summary for a given date."""
    return _mock_summaries[0]


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — Agent Configuration
# ══════════════════════════════════════════════════════════════

@router.get("/config")
async def get_agent_config():
    """Get email agent configuration."""
    return {
        "is_enabled": True, "auto_classify": True, "auto_draft_responses": True,
        "auto_process_resumes": True, "auto_extract_action_items": True,
        "auto_alert_escalations": True, "daily_summary_enabled": True,
        "daily_summary_time": "09:00",
        "escalation_keywords": ["urgent", "asap", "escalation", "immediately", "critical", "SLA breach", "overdue"],
        "recruitment_email_patterns": ["*@jobs.linkedin.com", "*@apply.indeed.com", "applications@*"],
        "max_drafts_per_day": 50,
    }


@router.put("/config")
async def update_agent_config():
    """Update email agent configuration."""
    return {"updated": True, "message": "Email agent configuration updated successfully"}


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — Dashboard
# ══════════════════════════════════════════════════════════════

@router.get("/dashboard")
async def get_dashboard():
    """Get email agent dashboard with KPIs and recent activity."""
    return {
        "total_emails_today": 8, "action_required": 4, "escalations": 1,
        "fyi_emails": 2, "resumes_captured": 2, "drafts_generated": 5,
        "action_items_pending": 7, "alerts_sent_today": 3,
        "classification_breakdown": {
            "escalation_urgent": 1, "candidate_application": 2, "interview_request": 1,
            "interview_reschedule": 1, "onboarding_related": 1, "meeting_minutes": 1, "fyi_cc": 1,
        },
        "priority_breakdown": {"critical": 1, "high": 3, "medium": 2, "low": 1, "fyi": 1},
        "top_senders": [
            {"name": "Sarah Johnson", "email": "sarah.johnson@techcorp.com", "count": 2, "org": "TechCorp"},
            {"name": "Michael Chen", "email": "michael.chen@staffpro.com", "count": 2, "org": "StaffPro"},
        ],
        "recent_escalations": [
            {"subject": "URGENT: Need Java Developer by Friday", "from": "Sarah Johnson", "priority": "critical", "time": "08:15 AM"},
        ],
        "response_rate": 0.85, "avg_response_time_hours": 1.2,
        "resumes_this_week": 12, "match_rate": 0.68,
    }


@router.get("/accounts")
async def get_email_accounts():
    """Get connected email accounts."""
    return {"items": [
        {"id": 1, "email_address": "recruiter@hotgigs.com", "provider": "gmail", "is_active": True,
         "last_synced_at": "2026-03-13T09:30:00Z", "auto_classify": True, "auto_draft": True},
        {"id": 2, "email_address": "recruiting@hotgigs.com", "provider": "gmail", "is_active": True,
         "last_synced_at": "2026-03-13T09:30:00Z", "auto_classify": True, "auto_draft": False},
    ]}


@router.post("/accounts")
async def connect_email_account():
    """Connect a new email account for monitoring."""
    return {"id": 3, "status": "connected", "message": "Email account connected. Initial sync in progress."}


@router.post("/sync")
async def trigger_sync(account_id: Optional[int] = None):
    """Trigger manual email sync."""
    return {"status": "syncing", "account_id": account_id, "message": "Email sync initiated"}
