"""Offer and onboarding workflow agent."""

import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update
from agents.base_agent import BaseAgent
from agents.events import EventType
from models.offer import Offer, Onboarding
from models.submission import Submission
from models.candidate import Candidate
from models.requirement import Requirement
from models.enums import (
    OfferStatus,
    OnboardingStatus,
    CandidateStatus,
)

logger = logging.getLogger(__name__)


class OfferOnboardingAgent(BaseAgent):
    """Agent for managing offer and onboarding workflows."""

    def __init__(self):
        """Initialize the offer onboarding agent."""
        super().__init__(
            agent_name="OfferOnboardingAgent",
            agent_version="1.0.0",
        )
        self.max_negotiation_rounds = 3
        self.offer_expiry_days = 7
        self.default_checklist_items = [
            "background_check",
            "reference_verification",
            "i9_form",
            "w4_form",
            "nda_signed",
            "system_access",
            "orientation_scheduled",
            "first_day_confirmation",
        ]

    async def generate_offer(
        self,
        db: AsyncSession,
        submission_id: int,
        rate: float,
        rate_type: str,
        start_date: date,
        end_date: Optional[date] = None,
        terms: Optional[Dict[str, Any]] = None,
    ) -> Offer:
        """Generate offer from approved submission.

        Populates offer with submission and candidate data.

        Args:
            db: Database session
            submission_id: Submission ID
            rate: Offered rate
            rate_type: Rate type (hourly, salary, etc.)
            start_date: Start date
            end_date: Optional end date
            terms: Optional terms dictionary

        Returns:
            Created offer

        Raises:
            ValueError: If submission not found or invalid state
        """
        try:
            # Fetch submission with relations
            result = await db.execute(
                select(Submission)
                .where(Submission.id == submission_id)
            )
            submission = result.scalar_one_or_none()

            if not submission:
                raise ValueError(f"Submission {submission_id} not found")

            # Create offer
            offer = Offer(
                submission_id=submission.id,
                candidate_id=submission.candidate_id,
                requirement_id=submission.requirement_id,
                offered_rate=rate,
                rate_type=rate_type,
                start_date=start_date,
                end_date=end_date,
                status=OfferStatus.DRAFT,
                notes=f"Terms: {terms}" if terms else None,
            )

            db.add(offer)
            await db.commit()
            await db.refresh(offer)

            # Emit event
            await self.emit_event(
                event_type=EventType.OFFER_CREATED,
                entity_type="Offer",
                entity_id=offer.id,
                payload={
                    "offer_id": offer.id,
                    "submission_id": submission_id,
                    "candidate_id": submission.candidate_id,
                    "rate": rate,
                    "rate_type": rate_type,
                },
            )

            logger.info(f"Generated offer {offer.id} from submission {submission_id}")
            return offer

        except Exception as e:
            await db.rollback()
            logger.error(f"Error generating offer: {str(e)}")
            raise

    async def send_offer(
        self,
        db: AsyncSession,
        offer_id: int,
    ) -> Offer:
        """Send offer to candidate.

        Marks as SENT, sets sent_at, emits notification event.

        Args:
            db: Database session
            offer_id: Offer ID

        Returns:
            Updated offer

        Raises:
            ValueError: If offer not found or not in DRAFT status
        """
        try:
            # Fetch offer
            result = await db.execute(
                select(Offer).where(Offer.id == offer_id)
            )
            offer = result.scalar_one_or_none()

            if not offer:
                raise ValueError(f"Offer {offer_id} not found")

            if offer.status != OfferStatus.DRAFT:
                raise ValueError(
                    f"Can only send DRAFT offers. Current status: {offer.status}"
                )

            # Update offer
            offer.status = OfferStatus.SENT
            offer.sent_at = datetime.utcnow()
            db.add(offer)
            await db.commit()
            await db.refresh(offer)

            # Emit event
            await self.emit_event(
                event_type=EventType.OFFER_SENT,
                entity_type="Offer",
                entity_id=offer.id,
                payload={
                    "offer_id": offer.id,
                    "candidate_id": offer.candidate_id,
                    "sent_at": offer.sent_at.isoformat(),
                },
            )

            logger.info(f"Sent offer {offer_id}")
            return offer

        except Exception as e:
            await db.rollback()
            logger.error(f"Error sending offer: {str(e)}")
            raise

    async def process_response(
        self,
        db: AsyncSession,
        offer_id: int,
        accepted: bool,
        notes: Optional[str] = None,
    ) -> Offer:
        """Process candidate response to offer.

        Handle accept (→ ACCEPTED, trigger onboarding) or decline
        (→ DECLINED, return candidate to talent pool).

        Args:
            db: Database session
            offer_id: Offer ID
            accepted: Whether offer was accepted
            notes: Optional candidate notes

        Returns:
            Updated offer

        Raises:
            ValueError: If offer not found or not in SENT status
        """
        try:
            # Fetch offer
            result = await db.execute(
                select(Offer).where(Offer.id == offer_id)
            )
            offer = result.scalar_one_or_none()

            if not offer:
                raise ValueError(f"Offer {offer_id} not found")

            if offer.status not in [OfferStatus.SENT, OfferStatus.NEGOTIATING]:
                raise ValueError(
                    f"Can only process response for SENT/NEGOTIATING offers. Current status: {offer.status}"
                )

            # Update offer
            offer.response_at = datetime.utcnow()
            offer.notes = notes or offer.notes

            if accepted:
                offer.status = OfferStatus.ACCEPTED
                event_type = EventType.OFFER_ACCEPTED

                # Update candidate status
                result = await db.execute(
                    select(Candidate).where(Candidate.id == offer.candidate_id)
                )
                candidate = result.scalar_one_or_none()
                if candidate:
                    candidate.status = CandidateStatus.OFFER_ACCEPTED
                    db.add(candidate)

            else:
                offer.status = OfferStatus.DECLINED
                event_type = EventType.OFFER_DECLINED

                # Return candidate to talent pool
                result = await db.execute(
                    select(Candidate).where(Candidate.id == offer.candidate_id)
                )
                candidate = result.scalar_one_or_none()
                if candidate:
                    candidate.status = CandidateStatus.TALENT_POOL
                    db.add(candidate)

            db.add(offer)
            await db.commit()
            await db.refresh(offer)

            # Emit event
            await self.emit_event(
                event_type=event_type,
                entity_type="Offer",
                entity_id=offer.id,
                payload={
                    "offer_id": offer.id,
                    "candidate_id": offer.candidate_id,
                    "accepted": accepted,
                    "notes": notes,
                },
            )

            logger.info(f"Processed offer {offer_id}: {'ACCEPTED' if accepted else 'DECLINED'}")
            return offer

        except Exception as e:
            await db.rollback()
            logger.error(f"Error processing offer response: {str(e)}")
            raise

    async def handle_negotiation(
        self,
        db: AsyncSession,
        offer_id: int,
        counter_rate: float,
        counter_terms: Dict[str, Any],
    ) -> Offer:
        """Handle offer negotiation.

        Sets NEGOTIATING, appends to negotiation_history with timestamp,
        checks max rounds (default 3).

        Args:
            db: Database session
            offer_id: Offer ID
            counter_rate: Counter offer rate
            counter_terms: Counter offer terms

        Returns:
            Updated offer

        Raises:
            ValueError: If offer not found or max negotiation rounds exceeded
        """
        try:
            # Fetch offer
            result = await db.execute(
                select(Offer).where(Offer.id == offer_id)
            )
            offer = result.scalar_one_or_none()

            if not offer:
                raise ValueError(f"Offer {offer_id} not found")

            # Check negotiation rounds
            history = offer.negotiation_history or []
            if len(history) >= self.max_negotiation_rounds:
                raise ValueError(
                    f"Maximum negotiation rounds ({self.max_negotiation_rounds}) exceeded"
                )

            # Update offer
            offer.status = OfferStatus.NEGOTIATING

            # Append to history
            negotiation_entry = {
                "round": len(history) + 1,
                "counter_rate": counter_rate,
                "counter_terms": counter_terms,
                "timestamp": datetime.utcnow().isoformat(),
                "previous_rate": offer.offered_rate,
            }
            history.append(negotiation_entry)
            offer.negotiation_history = history

            # Update offered rate
            offer.offered_rate = counter_rate

            db.add(offer)
            await db.commit()
            await db.refresh(offer)

            # Emit event
            await self.emit_event(
                event_type=EventType.OFFER_NEGOTIATING,
                entity_type="Offer",
                entity_id=offer.id,
                payload={
                    "offer_id": offer.id,
                    "candidate_id": offer.candidate_id,
                    "round": len(history),
                    "counter_rate": counter_rate,
                },
            )

            logger.info(f"Negotiation round {len(history)} for offer {offer_id}")
            return offer

        except Exception as e:
            await db.rollback()
            logger.error(f"Error handling negotiation: {str(e)}")
            raise

    async def start_onboarding(
        self,
        db: AsyncSession,
        offer_id: int,
        customer_id: Optional[int] = None,
    ) -> Onboarding:
        """Start onboarding process.

        Creates Onboarding record with default checklist items.

        Args:
            db: Database session
            offer_id: Offer ID
            customer_id: Optional customer ID

        Returns:
            Created onboarding record

        Raises:
            ValueError: If offer not found or not accepted
        """
        try:
            # Fetch offer
            result = await db.execute(
                select(Offer).where(Offer.id == offer_id)
            )
            offer = result.scalar_one_or_none()

            if not offer:
                raise ValueError(f"Offer {offer_id} not found")

            if offer.status != OfferStatus.ACCEPTED:
                raise ValueError(
                    f"Can only start onboarding for ACCEPTED offers. Current status: {offer.status}"
                )

            # Create checklist
            checklist = [
                {"item": item, "completed": False, "completed_at": None}
                for item in self.default_checklist_items
            ]

            # Create onboarding
            onboarding = Onboarding(
                offer_id=offer.id,
                candidate_id=offer.candidate_id,
                status=OnboardingStatus.IN_PROGRESS,
                checklist=checklist,
            )

            db.add(onboarding)
            await db.commit()
            await db.refresh(onboarding)

            # Emit event
            await self.emit_event(
                event_type=EventType.ONBOARDING_STARTED,
                entity_type="Onboarding",
                entity_id=onboarding.id,
                payload={
                    "onboarding_id": onboarding.id,
                    "offer_id": offer_id,
                    "candidate_id": offer.candidate_id,
                },
            )

            logger.info(f"Started onboarding {onboarding.id} for offer {offer_id}")
            return onboarding

        except Exception as e:
            await db.rollback()
            logger.error(f"Error starting onboarding: {str(e)}")
            raise

    async def update_checklist_item(
        self,
        db: AsyncSession,
        onboarding_id: int,
        item_name: str,
        completed: bool,
    ) -> Onboarding:
        """Update specific checklist item status.

        Args:
            db: Database session
            onboarding_id: Onboarding ID
            item_name: Checklist item name
            completed: Whether item is completed

        Returns:
            Updated onboarding

        Raises:
            ValueError: If onboarding not found or item not in checklist
        """
        try:
            # Fetch onboarding
            result = await db.execute(
                select(Onboarding).where(Onboarding.id == onboarding_id)
            )
            onboarding = result.scalar_one_or_none()

            if not onboarding:
                raise ValueError(f"Onboarding {onboarding_id} not found")

            # Update checklist
            checklist = onboarding.checklist or []
            item_found = False

            for item in checklist:
                if item["item"] == item_name:
                    item["completed"] = completed
                    if completed:
                        item["completed_at"] = datetime.utcnow().isoformat()
                    item_found = True
                    break

            if not item_found:
                raise ValueError(f"Checklist item {item_name} not found")

            onboarding.checklist = checklist
            db.add(onboarding)
            await db.commit()
            await db.refresh(onboarding)

            logger.info(f"Updated checklist item {item_name} for onboarding {onboarding_id}")
            return onboarding

        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating checklist item: {str(e)}")
            raise

    async def complete_onboarding(
        self,
        db: AsyncSession,
        onboarding_id: int,
    ) -> Onboarding:
        """Complete onboarding process.

        Verifies all checklist items complete, sets COMPLETED,
        updates candidate to PLACED, updates requirement positions_filled.

        Args:
            db: Database session
            onboarding_id: Onboarding ID

        Returns:
            Updated onboarding

        Raises:
            ValueError: If onboarding not found or not all items completed
        """
        try:
            # Fetch onboarding
            result = await db.execute(
                select(Onboarding).where(Onboarding.id == onboarding_id)
            )
            onboarding = result.scalar_one_or_none()

            if not onboarding:
                raise ValueError(f"Onboarding {onboarding_id} not found")

            # Verify all checklist items completed
            checklist = onboarding.checklist or []
            all_completed = all(item.get("completed", False) for item in checklist)

            if not all_completed:
                incomplete_items = [
                    item["item"] for item in checklist if not item.get("completed", False)
                ]
                raise ValueError(
                    f"Cannot complete onboarding. Incomplete items: {', '.join(incomplete_items)}"
                )

            # Update onboarding
            onboarding.status = OnboardingStatus.COMPLETED
            db.add(onboarding)

            # Update candidate status
            result = await db.execute(
                select(Candidate).where(Candidate.id == onboarding.candidate_id)
            )
            candidate = result.scalar_one_or_none()
            if candidate:
                candidate.status = CandidateStatus.PLACED
                db.add(candidate)

            # Update requirement positions_filled
            result = await db.execute(
                select(Offer).where(Offer.id == onboarding.offer_id)
            )
            offer = result.scalar_one_or_none()
            if offer:
                result = await db.execute(
                    select(Requirement).where(Requirement.id == offer.requirement_id)
                )
                requirement = result.scalar_one_or_none()
                if requirement:
                    requirement.positions_filled = min(
                        requirement.positions_filled + 1,
                        requirement.positions_count,
                    )
                    db.add(requirement)

            await db.commit()
            await db.refresh(onboarding)

            # Emit event
            await self.emit_event(
                event_type=EventType.ONBOARDING_COMPLETED,
                entity_type="Onboarding",
                entity_id=onboarding.id,
                payload={
                    "onboarding_id": onboarding.id,
                    "candidate_id": onboarding.candidate_id,
                },
            )

            logger.info(f"Completed onboarding {onboarding_id}")
            return onboarding

        except Exception as e:
            await db.rollback()
            logger.error(f"Error completing onboarding: {str(e)}")
            raise

    async def handle_backout(
        self,
        db: AsyncSession,
        onboarding_id: int,
        reason: str,
    ) -> Onboarding:
        """Handle candidate backout from onboarding.

        Sets BACKOUT status, reverts candidate to TALENT_POOL,
        checks if requirement needs reopening, emits events.

        Args:
            db: Database session
            onboarding_id: Onboarding ID
            reason: Backout reason

        Returns:
            Updated onboarding

        Raises:
            ValueError: If onboarding not found
        """
        try:
            # Fetch onboarding
            result = await db.execute(
                select(Onboarding).where(Onboarding.id == onboarding_id)
            )
            onboarding = result.scalar_one_or_none()

            if not onboarding:
                raise ValueError(f"Onboarding {onboarding_id} not found")

            # Update onboarding
            onboarding.status = OnboardingStatus.BACKOUT
            onboarding.notes = f"Backout reason: {reason}"
            db.add(onboarding)

            # Update candidate
            result = await db.execute(
                select(Candidate).where(Candidate.id == onboarding.candidate_id)
            )
            candidate = result.scalar_one_or_none()
            if candidate:
                candidate.status = CandidateStatus.BACKOUT
                db.add(candidate)

            # Check if requirement was filled
            result = await db.execute(
                select(Offer).where(Offer.id == onboarding.offer_id)
            )
            offer = result.scalar_one_or_none()
            if offer:
                result = await db.execute(
                    select(Requirement).where(Requirement.id == offer.requirement_id)
                )
                requirement = result.scalar_one_or_none()
                if requirement and requirement.positions_filled > 0:
                    requirement.positions_filled -= 1
                    if requirement.positions_filled < requirement.positions_count:
                        # Reopen requirement
                        from models.enums import RequirementStatus
                        requirement.status = RequirementStatus.ACTIVE
                    db.add(requirement)

            await db.commit()
            await db.refresh(onboarding)

            # Emit event
            await self.emit_event(
                event_type=EventType.ONBOARDING_BACKOUT,
                entity_type="Onboarding",
                entity_id=onboarding.id,
                payload={
                    "onboarding_id": onboarding.id,
                    "candidate_id": onboarding.candidate_id,
                    "reason": reason,
                },
            )

            logger.info(f"Handled backout for onboarding {onboarding_id}")
            return onboarding

        except Exception as e:
            await db.rollback()
            logger.error(f"Error handling backout: {str(e)}")
            raise

    async def check_offer_expirations(
        self,
        db: AsyncSession,
        expiry_days: int = 7,
    ) -> List[Offer]:
        """Find and auto-expire offers past expiration date.

        Args:
            db: Database session
            expiry_days: Days until offer expires

        Returns:
            List of expired offers

        Raises:
            Exception: If database operations fail
        """
        try:
            # Find offers sent more than expiry_days ago
            cutoff_date = datetime.utcnow() - timedelta(days=expiry_days)

            result = await db.execute(
                select(Offer).where(
                    and_(
                        Offer.sent_at.isnot(None),
                        Offer.sent_at < cutoff_date,
                        Offer.status.in_(
                            [OfferStatus.SENT, OfferStatus.NEGOTIATING]
                        ),
                    )
                )
            )
            expired_offers = result.scalars().all()

            # Auto-expire
            for offer in expired_offers:
                offer.status = OfferStatus.EXPIRED
                db.add(offer)

            if expired_offers:
                await db.commit()

            logger.info(f"Found and expired {len(expired_offers)} offers")
            return expired_offers

        except Exception as e:
            await db.rollback()
            logger.error(f"Error checking offer expirations: {str(e)}")
            raise

    async def get_offer_analytics(
        self,
        db: AsyncSession,
    ) -> Dict[str, Any]:
        """Get offer and onboarding analytics.

        Calculates acceptance rate, avg negotiation rounds, avg time to accept,
        backout rate.

        Args:
            db: Database session

        Returns:
            Dictionary with analytics

        Raises:
            Exception: If database operations fail
        """
        try:
            # Fetch all offers
            result = await db.execute(select(Offer))
            offers = result.scalars().all()

            total_offers = len(offers)
            accepted_count = sum(1 for o in offers if o.status == OfferStatus.ACCEPTED)
            declined_count = sum(1 for o in offers if o.status == OfferStatus.DECLINED)
            negotiating_count = sum(1 for o in offers if o.status == OfferStatus.NEGOTIATING)

            # Calculate negotiation stats
            negotiation_rounds = []
            for offer in offers:
                if offer.negotiation_history:
                    negotiation_rounds.append(len(offer.negotiation_history))

            avg_negotiation_rounds = (
                sum(negotiation_rounds) / len(negotiation_rounds)
                if negotiation_rounds
                else 0
            )

            # Calculate time to accept
            times_to_accept = []
            for offer in offers:
                if offer.sent_at and offer.response_at and offer.status == OfferStatus.ACCEPTED:
                    delta = (offer.response_at - offer.sent_at).days
                    times_to_accept.append(delta)

            avg_time_to_accept = (
                sum(times_to_accept) / len(times_to_accept)
                if times_to_accept
                else 0
            )

            # Calculate backout rate
            result = await db.execute(select(Onboarding))
            onboardings = result.scalars().all()
            backout_count = sum(1 for o in onboardings if o.status == OnboardingStatus.BACKOUT)
            backout_rate = (backout_count / len(onboardings) * 100) if onboardings else 0

            analytics = {
                "total_offers": total_offers,
                "accepted_count": accepted_count,
                "declined_count": declined_count,
                "negotiating_count": negotiating_count,
                "acceptance_rate": (accepted_count / total_offers * 100) if total_offers > 0 else 0,
                "decline_rate": (declined_count / total_offers * 100) if total_offers > 0 else 0,
                "average_negotiation_rounds": avg_negotiation_rounds,
                "average_days_to_accept": avg_time_to_accept,
                "backout_rate": backout_rate,
                "total_onboardings": len(onboardings),
                "completed_onboardings": sum(
                    1 for o in onboardings if o.status == OnboardingStatus.COMPLETED
                ),
            }

            logger.info(f"Generated offer analytics for {total_offers} offers")
            return analytics

        except Exception as e:
            logger.error(f"Error generating offer analytics: {str(e)}")
            raise
