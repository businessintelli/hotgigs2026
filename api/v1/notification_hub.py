"""Notification Hub API — Slack, WhatsApp, Telegram integration for alerts and collaboration."""
from datetime import datetime
from fastapi import APIRouter, Query
from typing import Optional

router = APIRouter(prefix="/notification-hub")


# ══════════════════════════════════════════════════════════════
#  MOCK DATA
# ══════════════════════════════════════════════════════════════

_mock_channels = [
    {
        "id": 1, "user_id": 2, "channel_type": "slack", "channel_identifier": "U04ABCDEF12",
        "channel_name": "Jane Recruiter - Slack DM", "is_active": True, "is_primary": True,
        "notification_preferences": {"escalations": True, "daily_summary": True, "action_items": True, "recruitment": True, "onboarding": True},
        "quiet_hours_start": "22:00", "quiet_hours_end": "07:00", "timezone": "America/Chicago",
    },
    {
        "id": 2, "user_id": 2, "channel_type": "whatsapp", "channel_identifier": "+1-555-0123",
        "channel_name": "Jane's WhatsApp", "is_active": True, "is_primary": False,
        "notification_preferences": {"escalations": True, "daily_summary": False, "action_items": False, "recruitment": False, "onboarding": False},
        "quiet_hours_start": "21:00", "quiet_hours_end": "08:00", "timezone": "America/Chicago",
    },
    {
        "id": 3, "user_id": 2, "channel_type": "telegram", "channel_identifier": "123456789",
        "channel_name": "Jane's Telegram", "is_active": True, "is_primary": False,
        "notification_preferences": {"escalations": True, "daily_summary": True, "action_items": False, "recruitment": False, "onboarding": False},
        "quiet_hours_start": None, "quiet_hours_end": None, "timezone": "America/Chicago",
    },
    {
        "id": 4, "user_id": 1, "channel_type": "slack", "channel_identifier": "U04XYZABC34",
        "channel_name": "Admin - Slack DM", "is_active": True, "is_primary": True,
        "notification_preferences": {"escalations": True, "daily_summary": True, "action_items": True, "recruitment": False, "onboarding": True},
        "quiet_hours_start": "23:00", "quiet_hours_end": "07:00", "timezone": "America/New_York",
    },
]

_mock_alerts = [
    {
        "id": 1, "user_id": 2, "channel_type": "slack", "alert_type": "escalation",
        "title": "🚨 ESCALATION: Java Developer SLA at Risk",
        "message": "*URGENT*: Sarah Johnson (TechCorp) has flagged an SLA risk for a Senior Java Developer requirement. Deadline: This Friday.\n\n📧 <mailto:sarah.johnson@techcorp.com|View Email> | 📋 <#|View Requirement>\n\n_Respond within 1 hour to prevent SLA breach._",
        "priority": "critical", "status": "delivered",
        "sent_at": "2026-03-13T08:16:00Z", "delivered_at": "2026-03-13T08:16:02Z",
        "read_at": None, "source_type": "email", "source_id": 1,
    },
    {
        "id": 2, "user_id": 2, "channel_type": "whatsapp", "alert_type": "escalation",
        "title": "ESCALATION: Java Developer SLA at Risk",
        "message": "URGENT from TechCorp: Senior Java Developer needed by Friday - SLA risk. Check Slack/email for details. - HotGigs Agent",
        "priority": "critical", "status": "delivered",
        "sent_at": "2026-03-13T08:16:05Z", "delivered_at": "2026-03-13T08:16:08Z",
        "read_at": "2026-03-13T08:20:00Z", "source_type": "email", "source_id": 1,
    },
    {
        "id": 3, "user_id": 2, "channel_type": "slack", "alert_type": "action_item",
        "title": "📋 MOM Action Item: Submit 5 .NET Developers by March 20",
        "message": "New action item from Q1 Workforce Planning Review:\n\n*Task*: Submit 5 additional .NET developers\n*Deadline*: March 20, 2026\n*Status*: ESCALATED\n*Assigned by*: Sarah Johnson\n\n✅ <#|Mark Complete> | 📅 <#|Set Reminder>",
        "priority": "high", "status": "delivered",
        "sent_at": "2026-03-12T17:05:00Z", "delivered_at": "2026-03-12T17:05:02Z",
        "read_at": "2026-03-12T17:30:00Z", "source_type": "action_item", "source_id": 1,
    },
    {
        "id": 4, "user_id": 2, "channel_type": "slack", "alert_type": "daily_summary",
        "title": "📊 Daily Email Summary - March 13, 2026",
        "message": "Good morning Jane! Here's your inbox summary:\n\n• 🚨 *1 Escalation*: Java Developer SLA risk (TechCorp)\n• 📄 *2 Applications*: Priya Sharma (Python), Amit Patel (React Native)\n• 📅 *1 Reschedule*: Vikram Singh interview\n• ✅ *1 Onboarding*: Rajesh Kumar checklist\n• 📝 *1 MOM*: Q1 Planning with 4 action items\n• 📰 *1 Newsletter*: TechCorp Q1 update\n\n5 drafts generated and ready for review.",
        "priority": "low", "status": "delivered",
        "sent_at": "2026-03-13T09:00:00Z", "delivered_at": "2026-03-13T09:00:02Z",
        "read_at": None, "source_type": "summary", "source_id": 1,
    },
    {
        "id": 5, "user_id": 2, "channel_type": "slack", "alert_type": "resume_match",
        "title": "🎯 Strong Resume Match: Carlos Rivera → Data Engineer",
        "message": "*Excellent Match (91%)* for Data Engineer - TechCorp\n\n👤 *Carlos Rivera* | 6 years exp\n🛠 Spark, Snowflake, dbt, Airflow, GCP\n📊 Match: Skills 95% | Exp 85% | Edu 88%\n💡 Recommendation: *Strong Yes*\n\n✅ <#|Review & Approve> | 📄 <#|View Resume>",
        "priority": "medium", "status": "delivered",
        "sent_at": "2026-03-12T11:02:00Z", "delivered_at": "2026-03-12T11:02:01Z",
        "read_at": "2026-03-12T11:15:00Z", "source_type": "resume_capture", "source_id": 4,
    },
]

_mock_slack_workspace = {
    "id": 1, "workspace_id": "T04HOTGIGS", "workspace_name": "HotGigs MSP Team",
    "is_active": True, "bot_user_id": "B04EMAILAGENT",
    "channels_config": {
        "escalations": "#escalations", "interviews": "#interview-coordination",
        "onboarding": "#onboarding-offboarding", "general": "#recruiting-general",
        "resumes": "#resume-pipeline", "action_items": "#action-items",
    },
}

_mock_channel_mappings = [
    {"id": 1, "event_type": "escalation", "channel_id": "C04ESC001", "channel_name": "#escalations", "is_active": True, "auto_thread": True, "mention_roles": ["@recruiters", "@msp-admins"]},
    {"id": 2, "event_type": "interview_request", "channel_id": "C04INT001", "channel_name": "#interview-coordination", "is_active": True, "auto_thread": True, "mention_roles": ["@recruiters"]},
    {"id": 3, "event_type": "interview_reschedule", "channel_id": "C04INT001", "channel_name": "#interview-coordination", "is_active": True, "auto_thread": True, "mention_roles": ["@recruiters", "@hiring-managers"]},
    {"id": 4, "event_type": "onboarding", "channel_id": "C04ONB001", "channel_name": "#onboarding-offboarding", "is_active": True, "auto_thread": True, "mention_roles": ["@onboarding-team"]},
    {"id": 5, "event_type": "offboarding", "channel_id": "C04ONB001", "channel_name": "#onboarding-offboarding", "is_active": True, "auto_thread": True, "mention_roles": ["@onboarding-team", "@it-admin"]},
    {"id": 6, "event_type": "resume_match", "channel_id": "C04RES001", "channel_name": "#resume-pipeline", "is_active": True, "auto_thread": True, "mention_roles": []},
    {"id": 7, "event_type": "action_item", "channel_id": "C04ACT001", "channel_name": "#action-items", "is_active": True, "auto_thread": False, "mention_roles": []},
    {"id": 8, "event_type": "daily_summary", "channel_id": "C04GEN001", "channel_name": "#recruiting-general", "is_active": True, "auto_thread": False, "mention_roles": []},
]


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — Notification Channels
# ══════════════════════════════════════════════════════════════

@router.get("/channels")
async def get_notification_channels(user_id: Optional[int] = None, channel_type: Optional[str] = None):
    """Get user notification channels (Slack, WhatsApp, Telegram)."""
    results = _mock_channels
    if user_id:
        results = [c for c in results if c["user_id"] == user_id]
    if channel_type:
        results = [c for c in results if c["channel_type"] == channel_type]
    return {"items": results, "total": len(results)}


@router.post("/channels")
async def create_notification_channel():
    """Connect a new notification channel."""
    return {"id": 5, "status": "connected", "message": "Notification channel connected successfully"}


@router.put("/channels/{channel_id}")
async def update_channel(channel_id: int):
    """Update notification channel preferences."""
    return {"id": channel_id, "updated": True}


@router.delete("/channels/{channel_id}")
async def deactivate_channel(channel_id: int):
    """Deactivate a notification channel."""
    return {"id": channel_id, "is_active": False, "message": "Channel deactivated"}


@router.post("/channels/{channel_id}/test")
async def test_channel(channel_id: int):
    """Send a test notification to verify channel connectivity."""
    return {"channel_id": channel_id, "test_sent": True, "message": "Test notification sent successfully"}


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — Alerts
# ══════════════════════════════════════════════════════════════

@router.get("/alerts")
async def get_alerts(
    alert_type: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    channel_type: Optional[str] = None,
    limit: int = Query(default=50, le=200),
):
    """Get sent alerts with filters."""
    results = _mock_alerts
    if alert_type:
        results = [a for a in results if a["alert_type"] == alert_type]
    if priority:
        results = [a for a in results if a["priority"] == priority]
    if status:
        results = [a for a in results if a["status"] == status]
    if channel_type:
        results = [a for a in results if a["channel_type"] == channel_type]
    return {"items": results[:limit], "total": len(results)}


@router.post("/alerts/send")
async def send_alert(
    user_id: int, title: str, message: str,
    priority: str = "medium", channels: list[str] = ["slack"],
):
    """Manually send an alert to a user across specified channels."""
    sent = []
    for ch in channels:
        sent.append({
            "channel": ch, "status": "sent",
            "sent_at": datetime.utcnow().isoformat(),
        })
    return {"alerts_sent": sent, "total": len(sent)}


@router.post("/alerts/escalate/{email_id}")
async def escalate_email(email_id: int, message: Optional[str] = None):
    """Escalate an email by sending urgent alerts to all configured channels."""
    return {
        "email_id": email_id, "escalated": True,
        "channels_notified": ["slack", "whatsapp", "telegram"],
        "alerts_created": 3,
    }


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — Slack Integration
# ══════════════════════════════════════════════════════════════

@router.get("/slack/workspace")
async def get_slack_workspace():
    """Get connected Slack workspace details."""
    return _mock_slack_workspace


@router.post("/slack/connect")
async def connect_slack_workspace():
    """Initiate Slack workspace connection (OAuth flow)."""
    return {"oauth_url": "https://slack.com/oauth/v2/authorize?client_id=...&scope=...", "status": "pending"}


@router.get("/slack/channels")
async def get_slack_channel_mappings():
    """Get Slack channel → event type mappings."""
    return {"items": _mock_channel_mappings, "total": len(_mock_channel_mappings)}


@router.post("/slack/channels")
async def create_channel_mapping(event_type: str, channel_id: str, channel_name: str):
    """Map a Slack channel to a platform event type."""
    return {"id": 9, "event_type": event_type, "channel_id": channel_id, "channel_name": channel_name, "created": True}


@router.put("/slack/channels/{mapping_id}")
async def update_channel_mapping(mapping_id: int):
    """Update a Slack channel mapping."""
    return {"id": mapping_id, "updated": True}


@router.post("/slack/send")
async def send_slack_message(channel: str, message: str, thread_ts: Optional[str] = None):
    """Send a message to a Slack channel."""
    return {
        "channel": channel, "sent": True, "ts": "1710316800.000100",
        "thread_ts": thread_ts,
    }


@router.post("/slack/thread/{event_type}")
async def create_slack_thread(event_type: str, title: str, details: str):
    """Create a new threaded conversation in the mapped Slack channel for an event."""
    mapping = next((m for m in _mock_channel_mappings if m["event_type"] == event_type), None)
    return {
        "event_type": event_type,
        "channel": mapping["channel_name"] if mapping else "#general",
        "thread_ts": "1710316800.000200",
        "message": f"New {event_type}: {title}",
    }


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — WhatsApp & Telegram
# ══════════════════════════════════════════════════════════════

@router.post("/whatsapp/send")
async def send_whatsapp(phone_number: str, message: str):
    """Send a WhatsApp message via Twilio/WhatsApp Business API."""
    return {"phone": phone_number, "sent": True, "message_id": "wamid.HBgN..."}


@router.post("/telegram/send")
async def send_telegram(chat_id: str, message: str):
    """Send a Telegram message."""
    return {"chat_id": chat_id, "sent": True, "message_id": 12345}


@router.get("/whatsapp/config")
async def get_whatsapp_config():
    """Get WhatsApp Business API configuration."""
    return {
        "provider": "twilio", "is_configured": True,
        "phone_number": "+1-555-HOTGIGS",
        "templates": ["escalation_alert", "daily_summary", "interview_reminder"],
    }


@router.get("/telegram/config")
async def get_telegram_config():
    """Get Telegram bot configuration."""
    return {
        "bot_name": "HotGigsAgent_bot", "is_configured": True,
        "active_chats": 5,
    }


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — Dashboard
# ══════════════════════════════════════════════════════════════

@router.get("/dashboard")
async def get_notification_dashboard():
    """Get notification hub dashboard."""
    return {
        "total_channels_configured": 4,
        "alerts_sent_today": 5, "alerts_sent_this_week": 32,
        "delivery_rate": 0.98, "read_rate": 0.72,
        "by_channel": {
            "slack": {"sent": 22, "delivered": 22, "read": 18},
            "whatsapp": {"sent": 6, "delivered": 6, "read": 5},
            "telegram": {"sent": 4, "delivered": 4, "read": 2},
        },
        "by_type": {
            "escalation": 3, "daily_summary": 7, "action_item": 12,
            "resume_match": 6, "interview": 4,
        },
        "slack_stats": {
            "channels_mapped": 8, "messages_sent_today": 14,
            "active_threads": 6, "pending_requests": {
                "onboarding": 2, "interview": 3, "offboarding": 1,
            },
        },
        "recent_activity": [
            {"type": "escalation", "channel": "slack+whatsapp", "title": "Java Developer SLA Risk", "time": "08:16 AM", "status": "delivered"},
            {"type": "action_item", "channel": "slack", "title": "Submit 5 .NET Developers", "time": "Yesterday 5:05 PM", "status": "read"},
            {"type": "resume_match", "channel": "slack", "title": "Carlos Rivera → Data Engineer (91%)", "time": "Yesterday 11:02 AM", "status": "read"},
            {"type": "daily_summary", "channel": "slack", "title": "Daily Email Summary", "time": "09:00 AM", "status": "delivered"},
        ],
    }
