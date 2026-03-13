"""App Admin Configuration API — Platform-level integrations, feature flags, and system settings.

Only accessible by HotGigs platform super-admins.
Manages: API keys for Twilio/SendGrid/OpenAI, global Slack app, feature flags,
         license limits, and health monitoring for all platform-level connectors.
"""
from datetime import datetime
from fastapi import APIRouter, Query
from typing import Optional

router = APIRouter(prefix="/app-admin")


# ══════════════════════════════════════════════════════════════
#  MOCK DATA
# ══════════════════════════════════════════════════════════════

_mock_integrations = [
    {
        "id": 1, "integration_type": "ai_provider", "name": "OpenAI GPT-4o",
        "description": "Primary AI model for email classification, resume parsing, draft generation, and match scoring",
        "provider": "openai", "status": "connected",
        "base_url": "https://api.openai.com/v1", "api_key_masked": "sk-...7xKm",
        "config_json": {"model": "gpt-4o", "max_tokens": 4096, "temperature": 0.3, "fallback_model": "gpt-4o-mini"},
        "is_active": True, "available_to_all_orgs": True,
        "rate_limit_per_minute": 500, "rate_limit_per_day": 50000,
        "last_health_check": "2026-03-13T09:00:00Z", "health_status": "healthy",
        "usage_today": {"requests": 1247, "tokens": 892000},
    },
    {
        "id": 2, "integration_type": "slack", "name": "Slack Platform App",
        "description": "HotGigs Slack app — installed by each company into their own workspace. App-level OAuth credentials.",
        "provider": "slack", "status": "connected",
        "base_url": "https://slack.com/api", "api_key_masked": "xoxb-...F4tQ",
        "config_json": {"client_id": "4829374928.7482937492", "signing_secret_masked": "a1b2...9z0x", "scopes": ["chat:write", "channels:read", "users:read", "files:write"]},
        "is_active": True, "available_to_all_orgs": True,
        "rate_limit_per_minute": None, "rate_limit_per_day": None,
        "last_health_check": "2026-03-13T09:00:00Z", "health_status": "healthy",
        "orgs_connected": 3,
    },
    {
        "id": 3, "integration_type": "whatsapp", "name": "Twilio WhatsApp Business",
        "description": "Platform-level Twilio account for WhatsApp Business API — companies configure their own phone numbers",
        "provider": "twilio", "status": "connected",
        "base_url": "https://api.twilio.com", "api_key_masked": "AC...8f2d",
        "config_json": {"account_sid": "AC...", "messaging_service_sid": "MG...", "from_number": "+1-555-HOTGIGS"},
        "is_active": True, "available_to_all_orgs": True,
        "rate_limit_per_minute": 60, "rate_limit_per_day": 5000,
        "last_health_check": "2026-03-13T09:00:00Z", "health_status": "healthy",
    },
    {
        "id": 4, "integration_type": "telegram", "name": "Telegram Bot API",
        "description": "Platform-level Telegram bot for alert notifications",
        "provider": "telegram", "status": "connected",
        "base_url": "https://api.telegram.org", "api_key_masked": "bot...3xYz",
        "config_json": {"bot_username": "@HotGigsAgent_bot"},
        "is_active": True, "available_to_all_orgs": True,
        "rate_limit_per_minute": 30, "rate_limit_per_day": 2000,
        "last_health_check": "2026-03-13T09:00:00Z", "health_status": "healthy",
    },
    {
        "id": 5, "integration_type": "email_gateway", "name": "SendGrid Email Gateway",
        "description": "Transactional email delivery for notifications, summaries, and candidate communications",
        "provider": "sendgrid", "status": "connected",
        "base_url": "https://api.sendgrid.com/v3", "api_key_masked": "SG...j9Kp",
        "config_json": {"from_email": "noreply@hotgigs.ai", "from_name": "HotGigs Platform", "daily_limit": 10000, "templates": {"escalation": "d-abc123", "summary": "d-def456", "candidate_ack": "d-ghi789"}},
        "is_active": True, "available_to_all_orgs": True,
        "rate_limit_per_minute": 100, "rate_limit_per_day": 10000,
        "last_health_check": "2026-03-13T09:00:00Z", "health_status": "healthy",
    },
    {
        "id": 6, "integration_type": "sms_gateway", "name": "Twilio SMS",
        "description": "SMS notifications for critical alerts when other channels are unavailable",
        "provider": "twilio", "status": "connected",
        "base_url": "https://api.twilio.com", "api_key_masked": "AC...8f2d",
        "config_json": {"from_number": "+1-555-0100"},
        "is_active": True, "available_to_all_orgs": False,
        "allowed_org_ids": [1, 2],
        "rate_limit_per_minute": 30, "rate_limit_per_day": 1000,
        "last_health_check": "2026-03-13T09:00:00Z", "health_status": "healthy",
    },
    {
        "id": 7, "integration_type": "bgc_provider", "name": "HireRight Background Checks",
        "description": "Background check provider integration for automated BGC initiation",
        "provider": "hireright", "status": "connected",
        "base_url": "https://api.hireright.com/v1", "api_key_masked": "hr...Kx4p",
        "config_json": {"package_ids": {"standard": "PKG-001", "enhanced": "PKG-002", "executive": "PKG-003"}},
        "is_active": True, "available_to_all_orgs": True,
        "rate_limit_per_minute": None, "rate_limit_per_day": None,
        "last_health_check": "2026-03-13T08:00:00Z", "health_status": "healthy",
    },
    {
        "id": 8, "integration_type": "storage", "name": "AWS S3 Document Storage",
        "description": "Cloud storage for resumes, contracts, and documents",
        "provider": "aws_s3", "status": "connected",
        "base_url": "https://s3.amazonaws.com", "api_key_masked": "AKIA...7xKm",
        "config_json": {"bucket": "hotgigs-documents", "region": "us-east-1", "max_file_size_mb": 25},
        "is_active": True, "available_to_all_orgs": True,
        "rate_limit_per_minute": None, "rate_limit_per_day": None,
        "last_health_check": "2026-03-13T09:00:00Z", "health_status": "healthy",
    },
    {
        "id": 9, "integration_type": "video_conferencing", "name": "Zoom Meetings",
        "description": "Zoom integration for auto-scheduling interview video calls",
        "provider": "zoom", "status": "disconnected",
        "base_url": "https://api.zoom.us/v2", "api_key_masked": None,
        "config_json": None,
        "is_active": False, "available_to_all_orgs": True,
        "rate_limit_per_minute": None, "rate_limit_per_day": None,
        "last_health_check": None, "health_status": None,
    },
    {
        "id": 10, "integration_type": "calendar", "name": "Google Calendar",
        "description": "Calendar sync for interview scheduling",
        "provider": "google", "status": "disconnected",
        "base_url": "https://www.googleapis.com/calendar/v3", "api_key_masked": None,
        "config_json": None,
        "is_active": False, "available_to_all_orgs": True,
        "rate_limit_per_minute": None, "rate_limit_per_day": None,
        "last_health_check": None, "health_status": None,
    },
]

_mock_feature_flags = [
    {"id": 1, "flag_key": "email_agent", "name": "Email Agent", "description": "AI-powered email classification, drafting, and action extraction", "status": "enabled", "category": "ai", "rollout_percentage": 100.0, "allowed_org_ids": None},
    {"id": 2, "flag_key": "auto_resume_processing", "name": "Auto Resume Processing", "description": "Automatically parse and score resumes from incoming emails", "status": "enabled", "category": "ai", "rollout_percentage": 100.0, "allowed_org_ids": None},
    {"id": 3, "flag_key": "cascade_invoicing", "name": "Cascading Auto-Invoicing", "description": "Auto-generate downstream invoices when upstream is approved", "status": "enabled", "category": "billing", "rollout_percentage": 100.0, "allowed_org_ids": None},
    {"id": 4, "flag_key": "whatsapp_alerts", "name": "WhatsApp Alert Delivery", "description": "Send critical alerts via WhatsApp Business API", "status": "enabled", "category": "notifications", "rollout_percentage": 100.0, "allowed_org_ids": None},
    {"id": 5, "flag_key": "telegram_alerts", "name": "Telegram Alert Delivery", "description": "Send alerts via Telegram bot", "status": "beta", "category": "notifications", "rollout_percentage": 50.0, "allowed_org_ids": [1]},
    {"id": 6, "flag_key": "ai_interview_scheduling", "name": "AI Interview Scheduling", "description": "Let AI agent auto-schedule interviews based on availability", "status": "disabled", "category": "ai", "rollout_percentage": 0, "allowed_org_ids": None},
    {"id": 7, "flag_key": "advanced_analytics_v2", "name": "Advanced Analytics V2", "description": "Next-gen analytics dashboards with predictive insights", "status": "beta", "category": "analytics", "rollout_percentage": 25.0, "allowed_org_ids": [1, 2]},
    {"id": 8, "flag_key": "multi_language_support", "name": "Multi-Language Support", "description": "Email drafts and notifications in multiple languages", "status": "disabled", "category": "general", "rollout_percentage": 0, "allowed_org_ids": None},
]

_mock_license = [
    {"config_key": "max_organizations", "config_value": "50", "config_type": "int", "category": "limits", "description": "Maximum number of organizations"},
    {"config_key": "max_users_per_org", "config_value": "200", "config_type": "int", "category": "limits", "description": "Maximum users per organization"},
    {"config_key": "max_email_syncs_per_day", "config_value": "100000", "config_type": "int", "category": "limits", "description": "Maximum email syncs across all orgs per day"},
    {"config_key": "max_ai_requests_per_day", "config_value": "50000", "config_type": "int", "category": "limits", "description": "Maximum AI model requests per day"},
    {"config_key": "max_file_storage_gb", "config_value": "500", "config_type": "int", "category": "limits", "description": "Total file storage limit in GB"},
    {"config_key": "session_timeout_minutes", "config_value": "60", "config_type": "int", "category": "security", "description": "Session timeout in minutes"},
    {"config_key": "enforce_2fa", "config_value": "false", "config_type": "bool", "category": "security", "description": "Require 2FA for all users"},
    {"config_key": "password_min_length", "config_value": "10", "config_type": "int", "category": "security", "description": "Minimum password length"},
    {"config_key": "data_retention_days", "config_value": "365", "config_type": "int", "category": "compliance", "description": "Data retention period in days"},
    {"config_key": "audit_log_enabled", "config_value": "true", "config_type": "bool", "category": "compliance", "description": "Enable audit logging"},
]


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — Platform Integrations
# ══════════════════════════════════════════════════════════════

@router.get("/integrations")
async def get_app_integrations(integration_type: Optional[str] = None, status: Optional[str] = None):
    """Get all platform-level integrations."""
    results = _mock_integrations
    if integration_type:
        results = [i for i in results if i["integration_type"] == integration_type]
    if status:
        results = [i for i in results if i["status"] == status]
    return {"items": results, "total": len(results)}


@router.get("/integrations/{integration_id}")
async def get_app_integration(integration_id: int):
    """Get a specific integration detail."""
    item = next((i for i in _mock_integrations if i["id"] == integration_id), None)
    return item or {"error": "Not found"}


@router.post("/integrations")
async def create_app_integration(integration_type: str, name: str, provider: str):
    """Create a new platform-level integration."""
    return {"id": 11, "integration_type": integration_type, "name": name, "provider": provider, "status": "pending", "created": True}


@router.put("/integrations/{integration_id}")
async def update_app_integration(integration_id: int):
    """Update integration configuration or credentials."""
    return {"id": integration_id, "updated": True}


@router.post("/integrations/{integration_id}/test")
async def test_integration(integration_id: int):
    """Test connectivity for an integration."""
    item = next((i for i in _mock_integrations if i["id"] == integration_id), None)
    if not item:
        return {"error": "Not found"}
    return {"id": integration_id, "test_result": "success" if item["status"] == "connected" else "failed", "latency_ms": 142, "tested_at": datetime.utcnow().isoformat()}


@router.post("/integrations/{integration_id}/toggle")
async def toggle_integration(integration_id: int, is_active: bool):
    """Enable/disable an integration."""
    return {"id": integration_id, "is_active": is_active}


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — Feature Flags
# ══════════════════════════════════════════════════════════════

@router.get("/feature-flags")
async def get_feature_flags(category: Optional[str] = None, status: Optional[str] = None):
    """Get all platform feature flags."""
    results = _mock_feature_flags
    if category:
        results = [f for f in results if f["category"] == category]
    if status:
        results = [f for f in results if f["status"] == status]
    return {"items": results, "total": len(results)}


@router.put("/feature-flags/{flag_id}")
async def update_feature_flag(flag_id: int, status: Optional[str] = None, rollout_percentage: Optional[float] = None):
    """Update a feature flag status or rollout percentage."""
    return {"id": flag_id, "status": status, "rollout_percentage": rollout_percentage, "updated": True}


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — License & System Config
# ══════════════════════════════════════════════════════════════

@router.get("/license")
async def get_license_config(category: Optional[str] = None):
    """Get platform license and system configuration."""
    results = _mock_license
    if category:
        results = [c for c in results if c["category"] == category]
    return {"items": results, "total": len(results)}


@router.put("/license/{config_key}")
async def update_license_config(config_key: str, config_value: str):
    """Update a license/system config value."""
    return {"config_key": config_key, "config_value": config_value, "updated": True}


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — Dashboard
# ══════════════════════════════════════════════════════════════

@router.get("/dashboard")
async def get_app_admin_dashboard():
    """Get app admin dashboard — system health, usage, and alerts."""
    return {
        "system_health": "healthy",
        "total_organizations": 3, "total_users": 42, "active_sessions": 18,
        "integrations": {
            "total": 10, "connected": 8, "disconnected": 2, "errors": 0,
        },
        "feature_flags": {
            "total": 8, "enabled": 4, "beta": 2, "disabled": 2,
        },
        "usage_today": {
            "ai_requests": 1247, "emails_processed": 856, "resumes_parsed": 23,
            "notifications_sent": 142, "api_calls": 12847,
        },
        "storage": {"used_gb": 47.3, "limit_gb": 500, "percent": 9.5},
        "recent_errors": [],
        "organizations_summary": [
            {"id": 1, "name": "HotGigs MSP", "type": "MSP", "users": 15, "integrations_active": 6},
            {"id": 2, "name": "TechCorp Inc", "type": "CLIENT", "users": 18, "integrations_active": 4},
            {"id": 3, "name": "StaffPro Solutions", "type": "SUPPLIER", "users": 9, "integrations_active": 3},
        ],
    }
