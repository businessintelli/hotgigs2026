"""
FastAPI dependencies — authentication, authorization, and tenant context.
Multi-tenant VMS/MSP platform.
"""

import logging
from typing import Optional, List
from functools import wraps
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from database.tenant_context import TenantContext, set_tenant_context, clear_tenant_context
from utils.security import verify_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.user import User
from models.organization import Organization
from models.tenant_management import OrganizationMembership

logger = logging.getLogger(__name__)

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_db),
) -> User:
    """Get current authenticated user from JWT token."""
    token = credentials.credentials
    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: str = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch user from database
    stmt = select(User).where(User.id == int(user_id))
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Set tenant context from JWT claims
    org_id = payload.get("organization_id")
    org_type = payload.get("organization_type", "")
    role_in_org = payload.get("role_in_org", str(user.role))
    accessible_org_ids = payload.get("accessible_org_ids", [])

    if org_id:
        ctx = TenantContext(
            organization_id=int(org_id),
            user_id=user.id,
            user_role=role_in_org,
            organization_type=org_type,
            accessible_org_ids=[int(x) for x in accessible_org_ids],
            is_platform_admin=(role_in_org == "platform_admin"),
        )
        set_tenant_context(ctx)

    return user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    session: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """Get optional authenticated user from JWT token."""
    if credentials is None:
        return None

    payload = verify_token(credentials.credentials)

    if payload is None:
        return None

    user_id: str = payload.get("sub")

    if user_id is None:
        return None

    stmt = select(User).where(User.id == int(user_id))
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        return None

    return user


async def get_current_organization(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_db),
) -> Organization:
    """
    Extract current organization from JWT and verify it exists.
    Returns the Organization object.
    """
    token = credentials.credentials
    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    org_id = payload.get("organization_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No organization context. Please switch to an organization.",
        )

    stmt = select(Organization).where(
        Organization.id == int(org_id),
        Organization.is_active == True,
    )
    result = await session.execute(stmt)
    org = result.scalar_one_or_none()

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found or inactive",
        )

    return org


async def get_tenant_context_dep(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_db),
) -> TenantContext:
    """
    FastAPI dependency that returns the TenantContext.
    Use when you need the full tenant context object.
    """
    token = credentials.credentials
    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user_id = payload.get("sub")
    org_id = payload.get("organization_id")
    org_type = payload.get("organization_type", "")
    role_in_org = payload.get("role_in_org", "viewer")
    accessible_org_ids = payload.get("accessible_org_ids", [])

    if not user_id or not org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incomplete token claims. Please log in again.",
        )

    ctx = TenantContext(
        organization_id=int(org_id),
        user_id=int(user_id),
        user_role=role_in_org,
        organization_type=org_type,
        accessible_org_ids=[int(x) for x in accessible_org_ids],
        is_platform_admin=(role_in_org == "platform_admin"),
    )
    set_tenant_context(ctx)
    return ctx


def require_role(*allowed_roles: str):
    """
    Dependency factory: restrict endpoint to specific roles.
    
    Usage:
        @router.get("/admin-only")
        async def admin_endpoint(user: User = Depends(require_role("msp_admin", "platform_admin"))):
            ...
    """
    async def _check_role(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        session: AsyncSession = Depends(get_db),
    ) -> User:
        user = await get_current_user(credentials, session)
        token = credentials.credentials
        payload = verify_token(token)
        
        role_in_org = payload.get("role_in_org", str(user.role)) if payload else str(user.role)
        
        # Check against allowed roles (check both role_in_org and user.role for backward compat)
        user_roles = {role_in_org, str(user.role)}
        if not user_roles.intersection(set(allowed_roles)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {', '.join(allowed_roles)}",
            )
        return user

    return _check_role


def require_org_type(*allowed_types: str):
    """
    Dependency factory: restrict endpoint to specific organization types.
    
    Usage:
        @router.get("/msp-only")
        async def msp_endpoint(user: User = Depends(require_org_type("msp"))):
            ...
    """
    async def _check_org_type(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        session: AsyncSession = Depends(get_db),
    ) -> User:
        user = await get_current_user(credentials, session)
        token = credentials.credentials
        payload = verify_token(token)
        
        org_type = payload.get("organization_type", "") if payload else ""
        
        if org_type.lower() not in [t.lower() for t in allowed_types]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This endpoint requires organization type: {', '.join(allowed_types)}",
            )
        return user

    return _check_org_type


# Convenience shortcuts
require_msp = lambda: require_org_type("msp")
require_client = lambda: require_org_type("client")
require_supplier = lambda: require_org_type("supplier")
require_msp_admin = lambda: require_role("msp_admin", "platform_admin")
