"""Asset allocation and tracking models — hardware, software, badges, access cards."""
from datetime import datetime, date
from typing import Optional
from sqlalchemy import (
    String, DateTime, Date, Enum, JSON, ForeignKey, Text, Float, Integer,
    Boolean, Index, func
)
from sqlalchemy.orm import Mapped, mapped_column
from models.base import BaseModel
import enum


# ── Enums ──────────────────────────────────────────────────

class AssetType(str, enum.Enum):
    LAPTOP = "laptop"
    DESKTOP = "desktop"
    MONITOR = "monitor"
    PHONE = "phone"
    HEADSET = "headset"
    BADGE = "badge"
    ACCESS_CARD = "access_card"
    PARKING_PASS = "parking_pass"
    SOFTWARE_LICENSE = "software_license"
    VPN_ACCESS = "vpn_access"
    EMAIL_ACCOUNT = "email_account"
    BUILDING_KEY = "building_key"
    SECURITY_TOKEN = "security_token"
    FURNITURE = "furniture"
    OTHER = "other"


class AssetStatus(str, enum.Enum):
    AVAILABLE = "available"
    ALLOCATED = "allocated"
    IN_USE = "in_use"
    RETURNED = "returned"
    DAMAGED = "damaged"
    LOST = "lost"
    RETIRED = "retired"
    IN_TRANSIT = "in_transit"
    PENDING_RETURN = "pending_return"


class AssetProvider(str, enum.Enum):
    """Who provides/owns the asset."""
    MSP = "msp"
    SUPPLIER = "supplier"
    CLIENT = "client"
    CONTRACTOR_OWNED = "contractor_owned"


class AssetManagedBy(str, enum.Enum):
    """Who manages the asset allocation/tracking."""
    SYSTEM_ADMIN_MSP = "system_admin_msp"
    SYSTEM_ADMIN_SUPPLIER = "system_admin_supplier"
    SYSTEM_ADMIN_CLIENT = "system_admin_client"
    CLIENT_IT = "client_it"
    CLIENT_FACILITIES = "client_facilities"
    MSP_OPS = "msp_ops"
    SUPPLIER_OPS = "supplier_ops"


class AllocationRequestStatus(str, enum.Enum):
    REQUESTED = "requested"
    APPROVED = "approved"
    ORDERED = "ordered"
    ALLOCATED = "allocated"
    DELIVERED = "delivered"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    RETURN_INITIATED = "return_initiated"
    RETURN_COMPLETED = "return_completed"


# ── Models ─────────────────────────────────────────────────

class AssetCatalog(BaseModel):
    """
    Master catalog of available assets an org can allocate.
    """
    __tablename__ = "asset_catalog"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    asset_type: Mapped[str] = mapped_column(Enum(AssetType), nullable=False, index=True)
    asset_name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    make: Mapped[Optional[str]] = mapped_column(String(100))
    model: Mapped[Optional[str]] = mapped_column(String(100))
    serial_number: Mapped[Optional[str]] = mapped_column(String(200))
    asset_tag: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    status: Mapped[str] = mapped_column(
        Enum(AssetStatus), default=AssetStatus.AVAILABLE, index=True
    )
    provider: Mapped[str] = mapped_column(
        Enum(AssetProvider), default=AssetProvider.CLIENT, nullable=False
    )
    managed_by: Mapped[str] = mapped_column(
        Enum(AssetManagedBy), default=AssetManagedBy.SYSTEM_ADMIN_CLIENT
    )
    # Cost
    purchase_cost: Mapped[Optional[float]] = mapped_column(Float)
    monthly_cost: Mapped[Optional[float]] = mapped_column(Float)
    # Location
    location: Mapped[Optional[str]] = mapped_column(String(300))
    building: Mapped[Optional[str]] = mapped_column(String(100))
    floor_office: Mapped[Optional[str]] = mapped_column(String(100))
    # Currently assigned
    assigned_to_candidate_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("candidates.id"), nullable=True
    )
    assigned_to_placement_id: Mapped[Optional[int]] = mapped_column(nullable=True)
    assigned_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    # Metadata
    purchase_date: Mapped[Optional[date]] = mapped_column(Date)
    warranty_end: Mapped[Optional[date]] = mapped_column(Date)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    specifications: Mapped[Optional[dict]] = mapped_column(JSON)

    __table_args__ = (
        Index("ix_asset_cat_org_type_status", "organization_id", "asset_type", "status"),
    )


class AssetAllocationRequest(BaseModel):
    """
    Request to allocate an asset to a contractor/placement.
    Tracks who requested, who approved, and who fulfilled.
    """
    __tablename__ = "asset_allocation_requests"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    placement_id: Mapped[int] = mapped_column(nullable=False, index=True)
    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id"), nullable=False, index=True
    )
    # Asset details
    asset_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("asset_catalog.id"), nullable=True
    )
    asset_type: Mapped[str] = mapped_column(Enum(AssetType), nullable=False)
    asset_description: Mapped[Optional[str]] = mapped_column(Text)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    # Provider & manager
    provider: Mapped[str] = mapped_column(
        Enum(AssetProvider), default=AssetProvider.CLIENT
    )
    managed_by: Mapped[str] = mapped_column(
        Enum(AssetManagedBy), default=AssetManagedBy.SYSTEM_ADMIN_CLIENT
    )
    managed_by_org_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("organizations.id"), nullable=True
    )
    # Status
    status: Mapped[str] = mapped_column(
        Enum(AllocationRequestStatus), default=AllocationRequestStatus.REQUESTED, index=True
    )
    # Users
    requested_by_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    approved_by_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    fulfilled_by_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    # Dates
    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    needed_by: Mapped[Optional[date]] = mapped_column(Date)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    allocated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    # Return tracking
    return_due_date: Mapped[Optional[date]] = mapped_column(Date)
    returned_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    return_condition: Mapped[Optional[str]] = mapped_column(String(100))
    # Metadata
    notes: Mapped[Optional[str]] = mapped_column(Text)
    delivery_address: Mapped[Optional[str]] = mapped_column(Text)
    tracking_number: Mapped[Optional[str]] = mapped_column(String(200))

    __table_args__ = (
        Index("ix_asset_alloc_placement_status", "placement_id", "status"),
        Index("ix_asset_alloc_org_status", "organization_id", "status"),
    )


class AssetAllocationRule(BaseModel):
    """
    Rules defining which assets are automatically requested for new placements.
    E.g., "All placements at Client X get laptop + badge + VPN from client IT."
    """
    __tablename__ = "asset_allocation_rules"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    rule_name: Mapped[str] = mapped_column(String(200), nullable=False)
    client_org_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("organizations.id"), nullable=True
    )  # NULL = all clients
    job_category: Mapped[Optional[str]] = mapped_column(String(100))
    location: Mapped[Optional[str]] = mapped_column(String(200))
    # What to allocate
    asset_types: Mapped[Optional[dict]] = mapped_column(JSON)  # List of asset types with provider info
    # Provider defaults
    default_provider: Mapped[str] = mapped_column(
        Enum(AssetProvider), default=AssetProvider.CLIENT
    )
    default_managed_by: Mapped[str] = mapped_column(
        Enum(AssetManagedBy), default=AssetManagedBy.SYSTEM_ADMIN_CLIENT
    )
    # Auto-request on placement
    auto_request: Mapped[bool] = mapped_column(Boolean, default=True)
    lead_days_before_start: Mapped[int] = mapped_column(Integer, default=5)
    auto_return_on_end: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[Optional[str]] = mapped_column(Text)
