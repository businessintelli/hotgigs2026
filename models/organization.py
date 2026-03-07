"""Organization model — core tenant entity for multi-tenant VMS/MSP."""

from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import String, DateTime, Date, Enum, JSON, ForeignKey, Text, Float, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import BaseModel
from models.enums import OrganizationType, OrgOnboardingStatus, SupplierTier


class Organization(BaseModel):
    """
    Core tenant entity. Every client, supplier, and the MSP itself
    is an Organization. This is the foundation of multi-tenancy.
    """

    __tablename__ = "organizations"

    # Identity
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    org_type: Mapped[str] = mapped_column(
        Enum(OrganizationType),
        nullable=False,
        index=True,
    )
    logo_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Onboarding
    onboarding_status: Mapped[str] = mapped_column(
        Enum(OrgOnboardingStatus),
        default=OrgOnboardingStatus.NEW,
        nullable=False,
        index=True,
    )

    # Hierarchy — MSP is parent of its clients and suppliers
    parent_org_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("organizations.id"), nullable=True, index=True
    )

    # Contact info
    primary_contact_name: Mapped[Optional[str]] = mapped_column(String(200))
    primary_contact_email: Mapped[Optional[str]] = mapped_column(String(255))
    primary_contact_phone: Mapped[Optional[str]] = mapped_column(String(50))

    # Address
    address: Mapped[Optional[str]] = mapped_column(Text)
    city: Mapped[Optional[str]] = mapped_column(String(100))
    state: Mapped[Optional[str]] = mapped_column(String(100))
    country: Mapped[Optional[str]] = mapped_column(String(100))
    zip_code: Mapped[Optional[str]] = mapped_column(String(20))

    # Industry & metadata
    industry: Mapped[Optional[str]] = mapped_column(String(100))
    website: Mapped[Optional[str]] = mapped_column(String(500))
    description: Mapped[Optional[str]] = mapped_column(Text)
    specializations: Mapped[Optional[dict]] = mapped_column(JSON, default=list)

    # Supplier-specific fields
    tier: Mapped[Optional[str]] = mapped_column(
        Enum(SupplierTier), nullable=True
    )
    commission_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Contract info
    contract_start: Mapped[Optional[date]] = mapped_column(Date)
    contract_end: Mapped[Optional[date]] = mapped_column(Date)
    billing_rate_type: Mapped[Optional[str]] = mapped_column(String(50))

    # Org-level settings (JSON blob)
    settings: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)

    # Relationships
    parent_org = relationship("Organization", remote_side="Organization.id", backref="child_orgs")

    __table_args__ = (
        Index("ix_org_type_status", "org_type", "onboarding_status"),
        Index("ix_org_parent", "parent_org_id", "org_type"),
    )

    def __repr__(self) -> str:
        return f"<Organization(id={self.id}, name={self.name}, type={self.org_type})>"

    @property
    def is_msp(self) -> bool:
        return self.org_type == OrganizationType.MSP or self.org_type == "MSP"

    @property
    def is_client(self) -> bool:
        return self.org_type == OrganizationType.CLIENT or self.org_type == "CLIENT"

    @property
    def is_supplier(self) -> bool:
        return self.org_type == OrganizationType.SUPPLIER or self.org_type == "SUPPLIER"
