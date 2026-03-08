"""Pydantic schemas for automation, search, and notifications."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ===== SAVED SEARCH SCHEMAS =====

class CandidateSearchFilter(BaseModel):
    """Filters for candidate search."""
    skills: Optional[List[str]] = None
    location: Optional[str] = None
    experience_min: Optional[int] = None
    experience_max: Optional[int] = None
    availability_status: Optional[str] = None
    tags: Optional[List[str]] = None
    min_score: Optional[float] = None
    status: Optional[List[str]] = None


class CandidateSearchRequest(BaseModel):
    """Advanced candidate search request."""
    skills: Optional[List[str]] = None
    location: Optional[str] = None
    experience_min: Optional[int] = None
    experience_max: Optional[int] = None
    availability_status: Optional[str] = None
    tags: Optional[List[str]] = None
    min_match_score: Optional[float] = Field(None, ge=0, le=100)
    salary_range_min: Optional[float] = None
    salary_range_max: Optional[float] = None
    current_title: Optional[str] = None
    certifications: Optional[List[str]] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)


class CandidateMatch(BaseModel):
    """Candidate match result."""
    id: int
    first_name: str
    last_name: str
    email: str
    current_title: Optional[str]
    location_city: Optional[str]
    location_country: Optional[str]
    total_experience_years: Optional[float]
    match_score: float = Field(..., ge=0, le=100, description="Relevance score 0-100")
    matched_fields: Dict[str, str] = Field(default_factory=dict, description="Highlighted matching fields")
    status: str


class CandidateSearchResponse(BaseModel):
    """Advanced candidate search response."""
    total: int
    results: List[CandidateMatch]
    filters_applied: Dict[str, Any]


class SavedSearchCreate(BaseModel):
    """Create saved search request."""
    name: str = Field(..., min_length=1, max_length=255)
    search_type: str = Field(..., description="CANDIDATE, REQUIREMENT, SUBMISSION, SUPPLIER")
    filters: Dict[str, Any] = Field(..., description="Filter criteria")
    sort_by: Optional[str] = None
    sort_order: str = Field("desc", pattern="^(asc|desc)$")
    is_default: bool = False


class SavedSearchUpdate(BaseModel):
    """Update saved search request."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    filters: Optional[Dict[str, Any]] = None
    sort_by: Optional[str] = None
    sort_order: Optional[str] = Field(None, pattern="^(asc|desc)$")
    is_default: Optional[bool] = None


class SavedSearchResponse(BaseModel):
    """Saved search response."""
    id: int
    name: str
    search_type: str
    filters: Dict[str, Any]
    sort_by: Optional[str]
    sort_order: str
    is_default: bool
    result_count: int
    last_run_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== AUTOMATION RULE SCHEMAS =====

class AutomationRuleCreate(BaseModel):
    """Create automation rule request."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    trigger_event: str = Field(..., description="Event that triggers the rule")
    trigger_conditions: Dict[str, Any] = Field(default_factory=dict)
    action_type: str = Field(..., description="Type of action to perform")
    action_config: Dict[str, Any] = Field(default_factory=dict)
    is_enabled: bool = True


class AutomationRuleUpdate(BaseModel):
    """Update automation rule request."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    trigger_conditions: Optional[Dict[str, Any]] = None
    action_config: Optional[Dict[str, Any]] = None
    is_enabled: Optional[bool] = None


class AutomationRuleResponse(BaseModel):
    """Automation rule response."""
    id: int
    name: str
    description: Optional[str]
    trigger_event: str
    trigger_conditions: Dict[str, Any]
    action_type: str
    action_config: Dict[str, Any]
    is_enabled: bool
    execution_count: int
    last_triggered_at: Optional[datetime]
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AutomationRuleTestRequest(BaseModel):
    """Test automation rule with sample data."""
    rule_id: int
    sample_data: Dict[str, Any]


class AutomationRuleTestResponse(BaseModel):
    """Test automation rule response."""
    success: bool
    rule_id: int
    action_type: str
    would_execute: bool
    message: str
    dry_run_output: Optional[Dict[str, Any]] = None


# ===== NOTIFICATION SCHEMAS =====

class NotificationCreate(BaseModel):
    """Create notification request."""
    user_id: int
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(...)
    notification_type: str = Field("info", description="INFO, WARNING, ALERT, SUCCESS, ACTION_REQUIRED")
    category: str = Field(..., description="SUBMISSION, INTERVIEW, OFFER, COMPLIANCE, SLA, TIMESHEET, SYSTEM")
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    action_url: Optional[str] = None


class NotificationUpdate(BaseModel):
    """Update notification request."""
    is_read: Optional[bool] = None


class NotificationResponse(BaseModel):
    """Notification response."""
    id: int
    user_id: int
    title: str
    message: str
    notification_type: str
    category: str
    reference_type: Optional[str]
    reference_id: Optional[int]
    is_read: bool
    read_at: Optional[datetime]
    action_url: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Notification list response."""
    total: int
    unread_count: int
    notifications: List[NotificationResponse]


class NotificationUnreadCount(BaseModel):
    """Unread notification count response."""
    unread_count: int
    by_category: Optional[Dict[str, int]] = None


# ===== AUTOMATION DASHBOARD SCHEMAS =====

class AutomationDashboardResponse(BaseModel):
    """Automation dashboard summary."""
    active_rules_count: int
    total_rules_count: int
    recent_triggers: List[Dict[str, Any]]
    notifications_summary: Dict[str, int]
    top_triggered_rules: List[Dict[str, Any]]
    last_updated: datetime
