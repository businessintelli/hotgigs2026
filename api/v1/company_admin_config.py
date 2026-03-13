"""Company Admin Configuration API — Per-organization settings for Slack, Email, Notifications, Branding.

Accessible by Company Admins (MSP Admin, Client Admin, Supplier Admin).
Each organization configures their OWN Slack workspace, WhatsApp number,
notification rules, email agent behavior, and branding.
"""
from datetime import datetime
from fastapi import APIRouter, Query
from typing import Optional

router = APIRouter(prefix="/company-admin")


# ══════════════════════════════════════════════════════════════
#  MOCK DATA — Per-Organization Integrations
# ══════════════════════════════════════════════════════════════

_mock_company_integrations = {
    1: [  # HotGigs MSP
        {
            "id": 1, "organization_id": 1, "integration_type": "slack", "name": "HotGigs MSP Slack",
            "status": "connected", "is_active": True, "uses_app_level_credentials": True,
            "config_json": {
                "workspace_id": "T04HOTGIGS", "workspace_name": "HotGigs MSP Team",
                "bot_user_id": "B04EMAILAGENT", "default_channel": "#general",
                "channels": {
                    "escalations": "#escalations", "interviews": "#interview-coordination",
                    "onboarding": "#onboarding-offboarding", "resumes": "#resume-pipeline",
                    "action_items": "#action-items", "general": "#recruiting-general",
                },
            },
            "connected_at": "2026-01-15T10:00:00Z", "last_used_at": "2026-03-13T09:30:00Z",
        },
        {
            "id": 2, "organization_id": 1, "integration_type": "whatsapp", "name": "MSP WhatsApp",
            "status": "connected", "is_active": True, "uses_app_level_credentials": True,
            "config_json": {"phone_number": "+1-555-0100", "provider": "twilio", "templates": ["escalation_alert", "daily_summary"]},
            "connected_at": "2026-02-01T10:00:00Z", "last_used_at": "2026-03-13T08:16:00Z",
        },
        {
            "id": 3, "organization_id": 1, "integration_type": "telegram", "name": "MSP Telegram Bot",
            "status": "connected", "is_active": True, "uses_app_level_credentials": True,
            "config_json": {"bot_username": "@HotGigsAgent_bot", "default_chat_id": "123456789", "admin_chat_ids": ["123456789", "987654321"]},
            "connected_at": "2026-02-10T10:00:00Z", "last_used_at": "2026-03-12T17:05:00Z",
        },
        {
            "id": 4, "organization_id": 1, "integration_type": "email_gateway", "name": "MSP Email",
            "status": "connected", "is_active": True, "uses_app_level_credentials": True,
            "config_json": {"from_email": "notifications@hotgigs.ai", "reply_to": "support@hotgigs.ai", "from_name": "HotGigs MSP"},
            "connected_at": "2026-01-10T10:00:00Z", "last_used_at": "2026-03-13T09:00:00Z",
        },
    ],
    2: [  # TechCorp Client
        {
            "id": 5, "organization_id": 2, "integration_type": "slack", "name": "TechCorp Slack",
            "status": "connected", "is_active": True, "uses_app_level_credentials": True,
            "config_json": {
                "workspace_id": "T04TECHCORP", "workspace_name": "TechCorp Engineering",
                "default_channel": "#staffing-updates",
                "channels": {
                    "onboarding": "#new-hires", "interviews": "#interview-schedule",
                    "escalations": "#staffing-urgent",
                },
            },
            "connected_at": "2026-01-20T10:00:00Z", "last_used_at": "2026-03-13T08:15:00Z",
        },
        {
            "id": 6, "organization_id": 2, "integration_type": "teams", "name": "TechCorp Teams",
            "status": "disconnected", "is_active": False, "uses_app_level_credentials": False,
            "config_json": None,
            "connected_at": None, "last_used_at": None,
        },
    ],
    3: [  # StaffPro Supplier
        {
            "id": 7, "organization_id": 3, "integration_type": "slack", "name": "StaffPro Slack",
            "status": "connected", "is_active": True, "uses_app_level_credentials": True,
            "config_json": {
                "workspace_id": "T04STAFFPRO", "workspace_name": "StaffPro Recruiting",
                "default_channel": "#general",
                "channels": {
                    "submissions": "#candidate-submissions", "interviews": "#interview-prep",
                },
            },
            "connected_at": "2026-02-05T10:00:00Z", "last_used_at": "2026-03-13T06:45:00Z",
        },
        {
            "id": 8, "organization_id": 3, "integration_type": "whatsapp", "name": "StaffPro WhatsApp",
            "status": "connected", "is_active": True, "uses_app_level_credentials": True,
            "config_json": {"phone_number": "+1-555-0200", "provider": "twilio"},
            "connected_at": "2026-02-05T10:00:00Z", "last_used_at": "2026-03-12T14:30:00Z",
        },
    ],
}

_mock_notification_rules = {
    1: [
        {"id": 1, "organization_id": 1, "rule_name": "Critical Escalations → Slack + WhatsApp + Telegram",
         "event_type": "escalation", "channels": [{"type": "slack", "channel": "#escalations", "mention": ["@recruiters", "@msp-admins"]}, {"type": "whatsapp"}, {"type": "telegram"}],
         "priority_filter": ["critical", "high"], "is_active": True, "override_quiet_hours_for_critical": True},
        {"id": 2, "organization_id": 1, "rule_name": "Interview Requests → Slack",
         "event_type": "interview_request", "channels": [{"type": "slack", "channel": "#interview-coordination", "mention": ["@recruiters"]}],
         "priority_filter": None, "is_active": True, "override_quiet_hours_for_critical": False},
        {"id": 3, "organization_id": 1, "rule_name": "Onboarding Tasks → Slack",
         "event_type": "onboarding", "channels": [{"type": "slack", "channel": "#onboarding-offboarding", "mention": ["@onboarding-team"]}],
         "priority_filter": None, "is_active": True, "override_quiet_hours_for_critical": False},
        {"id": 4, "organization_id": 1, "rule_name": "Resume Matches → Slack",
         "event_type": "resume_match", "channels": [{"type": "slack", "channel": "#resume-pipeline"}],
         "priority_filter": ["high", "medium"], "is_active": True, "override_quiet_hours_for_critical": False},
        {"id": 5, "organization_id": 1, "rule_name": "Daily Summary → Slack + Email",
         "event_type": "daily_summary", "channels": [{"type": "slack", "channel": "#recruiting-general"}, {"type": "email", "to": "team@hotgigs.com"}],
         "priority_filter": None, "is_active": True, "override_quiet_hours_for_critical": False},
        {"id": 6, "organization_id": 1, "rule_name": "MOM Action Items → Slack",
         "event_type": "mom_action_item", "channels": [{"type": "slack", "channel": "#action-items"}],
         "priority_filter": None, "is_active": True, "override_quiet_hours_for_critical": False},
        {"id": 7, "organization_id": 1, "rule_name": "SLA Breach → All Channels",
         "event_type": "sla_breach", "channels": [{"type": "slack", "channel": "#escalations"}, {"type": "whatsapp"}, {"type": "telegram"}, {"type": "email", "to": "admin@hotgigs.com"}],
         "priority_filter": ["critical"], "is_active": True, "override_quiet_hours_for_critical": True},
    ],
}

_mock_email_agent_config = {
    1: {
        "organization_id": 1, "is_enabled": True,
        "monitored_mailboxes": [
            {"email": "recruiter@hotgigs.com", "provider": "gmail", "folders": ["INBOX", "Recruiting"]},
            {"email": "recruiting@hotgigs.com", "provider": "gmail", "folders": ["INBOX"]},
        ],
        "auto_classify": True, "auto_draft_responses": True,
        "auto_process_resumes": True, "auto_extract_action_items": True,
        "auto_alert_escalations": True, "draft_tone": "professional",
        "draft_language": "en", "max_drafts_per_day": 50,
        "escalation_keywords": ["urgent", "asap", "escalation", "immediately", "critical", "SLA breach", "overdue", "at risk"],
        "auto_add_candidates": False, "minimum_match_score_to_auto_add": 70.0,
        "daily_summary_enabled": True, "daily_summary_time": "09:00",
        "daily_summary_channels": [{"type": "slack", "channel": "#recruiting-general"}],
        "ignored_senders": ["noreply@marketing.com", "promotions@vendor.com"],
        "ignored_domains": ["mailchimp.com", "sendgrid.net"],
        "spam_filter_enabled": True,
    },
}

_mock_branding = {
    1: {"organization_id": 1, "company_name": "HotGigs MSP", "primary_color": "#6366f1", "secondary_color": "#8b5cf6",
        "notification_from_name": "HotGigs MSP", "timezone": "America/Chicago", "date_format": "MM/DD/YYYY", "currency": "USD",
        "email_footer_text": "HotGigs MSP | Your Staffing Partner | hotgigs.ai"},
    2: {"organization_id": 2, "company_name": "TechCorp Inc", "primary_color": "#2563eb", "secondary_color": "#3b82f6",
        "notification_from_name": "TechCorp HR", "timezone": "America/New_York", "date_format": "MM/DD/YYYY", "currency": "USD",
        "email_footer_text": "TechCorp Inc | Technology Solutions"},
    3: {"organization_id": 3, "company_name": "StaffPro Solutions", "primary_color": "#059669", "secondary_color": "#10b981",
        "notification_from_name": "StaffPro", "timezone": "America/Los_Angeles", "date_format": "MM/DD/YYYY", "currency": "USD",
        "email_footer_text": "StaffPro Solutions | Quality Staffing"},
}


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — Company Integrations (Slack, WhatsApp, etc.)
# ══════════════════════════════════════════════════════════════

@router.get("/integrations")
async def get_company_integrations(org_id: int = 1):
    """Get all integrations for a company."""
    items = _mock_company_integrations.get(org_id, [])
    return {"items": items, "total": len(items), "organization_id": org_id}


@router.get("/integrations/{integration_id}")
async def get_company_integration(integration_id: int):
    """Get a specific company integration."""
    for org_items in _mock_company_integrations.values():
        item = next((i for i in org_items if i["id"] == integration_id), None)
        if item:
            return item
    return {"error": "Not found"}


@router.post("/integrations")
async def create_company_integration(org_id: int, integration_type: str, name: str):
    """Create a new company integration."""
    return {"id": 20, "organization_id": org_id, "integration_type": integration_type, "name": name, "status": "pending", "created": True}


@router.put("/integrations/{integration_id}")
async def update_company_integration(integration_id: int):
    """Update company integration config (channels, phone numbers, etc.)."""
    return {"id": integration_id, "updated": True}


@router.post("/integrations/{integration_id}/connect")
async def connect_integration(integration_id: int):
    """Initiate OAuth or API key connection for a company integration."""
    return {"id": integration_id, "status": "connected", "connected_at": datetime.utcnow().isoformat()}


@router.post("/integrations/{integration_id}/disconnect")
async def disconnect_integration(integration_id: int):
    """Disconnect an integration for this company."""
    return {"id": integration_id, "status": "disconnected"}


@router.post("/integrations/{integration_id}/test")
async def test_company_integration(integration_id: int):
    """Test a company integration."""
    return {"id": integration_id, "test_result": "success", "latency_ms": 98, "tested_at": datetime.utcnow().isoformat()}


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — Notification Rules
# ══════════════════════════════════════════════════════════════

@router.get("/notification-rules")
async def get_notification_rules(org_id: int = 1, event_type: Optional[str] = None):
    """Get all notification routing rules for a company."""
    items = _mock_notification_rules.get(org_id, [])
    if event_type:
        items = [r for r in items if r["event_type"] == event_type]
    return {"items": items, "total": len(items), "organization_id": org_id}


@router.post("/notification-rules")
async def create_notification_rule(org_id: int, rule_name: str, event_type: str, channels: list):
    """Create a new notification rule for a company."""
    return {"id": 20, "organization_id": org_id, "rule_name": rule_name, "event_type": event_type, "created": True}


@router.put("/notification-rules/{rule_id}")
async def update_notification_rule(rule_id: int):
    """Update a notification rule."""
    return {"id": rule_id, "updated": True}


@router.delete("/notification-rules/{rule_id}")
async def delete_notification_rule(rule_id: int):
    """Delete a notification rule."""
    return {"id": rule_id, "deleted": True}


@router.post("/notification-rules/{rule_id}/toggle")
async def toggle_notification_rule(rule_id: int, is_active: bool):
    """Enable/disable a notification rule."""
    return {"id": rule_id, "is_active": is_active}


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — Email Agent Config (per company)
# ══════════════════════════════════════════════════════════════

@router.get("/email-agent-config")
async def get_email_agent_config(org_id: int = 1):
    """Get email agent config for a company."""
    return _mock_email_agent_config.get(org_id, {"organization_id": org_id, "is_enabled": False})


@router.put("/email-agent-config")
async def update_email_agent_config(org_id: int = 1):
    """Update email agent config for a company."""
    return {"organization_id": org_id, "updated": True}


@router.post("/email-agent-config/mailboxes")
async def add_mailbox(org_id: int = 1, email: str = "", provider: str = "gmail"):
    """Add a monitored mailbox to the email agent."""
    return {"organization_id": org_id, "email": email, "provider": provider, "added": True}


@router.delete("/email-agent-config/mailboxes/{email}")
async def remove_mailbox(email: str, org_id: int = 1):
    """Remove a monitored mailbox."""
    return {"organization_id": org_id, "email": email, "removed": True}


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — Branding & General Settings
# ══════════════════════════════════════════════════════════════

@router.get("/branding")
async def get_branding(org_id: int = 1):
    """Get company branding and display settings."""
    return _mock_branding.get(org_id, {"organization_id": org_id, "company_name": "Unknown"})


@router.put("/branding")
async def update_branding(org_id: int = 1):
    """Update company branding settings."""
    return {"organization_id": org_id, "updated": True}


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — Dashboard
# ══════════════════════════════════════════════════════════════

@router.get("/dashboard")
async def get_company_admin_dashboard(org_id: int = 1):
    """Get company admin dashboard."""
    integrations = _mock_company_integrations.get(org_id, [])
    rules = _mock_notification_rules.get(org_id, [])
    return {
        "organization_id": org_id,
        "integrations": {
            "total": len(integrations),
            "connected": len([i for i in integrations if i["status"] == "connected"]),
            "disconnected": len([i for i in integrations if i["status"] != "connected"]),
        },
        "notification_rules": {
            "total": len(rules),
            "active": len([r for r in rules if r["is_active"]]),
        },
        "email_agent": {
            "is_enabled": True, "mailboxes_monitored": 2,
            "emails_processed_today": 8, "drafts_generated_today": 5,
        },
        "alerts_sent_today": 5,
        "channels_active": len([i for i in integrations if i["is_active"] and i["status"] == "connected"]),
        "available_integrations": [
            {"type": "slack", "connected": True}, {"type": "whatsapp", "connected": True},
            {"type": "telegram", "connected": True}, {"type": "teams", "connected": False},
            {"type": "email_gateway", "connected": True},
        ],
    }
