"""
Tenant-aware repository base class.

Provides CRUD operations that automatically scope all queries
to the current organization_id, enforcing row-level tenant isolation.
"""

import logging
from typing import TypeVar, Generic, Optional, List, Type, Any, Dict
from sqlalchemy import select, update, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from database.tenant_context import require_tenant_context, TenantContext

logger = logging.getLogger(__name__)

T = TypeVar("T")


class TenantAwareRepository(Generic[T]):
    """
    Base repository with automatic tenant isolation.
    All queries are scoped to the current organization_id.
    """

    def __init__(self, model: Type[T], session: AsyncSession):
        self.model = model
        self.session = session

    def _get_context(self) -> TenantContext:
        """Get and validate tenant context."""
        return require_tenant_context()

    def _apply_tenant_filter(self, stmt, org_id: Optional[int] = None):
        """Apply organization_id filter to a query statement."""
        ctx = self._get_context()
        target_org_id = org_id or ctx.organization_id

        # Verify access
        if not ctx.can_access(target_org_id):
            raise PermissionError(
                f"User {ctx.user_id} cannot access organization {target_org_id}"
            )

        # Only apply filter if model has organization_id
        if hasattr(self.model, "organization_id"):
            stmt = stmt.where(self.model.organization_id == target_org_id)

        return stmt

    async def create(self, data: Dict[str, Any], org_id: Optional[int] = None) -> T:
        """Create a new entity scoped to current tenant."""
        ctx = self._get_context()
        target_org_id = org_id or ctx.organization_id

        if not ctx.can_access(target_org_id):
            raise PermissionError(
                f"User {ctx.user_id} cannot create in organization {target_org_id}"
            )

        # Auto-inject organization_id
        if hasattr(self.model, "organization_id"):
            data["organization_id"] = target_org_id

        entity = self.model(**data)
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def get_by_id(self, entity_id: int, org_id: Optional[int] = None) -> Optional[T]:
        """Get entity by ID, scoped to tenant."""
        stmt = select(self.model).where(self.model.id == entity_id)
        stmt = self._apply_tenant_filter(stmt, org_id)

        # Also filter by is_active if model has it
        if hasattr(self.model, "is_active"):
            stmt = stmt.where(self.model.is_active == True)

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(
        self,
        org_id: Optional[int] = None,
        offset: int = 0,
        limit: int = 50,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        include_inactive: bool = False,
    ) -> List[T]:
        """List entities scoped to tenant with pagination and filtering."""
        stmt = select(self.model)
        stmt = self._apply_tenant_filter(stmt, org_id)

        # Active filter
        if not include_inactive and hasattr(self.model, "is_active"):
            stmt = stmt.where(self.model.is_active == True)

        # Additional filters
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key) and value is not None:
                    stmt = stmt.where(getattr(self.model, key) == value)

        # Ordering
        if order_by and hasattr(self.model, order_by):
            stmt = stmt.order_by(getattr(self.model, order_by).desc())
        elif hasattr(self.model, "created_at"):
            stmt = stmt.order_by(self.model.created_at.desc())

        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count(
        self,
        org_id: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
        include_inactive: bool = False,
    ) -> int:
        """Count entities scoped to tenant."""
        stmt = select(func.count(self.model.id))
        stmt = self._apply_tenant_filter(stmt, org_id)

        if not include_inactive and hasattr(self.model, "is_active"):
            stmt = stmt.where(self.model.is_active == True)

        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key) and value is not None:
                    stmt = stmt.where(getattr(self.model, key) == value)

        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def update_by_id(
        self, entity_id: int, data: Dict[str, Any], org_id: Optional[int] = None
    ) -> Optional[T]:
        """Update entity by ID, scoped to tenant."""
        entity = await self.get_by_id(entity_id, org_id)
        if entity is None:
            return None

        for key, value in data.items():
            if hasattr(entity, key) and key not in ("id", "organization_id", "created_at"):
                setattr(entity, key, value)

        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def soft_delete(self, entity_id: int, org_id: Optional[int] = None) -> bool:
        """Soft delete an entity by setting is_active = False."""
        entity = await self.get_by_id(entity_id, org_id)
        if entity is None:
            return False

        if hasattr(entity, "is_active"):
            entity.is_active = False
            await self.session.flush()
            return True

        return False

    async def list_for_multiple_orgs(
        self,
        org_ids: List[int],
        offset: int = 0,
        limit: int = 50,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[T]:
        """
        List entities across multiple organizations.
        Used by MSP users who need to see data from clients/suppliers.
        """
        ctx = self._get_context()

        # Verify access to all requested orgs
        for oid in org_ids:
            if not ctx.can_access(oid):
                raise PermissionError(
                    f"User {ctx.user_id} cannot access organization {oid}"
                )

        stmt = select(self.model)
        if hasattr(self.model, "organization_id"):
            stmt = stmt.where(self.model.organization_id.in_(org_ids))

        if hasattr(self.model, "is_active"):
            stmt = stmt.where(self.model.is_active == True)

        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key) and value is not None:
                    stmt = stmt.where(getattr(self.model, key) == value)

        if hasattr(self.model, "created_at"):
            stmt = stmt.order_by(self.model.created_at.desc())

        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
