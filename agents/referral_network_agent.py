import logging
import uuid
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from agents.base_agent import BaseAgent
from models.referral import (
    Referrer,
    Referral,
    ReferralBonus,
    ReferralBonusConfig,
)
from models.enums import ReferrerTier, ReferralStatus, BonusMilestone, BonusStatus

logger = logging.getLogger(__name__)


class ReferralNetworkAgent(BaseAgent):
    """Manages referral network automation with bonus tracking and analytics."""

    def __init__(self):
        """Initialize referral network agent."""
        super().__init__("ReferralNetworkAgent", "1.0.0")
        self.tier_thresholds = {
            ReferrerTier.BRONZE.value: 0,
            ReferrerTier.SILVER.value: 5,
            ReferrerTier.GOLD.value: 10,
            ReferrerTier.PLATINUM.value: 20,
        }

    async def register_referrer(
        self, db: AsyncSession, referrer_data: Dict[str, Any]
    ) -> Referrer:
        """Register employee/freelancer as referrer.

        Args:
            db: Database session
            referrer_data: Referrer registration data

        Returns:
            Created Referrer

        Raises:
            ValueError: If registration data invalid or email exists
        """
        try:
            # Check if email already exists
            query = select(Referrer).where(Referrer.email == referrer_data.get("email"))
            result = await db.execute(query)
            if result.scalars().first():
                raise ValueError(f"Email {referrer_data.get('email')} already registered")

            # Generate unique referral code
            referral_code = self._generate_referral_code()

            referrer = Referrer(
                first_name=referrer_data.get("first_name"),
                last_name=referrer_data.get("last_name"),
                email=referrer_data.get("email"),
                phone=referrer_data.get("phone"),
                referrer_type=referrer_data.get("referrer_type", "freelancer"),
                company=referrer_data.get("company"),
                referral_code=referral_code,
                specializations=referrer_data.get("specializations", []),
                network_size_estimate=referrer_data.get("network_size_estimate"),
                is_active=True,
                tier=ReferrerTier.BRONZE.value,
            )

            db.add(referrer)
            await db.commit()

            logger.info(f"Registered referrer {referrer.id} with code {referral_code}")

            await self.emit_event(
                event_type="referrer_registered",
                entity_type="referrer",
                entity_id=referrer.id,
                payload={
                    "email": referrer.email,
                    "referral_code": referral_code,
                    "referrer_type": referrer.referrer_type,
                },
            )

            return referrer

        except Exception as e:
            await db.rollback()
            logger.error(f"Error registering referrer: {str(e)}")
            raise

    async def create_referral(
        self,
        db: AsyncSession,
        referrer_id: int,
        candidate_data: Dict[str, Any],
        requirement_id: Optional[int] = None,
    ) -> Referral:
        """Process a new referral linking referrer to candidate.

        Args:
            db: Database session
            referrer_id: ID of referrer
            candidate_data: Candidate data dictionary
            requirement_id: Optional requirement being referred for

        Returns:
            Created Referral

        Raises:
            ValueError: If referrer not found or duplicate referral exists
        """
        try:
            # Validate referrer exists
            referrer = await db.get(Referrer, referrer_id)
            if not referrer:
                raise ValueError(f"Referrer {referrer_id} not found")

            # Check for duplicate referrals of same candidate
            candidate_email = candidate_data.get("email")
            if requirement_id:
                query = select(Referral).where(
                    and_(
                        Referral.referrer_id == referrer_id,
                        Referral.requirement_id == requirement_id,
                    )
                )
                result = await db.execute(query)
                if result.scalars().first():
                    raise ValueError(
                        f"Referrer already referred candidate for this requirement"
                    )

            # Create referral
            referral = Referral(
                referrer_id=referrer_id,
                candidate_id=0,  # Would be set to actual candidate ID after creation
                requirement_id=requirement_id,
                referral_code_used=referrer.referral_code,
                relationship_to_candidate=candidate_data.get("relationship"),
                referral_notes=candidate_data.get("notes"),
                status=ReferralStatus.REFERRED.value,
                current_milestone=BonusMilestone.INTERVIEWED.value,
            )

            db.add(referral)
            await db.flush()

            # Update referrer stats
            referrer.total_referrals += 1
            await self._update_referrer_tier(db, referrer)

            await db.commit()

            logger.info(f"Created referral {referral.id} from referrer {referrer_id}")

            await self.emit_event(
                event_type="referral_created",
                entity_type="referral",
                entity_id=referral.id,
                payload={
                    "referrer_id": referrer_id,
                    "requirement_id": requirement_id,
                },
            )

            return referral

        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating referral: {str(e)}")
            raise

    async def match_referral_to_requirements(
        self, db: AsyncSession, referral_id: int
    ) -> List[Dict[str, Any]]:
        """Auto-match referred candidate to open requirements.

        Args:
            db: Database session
            referral_id: ID of referral

        Returns:
            List of matching requirements

        Raises:
            ValueError: If referral not found
        """
        try:
            referral = await db.get(Referral, referral_id)
            if not referral:
                raise ValueError(f"Referral {referral_id} not found")

            # Placeholder: would implement full matching algorithm
            # For now, return empty list
            matches = []

            logger.info(f"Matched referral {referral_id} to {len(matches)} requirements")

            await self.emit_event(
                event_type="referral_matched",
                entity_type="referral",
                entity_id=referral_id,
                payload={"match_count": len(matches)},
            )

            return matches

        except Exception as e:
            logger.error(f"Error matching referral: {str(e)}")
            raise

    async def process_referral_milestone(
        self,
        db: AsyncSession,
        referral_id: int,
        milestone: str,
    ) -> Optional[ReferralBonus]:
        """Track referral milestones and calculate bonuses.

        Args:
            db: Database session
            referral_id: ID of referral
            milestone: Milestone type

        Returns:
            Created ReferralBonus if applicable

        Raises:
            ValueError: If referral not found
        """
        try:
            referral = await db.get(Referral, referral_id)
            if not referral:
                raise ValueError(f"Referral {referral_id} not found")

            # Update referral milestone
            referral.current_milestone = milestone
            referral.last_milestone_at = datetime.utcnow()

            # Check if bonus applies to this milestone
            bonus_amount = await self._get_milestone_bonus(db, referral, milestone)

            bonus = None
            if bonus_amount and bonus_amount > 0:
                # Create bonus
                bonus = ReferralBonus(
                    referral_id=referral_id,
                    referrer_id=referral.referrer_id,
                    milestone=milestone,
                    bonus_amount=bonus_amount,
                    status=BonusStatus.PENDING.value,
                )
                db.add(bonus)

                # Update referrer earnings
                referrer = await db.get(Referrer, referral.referrer_id)
                if referrer:
                    referrer.pending_earnings += bonus_amount

            # Handle placement milestone
            if milestone == BonusMilestone.PLACED.value:
                referral.placed_at = datetime.utcnow()
                referral.status = ReferralStatus.PLACED.value

                referrer = await db.get(Referrer, referral.referrer_id)
                if referrer:
                    referrer.successful_placements += 1
                    await self._update_referrer_tier(db, referrer)

            await db.commit()

            logger.info(
                f"Processed milestone {milestone} for referral {referral_id}"
            )

            await self.emit_event(
                event_type="referral_milestone_achieved",
                entity_type="referral",
                entity_id=referral_id,
                payload={
                    "milestone": milestone,
                    "bonus_amount": bonus_amount,
                },
            )

            return bonus

        except Exception as e:
            await db.rollback()
            logger.error(f"Error processing referral milestone: {str(e)}")
            raise

    async def calculate_bonus(
        self,
        db: AsyncSession,
        referral_id: int,
        milestone: str,
    ) -> float:
        """Calculate referral bonus for milestone.

        Args:
            db: Database session
            referral_id: ID of referral
            milestone: Milestone type

        Returns:
            Bonus amount

        Raises:
            ValueError: If referral not found
        """
        try:
            referral = await db.get(Referral, referral_id)
            if not referral:
                raise ValueError(f"Referral {referral_id} not found")

            return await self._get_milestone_bonus(db, referral, milestone)

        except Exception as e:
            logger.error(f"Error calculating bonus: {str(e)}")
            raise

    async def process_payout(
        self,
        db: AsyncSession,
        bonus_id: int,
        user_id: int,
    ) -> Dict[str, Any]:
        """Mark bonus as approved for payout.

        Args:
            db: Database session
            bonus_id: ID of bonus
            user_id: ID of approving user

        Returns:
            Payout details

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

            # Update referrer pending/paid earnings
            referrer = await db.get(Referrer, bonus.referrer_id)
            if referrer:
                referrer.pending_earnings -= bonus.bonus_amount
                referrer.total_earnings += bonus.bonus_amount

            await db.commit()

            logger.info(f"Approved bonus {bonus_id} for payout")

            await self.emit_event(
                event_type="bonus_approved",
                entity_type="bonus",
                entity_id=bonus_id,
                payload={
                    "referrer_id": bonus.referrer_id,
                    "amount": bonus.bonus_amount,
                },
                user_id=user_id,
            )

            return {
                "bonus_id": bonus_id,
                "amount": bonus.bonus_amount,
                "referrer_id": bonus.referrer_id,
                "status": bonus.status,
                "approved_at": bonus.approved_at.isoformat(),
            }

        except Exception as e:
            await db.rollback()
            logger.error(f"Error processing payout: {str(e)}")
            raise

    async def get_referrer_dashboard(
        self, db: AsyncSession, referrer_id: int
    ) -> Dict[str, Any]:
        """Get referrer's dashboard data.

        Args:
            db: Database session
            referrer_id: ID of referrer

        Returns:
            Dashboard dictionary

        Raises:
            ValueError: If referrer not found
        """
        try:
            referrer = await db.get(Referrer, referrer_id)
            if not referrer:
                raise ValueError(f"Referrer {referrer_id} not found")

            # Get referrals
            query = select(Referral).where(Referral.referrer_id == referrer_id)
            result = await db.execute(query)
            referrals = result.scalars().all()

            placed_count = sum(1 for r in referrals if r.status == ReferralStatus.PLACED.value)
            active_count = sum(1 for r in referrals if r.status in [
                ReferralStatus.REFERRED.value,
                ReferralStatus.SCREENING.value,
                ReferralStatus.INTERVIEWED.value,
            ])

            # Get bonuses
            bonus_query = select(ReferralBonus).where(
                ReferralBonus.referrer_id == referrer_id
            )
            bonus_result = await db.execute(bonus_query)
            bonuses = bonus_result.scalars().all()

            dashboard = {
                "referrer": referrer,
                "total_referrals": len(referrals),
                "active_referrals": active_count,
                "placed_referrals": placed_count,
                "rejected_referrals": sum(1 for r in referrals if r.status == ReferralStatus.REJECTED.value),
                "total_earnings": referrer.total_earnings,
                "pending_earnings": referrer.pending_earnings,
                "recent_referrals": referrals[:5],
                "pending_bonuses": [b for b in bonuses if b.status == BonusStatus.PENDING.value],
                "tier": referrer.tier,
                "progress_to_next_tier": self._get_tier_progress(referrer),
            }

            logger.info(f"Retrieved dashboard for referrer {referrer_id}")
            return dashboard

        except Exception as e:
            logger.error(f"Error getting referrer dashboard: {str(e)}")
            raise

    async def get_hidden_roles(
        self, db: AsyncSession, referrer_id: int
    ) -> List[Dict[str, Any]]:
        """Get unadvertised roles available to referrer.

        Args:
            db: Database session
            referrer_id: ID of referrer

        Returns:
            List of hidden role opportunities

        Raises:
            ValueError: If referrer not found
        """
        try:
            referrer = await db.get(Referrer, referrer_id)
            if not referrer:
                raise ValueError(f"Referrer {referrer_id} not found")

            # Placeholder: would query requirements with is_hidden=true
            # and match by specializations
            hidden_roles = []

            logger.info(f"Retrieved {len(hidden_roles)} hidden roles for referrer {referrer_id}")
            return hidden_roles

        except Exception as e:
            logger.error(f"Error getting hidden roles: {str(e)}")
            raise

    async def generate_referral_link(
        self,
        db: AsyncSession,
        referrer_id: int,
        requirement_id: Optional[int] = None,
    ) -> str:
        """Generate trackable referral link.

        Args:
            db: Database session
            referrer_id: ID of referrer
            requirement_id: Optional specific requirement

        Returns:
            Trackable referral link

        Raises:
            ValueError: If referrer not found
        """
        try:
            referrer = await db.get(Referrer, referrer_id)
            if not referrer:
                raise ValueError(f"Referrer {referrer_id} not found")

            token = secrets.token_urlsafe(16)
            base_url = "https://app.hrplatform.com"

            if requirement_id:
                link = (
                    f"{base_url}/refer?code={referrer.referral_code}"
                    f"&req={requirement_id}&token={token}"
                )
            else:
                link = f"{base_url}/refer?code={referrer.referral_code}&token={token}"

            logger.info(f"Generated referral link for referrer {referrer_id}")
            return link

        except Exception as e:
            logger.error(f"Error generating referral link: {str(e)}")
            raise

    async def get_network_analytics(
        self, db: AsyncSession
    ) -> Dict[str, Any]:
        """Get network-wide analytics.

        Args:
            db: Database session

        Returns:
            Analytics dictionary

        Raises:
            Exception: If database error occurs
        """
        try:
            # Total referrers
            referrer_query = select(Referrer)
            referrer_result = await db.execute(referrer_query)
            all_referrers = referrer_result.scalars().all()
            total_referrers = len(all_referrers)
            active_referrers = sum(1 for r in all_referrers if r.is_active)

            # Total referrals
            referral_query = select(Referral)
            referral_result = await db.execute(referral_query)
            all_referrals = referral_result.scalars().all()
            total_referrals = len(all_referrals)
            placed = sum(1 for r in all_referrals if r.status == ReferralStatus.PLACED.value)

            conversion_rate = (
                (placed / total_referrals * 100) if total_referrals > 0 else 0
            )

            # Total bonuses
            bonus_query = select(ReferralBonus)
            bonus_result = await db.execute(bonus_query)
            all_bonuses = bonus_result.scalars().all()
            total_paid = sum(
                b.bonus_amount
                for b in all_bonuses
                if b.status == BonusStatus.PAID.value
            )

            analytics = {
                "total_referrers": total_referrers,
                "active_referrers": active_referrers,
                "total_referrals": total_referrals,
                "placed_referrals": placed,
                "conversion_rate": round(conversion_rate, 2),
                "total_bonuses_paid": total_paid,
                "avg_time_to_hire_days": 0,  # Would calculate from data
                "referrers_by_tier": self._get_referrers_by_tier(all_referrers),
            }

            logger.info("Generated network analytics")
            return analytics

        except Exception as e:
            logger.error(f"Error generating network analytics: {str(e)}")
            raise

    async def send_referral_opportunity(
        self,
        db: AsyncSession,
        referrer_ids: List[int],
        requirement_id: int,
    ) -> List[Dict[str, Any]]:
        """Push opportunity to specific referrers.

        Args:
            db: Database session
            referrer_ids: List of referrer IDs
            requirement_id: ID of requirement

        Returns:
            List of notification results

        Raises:
            Exception: If operation fails
        """
        try:
            results = []

            for referrer_id in referrer_ids:
                referrer = await db.get(Referrer, referrer_id)
                if referrer:
                    # Would send notification here
                    results.append({
                        "referrer_id": referrer_id,
                        "requirement_id": requirement_id,
                        "notified": True,
                        "sent_at": datetime.utcnow().isoformat(),
                    })

            logger.info(f"Sent opportunity to {len(results)} referrers")

            await self.emit_event(
                event_type="referral_opportunity_pushed",
                entity_type="requirement",
                entity_id=requirement_id,
                payload={"referrer_count": len(results)},
            )

            return results

        except Exception as e:
            logger.error(f"Error sending referral opportunity: {str(e)}")
            raise

    async def track_retention(
        self, db: AsyncSession
    ) -> List[Dict[str, Any]]:
        """Check and process retention milestones.

        Args:
            db: Database session

        Returns:
            List of processed retentions

        Raises:
            Exception: If operation fails
        """
        try:
            processed = []

            # Get placed referrals
            query = select(Referral).where(
                Referral.status == ReferralStatus.PLACED.value
            )
            result = await db.execute(query)
            placed_referrals = result.scalars().all()

            now = datetime.utcnow()

            for referral in placed_referrals:
                if not referral.placed_at:
                    continue

                days_since_placement = (now - referral.placed_at).days

                # Check 30-day retention
                if days_since_placement >= 30 and referral.current_milestone != BonusMilestone.RETAINED_30D.value:
                    await self.process_referral_milestone(
                        db,
                        referral.id,
                        BonusMilestone.RETAINED_30D.value,
                    )
                    processed.append({
                        "referral_id": referral.id,
                        "milestone": BonusMilestone.RETAINED_30D.value,
                    })

                # Check 90-day retention
                if days_since_placement >= 90 and referral.current_milestone != BonusMilestone.RETAINED_90D.value:
                    await self.process_referral_milestone(
                        db,
                        referral.id,
                        BonusMilestone.RETAINED_90D.value,
                    )
                    processed.append({
                        "referral_id": referral.id,
                        "milestone": BonusMilestone.RETAINED_90D.value,
                    })

            logger.info(f"Processed {len(processed)} retention milestones")

            await self.emit_event(
                event_type="retention_milestones_processed",
                entity_type="referral_network",
                entity_id=0,
                payload={"count": len(processed)},
            )

            return processed

        except Exception as e:
            logger.error(f"Error tracking retention: {str(e)}")
            raise

    # Helper methods

    def _generate_referral_code(self) -> str:
        """Generate unique referral code."""
        code = uuid.uuid4().hex[:8].upper()
        return f"REF{code}"

    async def _get_milestone_bonus(
        self, db: AsyncSession, referral: Referral, milestone: str
    ) -> float:
        """Get bonus amount for milestone."""
        # Default bonus structure
        bonus_defaults = {
            BonusMilestone.INTERVIEWED.value: 100,
            BonusMilestone.SUBMITTED.value: 200,
            BonusMilestone.PLACED.value: 500,
            BonusMilestone.RETAINED_30D.value: 250,
            BonusMilestone.RETAINED_90D.value: 250,
        }

        return float(bonus_defaults.get(milestone, 0))

    async def _update_referrer_tier(self, db: AsyncSession, referrer: Referrer) -> None:
        """Update referrer tier based on placements."""
        placements = referrer.successful_placements

        for tier, threshold in sorted(
            self.tier_thresholds.items(),
            key=lambda x: x[1],
            reverse=True,
        ):
            if placements >= threshold:
                referrer.tier = tier
                break

    def _get_tier_progress(self, referrer: Referrer) -> Dict[str, Any]:
        """Get progress to next tier."""
        current_threshold = self.tier_thresholds.get(referrer.tier, 0)
        next_tier = None
        next_threshold = None

        thresholds = sorted(self.tier_thresholds.items(), key=lambda x: x[1])
        for tier, threshold in thresholds:
            if threshold > current_threshold:
                next_tier = tier
                next_threshold = threshold
                break

        if next_tier:
            progress = (
                (referrer.successful_placements - current_threshold)
                / (next_threshold - current_threshold)
                * 100
            )
        else:
            progress = 100

        return {
            "current_tier": referrer.tier,
            "next_tier": next_tier,
            "progress_percent": round(min(progress, 100), 2),
            "placements_for_next": (
                next_threshold - referrer.successful_placements
                if next_threshold
                else 0
            ),
        }

    def _get_referrers_by_tier(self, referrers: List[Referrer]) -> Dict[str, int]:
        """Count referrers by tier."""
        by_tier = {
            ReferrerTier.BRONZE.value: 0,
            ReferrerTier.SILVER.value: 0,
            ReferrerTier.GOLD.value: 0,
            ReferrerTier.PLATINUM.value: 0,
        }

        for referrer in referrers:
            by_tier[referrer.tier] = by_tier.get(referrer.tier, 0) + 1

        return by_tier
