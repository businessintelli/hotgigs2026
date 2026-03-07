"""Tenant management models — membership, invitations, audit, settings."""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Enum, JSON, ForeignKey, Text, Boolean, Index, func, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import BaseModel
from models.enums import UserRole, AuditAction


class OrganizationMembership(BaseModel):
    """
    Tracks user membership in organizations.
    A user can belong to multiple organizations with different roles.
    """

    __tablename__ = "organization_memberships"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(
        Enum(UserRole), nullable=False
    )
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    department: Mapped[Optional[str]] = mapped_column(String(100))
    title: Mapped[Optional[str]] = mapped_column(String(200))
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    permissions_override: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)

    # Relationships
    organization = relationship("Organization", backref="memberships")
    user = relationship("User", backref="memberships")

    __table_args__ = (
        Index("ix_membership_org_user", "organization_id", "user_id", unique=True),
        Index("ix_membership_user_primary", "user_id", "is_primary"),
    )

    def __repr__(self) -> str:
        return f"<OrgMembership(org={self.organization_id}, user={self.user_id}, role={self.role})>"


class OrganizationInvitation(BaseModel):
    """Invitation to join an organization."""

    __tablename__ = "organization_invitations"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    role: Mapped[str] = mapped_column(Enum(UserRole), nullable=False)
    invited_by_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), default="pending", nullable=False
    )  # pending, accepted, declined, expired
    token: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    accepted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    message: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    organization = relationship("Organization", backref="invitations")
    invited_by = relationship("User", backref="sent_invitations")

    __table_args__ = (
        Index("ix_invitation_org_email", "organization_id", "email"),
    )

    def __repr__(self) -> str:
        return f"<OrgInvitation(org={self.organization_id}, email={self.email}, status={self.status})>"


class OrganizationSettings(BaseModel):
    """Key-value settings per organization."""

    __tablename__ = "organization_settings"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    key: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[Optional[dict]] = mapped_column(JSON)
    description: Mapped[Optional[str]] = mapped_column(String(500))

    # Relationships
    organization = relationship("Organization", backref="org_settings")

    __table_args__ = (
        Index("ix_org_settings_key", "organization_id", "key", unique=True),
    )

    def __repr__(self) -> str:
        return f"<OrgSettings(org={self.organization_id}, key={self.key})>"


class TenantAuditLog(BaseModel):
    """
    Comprehensive audit trail for multi-tenant operations.
    Separate from existing AuditLog to track org-level actions.
    """

    __tablename__ = "tenant_audit_logs"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    action: Mapped[str] = mapped_column(
        Enum(AuditAction), nullable=False, index=True
    )
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_id: Mapped[Optional[int]] = mapped_column(Integer)
    changes: Mapped[Optional[dict]] = mapped_column(JSON)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(String(500))
    details: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    organization = relationship("Organization", backref="audit_logs")
    user = relationship("User", backref="audit_logs")

    __table_args__ = (
        Index("ix_audit_org_action", "organization_id", "action"),
        Index("ix_audit_org_resource", "organization_id", "resource_type", "resource_id"),
        Index("ix_audit_org_created", "organization_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<TenantAuditLog(org={self.organization_id}, action={self.action}, resource={self.resource_type})>"
