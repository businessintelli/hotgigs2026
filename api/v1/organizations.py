"""Organization management endpoints — switch org, list memberships, invite users."""

import logging
import secrets
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from database import get_db
from api.dependencies import get_current_user, get_current_organization, require_role
from models.user import User
from models.organization import Organization
from models.tenant_management import OrganizationMembership, OrganizationInvitation
from schemas.organization import (
    OrganizationResponse,
    OrganizationListResponse,
    MembershipResponse,
    InvitationCreate,
    InvitationResponse,
    SwitchOrgRequest,
    SwitchOrgResponse,
)
from utils.security import create_tenant_token

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.get("/me", response_model=List[OrganizationResponse])
async def get_my_organizations(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Get all organizations the current user belongs to."""
    # Get memberships
    stmt = (
        select(Organization)
        .join(OrganizationMembership, OrganizationMembership.organization_id == Organization.id)
        .where(
            OrganizationMembership.user_id == user.id,
            OrganizationMembership.is_active == True,
            Organization.is_active == True,
        )
    )
    result = await session.execute(stmt)
    orgs = list(result.scalars().all())

    # Also include the user's primary org if not in memberships
    if user.organization_id:
        primary_in_list = any(o.id == user.organization_id for o in orgs)
        if not primary_in_list:
            stmt2 = select(Organization).where(
                Organization.id == user.organization_id,
                Organization.is_active == True,
            )
            result2 = await session.execute(stmt2)
            primary_org = result2.scalar_one_or_none()
            if primary_org:
                orgs.insert(0, primary_org)

    return orgs


@router.post("/{org_id}/switch", response_model=SwitchOrgResponse)
async def switch_organization(
    org_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Switch the active organization context. Returns new JWT token."""
    # Verify user has membership in target org
    stmt = select(OrganizationMembership).where(
        OrganizationMembership.organization_id == org_id,
        OrganizationMembership.user_id == user.id,
        OrganizationMembership.is_active == True,
    )
    result = await session.execute(stmt)
    membership = result.scalar_one_or_none()

    # Also allow if it's the user's primary org
    if not membership and user.organization_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this organization",
        )

    # Get the organization
    stmt2 = select(Organization).where(
        Organization.id == org_id,
        Organization.is_active == True,
    )
    result2 = await session.execute(stmt2)
    org = result2.scalar_one_or_none()

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    # Determine role in this org
    role_in_org = membership.role if membership else user.role
    # Normalize enum to value string
    org_type_str = org.org_type.value if hasattr(org.org_type, 'value') else str(org.org_type).lower()
    role_str = role_in_org.value if hasattr(role_in_org, 'value') else str(role_in_org).lower()

    # Get all accessible org IDs (for MSP users, include child orgs)
    accessible_ids = [org_id]
    if org_type_str == "msp":
        child_stmt = select(Organization.id).where(
            Organization.parent_org_id == org_id,
            Organization.is_active == True,
        )
        child_result = await session.execute(child_stmt)
        accessible_ids.extend([r[0] for r in child_result.all()])

    # Create new token with org context
    token = create_tenant_token(
        user_id=user.id,
        organization_id=org_id,
        organization_type=org_type_str,
        role_in_org=role_str,
        accessible_org_ids=accessible_ids,
    )

    return SwitchOrgResponse(
        access_token=token,
        organization=OrganizationResponse.model_validate(org),
        role=role_str,
    )


@router.get("/{org_id}/members", response_model=List[MembershipResponse])
async def list_organization_members(
    org_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """List members of an organization."""
    # Verify user has access to this org
    stmt_check = select(OrganizationMembership).where(
        OrganizationMembership.organization_id == org_id,
        OrganizationMembership.user_id == user.id,
        OrganizationMembership.is_active == True,
    )
    result_check = await session.execute(stmt_check)
    if not result_check.scalar_one_or_none() and user.organization_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this organization",
        )

    # Get memberships with user info
    stmt = (
        select(OrganizationMembership, User)
        .join(User, User.id == OrganizationMembership.user_id)
        .where(
            OrganizationMembership.organization_id == org_id,
            OrganizationMembership.is_active == True,
        )
    )
    result = await session.execute(stmt)
    rows = result.all()

    members = []
    for membership, member_user in rows:
        members.append(MembershipResponse(
            id=membership.id,
            organization_id=membership.organization_id,
            user_id=membership.user_id,
            role=str(membership.role),
            is_primary=membership.is_primary,
            department=membership.department,
            title=membership.title,
            joined_at=membership.joined_at,
            user_email=member_user.email,
            user_name=member_user.full_name,
        ))

    return members


@router.post("/{org_id}/invite", response_model=InvitationResponse)
async def invite_to_organization(
    org_id: int,
    invitation: InvitationCreate,
    user: User = Depends(require_role(
        "msp_admin", "msp_manager", "client_admin", "supplier_admin", "platform_admin", "admin"
    )),
    session: AsyncSession = Depends(get_db),
):
    """Invite a user to join an organization."""
    # Verify org exists
    stmt = select(Organization).where(
        Organization.id == org_id,
        Organization.is_active == True,
    )
    result = await session.execute(stmt)
    org = result.scalar_one_or_none()

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    # Check if already invited
    stmt_existing = select(OrganizationInvitation).where(
        OrganizationInvitation.organization_id == org_id,
        OrganizationInvitation.email == invitation.email,
        OrganizationInvitation.status == "pending",
    )
    result_existing = await session.execute(stmt_existing)
    if result_existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Invitation already pending for this email",
        )

    # Create invitation
    invite = OrganizationInvitation(
        organization_id=org_id,
        email=invitation.email,
        role=invitation.role,
        invited_by_user_id=user.id,
        status="pending",
        token=secrets.token_urlsafe(32),
        expires_at=datetime.utcnow() + timedelta(days=7),
        message=invitation.message,
    )
    session.add(invite)
    await session.commit()
    await session.refresh(invite)

    return InvitationResponse.model_validate(invite)
