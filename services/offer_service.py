"""Offer and onboarding service."""

import logging
from datetime import datetime
from typing import List, Dict, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func
from models.offer import Offer, Onboarding
from models.enums import OfferStatus, OnboardingStatus
from schemas.offer import OfferCreate, OfferUpdate, OnboardingCreate, OnboardingUpdate

logger = logging.getLogger(__name__)


class OfferService:
    """Service for offer CRUD and lifecycle management."""

    def __init__(self, db: AsyncSession):
        """Initialize offer service.

        Args:
            db: Database session
        """
        self.db = db

    async def create_offer(self, offer_data: OfferCreate) -> Offer:
        """Create a new offer.

        Args:
            offer_data: Offer creation data

        Returns:
            Created offer

        Raises:
            Exception: If database operation fails
        """
        try:
            offer = Offer(**offer_data.model_dump())
            self.db.add(offer)
            await self.db.commit()
            await self.db.refresh(offer)

            logger.info(f"Created offer {offer.id}")
            return offer

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating offer: {str(e)}")
            raise

    async def get_offer(self, offer_id: int) -> Optional[Offer]:
        """Get offer by ID.

        Args:
            offer_id: Offer ID

        Returns:
            Offer or None

        Raises:
            Exception: If database operation fails
        """
        try:
            result = await self.db.execute(
                select(Offer).where(Offer.id == offer_id)
            )
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"Error getting offer: {str(e)}")
            raise

    async def get_offers(
        self,
        skip: int = 0,
        limit: int = 20,
        candidate_id: Optional[int] = None,
        requirement_id: Optional[int] = None,
        status: Optional[OfferStatus] = None,
    ) -> tuple[List[Offer], int]:
        """Get offers with filtering and pagination.

        Args:
            skip: Skip count
            limit: Result limit
            candidate_id: Filter by candidate
            requirement_id: Filter by requirement
            status: Filter by status

        Returns:
            Tuple of offers and total count

        Raises:
            Exception: If database operation fails
        """
        try:
            query = select(Offer)
            count_query = select(func.count(Offer.id))

            # Apply filters
            filters = []
            if candidate_id:
                filters.append(Offer.candidate_id == candidate_id)
            if requirement_id:
                filters.append(Offer.requirement_id == requirement_id)
            if status:
                filters.append(Offer.status == status)

            if filters:
                query = query.where(and_(*filters))
                count_query = count_query.where(and_(*filters))

            # Get total
            result = await self.db.execute(count_query)
            total = result.scalar() or 0

            # Get paginated
            result = await self.db.execute(
                query.order_by(desc(Offer.created_at))
                .offset(skip)
                .limit(limit)
            )
            offers = result.scalars().all()

            logger.info(f"Retrieved {len(offers)} offers")
            return offers, total

        except Exception as e:
            logger.error(f"Error getting offers: {str(e)}")
            raise

    async def update_offer(
        self,
        offer_id: int,
        offer_data: OfferUpdate,
    ) -> Offer:
        """Update offer.

        Args:
            offer_id: Offer ID
            offer_data: Update data

        Returns:
            Updated offer

        Raises:
            ValueError: If offer not found
        """
        try:
            # Fetch offer
            result = await self.db.execute(
                select(Offer).where(Offer.id == offer_id)
            )
            offer = result.scalar_one_or_none()

            if not offer:
                raise ValueError(f"Offer {offer_id} not found")

            # Update fields
            update_data = offer_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(offer, field, value)

            self.db.add(offer)
            await self.db.commit()
            await self.db.refresh(offer)

            logger.info(f"Updated offer {offer_id}")
            return offer

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating offer: {str(e)}")
            raise

    async def delete_offer(self, offer_id: int) -> bool:
        """Soft delete offer.

        Args:
            offer_id: Offer ID

        Returns:
            True if successful

        Raises:
            ValueError: If offer not found
        """
        try:
            result = await self.db.execute(
                select(Offer).where(Offer.id == offer_id)
            )
            offer = result.scalar_one_or_none()

            if not offer:
                raise ValueError(f"Offer {offer_id} not found")

            offer.is_active = False
            self.db.add(offer)
            await self.db.commit()

            logger.info(f"Deleted offer {offer_id}")
            return True

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting offer: {str(e)}")
            raise

    async def get_pending_offers(
        self,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[Offer], int]:
        """Get pending offers awaiting response.

        Args:
            skip: Skip count
            limit: Result limit

        Returns:
            Tuple of offers and count

        Raises:
            Exception: If database operation fails
        """
        try:
            query = select(Offer).where(
                Offer.status.in_([OfferStatus.SENT, OfferStatus.NEGOTIATING])
            )
            count_query = select(func.count(Offer.id)).where(
                Offer.status.in_([OfferStatus.SENT, OfferStatus.NEGOTIATING])
            )

            # Get total
            result = await self.db.execute(count_query)
            total = result.scalar() or 0

            # Get paginated
            result = await self.db.execute(
                query.order_by(desc(Offer.created_at))
                .offset(skip)
                .limit(limit)
            )
            offers = result.scalars().all()

            logger.info(f"Retrieved {len(offers)} pending offers")
            return offers, total

        except Exception as e:
            logger.error(f"Error getting pending offers: {str(e)}")
            raise

    async def get_accepted_offers(
        self,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[Offer], int]:
        """Get accepted offers.

        Args:
            skip: Skip count
            limit: Result limit

        Returns:
            Tuple of offers and count

        Raises:
            Exception: If database operation fails
        """
        try:
            query = select(Offer).where(
                Offer.status == OfferStatus.ACCEPTED
            )
            count_query = select(func.count(Offer.id)).where(
                Offer.status == OfferStatus.ACCEPTED
            )

            # Get total
            result = await self.db.execute(count_query)
            total = result.scalar() or 0

            # Get paginated
            result = await self.db.execute(
                query.order_by(desc(Offer.created_at))
                .offset(skip)
                .limit(limit)
            )
            offers = result.scalars().all()

            logger.info(f"Retrieved {len(offers)} accepted offers")
            return offers, total

        except Exception as e:
            logger.error(f"Error getting accepted offers: {str(e)}")
            raise


class OnboardingService:
    """Service for onboarding tracking and management."""

    def __init__(self, db: AsyncSession):
        """Initialize onboarding service.

        Args:
            db: Database session
        """
        self.db = db

    async def create_onboarding(
        self,
        onboarding_data: OnboardingCreate,
    ) -> Onboarding:
        """Create onboarding record.

        Args:
            onboarding_data: Onboarding creation data

        Returns:
            Created onboarding

        Raises:
            Exception: If database operation fails
        """
        try:
            onboarding = Onboarding(**onboarding_data.model_dump())
            self.db.add(onboarding)
            await self.db.commit()
            await self.db.refresh(onboarding)

            logger.info(f"Created onboarding {onboarding.id}")
            return onboarding

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating onboarding: {str(e)}")
            raise

    async def get_onboarding(self, onboarding_id: int) -> Optional[Onboarding]:
        """Get onboarding by ID.

        Args:
            onboarding_id: Onboarding ID

        Returns:
            Onboarding or None

        Raises:
            Exception: If database operation fails
        """
        try:
            result = await self.db.execute(
                select(Onboarding).where(Onboarding.id == onboarding_id)
            )
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"Error getting onboarding: {str(e)}")
            raise

    async def get_onboardings(
        self,
        skip: int = 0,
        limit: int = 20,
        candidate_id: Optional[int] = None,
        status: Optional[OnboardingStatus] = None,
    ) -> tuple[List[Onboarding], int]:
        """Get onboardings with filtering and pagination.

        Args:
            skip: Skip count
            limit: Result limit
            candidate_id: Filter by candidate
            status: Filter by status

        Returns:
            Tuple of onboardings and total count

        Raises:
            Exception: If database operation fails
        """
        try:
            query = select(Onboarding)
            count_query = select(func.count(Onboarding.id))

            # Apply filters
            filters = []
            if candidate_id:
                filters.append(Onboarding.candidate_id == candidate_id)
            if status:
                filters.append(Onboarding.status == status)

            if filters:
                query = query.where(and_(*filters))
                count_query = count_query.where(and_(*filters))

            # Get total
            result = await self.db.execute(count_query)
            total = result.scalar() or 0

            # Get paginated
            result = await self.db.execute(
                query.order_by(desc(Onboarding.created_at))
                .offset(skip)
                .limit(limit)
            )
            onboardings = result.scalars().all()

            logger.info(f"Retrieved {len(onboardings)} onboardings")
            return onboardings, total

        except Exception as e:
            logger.error(f"Error getting onboardings: {str(e)}")
            raise

    async def update_onboarding(
        self,
        onboarding_id: int,
        onboarding_data: OnboardingUpdate,
    ) -> Onboarding:
        """Update onboarding.

        Args:
            onboarding_id: Onboarding ID
            onboarding_data: Update data

        Returns:
            Updated onboarding

        Raises:
            ValueError: If onboarding not found
        """
        try:
            # Fetch onboarding
            result = await self.db.execute(
                select(Onboarding).where(Onboarding.id == onboarding_id)
            )
            onboarding = result.scalar_one_or_none()

            if not onboarding:
                raise ValueError(f"Onboarding {onboarding_id} not found")

            # Update fields
            update_data = onboarding_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(onboarding, field, value)

            self.db.add(onboarding)
            await self.db.commit()
            await self.db.refresh(onboarding)

            logger.info(f"Updated onboarding {onboarding_id}")
            return onboarding

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating onboarding: {str(e)}")
            raise

    async def get_in_progress_onboardings(
        self,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[Onboarding], int]:
        """Get in-progress onboardings.

        Args:
            skip: Skip count
            limit: Result limit

        Returns:
            Tuple of onboardings and count

        Raises:
            Exception: If database operation fails
        """
        return await self.get_onboardings(
            skip=skip,
            limit=limit,
            status=OnboardingStatus.IN_PROGRESS,
        )

    async def get_completed_onboardings(
        self,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[Onboarding], int]:
        """Get completed onboardings.

        Args:
            skip: Skip count
            limit: Result limit

        Returns:
            Tuple of onboardings and count

        Raises:
            Exception: If database operation fails
        """
        return await self.get_onboardings(
            skip=skip,
            limit=limit,
            status=OnboardingStatus.COMPLETED,
        )

    async def get_onboarding_by_offer(
        self,
        offer_id: int,
    ) -> Optional[Onboarding]:
        """Get onboarding by offer ID.

        Args:
            offer_id: Offer ID

        Returns:
            Onboarding or None

        Raises:
            Exception: If database operation fails
        """
        try:
            result = await self.db.execute(
                select(Onboarding).where(Onboarding.offer_id == offer_id)
            )
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"Error getting onboarding by offer: {str(e)}")
            raise

    async def get_onboarding_progress(
        self,
        onboarding_id: int,
    ) -> Dict[str, Any]:
        """Get onboarding progress summary.

        Args:
            onboarding_id: Onboarding ID

        Returns:
            Progress dictionary

        Raises:
            ValueError: If onboarding not found
        """
        try:
            result = await self.db.execute(
                select(Onboarding).where(Onboarding.id == onboarding_id)
            )
            onboarding = result.scalar_one_or_none()

            if not onboarding:
                raise ValueError(f"Onboarding {onboarding_id} not found")

            # Count checklist items
            checklist = onboarding.checklist or []
            completed = sum(1 for item in checklist if item.get("completed", False))
            total = len(checklist)

            progress = {
                "onboarding_id": onboarding_id,
                "status": onboarding.status.value,
                "total_items": total,
                "completed_items": completed,
                "completion_percentage": (completed / total * 100) if total > 0 else 0,
                "remaining_items": [
                    item["item"] for item in checklist
                    if not item.get("completed", False)
                ],
                "documents_collected": len(onboarding.documents_collected or []),
                "background_check_status": onboarding.background_check_status,
                "start_date_confirmed": onboarding.start_date_confirmed,
            }

            return progress

        except Exception as e:
            logger.error(f"Error getting onboarding progress: {str(e)}")
            raise
