"""MSP Onboarding Service — onboard clients and suppliers into the VMS platform."""

import logging
import re
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from models.organization import Organization
from models.user import User
from models.tenant_management import OrganizationMembership, OrganizationInvitation
from models.enums import OrganizationType, OrgOnboardingStatus, UserRole, SupplierTier
from utils.security import hash_password

logger = logging.getLogger(__name__)


class MSPOnboardingService:
    """Handles onboarding of clients and suppliers into the MSP ecosystem."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _slugify(self, name: str) -> str:
        """Generate URL-safe slug from name."""
        slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
        return slug[:100]

    async def _ensure_unique_slug(self, slug: str) -> str:
        """Ensure slug is unique, append number if needed."""
        base_slug = slug
        counter = 1
        while True:
            stmt = select(Organization).where(Organization.slug == slug)
            result = await self.session.execute(stmt)
            if result.scalar_one_or_none() is None:
                return slug
            slug = f"{base_slug}-{counter}"
            counter += 1

    async def onboard_client(
        self,
        msp_org_id: int,
        name: str,
        primary_contact_email: str,
        primary_contact_name: Optional[str] = None,
        industry: Optional[str] = None,
        website: Optional[str] = None,
        description: Optional[str] = None,
        address: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        country: Optional[str] = None,
        contract_start: Optional[Any] = None,
        contract_end: Optional[Any] = None,
        admin_password: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Onboard a new client organization.
        Creates: Organization + CLIENT_ADMIN user + OrganizationMembership.
        """
        slug = await self._ensure_unique_slug(self._slugify(name))

        # Create the client organization
        client_org = Organization(
            name=name,
            slug=slug,
            org_type=OrganizationType.CLIENT,
            onboarding_status=OrgOnboardingStatus.PENDING_REVIEW,
            parent_org_id=msp_org_id,
            primary_contact_name=primary_contact_name or name,
            primary_contact_email=primary_contact_email,
            industry=industry,
            website=website,
            description=description,
            address=address,
            city=city,
            state=state,
            country=country,
            contract_start=contract_start,
            contract_end=contract_end,
        )
        self.session.add(client_org)
        await self.session.flush()

        # Create admin user for the client
        password = admin_password or secrets.token_urlsafe(12)
        admin_user = User(
            email=primary_contact_email,
            hashed_password=hash_password(password),
            first_name=primary_contact_name.split()[0] if primary_contact_name else "Admin",
            last_name=primary_contact_name.split()[-1] if primary_contact_name and len(primary_contact_name.split()) > 1 else name,
            role=UserRole.CLIENT_ADMIN,
            organization_id=client_org.id,
        )
        self.session.add(admin_user)
        await self.session.flush()

        # Create membership
        membership = OrganizationMembership(
            organization_id=client_org.id,
            user_id=admin_user.id,
            role=UserRole.CLIENT_ADMIN,
            is_primary=True,
        )
        self.session.add(membership)
        await self.session.commit()

        logger.info(f"Onboarded client: {name} (org_id={client_org.id})")

        return {
            "organization": client_org,
            "admin_user": admin_user,
            "membership": membership,
            "temp_password": password if not admin_password else None,
        }

    async def onboard_supplier(
        self,
        msp_org_id: int,
        name: str,
        primary_contact_email: str,
        primary_contact_name: Optional[str] = None,
        tier: str = "standard",
        commission_rate: Optional[float] = None,
        specializations: Optional[List[str]] = None,
        industry: Optional[str] = None,
        website: Optional[str] = None,
        description: Optional[str] = None,
        address: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        country: Optional[str] = None,
        admin_password: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Onboard a new supplier organization.
        Creates: Organization + SUPPLIER_ADMIN user + OrganizationMembership.
        """
        slug = await self._ensure_unique_slug(self._slugify(name))

        supplier_org = Organization(
            name=name,
            slug=slug,
            org_type=OrganizationType.SUPPLIER,
            onboarding_status=OrgOnboardingStatus.PENDING_REVIEW,
            parent_org_id=msp_org_id,
            primary_contact_name=primary_contact_name or name,
            primary_contact_email=primary_contact_email,
            tier=tier,
            commission_rate=commission_rate,
            specializations=specializations or [],
            industry=industry,
            website=website,
            description=description,
            address=address,
            city=city,
            state=state,
            country=country,
        )
        self.session.add(supplier_org)
        await self.session.flush()

        password = admin_password or secrets.token_urlsafe(12)
        admin_user = User(
            email=primary_contact_email,
            hashed_password=hash_password(password),
            first_name=primary_contact_name.split()[0] if primary_contact_name else "Admin",
            last_name=primary_contact_name.split()[-1] if primary_contact_name and len(primary_contact_name.split()) > 1 else name,
            role=UserRole.SUPPLIER_ADMIN,
            organization_id=supplier_org.id,
        )
        self.session.add(admin_user)
        await self.session.flush()

        membership = OrganizationMembership(
            organization_id=supplier_org.id,
            user_id=admin_user.id,
            role=UserRole.SUPPLIER_ADMIN,
            is_primary=True,
        )
        self.session.add(membership)
        await self.session.commit()

        logger.info(f"Onboarded supplier: {name} (org_id={supplier_org.id}, tier={tier})")

        return {
            "organization": supplier_org,
            "admin_user": admin_user,
            "membership": membership,
            "temp_password": password if not admin_password else None,
        }

    async def activate_organization(self, org_id: int) -> Organization:
        """Move organization from PENDING_REVIEW to ACTIVE."""
        stmt = select(Organization).where(Organization.id == org_id)
        result = await self.session.execute(stmt)
        org = result.scalar_one_or_none()

        if not org:
            raise ValueError(f"Organization {org_id} not found")

        org.onboarding_status = OrgOnboardingStatus.ACTIVE
        await self.session.commit()
        logger.info(f"Activated organization: {org.name} (id={org_id})")
        return org

    async def suspend_organization(self, org_id: int, reason: Optional[str] = None) -> Organization:
        """Suspend an organization."""
        stmt = select(Organization).where(Organization.id == org_id)
        result = await self.session.execute(stmt)
        org = result.scalar_one_or_none()

        if not org:
            raise ValueError(f"Organization {org_id} not found")

        org.onboarding_status = OrgOnboardingStatus.SUSPENDED
        if reason:
            settings = org.settings or {}
            settings["suspension_reason"] = reason
            settings["suspended_at"] = datetime.utcnow().isoformat()
            org.settings = settings
        await self.session.commit()
        logger.info(f"Suspended organization: {org.name} (reason={reason})")
        return org

    async def offboard_organization(self, org_id: int) -> Organization:
        """Offboard (soft-delete) an organization."""
        stmt = select(Organization).where(Organization.id == org_id)
        result = await self.session.execute(stmt)
        org = result.scalar_one_or_none()

        if not org:
            raise ValueError(f"Organization {org_id} not found")

        org.onboarding_status = OrgOnboardingStatus.OFFBOARDED
        org.is_active = False
        await self.session.commit()
        logger.info(f"Offboarded organization: {org.name}")
        return org

    async def get_clients(self, msp_org_id: int, include_inactive: bool = False) -> List[Organization]:
        """Get all client organizations under an MSP."""
        stmt = select(Organization).where(
            Organization.parent_org_id == msp_org_id,
            Organization.org_type == OrganizationType.CLIENT,
        )
        if not include_inactive:
            stmt = stmt.where(Organization.is_active == True)
        stmt = stmt.order_by(Organization.name)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_suppliers(self, msp_org_id: int, include_inactive: bool = False) -> List[Organization]:
        """Get all supplier organizations under an MSP."""
        stmt = select(Organization).where(
            Organization.parent_org_id == msp_org_id,
            Organization.org_type == OrganizationType.SUPPLIER,
        )
        if not include_inactive:
            stmt = stmt.where(Organization.is_active == True)
        stmt = stmt.order_by(Organization.name)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
