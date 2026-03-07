"""
Tenant context management for multi-tenant VMS/MSP platform.

Provides request-scoped tenant context that automatically filters
all database queries by organization_id.
"""

import logging
from dataclasses import dataclass, field
from typing import Optional, List
from contextvars import ContextVar

logger = logging.getLogger(__name__)

# Context variable for async-safe tenant context
_tenant_context_var: ContextVar[Optional["TenantContext"]] = ContextVar(
    "tenant_context", default=None
)


@dataclass
class TenantContext:
    """
    Holds the current request's tenant information.
    Extracted from JWT token by FastAPI dependency.
    """
    organization_id: int
    user_id: int
    user_role: str
    organization_type: str  # MSP, CLIENT, SUPPLIER
    # Additional accessible org IDs (for MSP users who can see client/supplier data)
    accessible_org_ids: List[int] = field(default_factory=list)
    # Is this a platform admin with cross-tenant access?
    is_platform_admin: bool = False

    @property
    def can_access_org(self) -> bool:
        """Check if user has access to their current org."""
        return self.organization_id > 0

    def can_access(self, org_id: int) -> bool:
        """Check if user can access data from a specific organization."""
        if self.is_platform_admin:
            return True
        if org_id == self.organization_id:
            return True
        if org_id in self.accessible_org_ids:
            return True
        return False

    @property
    def is_msp(self) -> bool:
        return self.organization_type in ("MSP", "msp")

    @property
    def is_client(self) -> bool:
        return self.organization_type in ("CLIENT", "client")

    @property
    def is_supplier(self) -> bool:
        return self.organization_type in ("SUPPLIER", "supplier")


def set_tenant_context(ctx: TenantContext) -> None:
    """Set the tenant context for the current async request."""
    _tenant_context_var.set(ctx)


def get_tenant_context() -> Optional[TenantContext]:
    """Get the current tenant context. Returns None if not set."""
    return _tenant_context_var.get()


def require_tenant_context() -> TenantContext:
    """
    Get tenant context, raising error if not set.
    Use in places where tenant context is required.
    """
    ctx = _tenant_context_var.get()
    if ctx is None:
        raise RuntimeError("Tenant context not set. Ensure request has valid auth.")
    return ctx


def clear_tenant_context() -> None:
    """Clear the tenant context (e.g., at end of request)."""
    _tenant_context_var.set(None)
