from datetime import datetime
from typing import Optional
from sqlalchemy import Column, DateTime, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column
from database.base import Base


class BaseModel(Base):
    """Base model with common fields for all entities."""

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class TenantBaseModel(BaseModel):
    """
    Base model for tenant-scoped entities.
    Adds organization_id for multi-tenant data isolation.
    Entities inheriting this will have automatic tenant scoping.
    
    Note: Organization model itself inherits BaseModel (not TenantBaseModel)
    since it IS the tenant.
    """

    __abstract__ = True

    # Subclasses that need org scoping will define this column directly
    # because each may have different FK targets or constraints.
    # This class exists as a marker/type for tenant-aware entities.
