"""Supplier service for CRUD operations and analytics."""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from models.supplier import Supplier, SupplierPerformance
from models.supplier_network import SupplierRequirement, SupplierRateCard, SupplierCommunication
from models.enums import SupplierTier

logger = logging.getLogger(__name__)


class SupplierService:
    """Service for supplier management operations."""

    @staticmethod
    async def create_supplier(
        db: AsyncSession,
        company_name: str,
        contact_name: Optional[str] = None,
        contact_email: Optional[str] = None,
        contact_phone: Optional[str] = None,
        website: Optional[str] = None,
        specializations: Optional[List[str]] = None,
        locations_served: Optional[List[str]] = None,
        commission_rate: Optional[float] = None,
        contract_start: Optional[datetime] = None,
        contract_end: Optional[datetime] = None,
        notes: Optional[str] = None,
    ) -> Supplier:
        """Create a new supplier.

        Args:
            db: Database session
            company_name: Company name
            contact_name: Contact name
            contact_email: Contact email
            contact_phone: Contact phone
            website: Website URL
            specializations: List of specializations
            locations_served: List of locations served
            commission_rate: Commission rate percentage
            contract_start: Contract start date
            contract_end: Contract end date
            notes: Notes

        Returns:
            Created Supplier object
        """
        try:
            supplier = Supplier(
                company_name=company_name,
                contact_name=contact_name,
                contact_email=contact_email,
                contact_phone=contact_phone,
                website=website,
                specializations=specializations or [],
                locations_served=locations_served or [],
                tier=SupplierTier.NEW,
                commission_rate=commission_rate,
                contract_start=contract_start,
                contract_end=contract_end,
                notes=notes,
            )
            db.add(supplier)
            await db.commit()
            await db.refresh(supplier)
            logger.info(f"Created supplier: {supplier.id}")
            return supplier
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating supplier: {str(e)}")
            raise

    @staticmethod
    async def get_supplier(db: AsyncSession, supplier_id: int) -> Optional[Supplier]:
        """Get supplier by ID.

        Args:
            db: Database session
            supplier_id: Supplier ID

        Returns:
            Supplier object or None
        """
        try:
            result = await db.execute(
                select(Supplier).where(Supplier.id == supplier_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting supplier: {str(e)}")
            raise

    @staticmethod
    async def list_suppliers(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        tier: Optional[str] = None,
        specialization: Optional[str] = None,
        location: Optional[str] = None,
    ) -> tuple[List[Supplier], int]:
        """List suppliers with optional filters.

        Args:
            db: Database session
            skip: Number to skip
            limit: Number to limit
            tier: Filter by tier
            specialization: Filter by specialization
            location: Filter by location

        Returns:
            Tuple of (suppliers list, total count)
        """
        try:
            query = select(Supplier).where(Supplier.is_active == True)

            if tier:
                query = query.where(Supplier.tier == tier)

            if specialization:
                # Filter by specialization array contains value
                from sqlalchemy import func as sql_func
                query = query.where(
                    sql_func.array_contains(Supplier.specializations, specialization)
                )

            if location:
                from sqlalchemy import func as sql_func
                query = query.where(
                    sql_func.array_contains(Supplier.locations_served, location)
                )

            # Count total
            count_result = await db.execute(
                select(func.count(Supplier.id)).where(
                    query.whereclause if hasattr(query, "whereclause") else True
                )
            )
            total = count_result.scalar() or 0

            # Get paginated results
            result = await db.execute(
                query.order_by(Supplier.created_at.desc())
                .offset(skip)
                .limit(limit)
            )
            suppliers = result.scalars().all()

            return suppliers, total
        except Exception as e:
            logger.error(f"Error listing suppliers: {str(e)}")
            raise

    @staticmethod
    async def update_supplier(
        db: AsyncSession,
        supplier_id: int,
        **kwargs: Any,
    ) -> Supplier:
        """Update supplier.

        Args:
            db: Database session
            supplier_id: Supplier ID
            **kwargs: Fields to update

        Returns:
            Updated Supplier object
        """
        try:
            supplier = await SupplierService.get_supplier(db, supplier_id)
            if not supplier:
                raise ValueError(f"Supplier {supplier_id} not found")

            for key, value in kwargs.items():
                if hasattr(supplier, key):
                    setattr(supplier, key, value)

            db.add(supplier)
            await db.commit()
            await db.refresh(supplier)
            logger.info(f"Updated supplier: {supplier_id}")
            return supplier
        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating supplier: {str(e)}")
            raise

    @staticmethod
    async def get_supplier_performance(
        db: AsyncSession,
        supplier_id: int,
        days: int = 180,
    ) -> List[SupplierPerformance]:
        """Get supplier performance history.

        Args:
            db: Database session
            supplier_id: Supplier ID
            days: Number of days to look back

        Returns:
            List of SupplierPerformance records
        """
        try:
            cutoff_date = (datetime.utcnow() - timedelta(days=days)).date()

            result = await db.execute(
                select(SupplierPerformance)
                .where(
                    and_(
                        SupplierPerformance.supplier_id == supplier_id,
                        SupplierPerformance.period_end >= cutoff_date,
                    )
                )
                .order_by(desc(SupplierPerformance.period_end))
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting supplier performance: {str(e)}")
            raise

    @staticmethod
    async def create_rate_card(
        db: AsyncSession,
        supplier_id: int,
        role_title: str,
        skill_category: str,
        min_rate: float,
        max_rate: float,
        rate_type: str = "hourly",
        location: Optional[str] = None,
        effective_date: Optional[datetime] = None,
        expiry_date: Optional[datetime] = None,
        notes: Optional[str] = None,
    ) -> SupplierRateCard:
        """Create supplier rate card.

        Args:
            db: Database session
            supplier_id: Supplier ID
            role_title: Role title
            skill_category: Skill category
            min_rate: Minimum rate
            max_rate: Maximum rate
            rate_type: Rate type (hourly, annual, contract)
            location: Location
            effective_date: Effective date
            expiry_date: Expiry date
            notes: Notes

        Returns:
            Created SupplierRateCard object
        """
        try:
            rate_card = SupplierRateCard(
                supplier_id=supplier_id,
                role_title=role_title,
                skill_category=skill_category,
                min_rate=min_rate,
                max_rate=max_rate,
                rate_type=rate_type,
                location=location,
                effective_date=effective_date or datetime.utcnow().date(),
                expiry_date=expiry_date,
                notes=notes,
            )
            db.add(rate_card)
            await db.commit()
            await db.refresh(rate_card)
            logger.info(f"Created rate card for supplier {supplier_id}")
            return rate_card
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating rate card: {str(e)}")
            raise

    @staticmethod
    async def get_rate_cards(
        db: AsyncSession,
        supplier_id: int,
    ) -> List[SupplierRateCard]:
        """Get supplier rate cards.

        Args:
            db: Database session
            supplier_id: Supplier ID

        Returns:
            List of SupplierRateCard objects
        """
        try:
            result = await db.execute(
                select(SupplierRateCard).where(
                    SupplierRateCard.supplier_id == supplier_id
                )
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting rate cards: {str(e)}")
            raise

    @staticmethod
    async def record_communication(
        db: AsyncSession,
        supplier_id: int,
        communication_type: str,
        subject: str,
        content: str,
        sent_by: Optional[int] = None,
    ) -> SupplierCommunication:
        """Record supplier communication.

        Args:
            db: Database session
            supplier_id: Supplier ID
            communication_type: Type of communication
            subject: Subject
            content: Content
            sent_by: User ID who sent

        Returns:
            Created SupplierCommunication object
        """
        try:
            comm = SupplierCommunication(
                supplier_id=supplier_id,
                communication_type=communication_type,
                subject=subject,
                content=content,
                sent_at=datetime.utcnow(),
                sent_by=sent_by,
            )
            db.add(comm)
            await db.commit()
            await db.refresh(comm)
            logger.info(f"Recorded communication for supplier {supplier_id}")
            return comm
        except Exception as e:
            await db.rollback()
            logger.error(f"Error recording communication: {str(e)}")
            raise

    @staticmethod
    async def get_communications(
        db: AsyncSession,
        supplier_id: int,
        limit: int = 50,
    ) -> List[SupplierCommunication]:
        """Get supplier communications.

        Args:
            db: Database session
            supplier_id: Supplier ID
            limit: Number to limit

        Returns:
            List of SupplierCommunication objects
        """
        try:
            result = await db.execute(
                select(SupplierCommunication)
                .where(SupplierCommunication.supplier_id == supplier_id)
                .order_by(desc(SupplierCommunication.sent_at))
                .limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting communications: {str(e)}")
            raise

    @staticmethod
    async def get_supplier_requirement_distributions(
        db: AsyncSession,
        supplier_id: int,
        status: Optional[str] = None,
    ) -> List[SupplierRequirement]:
        """Get requirement distributions for supplier.

        Args:
            db: Database session
            supplier_id: Supplier ID
            status: Filter by response status

        Returns:
            List of SupplierRequirement objects
        """
        try:
            query = select(SupplierRequirement).where(
                SupplierRequirement.supplier_id == supplier_id
            )

            if status:
                query = query.where(SupplierRequirement.response_status == status)

            result = await db.execute(
                query.order_by(desc(SupplierRequirement.distributed_at))
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting requirement distributions: {str(e)}")
            raise
