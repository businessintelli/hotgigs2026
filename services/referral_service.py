import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from models.referral import (
    Referrer,
    Referral,
    ReferralBonus,
    ReferralBonusConfig,
)
from models.enums import ReferralStatus, BonusMilestone, BonusStatus
from schemas.referral import (
    ReferrerSchema,
    ReferralSchema,
    ReferralBonusSchema,
    ReferralDashboardSchema,
)

logger = logging.getLogger(__name__)


class ReferralService:
    """Service layer for referral operations."""

    @staticmethod
    async def create_referrer(
        db: AsyncSession, referrer_data: Dict[str, Any]
    ) -> ReferrerSchema:
        """Create new referrer.

        Args:
            db: Database session
            referrer_data: Referrer data

        Returns:
            ReferrerSchema

        Raises:
            ValueError: If email already exists
        """
        try:
            # Check email uniqueness
            existing = await db.execute(
                select(Referrer).where(Referrer.email == referrer_data.get("email"))
            )
            if existing.scalars().first():
                raise ValueError(f"Email already registered")

            referrer = Referrer(
                first_name=referrer_data.get("first_name"),
                last_name=referrer_data.get("last_name"),
                email=referrer_data.get("email"),
                phone=referrer_data.get("phone"),
                referrer_type=referrer_data.get("referrer_type", "freelancer"),
                company=referrer_data.get("company"),
                referral_code=ReferralService._generate_code(),
                specializations=referrer_data.get("specializations", []),
                network_size_estimate=referrer_data.get("network_size_estimate"),
                is_active=True,
                tier="bronze",
            )

            db.add(referrer)
            await db.commit()

            logger.info(f"Created referrer {referrer.id}")

            return ReferrerSchema.from_orm(referrer)

        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating referrer: {str(e)}")
            raise

    @staticmethod
    async def get_referrer(db: AsyncSession, referrer_id: int) -> Optional[ReferrerSchema]:
        """Get referrer by ID.

        Args:
            db: Database session
            referrer_id: ID of referrer

        Returns:
            ReferrerSchema or None

        Raises:
            Exception: If database error occurs
        """
        try:
            referrer = await db.get(Referrer, referrer_id)
            if not referrer:
                return None

            return ReferrerSchema.from_orm(referrer)

        except Exception as e:
            logger.error(f"Error getting referrer: {str(e)}")
            raise

    @staticmethod
    async def update_referrer(
        db: AsyncSession,
        referrer_id: int,
        referrer_data: Dict[str, Any],
    ) -> ReferrerSchema:
        """Update referrer profile.

        Args:
            db: Database session
            referrer_id: ID of referrer
            referrer_data: Update data

        Returns:
            Updated ReferrerSchema

        Raises:
            ValueError: If referrer not found
        """
        try:
            referrer = await db.get(Referrer, referrer_id)
            if not referrer:
                raise ValueError(f"Referrer {referrer_id} not found")

            for key, value in referrer_data.items():
                if hasattr(referrer, key) and value is not None:
                    setattr(referrer, key, value)

            await db.commit()

            logger.info(f"Updated referrer {referrer_id}")

            return ReferrerSchema.from_orm(referrer)

        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating referrer: {str(e)}")
            raise

    @staticmethod
    async def create_referral(
        db: AsyncSession,
        referral_data: Dict[str, Any],
    ) -> ReferralSchema:
        """Create new referral.

        Args:
            db: Database session
            referral_data: Referral data

        Returns:
            ReferralSchema

        Raises:
            ValueError: If referrer not found
        """
        try:
            referrer_id = referral_data.get("referrer_id")
            referrer = await db.get(Referrer, referrer_id)
            if not referrer:
                raise ValueError(f"Referrer {referrer_id} not found")

            # Placeholder: candidate_id would be created or fetched
            referral = Referral(
                referrer_id=referrer_id,
                candidate_id=referral_data.get("candidate_id", 0),
                requirement_id=referral_data.get("requirement_id"),
                referral_code_used=referrer.referral_code,
                relationship_to_candidate=referral_data.get("relationship"),
                referral_notes=referral_data.get("notes"),
                status=ReferralStatus.REFERRED.value,
                current_milestone=BonusMilestone.INTERVIEWED.value,
            )

            db.add(referral)
            await db.flush()

            # Update referrer stats
            referrer.total_referrals += 1

            await db.commit()

            logger.info(f"Created referral {referral.id}")

            return ReferralSchema.from_orm(referral)

        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating referral: {str(e)}")
            raise

    @staticmethod
    async def get_referral(db: AsyncSession, referral_id: int) -> Optional[ReferralSchema]:
        """Get referral by ID.

        Args:
            db: Database session
            referral_id: ID of referral

        Returns:
            ReferralSchema or None

        Raises:
            Exception: If database error occurs
        """
        try:
            referral = await db.get(Referral, referral_id)
            if not referral:
                return None

            return ReferralSchema.from_orm(referral)

        except Exception as e:
            logger.error(f"Error getting referral: {str(e)}")
            raise

    @staticmethod
    async def list_referrals(
        db: AsyncSession,
        referrer_id: Optional[int] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[ReferralSchema], int]:
        """List referrals with filtering.

        Args:
            db: Database session
            referrer_id: Filter by referrer
            status: Filter by status
            skip: Offset
            limit: Limit

        Returns:
            Tuple of (referrals, total count)

        Raises:
            Exception: If database error occurs
        """
        try:
            filters = []

            if referrer_id:
                filters.append(Referral.referrer_id == referrer_id)
            if status:
                filters.append(Referral.status == status)

            # Count total
            count_query = select(Referral)
            if filters:
                count_query = count_query.where(and_(*filters))
            count_result = await db.execute(count_query)
            total = len(count_result.scalars().all())

            # Get paginated
            query = select(Referral)
            if filters:
                query = query.where(and_(*filters))
            query = query.offset(skip).limit(limit).order_by(Referral.submitted_at.desc())

            result = await db.execute(query)
            referrals = result.scalars().all()

            return (
                [ReferralSchema.from_orm(r) for r in referrals],
                total,
            )

        except Exception as e:
            logger.error(f"Error listing referrals: {str(e)}")
            raise

    @staticmethod
    async def create_bonus(
        db: AsyncSession,
        bonus_data: Dict[str, Any],
    ) -> ReferralBonusSchema:
        """Create referral bonus.

        Args:
            db: Database session
            bonus_data: Bonus data

        Returns:
            ReferralBonusSchema

        Raises:
            ValueError: If referral not found
        """
        try:
            referral_id = bonus_data.get("referral_id")
            referral = await db.get(Referral, referral_id)
            if not referral:
                raise ValueError(f"Referral {referral_id} not found")

            bonus = ReferralBonus(
                referral_id=referral_id,
                referrer_id=referral.referrer_id,
                milestone=bonus_data.get("milestone"),
                bonus_amount=bonus_data.get("bonus_amount"),
                bonus_currency=bonus_data.get("bonus_currency", "USD"),
                status=BonusStatus.PENDING.value,
            )

            db.add(bonus)

            # Update referrer pending earnings
            referrer = await db.get(Referrer, referral.referrer_id)
            if referrer:
                referrer.pending_earnings += bonus.bonus_amount

            await db.commit()

            logger.info(f"Created bonus {bonus.id}")

            return ReferralBonusSchema.from_orm(bonus)

        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating bonus: {str(e)}")
            raise

    @staticmethod
    async def get_bonus(db: AsyncSession, bonus_id: int) -> Optional[ReferralBonusSchema]:
        """Get bonus by ID.

        Args:
            db: Database session
            bonus_id: ID of bonus

        Returns:
            ReferralBonusSchema or None

        Raises:
            Exception: If database error occurs
        """
        try:
            bonus = await db.get(ReferralBonus, bonus_id)
            if not bonus:
                return None

            return ReferralBonusSchema.from_orm(bonus)

        except Exception as e:
            logger.error(f"Error getting bonus: {str(e)}")
            raise

    @staticmethod
    async def approve_bonus(
        db: AsyncSession,
        bonus_id: int,
        user_id: int,
        notes: Optional[str] = None,
    ) -> ReferralBonusSchema:
        """Approve bonus for payment.

        Args:
            db: Database session
            bonus_id: ID of bonus
            user_id: Approving user
            notes: Optional notes

        Returns:
            Updated ReferralBonusSchema

        Raises:
            ValueError: If bonus not found
        """
        try:
            bonus = await db.get(ReferralBonus, bonus_id)
            if not bonus:
                raise ValueError(f"Bonus {bonus_id} not found")

            if bonus.status == BonusStatus.PAID.value:
                raise ValueError("Bonus already paid")

            bonus.status = BonusStatus.APPROVED.value
            bonus.approved_by_id = user_id
            bonus.approved_at = datetime.utcnow()
            bonus.notes = notes

            await db.commit()

            logger.info(f"Approved bonus {bonus_id}")

            return ReferralBonusSchema.from_orm(bonus)

        except Exception as e:
            await db.rollback()
            logger.error(f"Error approving bonus: {str(e)}")
            raise

    @staticmethod
    async def mark_bonus_paid(
        db: AsyncSession,
        bonus_id: int,
        payment_reference: str,
        notes: Optional[str] = None,
    ) -> ReferralBonusSchema:
        """Mark bonus as paid.

        Args:
            db: Database session
            bonus_id: ID of bonus
            payment_reference: Payment reference number
            notes: Optional notes

        Returns:
            Updated ReferralBonusSchema

        Raises:
            ValueError: If bonus not found
        """
        try:
            bonus = await db.get(ReferralBonus, bonus_id)
            if not bonus:
                raise ValueError(f"Bonus {bonus_id} not found")

            if bonus.status == BonusStatus.PAID.value:
                raise ValueError("Bonus already paid")

            bonus.status = BonusStatus.PAID.value
            bonus.paid_at = datetime.utcnow()
            bonus.payment_reference = payment_reference
            bonus.notes = notes

            # Update referrer earnings
            referrer = await db.get(Referrer, bonus.referrer_id)
            if referrer:
                referrer.pending_earnings -= bonus.bonus_amount
                referrer.total_earnings += bonus.bonus_amount

            await db.commit()

            logger.info(f"Marked bonus {bonus_id} as paid")

            return ReferralBonusSchema.from_orm(bonus)

        except Exception as e:
            await db.rollback()
            logger.error(f"Error marking bonus paid: {str(e)}")
            raise

    @staticmethod
    async def list_referrer_bonuses(
        db: AsyncSession,
        referrer_id: int,
        status: Optional[str] = None,
    ) -> List[ReferralBonusSchema]:
        """List bonuses for referrer.

        Args:
            db: Database session
            referrer_id: ID of referrer
            status: Filter by status

        Returns:
            List of bonuses

        Raises:
            Exception: If database error occurs
        """
        try:
            filters = [ReferralBonus.referrer_id == referrer_id]
            if status:
                filters.append(ReferralBonus.status == status)

            query = select(ReferralBonus).where(and_(*filters)).order_by(
                ReferralBonus.created_at.desc()
            )

            result = await db.execute(query)
            bonuses = result.scalars().all()

            return [ReferralBonusSchema.from_orm(b) for b in bonuses]

        except Exception as e:
            logger.error(f"Error listing referrer bonuses: {str(e)}")
            raise

    @staticmethod
    async def get_leaderboard(
        db: AsyncSession, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get referrer leaderboard.

        Args:
            db: Database session
            limit: Number of entries

        Returns:
            List of leaderboard entries

        Raises:
            Exception: If database error occurs
        """
        try:
            query = select(Referrer).where(
                Referrer.is_active == True
            ).order_by(
                Referrer.successful_placements.desc()
            ).limit(limit)

            result = await db.execute(query)
            referrers = result.scalars().all()

            leaderboard = [
                {
                    "rank": idx + 1,
                    "referrer_id": r.id,
                    "name": f"{r.first_name} {r.last_name}",
                    "placements": r.successful_placements,
                    "earnings": r.total_earnings,
                    "tier": r.tier,
                }
                for idx, r in enumerate(referrers)
            ]

            return leaderboard

        except Exception as e:
            logger.error(f"Error getting leaderboard: {str(e)}")
            raise

    @staticmethod
    async def create_bonus_config(
        db: AsyncSession,
        config_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create bonus configuration.

        Args:
            db: Database session
            config_data: Configuration data

        Returns:
            Created configuration

        Raises:
            Exception: If error occurs
        """
        try:
            config = ReferralBonusConfig(
                name=config_data.get("name"),
                requirement_id=config_data.get("requirement_id"),
                customer_id=config_data.get("customer_id"),
                bonus_structure=config_data.get("bonus_structure", {}),
                max_bonus_per_referral=config_data.get("max_bonus_per_referral"),
                is_default=config_data.get("is_default", False),
                is_active=True,
            )

            db.add(config)
            await db.commit()

            logger.info(f"Created bonus config {config.id}")

            return {
                "id": config.id,
                "name": config.name,
                "bonus_structure": config.bonus_structure,
            }

        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating bonus config: {str(e)}")
            raise

    @staticmethod
    def _generate_code() -> str:
        """Generate referral code."""
        import uuid
        code = uuid.uuid4().hex[:8].upper()
        return f"REF{code}"
