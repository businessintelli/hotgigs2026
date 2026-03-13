"""Email Agent models — intelligent email reading, classification, drafting, and MOM extraction."""
from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import (
    String, DateTime, Date, Enum, JSON, ForeignKey, Text, Float, Integer,
    Boolean, Index, func, Numeric
)
from sqlalchemy.orm import Mapped, mapped_column
from models.base import BaseModel
import enum


# ── Enums ──────────────────────────────────────────────────

class EmailClassification(str, enum.Enum):
    ACTION_REQUIRED = "action_required"
    ESCALATION_URGENT = "escalation_urgent"
    CANDIDATE_APPLICATION = "candidate_application"
    REQUIREMENT_PUBLISHED = "requirement_published"
    MEETING_MINUTES = "meeting_minutes"
    INTERVIEW_REQUEST = "interview_request"
    INTERVIEW_RESCHEDULE = "interview_reschedule"
    ONBOARDING_RELATED = "onboarding_related"
    OFFBOARDING_RELATED = "offboarding_related"
    TIMESHEET_APPROVAL = "timesheet_approval"
    INVOICE_RELATED = "invoice_related"
    FYI_CC = "fyi_cc"
    NEWSLETTER = "newsletter"
    SPAM = "spam"
    GENERAL = "general"


class EmailPriority(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    FYI = "fyi"


class DraftStatus(str, enum.Enum):
    GENERATED = "generated"
    REVIEWED = "reviewed"
    EDITED = "edited"
    SENT = "sent"
    DISCARDED = "discarded"


class ActionItemStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ESCALATED = "escalated"
    OVERDUE = "overdue"


class ActionItemSource(str, enum.Enum):
    EMAIL_BODY = "email_body"
    MOM_DOCUMENT = "mom_document"
    ATTACHMENT = "attachment"
    THREAD_CONTEXT = "thread_context"


class AlertChannel(str, enum.Enum):
    SLACK = "slack"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    IN_APP = "in_app"
    SMS = "sms"
    EMAIL = "email"
    TEAMS = "teams"


class AlertStatus(str, enum.Enum):
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    EXPIRED = "expired"


class ResumeSourceType(str, enum.Enum):
    EMAIL_ATTACHMENT = "email_attachment"
    JOB_BOARD = "job_board"
    CAREER_PAGE = "career_page"
    REFERRAL = "referral"
    LINKEDIN = "linkedin"
    DIRECT_UPLOAD = "direct_upload"


class MatchScoreLevel(str, enum.Enum):
    EXCELLENT = "excellent"      # 90-100
    STRONG = "strong"            # 75-89
    GOOD = "good"                # 60-74
    FAIR = "fair"                # 40-59
    POOR = "poor"                # 0-39


# ── Email Inbox Models ─────────────────────────────────────

class EmailAccount(BaseModel):
    """Connected email accounts for the agent to monitor."""
    __tablename__ = "email_accounts"

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    organization_id: Mapped[int] = mapped_column(Integer, index=True)
    email_address: Mapped[str] = mapped_column(String(255))
    provider: Mapped[str] = mapped_column(String(50))  # gmail, outlook, exchange
    access_token_encrypted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    refresh_token_encrypted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    sync_from_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    folders_monitored: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # ["INBOX", "Recruiting"]
    auto_classify: Mapped[bool] = mapped_column(Boolean, default=True)
    auto_draft: Mapped[bool] = mapped_column(Boolean, default=False)
    auto_alert_escalations: Mapped[bool] = mapped_column(Boolean, default=True)


class EmailMessage(BaseModel):
    """Ingested email messages with AI classification."""
    __tablename__ = "email_messages"

    email_account_id: Mapped[int] = mapped_column(Integer, ForeignKey("email_accounts.id"), index=True)
    organization_id: Mapped[int] = mapped_column(Integer, index=True)
    message_id: Mapped[str] = mapped_column(String(512), unique=True)  # RFC message-id
    thread_id: Mapped[Optional[str]] = mapped_column(String(512), nullable=True, index=True)
    from_address: Mapped[str] = mapped_column(String(255))
    from_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    to_addresses: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # [{email, name}]
    cc_addresses: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    bcc_addresses: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    subject: Mapped[str] = mapped_column(String(1000))
    body_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    body_html: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    received_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    has_attachments: Mapped[bool] = mapped_column(Boolean, default=False)
    attachment_count: Mapped[int] = mapped_column(Integer, default=0)
    attachments_meta: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # [{filename, size, mime}]

    # AI classification
    classification: Mapped[Optional[str]] = mapped_column(
        Enum(EmailClassification), nullable=True, index=True
    )
    priority: Mapped[Optional[str]] = mapped_column(
        Enum(EmailPriority), nullable=True, index=True
    )
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ai_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    requires_response: Mapped[bool] = mapped_column(Boolean, default=False)
    is_user_in_cc_only: Mapped[bool] = mapped_column(Boolean, default=False)
    sentiment: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # positive, neutral, negative, urgent
    detected_entities: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # {candidates, requirements, companies}
    classification_tags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # ["recruitment", "interview", etc.]

    # Processing state
    draft_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    alert_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    resume_processed: Mapped[bool] = mapped_column(Boolean, default=False)
    action_items_extracted: Mapped[bool] = mapped_column(Boolean, default=False)

    __table_args__ = (
        Index("ix_email_messages_org_class", "organization_id", "classification"),
        Index("ix_email_messages_org_priority", "organization_id", "priority"),
    )


class EmailDraft(BaseModel):
    """AI-generated response drafts for emails requiring attention."""
    __tablename__ = "email_drafts"

    email_message_id: Mapped[int] = mapped_column(Integer, ForeignKey("email_messages.id"), index=True)
    organization_id: Mapped[int] = mapped_column(Integer, index=True)
    drafted_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    draft_subject: Mapped[str] = mapped_column(String(1000))
    draft_body: Mapped[str] = mapped_column(Text)
    draft_tone: Mapped[str] = mapped_column(String(50), default="professional")  # professional, friendly, formal, urgent
    status: Mapped[str] = mapped_column(Enum(DraftStatus), default=DraftStatus.GENERATED)
    ai_reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # why this response
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    suggested_recipients: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # to/cc overrides
    edited_body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    reviewed_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    review_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class EmailSummary(BaseModel):
    """Summarized view of FYI/CC emails grouped by topic."""
    __tablename__ = "email_summaries"

    organization_id: Mapped[int] = mapped_column(Integer, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    summary_date: Mapped[date] = mapped_column(Date, index=True)
    summary_type: Mapped[str] = mapped_column(String(50), default="daily")  # daily, weekly
    total_emails: Mapped[int] = mapped_column(Integer, default=0)
    action_required_count: Mapped[int] = mapped_column(Integer, default=0)
    fyi_count: Mapped[int] = mapped_column(Integer, default=0)
    escalation_count: Mapped[int] = mapped_column(Integer, default=0)
    recruitment_count: Mapped[int] = mapped_column(Integer, default=0)
    summary_text: Mapped[str] = mapped_column(Text)
    topic_clusters: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    email_ids: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # [email_message_ids]
    delivered_via: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # ["slack", "in_app"]


# ── MOM & Action Items ─────────────────────────────────────

class MeetingMinutes(BaseModel):
    """Extracted meeting minutes from email content."""
    __tablename__ = "meeting_minutes"

    email_message_id: Mapped[int] = mapped_column(Integer, ForeignKey("email_messages.id"), index=True)
    organization_id: Mapped[int] = mapped_column(Integer, index=True)
    meeting_title: Mapped[str] = mapped_column(String(500))
    meeting_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    attendees: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # [{name, email, role}]
    key_decisions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # [decision_text]
    discussion_topics: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    summary: Mapped[str] = mapped_column(Text)
    next_meeting_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    total_action_items: Mapped[int] = mapped_column(Integer, default=0)
    escalated_items_count: Mapped[int] = mapped_column(Integer, default=0)


class ActionItem(BaseModel):
    """Action items extracted from emails or MOMs."""
    __tablename__ = "email_action_items"

    email_message_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("email_messages.id"), nullable=True, index=True)
    meeting_minutes_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("meeting_minutes.id"), nullable=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, index=True)
    source: Mapped[str] = mapped_column(Enum(ActionItemSource))
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    assigned_to_user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    assigned_to_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    assigned_to_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    assigned_by_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    priority: Mapped[str] = mapped_column(Enum(EmailPriority), default=EmailPriority.MEDIUM)
    status: Mapped[str] = mapped_column(Enum(ActionItemStatus), default=ActionItemStatus.PENDING, index=True)
    is_escalation: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    escalation_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    follow_up_count: Mapped[int] = mapped_column(Integer, default=0)
    last_follow_up_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    alert_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    related_entity_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # candidate, requirement, placement
    related_entity_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)


# ── Notification & Alert Models ────────────────────────────

class NotificationChannel(BaseModel):
    """User's connected notification channels (Slack, WhatsApp, Telegram, etc.)."""
    __tablename__ = "notification_channels"

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    organization_id: Mapped[int] = mapped_column(Integer, index=True)
    channel_type: Mapped[str] = mapped_column(Enum(AlertChannel), index=True)
    channel_identifier: Mapped[str] = mapped_column(String(500))  # slack user ID, phone number, telegram chat ID
    channel_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # "My Work Slack", "+1-555-0123"
    webhook_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    access_token_encrypted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    notification_preferences: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # preferences: {escalations: true, daily_summary: true, action_items: true, recruitment: false}
    quiet_hours_start: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # "22:00"
    quiet_hours_end: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)    # "08:00"
    timezone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)


class AlertNotification(BaseModel):
    """Individual alert notifications sent to users."""
    __tablename__ = "alert_notifications"

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    organization_id: Mapped[int] = mapped_column(Integer, index=True)
    channel_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("notification_channels.id"), nullable=True)
    channel_type: Mapped[str] = mapped_column(Enum(AlertChannel))
    alert_type: Mapped[str] = mapped_column(String(100), index=True)  # escalation, action_item, daily_summary, etc.
    title: Mapped[str] = mapped_column(String(500))
    message: Mapped[str] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(Enum(EmailPriority), default=EmailPriority.MEDIUM)
    status: Mapped[str] = mapped_column(Enum(AlertStatus), default=AlertStatus.QUEUED, index=True)
    source_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # email, action_item, mom
    source_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    external_message_id: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # Slack ts, WhatsApp msg ID
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)


# ── Slack Integration Models ───────────────────────────────

class SlackWorkspace(BaseModel):
    """Connected Slack workspaces for team collaboration."""
    __tablename__ = "slack_workspaces"

    organization_id: Mapped[int] = mapped_column(Integer, index=True)
    workspace_id: Mapped[str] = mapped_column(String(100), unique=True)
    workspace_name: Mapped[str] = mapped_column(String(255))
    bot_token_encrypted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    bot_user_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    installed_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    default_channel_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    channels_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # channels_config: {onboarding: "#onboarding", interviews: "#interviews", escalations: "#escalations"}


class SlackChannelMapping(BaseModel):
    """Maps platform events to Slack channels."""
    __tablename__ = "slack_channel_mappings"

    workspace_id: Mapped[int] = mapped_column(Integer, ForeignKey("slack_workspaces.id"), index=True)
    organization_id: Mapped[int] = mapped_column(Integer, index=True)
    event_type: Mapped[str] = mapped_column(String(100), index=True)
    # event_types: onboarding, offboarding, interview_request, interview_reschedule, escalation, etc.
    channel_id: Mapped[str] = mapped_column(String(100))
    channel_name: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    message_template: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Slack Block Kit template
    mention_roles: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # ["@recruiters", "@hiring-managers"]
    auto_thread: Mapped[bool] = mapped_column(Boolean, default=True)


# ── Email-to-Resume Processing Models ──────────────────────

class EmailResumeCapture(BaseModel):
    """Resumes extracted from emails for processing."""
    __tablename__ = "email_resume_captures"

    email_message_id: Mapped[int] = mapped_column(Integer, ForeignKey("email_messages.id"), index=True)
    organization_id: Mapped[int] = mapped_column(Integer, index=True)
    candidate_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    candidate_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    candidate_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    source_type: Mapped[str] = mapped_column(Enum(ResumeSourceType), default=ResumeSourceType.EMAIL_ATTACHMENT)
    attachment_filename: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    attachment_size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    file_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Parsing results
    parsed_successfully: Mapped[bool] = mapped_column(Boolean, default=False)
    parsed_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # parsed_data: {skills, experience_years, education, certifications, current_title, current_company, etc.}
    skills_extracted: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # ["Python", "React", "AWS"]
    experience_years: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    education_level: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    current_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    current_company: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Match scoring
    matched_requirement_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    match_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    match_level: Mapped[Optional[str]] = mapped_column(Enum(MatchScoreLevel), nullable=True)
    match_breakdown: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # match_breakdown: {skills: 85, experience: 70, education: 90, location: 60, overall: 76}
    recommendation: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # strong_yes, yes, maybe, no
    recommendation_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Platform integration
    candidate_id_created: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    added_to_platform: Mapped[bool] = mapped_column(Boolean, default=False)
    added_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    reviewed_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    review_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # pending, approved, rejected


# ── Agent Configuration ────────────────────────────────────

class EmailAgentConfig(BaseModel):
    """Per-organization email agent configuration."""
    __tablename__ = "email_agent_configs"

    organization_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    auto_classify: Mapped[bool] = mapped_column(Boolean, default=True)
    auto_draft_responses: Mapped[bool] = mapped_column(Boolean, default=False)
    auto_process_resumes: Mapped[bool] = mapped_column(Boolean, default=True)
    auto_extract_action_items: Mapped[bool] = mapped_column(Boolean, default=True)
    auto_alert_escalations: Mapped[bool] = mapped_column(Boolean, default=True)
    daily_summary_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    daily_summary_time: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # "09:00"
    escalation_keywords: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # ["urgent", "asap", "escalation", "immediately", "critical", "SLA breach"]
    recruitment_email_patterns: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # ["*@jobs.linkedin.com", "*@apply.indeed.com", "applications@*"]
    ignored_senders: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    ai_model: Mapped[str] = mapped_column(String(100), default="gpt-4o")
    max_drafts_per_day: Mapped[int] = mapped_column(Integer, default=50)
    retention_days: Mapped[int] = mapped_column(Integer, default=90)
