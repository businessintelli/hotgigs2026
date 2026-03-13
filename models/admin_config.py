"""Admin configuration models — App-level and Company-level settings.

Two tiers:
  1. AppConfig — Platform-wide settings managed by HotGigs App Admins
     (API keys, global integrations, feature flags, license limits)
  2. CompanyConfig — Per-organization settings managed by each Company Admin
     (their own Slack workspace, email gateway, WhatsApp/Telegram, notification rules)
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    String, DateTime, Enum, JSON, ForeignKey, Text, Float, Integer,
    Boolean, Index, func
)
from sqlalchemy.orm import Mapped, mapped_column
from models.base import BaseModel
import enum


# ── Enums ──────────────────────────────────────────────────

class IntegrationStatus(str, enum.Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    PENDING = "pending"
    EXPIRED = "expired"


class IntegrationType(str, enum.Enum):
    SLACK = "slack"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    TEAMS = "teams"
    EMAIL_GATEWAY = "email_gateway"
    SMS_GATEWAY = "sms_gateway"
    AI_PROVIDER = "ai_provider"
    STORAGE = "storage"
    BGC_PROVIDER = "bgc_provider"
    ATS_CONNECTOR = "ats_connector"
    JOB_BOARD = "job_board"
    CALENDAR = "calendar"
    VIDEO_CONFERENCING = "video_conferencing"
    HRIS = "hris"
    PAYROLL = "payroll"
    ACCOUNTING = "accounting"
    SSO = "sso"
    WEBHOOK = "webhook"


class FeatureFlagStatus(str, enum.Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"
    BETA = "beta"
    ENTERPRISE_ONLY = "enterprise_only"


# ══════════════════════════════════════════════════════════════
#  APP-LEVEL CONFIG (Platform Admin — HotGigs Super Admin)
# ══════════════════════════════════════════════════════════════

class AppIntegration(BaseModel):
    """Platform-level integration connectors managed by App Admin."""
    __tablename__ = "app_integrations"

    integration_type: Mapped[str] = mapped_column(Enum(IntegrationType), index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    provider: Mapped[str] = mapped_column(String(100))  # twilio, sendgrid, openai, etc.
    status: Mapped[str] = mapped_column(Enum(IntegrationStatus), default=IntegrationStatus.DISCONNECTED)
    api_key_encrypted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    api_secret_encrypted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    base_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    webhook_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    oauth_client_id: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    oauth_client_secret_encrypted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    scopes: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    config_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # config_json examples:
    #   AI: {model: "gpt-4o", max_tokens: 4096, temperature: 0.7}
    #   Twilio: {account_sid: "...", messaging_service_sid: "..."}
    #   SendGrid: {from_email: "noreply@hotgigs.com", daily_limit: 10000}
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    available_to_all_orgs: Mapped[bool] = mapped_column(Boolean, default=True)
    allowed_org_ids: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # null = all, [1,2,3] = specific
    rate_limit_per_minute: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    rate_limit_per_day: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    last_health_check: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    health_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    updated_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)


class AppFeatureFlag(BaseModel):
    """Platform-level feature flags managed by App Admin."""
    __tablename__ = "app_feature_flags"

    flag_key: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(Enum(FeatureFlagStatus), default=FeatureFlagStatus.DISABLED)
    category: Mapped[str] = mapped_column(String(100), default="general")  # ai, billing, notifications, recruitment
    config_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # per-flag config
    allowed_org_ids: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    rollout_percentage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0.0 - 100.0
    updated_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)


class AppLicenseConfig(BaseModel):
    """Platform license and usage limits."""
    __tablename__ = "app_license_configs"

    config_key: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    config_value: Mapped[str] = mapped_column(Text)
    config_type: Mapped[str] = mapped_column(String(50), default="string")  # string, int, bool, json
    category: Mapped[str] = mapped_column(String(100))  # limits, branding, security, compliance
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_sensitive: Mapped[bool] = mapped_column(Boolean, default=False)


# ══════════════════════════════════════════════════════════════
#  COMPANY-LEVEL CONFIG (Per-Organization — Company Admin)
# ══════════════════════════════════════════════════════════════

class CompanyIntegration(BaseModel):
    """Per-organization integration settings managed by Company Admin."""
    __tablename__ = "company_integrations"

    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), index=True)
    integration_type: Mapped[str] = mapped_column(Enum(IntegrationType), index=True)
    name: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(Enum(IntegrationStatus), default=IntegrationStatus.DISCONNECTED)

    # Credentials (per company)
    api_key_encrypted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    api_secret_encrypted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    access_token_encrypted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    refresh_token_encrypted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    webhook_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    webhook_secret: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    oauth_client_id: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Company-specific config
    config_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # Slack: {workspace_id, workspace_name, bot_token, default_channel, channels: {escalation: "#esc", ...}}
    # WhatsApp: {phone_number, provider: "twilio", account_sid, messaging_service_sid}
    # Telegram: {bot_token, bot_username, default_chat_id}
    # Email: {smtp_host, smtp_port, from_address, reply_to, use_tls, daily_limit}
    # Teams: {tenant_id, team_id, webhook_url}

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    uses_app_level_credentials: Mapped[bool] = mapped_column(Boolean, default=False)
    # If True, this integration inherits API keys from the app-level AppIntegration
    # Company only provides workspace/channel/phone config, not API keys

    connected_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    updated_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    __table_args__ = (
        Index("ix_company_integrations_org_type", "organization_id", "integration_type"),
    )


class CompanyNotificationRule(BaseModel):
    """Per-organization notification routing rules set by Company Admin."""
    __tablename__ = "company_notification_rules"

    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), index=True)
    rule_name: Mapped[str] = mapped_column(String(255))
    event_type: Mapped[str] = mapped_column(String(100), index=True)
    # event_types: escalation, new_requirement, candidate_application, interview_request,
    # interview_reschedule, onboarding, offboarding, timesheet_approval, invoice, bgc_update,
    # sla_breach, daily_summary, mom_action_item, resume_match

    # Where to send
    channels: Mapped[dict] = mapped_column(JSON)
    # [{type: "slack", channel: "#escalations", mention: ["@recruiters"]},
    #  {type: "whatsapp", phone: "+1-555-0123"},
    #  {type: "email", to: "admin@company.com"}]

    # Conditions
    priority_filter: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # ["critical", "high"]
    role_filter: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # ["MSP_ADMIN", "RECRUITER"]
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    quiet_hours_start: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    quiet_hours_end: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    override_quiet_hours_for_critical: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)


class CompanyEmailAgentConfig(BaseModel):
    """Per-organization email agent configuration by Company Admin."""
    __tablename__ = "company_email_agent_configs"

    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), unique=True, index=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    # Email monitoring
    monitored_mailboxes: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # [{email: "recruiting@company.com", provider: "gmail", folders: ["INBOX", "Recruiting"]}]

    # AI behavior
    auto_classify: Mapped[bool] = mapped_column(Boolean, default=True)
    auto_draft_responses: Mapped[bool] = mapped_column(Boolean, default=False)
    auto_process_resumes: Mapped[bool] = mapped_column(Boolean, default=True)
    auto_extract_action_items: Mapped[bool] = mapped_column(Boolean, default=True)
    auto_alert_escalations: Mapped[bool] = mapped_column(Boolean, default=True)
    draft_tone: Mapped[str] = mapped_column(String(50), default="professional")
    draft_language: Mapped[str] = mapped_column(String(50), default="en")
    max_drafts_per_day: Mapped[int] = mapped_column(Integer, default=50)

    # Escalation keywords (company-specific)
    escalation_keywords: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # ["urgent", "asap", "escalation", "SLA", "critical"]

    # Resume processing
    auto_add_candidates: Mapped[bool] = mapped_column(Boolean, default=False)
    minimum_match_score_to_auto_add: Mapped[float] = mapped_column(Float, default=70.0)
    default_requirement_ids_for_matching: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Summary delivery
    daily_summary_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    daily_summary_time: Mapped[str] = mapped_column(String(10), default="09:00")
    daily_summary_channels: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # [{type: "slack", channel: "#daily-digest"}, {type: "email", to: "team@company.com"}]

    # Ignore rules
    ignored_senders: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    ignored_domains: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    spam_filter_enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    updated_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)


class CompanyBrandingConfig(BaseModel):
    """Per-organization branding and white-label settings."""
    __tablename__ = "company_branding_configs"

    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), unique=True, index=True)
    company_name: Mapped[str] = mapped_column(String(255))
    logo_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    favicon_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    primary_color: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # #6366f1
    secondary_color: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    email_footer_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    email_signature_template: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notification_from_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    custom_domain: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), default="America/Chicago")
    date_format: Mapped[str] = mapped_column(String(20), default="MM/DD/YYYY")
    currency: Mapped[str] = mapped_column(String(10), default="USD")
