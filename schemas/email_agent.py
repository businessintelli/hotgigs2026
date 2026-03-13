"""Pydantic schemas for the Email Agent module."""
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ── Email Account Schemas ──────────────────────────────────
class EmailAccountCreate(BaseModel):
    email_address: str
    provider: str = "gmail"
    folders_monitored: Optional[List[str]] = ["INBOX"]
    auto_classify: bool = True
    auto_draft: bool = False
    auto_alert_escalations: bool = True

class EmailAccountResponse(BaseModel):
    id: int
    email_address: str
    provider: str
    is_active: bool
    last_synced_at: Optional[datetime] = None
    folders_monitored: Optional[List[str]] = None
    auto_classify: bool
    auto_draft: bool
    auto_alert_escalations: bool


# ── Email Message Schemas ──────────────────────────────────
class EmailMessageResponse(BaseModel):
    id: int
    from_address: str
    from_name: Optional[str] = None
    to_addresses: Optional[List[Dict[str, str]]] = None
    cc_addresses: Optional[List[Dict[str, str]]] = None
    subject: str
    body_text: Optional[str] = None
    received_at: datetime
    is_read: bool
    has_attachments: bool
    attachment_count: int
    classification: Optional[str] = None
    priority: Optional[str] = None
    confidence_score: Optional[float] = None
    ai_summary: Optional[str] = None
    requires_response: bool
    is_user_in_cc_only: bool
    sentiment: Optional[str] = None
    classification_tags: Optional[List[str]] = None
    draft_generated: bool
    alert_sent: bool
    resume_processed: bool
    action_items_extracted: bool

class EmailClassifyRequest(BaseModel):
    email_ids: List[int]

class EmailClassifyResponse(BaseModel):
    email_id: int
    classification: str
    priority: str
    confidence: float
    summary: str
    requires_response: bool


# ── Draft Schemas ──────────────────────────────────────────
class DraftResponse(BaseModel):
    id: int
    email_message_id: int
    draft_subject: str
    draft_body: str
    draft_tone: str
    status: str
    ai_reasoning: Optional[str] = None
    confidence_score: Optional[float] = None
    created_at: datetime

class DraftUpdateRequest(BaseModel):
    edited_body: Optional[str] = None
    draft_tone: Optional[str] = None
    status: Optional[str] = None
    review_notes: Optional[str] = None


# ── Action Item Schemas ────────────────────────────────────
class ActionItemResponse(BaseModel):
    id: int
    source: str
    title: str
    description: Optional[str] = None
    assigned_to_name: Optional[str] = None
    assigned_to_email: Optional[str] = None
    due_date: Optional[date] = None
    priority: str
    status: str
    is_escalation: bool
    escalation_reason: Optional[str] = None
    follow_up_count: int
    email_subject: Optional[str] = None
    meeting_title: Optional[str] = None

class ActionItemUpdateRequest(BaseModel):
    status: Optional[str] = None
    assigned_to_user_id: Optional[int] = None
    due_date: Optional[date] = None
    priority: Optional[str] = None


# ── MOM Schemas ────────────────────────────────────────────
class MeetingMinutesResponse(BaseModel):
    id: int
    meeting_title: str
    meeting_date: Optional[date] = None
    attendees: Optional[List[Dict[str, str]]] = None
    key_decisions: Optional[List[str]] = None
    summary: str
    total_action_items: int
    escalated_items_count: int
    action_items: Optional[List[ActionItemResponse]] = None


# ── Notification Channel Schemas ───────────────────────────
class ChannelCreateRequest(BaseModel):
    channel_type: str  # slack, whatsapp, telegram
    channel_identifier: str
    channel_name: Optional[str] = None
    webhook_url: Optional[str] = None
    is_primary: bool = False
    notification_preferences: Optional[Dict[str, bool]] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    timezone: Optional[str] = None

class ChannelResponse(BaseModel):
    id: int
    channel_type: str
    channel_identifier: str
    channel_name: Optional[str] = None
    is_active: bool
    is_primary: bool
    notification_preferences: Optional[Dict[str, bool]] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None


# ── Alert Schemas ──────────────────────────────────────────
class AlertResponse(BaseModel):
    id: int
    channel_type: str
    alert_type: str
    title: str
    message: str
    priority: str
    status: str
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None


# ── Resume Capture Schemas ─────────────────────────────────
class ResumeCaptureResponse(BaseModel):
    id: int
    candidate_name: Optional[str] = None
    candidate_email: Optional[str] = None
    source_type: str
    attachment_filename: Optional[str] = None
    parsed_successfully: bool
    skills_extracted: Optional[List[str]] = None
    experience_years: Optional[float] = None
    current_title: Optional[str] = None
    current_company: Optional[str] = None
    match_score: Optional[float] = None
    match_level: Optional[str] = None
    match_breakdown: Optional[Dict[str, float]] = None
    recommendation: Optional[str] = None
    recommendation_notes: Optional[str] = None
    added_to_platform: bool
    review_status: Optional[str] = None
    email_subject: Optional[str] = None
    email_from: Optional[str] = None


# ── Slack Schemas ──────────────────────────────────────────
class SlackWorkspaceResponse(BaseModel):
    id: int
    workspace_id: str
    workspace_name: str
    is_active: bool
    channels_config: Optional[Dict[str, str]] = None

class SlackChannelMappingCreate(BaseModel):
    event_type: str
    channel_id: str
    channel_name: str
    message_template: Optional[str] = None
    mention_roles: Optional[List[str]] = None
    auto_thread: bool = True

class SlackChannelMappingResponse(BaseModel):
    id: int
    event_type: str
    channel_id: str
    channel_name: str
    is_active: bool
    auto_thread: bool


# ── Agent Config Schemas ───────────────────────────────────
class AgentConfigResponse(BaseModel):
    is_enabled: bool
    auto_classify: bool
    auto_draft_responses: bool
    auto_process_resumes: bool
    auto_extract_action_items: bool
    auto_alert_escalations: bool
    daily_summary_enabled: bool
    daily_summary_time: Optional[str] = None
    escalation_keywords: Optional[List[str]] = None
    max_drafts_per_day: int

class AgentConfigUpdateRequest(BaseModel):
    is_enabled: Optional[bool] = None
    auto_classify: Optional[bool] = None
    auto_draft_responses: Optional[bool] = None
    auto_process_resumes: Optional[bool] = None
    auto_extract_action_items: Optional[bool] = None
    auto_alert_escalations: Optional[bool] = None
    daily_summary_enabled: Optional[bool] = None
    daily_summary_time: Optional[str] = None
    escalation_keywords: Optional[List[str]] = None
    max_drafts_per_day: Optional[int] = None


# ── Dashboard Schemas ──────────────────────────────────────
class EmailAgentDashboardResponse(BaseModel):
    total_emails_today: int
    action_required: int
    escalations: int
    fyi_emails: int
    resumes_captured: int
    drafts_generated: int
    action_items_pending: int
    alerts_sent_today: int
    classification_breakdown: Dict[str, int]
    priority_breakdown: Dict[str, int]
    top_senders: List[Dict[str, Any]]
    recent_escalations: List[Dict[str, Any]]

class SlackCollabDashboardResponse(BaseModel):
    total_channels_mapped: int
    messages_sent_today: int
    active_threads: int
    pending_requests: Dict[str, int]
    recent_activity: List[Dict[str, Any]]
