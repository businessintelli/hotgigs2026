"""Pydantic schemas for security and RBAC."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from schemas.common import BaseResponse


# ===== Permission Schemas =====


class PermissionCreate(BaseModel):
    """Create permission."""

    name: str = Field(..., min_length=1, max_length=255)
    resource: str = Field(..., min_length=1, max_length=100)
    action: str = Field(..., min_length=1, max_length=50)
    scope: str = Field(default="own", max_length=50)
    description: Optional[str] = Field(None, max_length=1000)


class PermissionResponse(BaseResponse):
    """Permission response."""

    name: str
    resource: str
    action: str
    scope: str
    description: Optional[str] = None
    is_system: bool

    class Config:
        from_attributes = True


# ===== Role Template Schemas =====


class RoleTemplateCreate(BaseModel):
    """Create role template."""

    name: str = Field(..., min_length=1, max_length=100)
    display_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    permissions: Optional[List[int]] = None
    agent_access: Optional[Dict[str, List[str]]] = None
    feature_access: Optional[Dict[str, bool]] = None


class RoleTemplateUpdate(BaseModel):
    """Update role template."""

    display_name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    permissions: Optional[List[int]] = None
    agent_access: Optional[Dict[str, List[str]]] = None
    feature_access: Optional[Dict[str, bool]] = None
    is_active: Optional[bool] = None


class RoleTemplateResponse(BaseResponse):
    """Role template response."""

    name: str
    display_name: str
    description: Optional[str] = None
    permissions: Optional[List[Dict[str, Any]]] = None
    agent_access: Optional[Dict[str, List[str]]] = None
    feature_access: Optional[Dict[str, bool]] = None
    is_system: bool
    is_active: bool

    class Config:
        from_attributes = True


# ===== User Role Assignment Schemas =====


class UserRoleAssignmentCreate(BaseModel):
    """Assign role to user."""

    user_id: int
    role_template_id: int
    expires_at: Optional[datetime] = None


class UserRoleAssignmentResponse(BaseResponse):
    """User role assignment response."""

    user_id: int
    role_template_id: int
    role_template_name: str
    assigned_by: Optional[int] = None
    assigned_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool

    class Config:
        from_attributes = True


# ===== API Key Schemas =====


class APIKeyCreate(BaseModel):
    """Create API key."""

    name: str = Field(..., min_length=1, max_length=255)
    scope: Optional[Dict[str, List[str]]] = None
    expires_in_days: Optional[int] = Field(None, ge=1, le=36500)


class APIKeyResponse(BaseResponse):
    """API key response (without secret)."""

    user_id: int
    key_prefix: str
    name: str
    scope: Optional[Dict[str, List[str]]] = None
    is_active: bool
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    last_used_ip: Optional[str] = None
    revoked_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class APIKeyGeneratedResponse(BaseModel):
    """API key generation response with secret."""

    key: str
    key_prefix: str
    name: str
    expires_at: Optional[datetime] = None
    message: str = "Save this key securely. You won't be able to see it again."


# ===== Access Log Schemas =====


class AccessLogResponse(BaseResponse):
    """Access log response."""

    user_id: Optional[int] = None
    api_key_id: Optional[int] = None
    resource: str
    action: str
    entity_id: Optional[int] = None
    result: str
    ip_address: str
    user_agent: Optional[str] = None
    request_path: str
    request_method: str
    response_status: Optional[int] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class AccessLogQuery(BaseModel):
    """Query parameters for access logs."""

    user_id: Optional[int] = None
    resource: Optional[str] = None
    action: Optional[str] = None
    result: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


# ===== Security Alert Schemas =====


class SecurityAlertResponse(BaseResponse):
    """Security alert response."""

    user_id: Optional[int] = None
    alert_type: str
    severity: str
    description: str
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    status: str
    resolved_by: Optional[int] = None
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SecurityAlertUpdate(BaseModel):
    """Update security alert."""

    status: Optional[str] = Field(None, max_length=50)


# ===== Session Policy Schemas =====


class SessionPolicyCreate(BaseModel):
    """Create session policy."""

    name: str = Field(..., min_length=1, max_length=255)
    max_session_duration_hours: int = Field(default=8, ge=1)
    max_concurrent_sessions: int = Field(default=3, ge=1)
    idle_timeout_minutes: int = Field(default=30, ge=1)
    ip_restriction_enabled: bool = False
    allowed_ips: Optional[List[str]] = None
    mfa_required: bool = False
    applies_to_roles: Optional[List[str]] = None


class SessionPolicyUpdate(BaseModel):
    """Update session policy."""

    max_session_duration_hours: Optional[int] = Field(None, ge=1)
    max_concurrent_sessions: Optional[int] = Field(None, ge=1)
    idle_timeout_minutes: Optional[int] = Field(None, ge=1)
    ip_restriction_enabled: Optional[bool] = None
    allowed_ips: Optional[List[str]] = None
    mfa_required: Optional[bool] = None
    applies_to_roles: Optional[List[str]] = None
    is_active: Optional[bool] = None


class SessionPolicyResponse(BaseResponse):
    """Session policy response."""

    name: str
    max_session_duration_hours: int
    max_concurrent_sessions: int
    idle_timeout_minutes: int
    ip_restriction_enabled: bool
    allowed_ips: Optional[List[str]] = None
    mfa_required: bool
    applies_to_roles: Optional[List[str]] = None
    is_active: bool

    class Config:
        from_attributes = True


# ===== Security Dashboard Schemas =====


class SecurityDashboard(BaseModel):
    """Security dashboard data."""

    active_users_count: int
    recent_access_count: int
    failed_access_attempts: int
    suspicious_activities: List[SecurityAlertResponse]
    permission_distribution: Dict[str, int]
    top_accessed_resources: List[Dict[str, Any]]
    access_by_role: Dict[str, int]
    api_keys_active: int
    sessions_active: int
    alerts_open: int


# ===== Permission Check Response =====


class PermissionCheckResponse(BaseModel):
    """Permission check result."""

    user_id: int
    resource: str
    action: str
    has_permission: bool
    scope: Optional[str] = None
    reason: Optional[str] = None


# ===== User Effective Permissions =====


class UserEffectivePermissions(BaseModel):
    """User's effective permissions from all assigned roles."""

    user_id: int
    roles: List[str]
    permissions: List[Dict[str, str]]  # {resource, action, scope}
    agent_access: Dict[str, List[str]]
    feature_access: Dict[str, bool]
    effective_at: datetime
    expires_at: Optional[datetime] = None


# ===== Security Report =====


class SecurityReport(BaseModel):
    """Comprehensive security audit report."""

    period: str
    generated_at: datetime
    total_access_logs: int
    successful_accesses: int
    denied_accesses: int
    unique_users: int
    unique_resources: int
    top_users_by_activity: List[Dict[str, Any]]
    top_resources_accessed: List[Dict[str, Any]]
    security_alerts_summary: Dict[str, int]
    failed_logins: int
    suspicious_activities: int
    api_key_usage: Dict[str, int]
    role_distribution: Dict[str, int]
    recommendations: List[str]
