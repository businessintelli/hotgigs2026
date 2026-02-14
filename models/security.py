"""Security, RBAC, and access control models."""

from datetime import datetime
from typing import Optional, Dict, List, Any
from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, JSON, ForeignKey, Index, func, UniqueConstraint, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import BaseModel
from database.base import Base


# Association table for many-to-many between permissions and role_templates
role_template_permissions = Table(
    "role_template_permissions",
    Base.metadata,
    Column("role_template_id", Integer, ForeignKey("role_templates.id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True),
)


class Permission(BaseModel):
    """Granular permission for resource + action access control."""

    __tablename__ = "permissions"

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    resource: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    scope: Mapped[str] = mapped_column(String(50), default="own", nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    role_templates: "Mapped[List[RoleTemplate]]" = relationship("RoleTemplate", secondary=role_template_permissions, back_populates="permissions")

    __table_args__ = (
        Index("ix_permission_resource_action", "resource", "action"),
    )


class RoleTemplate(BaseModel):
    """Role template with bundled permissions and agent/feature access."""

    __tablename__ = "role_templates"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    json_permissions: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column("permissions_json", JSON, nullable=True)
    agent_access: Mapped[Optional[Dict[str, List[str]]]] = mapped_column(JSON, nullable=True)
    feature_access: Mapped[Optional[Dict[str, bool]]] = mapped_column(JSON, nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    permissions: "Mapped[List[Permission]]" = relationship("Permission", secondary=role_template_permissions, back_populates="role_templates")
    user_assignments: "Mapped[List[UserRoleAssignment]]" = relationship("UserRoleAssignment", back_populates="role_template", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_role_template_is_active", "is_active"),
    )


class UserRoleAssignment(BaseModel):
    """Assignment of roles to users."""

    __tablename__ = "user_role_assignments"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    role_template_id: Mapped[int] = mapped_column(ForeignKey("role_templates.id"), index=True, nullable=False)
    assigned_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    role_template: "Mapped[RoleTemplate]" = relationship("RoleTemplate", back_populates="user_assignments")

    __table_args__ = (
        Index("ix_user_role_assignment_user_role", "user_id", "role_template_id"),
        Index("ix_user_role_assignment_is_active", "is_active"),
        UniqueConstraint("user_id", "role_template_id", name="uq_user_role_assignment"),
    )


class APIKey(BaseModel):
    """API key for service authentication and integration."""

    __tablename__ = "api_keys"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    key_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)  # Never store plaintext
    key_prefix: Mapped[str] = mapped_column(String(10), nullable=False)  # First chars for identification
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    scope: Mapped[Optional[Dict[str, List[str]]]] = mapped_column(JSON, nullable=True)  # Allowed resources and actions
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_used_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_api_key_user_is_active", "user_id", "is_active"),
    )


class AccessLog(BaseModel):
    """Audit log for all resource access."""

    __tablename__ = "access_logs"

    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), index=True, nullable=True)
    api_key_id: Mapped[Optional[int]] = mapped_column(ForeignKey("api_keys.id"), nullable=True)
    resource: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    result: Mapped[str] = mapped_column(String(20), nullable=False)  # allowed/denied
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    request_path: Mapped[str] = mapped_column(String(500), nullable=False)
    request_method: Mapped[str] = mapped_column(String(10), nullable=False)
    response_status: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True, nullable=False)

    __table_args__ = (
        Index("ix_access_log_timestamp", "timestamp"),
        Index("ix_access_log_user_resource", "user_id", "resource"),
    )


class SecurityAlert(BaseModel):
    """Security incident alerts."""

    __tablename__ = "security_alerts"

    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), index=True, nullable=True)
    alert_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False)  # failed_login/suspicious_access/bulk_export/privilege_escalation/brute_force
    severity: Mapped[str] = mapped_column(String(20), nullable=False)  # low/medium/high/critical
    description: Mapped[str] = mapped_column(Text, nullable=False)
    details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="open", nullable=False)  # open/investigating/resolved/dismissed
    resolved_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_security_alert_status", "status"),
        Index("ix_security_alert_severity", "severity"),
        Index("ix_security_alert_created_at", "created_at"),
    )


class SessionPolicy(BaseModel):
    """Session security policies."""

    __tablename__ = "session_policies"

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    max_session_duration_hours: Mapped[int] = mapped_column(Integer, default=8, nullable=False)
    max_concurrent_sessions: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    idle_timeout_minutes: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    ip_restriction_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    allowed_ips: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    mfa_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    applies_to_roles: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)  # null = all roles
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (
        Index("ix_session_policy_is_active", "is_active"),
    )
