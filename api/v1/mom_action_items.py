"""MOM Action Items API — extract action items from meeting minutes, track, escalate, follow-up."""
from datetime import datetime, date
from fastapi import APIRouter, Query
from typing import Optional

router = APIRouter(prefix="/mom-actions")


# ══════════════════════════════════════════════════════════════
#  MOCK DATA
# ══════════════════════════════════════════════════════════════

_mock_moms = [
    {
        "id": 1, "email_message_id": 4,
        "meeting_title": "Q1 Workforce Planning Review",
        "meeting_date": "2026-03-12",
        "attendees": [
            {"name": "Sarah Johnson", "email": "sarah.johnson@techcorp.com", "role": "Client Manager"},
            {"name": "Jane Recruiter", "email": "recruiter@hotgigs.com", "role": "MSP Recruiter"},
            {"name": "Michael Chen", "email": "michael.chen@staffpro.com", "role": "Supplier Account Manager"},
            {"name": "Admin User", "email": "admin@hotgigs.com", "role": "MSP Admin"},
        ],
        "key_decisions": [
            "Expand .NET team size from 3 to 8 for Q2 project ramp",
            "Approved revised Data Engineering rate card ($90-$160/hr)",
            "Moved BGC provider from Sterling to HireRight for cost savings",
            "Q2 forecast: 15 additional contractors needed across 4 positions",
        ],
        "discussion_topics": [
            "Q1 performance review: 94% fill rate, 98% SLA compliance",
            "Q2 hiring forecast and budget allocation",
            "Supplier performance rankings and tier adjustments",
            "Background check process improvements",
        ],
        "summary": "Q1 performance strong at 94% fill rate. Major Q2 initiative: expand .NET team to 8 (currently 3). Rate card for Data Engineering approved. BGC vendor switch to HireRight. 15 new contractors forecasted for Q2.",
        "next_meeting_date": "2026-03-20T14:00:00Z",
        "total_action_items": 4, "escalated_items_count": 1,
    },
    {
        "id": 2, "email_message_id": None,
        "meeting_title": "Weekly Recruitment Stand-up",
        "meeting_date": "2026-03-11",
        "attendees": [
            {"name": "Jane Recruiter", "email": "recruiter@hotgigs.com", "role": "MSP Recruiter"},
            {"name": "Admin User", "email": "admin@hotgigs.com", "role": "MSP Admin"},
            {"name": "Tom Wilson", "email": "tom@hotgigs.com", "role": "Senior Recruiter"},
        ],
        "key_decisions": [
            "Prioritize TechCorp Java Developer requirement (SLA critical)",
            "Start sourcing for Q2 .NET developer pipeline",
            "Implement new resume scoring model for better match accuracy",
        ],
        "discussion_topics": [
            "Open requirements status update",
            "Submission pipeline review",
            "Interview feedback aggregation",
            "Q2 pipeline preparation",
        ],
        "summary": "Weekly standup focused on prioritizing TechCorp Java Developer (SLA critical), Q2 .NET pipeline preparation, and new resume scoring model rollout.",
        "next_meeting_date": "2026-03-18T10:00:00Z",
        "total_action_items": 3, "escalated_items_count": 0,
    },
]

_mock_action_items = [
    {
        "id": 1, "meeting_minutes_id": 1, "email_message_id": 4,
        "source": "mom_document", "title": "Submit 5 additional .NET developers by March 20",
        "description": "Per Q1 Workforce Planning Review — expand .NET team from 3 to 8 for Q2 project ramp. Source and submit 5 qualified .NET developers.",
        "assigned_to_name": "Jane Recruiter", "assigned_to_email": "recruiter@hotgigs.com",
        "assigned_to_user_id": 2, "assigned_by_name": "Sarah Johnson",
        "due_date": "2026-03-20", "priority": "critical", "status": "in_progress",
        "is_escalation": True, "escalation_reason": "Q2 project start date is April 1 — team must be assembled before then",
        "follow_up_count": 1, "last_follow_up_at": "2026-03-13T09:00:00Z",
        "alert_sent": True, "related_entity_type": "requirement", "related_entity_id": 1055,
    },
    {
        "id": 2, "meeting_minutes_id": 1, "email_message_id": 4,
        "source": "mom_document", "title": "Complete BGC for Vikram Singh by March 15",
        "description": "StaffPro to complete background check for Vikram Singh through HireRight.",
        "assigned_to_name": "Michael Chen", "assigned_to_email": "michael.chen@staffpro.com",
        "assigned_to_user_id": 4, "assigned_by_name": "Jane Recruiter",
        "due_date": "2026-03-15", "priority": "high", "status": "in_progress",
        "is_escalation": False, "escalation_reason": None,
        "follow_up_count": 0, "last_follow_up_at": None,
        "alert_sent": True, "related_entity_type": "candidate", "related_entity_id": 847,
    },
    {
        "id": 3, "meeting_minutes_id": 1, "email_message_id": 4,
        "source": "mom_document", "title": "Approve revised rate card for Data Engineering roles by March 18",
        "description": "TechCorp to approve the updated rate card: $90-$160/hr for Data Engineering roles.",
        "assigned_to_name": "Sarah Johnson", "assigned_to_email": "sarah.johnson@techcorp.com",
        "assigned_to_user_id": 3, "assigned_by_name": "Admin User",
        "due_date": "2026-03-18", "priority": "medium", "status": "pending",
        "is_escalation": False, "escalation_reason": None,
        "follow_up_count": 0, "last_follow_up_at": None,
        "alert_sent": False, "related_entity_type": "rate_card", "related_entity_id": 2,
    },
    {
        "id": 4, "meeting_minutes_id": 1, "email_message_id": 4,
        "source": "mom_document", "title": "Update placement forecasts in the system by end of week",
        "description": "All team members to update their Q2 placement forecasts in the HotGigs platform.",
        "assigned_to_name": "All Team Members", "assigned_to_email": None,
        "assigned_to_user_id": None, "assigned_by_name": "Sarah Johnson",
        "due_date": "2026-03-14", "priority": "medium", "status": "pending",
        "is_escalation": False, "escalation_reason": None,
        "follow_up_count": 0, "last_follow_up_at": None,
        "alert_sent": False, "related_entity_type": None, "related_entity_id": None,
    },
    {
        "id": 5, "meeting_minutes_id": 2, "email_message_id": None,
        "source": "mom_document", "title": "Source 10 .NET developer profiles for Q2 pipeline",
        "description": "Start building pipeline for Q2 .NET developer needs. Target: 10 qualified profiles by March 18.",
        "assigned_to_name": "Tom Wilson", "assigned_to_email": "tom@hotgigs.com",
        "assigned_to_user_id": None, "assigned_by_name": "Admin User",
        "due_date": "2026-03-18", "priority": "high", "status": "pending",
        "is_escalation": False, "escalation_reason": None,
        "follow_up_count": 0, "last_follow_up_at": None,
        "alert_sent": True, "related_entity_type": "requirement", "related_entity_id": 1055,
    },
    {
        "id": 6, "meeting_minutes_id": None, "email_message_id": 6,
        "source": "email_body", "title": "Send NDA to Rajesh Kumar for signature",
        "description": "MSP to coordinate NDA signing for Rajesh Kumar before his March 17 start date.",
        "assigned_to_name": "Jane Recruiter", "assigned_to_email": "recruiter@hotgigs.com",
        "assigned_to_user_id": 2, "assigned_by_name": "Sarah Johnson",
        "due_date": "2026-03-14", "priority": "high", "status": "pending",
        "is_escalation": False, "escalation_reason": None,
        "follow_up_count": 0, "last_follow_up_at": None,
        "alert_sent": False, "related_entity_type": "candidate", "related_entity_id": 845,
    },
    {
        "id": 7, "meeting_minutes_id": None, "email_message_id": 8,
        "source": "email_body", "title": "Reschedule Vikram Singh interview to Thursday/Friday",
        "description": "Coordinate with TechCorp hiring manager to reschedule Vikram Singh's interview from Wednesday to Thursday or Friday.",
        "assigned_to_name": "Jane Recruiter", "assigned_to_email": "recruiter@hotgigs.com",
        "assigned_to_user_id": 2, "assigned_by_name": "Michael Chen",
        "due_date": "2026-03-13", "priority": "high", "status": "pending",
        "is_escalation": False, "escalation_reason": None,
        "follow_up_count": 0, "last_follow_up_at": None,
        "alert_sent": False, "related_entity_type": "interview", "related_entity_id": 223,
    },
]


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — Meeting Minutes
# ══════════════════════════════════════════════════════════════

@router.get("/meetings")
async def get_meeting_minutes(limit: int = Query(default=20, le=100)):
    """Get all extracted meeting minutes."""
    return {"items": _mock_moms[:limit], "total": len(_mock_moms)}


@router.get("/meetings/{mom_id}")
async def get_meeting_detail(mom_id: int):
    """Get full meeting minutes with action items."""
    mom = next((m for m in _mock_moms if m["id"] == mom_id), None)
    if not mom:
        return {"error": "Meeting minutes not found"}
    actions = [a for a in _mock_action_items if a.get("meeting_minutes_id") == mom_id]
    return {**mom, "action_items": actions}


@router.post("/meetings/extract/{email_id}")
async def extract_mom_from_email(email_id: int):
    """Extract meeting minutes and action items from an email."""
    return {
        "email_id": email_id, "meeting_minutes_id": 3,
        "action_items_extracted": 2,
        "message": "Meeting minutes extracted and action items created successfully",
    }


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — Action Items
# ══════════════════════════════════════════════════════════════

@router.get("/actions")
async def get_action_items(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assigned_to_user_id: Optional[int] = None,
    is_escalation: Optional[bool] = None,
    source: Optional[str] = None,
    overdue_only: bool = False,
    limit: int = Query(default=50, le=200),
):
    """Get action items with filters."""
    results = _mock_action_items
    if status:
        results = [a for a in results if a["status"] == status]
    if priority:
        results = [a for a in results if a["priority"] == priority]
    if assigned_to_user_id:
        results = [a for a in results if a.get("assigned_to_user_id") == assigned_to_user_id]
    if is_escalation is not None:
        results = [a for a in results if a["is_escalation"] == is_escalation]
    if source:
        results = [a for a in results if a["source"] == source]
    if overdue_only:
        today = date.today().isoformat()
        results = [a for a in results if a.get("due_date") and a["due_date"] < today and a["status"] not in ("completed",)]
    return {"items": results[:limit], "total": len(results)}


@router.get("/actions/{action_id}")
async def get_action_item(action_id: int):
    """Get a specific action item with context."""
    action = next((a for a in _mock_action_items if a["id"] == action_id), None)
    if not action:
        return {"error": "Action item not found"}
    mom = next((m for m in _mock_moms if m["id"] == action.get("meeting_minutes_id")), None)
    return {**action, "meeting": mom}


@router.put("/actions/{action_id}/status")
async def update_action_status(action_id: int, status: str, notes: Optional[str] = None):
    """Update action item status."""
    return {"id": action_id, "status": status, "updated_at": datetime.utcnow().isoformat()}


@router.post("/actions/{action_id}/follow-up")
async def send_follow_up(action_id: int, message: Optional[str] = None, channels: list[str] = ["slack"]):
    """Send a follow-up reminder for an action item via configured channels."""
    return {
        "action_id": action_id, "follow_up_sent": True,
        "channels": channels, "sent_at": datetime.utcnow().isoformat(),
        "follow_up_count": 2,
    }


@router.post("/actions/{action_id}/escalate")
async def escalate_action_item(action_id: int, reason: str = "Overdue", channels: list[str] = ["slack", "whatsapp"]):
    """Escalate an action item — sends urgent alerts to assignee and managers."""
    return {
        "action_id": action_id, "escalated": True,
        "reason": reason, "channels_notified": channels,
        "alerts_created": len(channels),
    }


@router.post("/actions/{action_id}/reassign")
async def reassign_action_item(action_id: int, new_user_id: int, reason: Optional[str] = None):
    """Reassign an action item to a different user."""
    return {
        "action_id": action_id, "reassigned_to": new_user_id,
        "previous_assignee_notified": True,
    }


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — Dashboard
# ══════════════════════════════════════════════════════════════

@router.get("/dashboard")
async def get_mom_dashboard():
    """Get MOM & Action Items dashboard."""
    today = date.today().isoformat()
    return {
        "total_moms": 2, "total_action_items": 7,
        "by_status": {
            "pending": 4, "in_progress": 2, "completed": 0,
            "escalated": 1, "overdue": 0,
        },
        "by_priority": {"critical": 1, "high": 4, "medium": 2, "low": 0},
        "by_source": {"mom_document": 5, "email_body": 2},
        "escalations": [
            {"id": 1, "title": "Submit 5 .NET developers by March 20", "assigned_to": "Jane Recruiter", "due_date": "2026-03-20", "priority": "critical"},
        ],
        "due_this_week": [
            {"id": 4, "title": "Update placement forecasts", "due_date": "2026-03-14", "assigned_to": "All"},
            {"id": 6, "title": "Send NDA to Rajesh Kumar", "due_date": "2026-03-14", "assigned_to": "Jane Recruiter"},
            {"id": 7, "title": "Reschedule Vikram Singh interview", "due_date": "2026-03-13", "assigned_to": "Jane Recruiter"},
            {"id": 2, "title": "Complete BGC for Vikram Singh", "due_date": "2026-03-15", "assigned_to": "Michael Chen"},
        ],
        "upcoming_meetings": [
            {"title": "Q1 Workforce Planning Review", "date": "2026-03-20T14:00:00Z", "pending_items": 3},
            {"title": "Weekly Recruitment Stand-up", "date": "2026-03-18T10:00:00Z", "pending_items": 1},
        ],
        "assignee_workload": [
            {"name": "Jane Recruiter", "pending": 3, "in_progress": 1, "escalated": 1},
            {"name": "Michael Chen", "pending": 0, "in_progress": 1, "escalated": 0},
            {"name": "Sarah Johnson", "pending": 1, "in_progress": 0, "escalated": 0},
        ],
    }
