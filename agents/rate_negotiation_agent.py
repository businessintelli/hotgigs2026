"""Rate negotiation and interview scheduling agent."""

import logging
from datetime import datetime, date
from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from agents.base_agent import BaseAgent
from agents.events import EventType
from models.negotiation import RateNegotiation, NegotiationRound, InterviewSchedule
from models.submission import Submission
from models.candidate import Candidate
from models.requirement import Requirement
from services.rate_negotiation_service import RateNegotiationService, InterviewSchedulingService
from schemas.negotiation import (
    RateNegotiationCreate,
    RateNegotiationUpdate,
    NegotiationRoundCreate,
    NegotiationRoundUpdate,
    InterviewScheduleCreate,
    InterviewRescheduleRequest,
    InterviewCancelRequest,
)

logger = logging.getLogger(__name__)


class RateNegotiationAgent(BaseAgent):
    """Agent for managing rate negotiation workflows and interview scheduling."""

    def __init__(self):
        """Initialize the rate negotiation agent."""
        super().__init__(
            agent_name="RateNegotiationAgent",
            agent_version="1.0.0",
        )
        self.market_rate_multipliers = {
            "junior": 0.8,
            "mid": 1.0,
            "senior": 1.2,
            "lead": 1.5,
        }

    async def initiate_negotiation(
        self,
        db: AsyncSession,
        submission_id: int,
        initial_offer: float,
        rate_type: str,
        candidate_desired_rate: Optional[float] = None,
        customer_max_rate: Optional[float] = None,
        bill_rate: Optional[float] = None,
        pay_rate: Optional[float] = None,
        target_margin_percentage: float = 20.0,
    ) -> RateNegotiation:
        """Start rate negotiation for a submission.

        Args:
            db: Database session
            submission_id: Submission ID
            initial_offer: Initial proposed rate
            rate_type: Rate type (hourly/annual/monthly)
            candidate_desired_rate: Candidate's desired rate
            customer_max_rate: Customer's maximum budget
            bill_rate: Bill rate (if known)
            pay_rate: Pay rate (if known)
            target_margin_percentage: Target margin percentage

        Returns:
            Created rate negotiation

        Raises:
            ValueError: If submission not found
        """
        try:
            service = RateNegotiationService(db)

            negotiation_data = RateNegotiationCreate(
                submission_id=submission_id,
                initial_offer=initial_offer,
                rate_type=rate_type,
                candidate_desired_rate=candidate_desired_rate,
                customer_max_rate=customer_max_rate,
                bill_rate=bill_rate,
                pay_rate=pay_rate,
                target_margin_percentage=target_margin_percentage,
            )

            negotiation = await service.create_negotiation(negotiation_data)

            # Emit event
            await self.emit_event(
                event_type=EventType.RATE_NEGOTIATION_STARTED,
                entity_type="RateNegotiation",
                entity_id=negotiation.id,
                payload={
                    "negotiation_id": negotiation.id,
                    "submission_id": submission_id,
                    "initial_offer": initial_offer,
                    "rate_type": rate_type,
                },
            )

            logger.info(f"Initiated rate negotiation {negotiation.id} for submission {submission_id}")
            return negotiation

        except Exception as e:
            logger.error(f"Error initiating negotiation: {str(e)}")
            raise

    async def submit_counter_offer(
        self,
        db: AsyncSession,
        negotiation_id: int,
        counter_rate: float,
        counter_notes: Optional[str] = None,
    ) -> NegotiationRound:
        """Submit counter offer in negotiation.

        Args:
            db: Database session
            negotiation_id: Negotiation ID
            counter_rate: Counter rate proposed
            counter_notes: Optional notes

        Returns:
            Updated negotiation round

        Raises:
            ValueError: If negotiation not found
        """
        try:
            service = RateNegotiationService(db)

            round_data = NegotiationRoundUpdate(
                counter_rate=counter_rate,
                counter_notes=counter_notes,
                status="countered",
            )

            round = await service.submit_counter_offer(negotiation_id, round_data)

            # Emit event
            await self.emit_event(
                event_type=EventType.RATE_COUNTER_OFFERED,
                entity_type="NegotiationRound",
                entity_id=round.id,
                payload={
                    "negotiation_id": negotiation_id,
                    "counter_rate": counter_rate,
                    "round_number": round.round_number,
                },
            )

            logger.info(f"Counter offer submitted for negotiation {negotiation_id}")
            return round

        except Exception as e:
            logger.error(f"Error submitting counter offer: {str(e)}")
            raise

    async def suggest_rate(
        self,
        db: AsyncSession,
        negotiation_id: int,
    ) -> Dict[str, Any]:
        """AI-powered rate suggestion based on market data and history.

        Args:
            db: Database session
            negotiation_id: Negotiation ID

        Returns:
            Rate suggestion with reasoning

        Raises:
            ValueError: If negotiation not found
        """
        try:
            service = RateNegotiationService(db)
            negotiation = await service.get_negotiation(negotiation_id)

            if not negotiation:
                raise ValueError(f"Negotiation {negotiation_id} not found")

            # Get candidate info for level estimation
            result = await db.execute(
                select(Candidate).where(Candidate.id == negotiation.candidate_id)
            )
            candidate = result.scalar_one_or_none()

            # Fetch requirement for context
            result = await db.execute(
                select(Requirement).where(Requirement.id == negotiation.requirement_id)
            )
            requirement = result.scalar_one_or_none()

            # Estimate level (simplified - would use ML in production)
            level = "mid"  # Default
            if candidate and candidate.experience_years:
                if candidate.experience_years < 2:
                    level = "junior"
                elif candidate.experience_years < 5:
                    level = "mid"
                elif candidate.experience_years < 10:
                    level = "senior"
                else:
                    level = "lead"

            # Calculate suggested rate
            base_rate = negotiation.current_proposed_rate
            multiplier = self.market_rate_multipliers.get(level, 1.0)
            suggested_rate = base_rate * multiplier

            # Adjust for candidate desires and customer max
            if negotiation.candidate_desired_rate:
                suggested_rate = (suggested_rate + negotiation.candidate_desired_rate) / 2

            if negotiation.customer_max_rate:
                suggested_rate = min(suggested_rate, negotiation.customer_max_rate)

            return {
                "suggested_rate": round(suggested_rate, 2),
                "rate_type": negotiation.rate_type,
                "reasoning": f"Based on {level}-level candidate with {candidate.experience_years if candidate else 'unknown'} years experience",
                "confidence_score": 0.75,
                "market_comparison": {
                    "current_proposed": negotiation.current_proposed_rate,
                    "candidate_desired": negotiation.candidate_desired_rate,
                    "customer_max": negotiation.customer_max_rate,
                    "suggested": suggested_rate,
                },
                "next_steps": [
                    "Review suggested rate with candidate",
                    "Validate with customer budget",
                    "Check margin acceptability",
                ],
            }

        except Exception as e:
            logger.error(f"Error suggesting rate: {str(e)}")
            raise

    async def evaluate_margin(
        self,
        db: AsyncSession,
        negotiation_id: int,
        proposed_rate: float,
    ) -> Dict[str, Any]:
        """Evaluate margin at proposed rate.

        Args:
            db: Database session
            negotiation_id: Negotiation ID
            proposed_rate: Rate to evaluate

        Returns:
            Margin evaluation results

        Raises:
            ValueError: If negotiation not found
        """
        try:
            service = RateNegotiationService(db)
            return await service.evaluate_margin(negotiation_id, proposed_rate)

        except Exception as e:
            logger.error(f"Error evaluating margin: {str(e)}")
            raise

    async def auto_negotiate(
        self,
        db: AsyncSession,
        negotiation_id: int,
        strategy: str = "balanced",
    ) -> Dict[str, Any]:
        """AI auto-negotiation response generation.

        Strategies:
        - aggressive: Maximize margin, may lose deals
        - balanced: Balance margin and success rate
        - candidate_friendly: Prioritize candidate acceptance

        Args:
            db: Database session
            negotiation_id: Negotiation ID
            strategy: Negotiation strategy

        Returns:
            Auto-negotiation recommendation

        Raises:
            ValueError: If negotiation not found
        """
        try:
            service = RateNegotiationService(db)
            negotiation = await service.get_negotiation(negotiation_id)

            if not negotiation:
                raise ValueError(f"Negotiation {negotiation_id} not found")

            # Get latest round
            result = await db.execute(
                select(NegotiationRound)
                .where(NegotiationRound.negotiation_id == negotiation_id)
                .order_by(NegotiationRound.round_number.desc())
                .limit(1)
            )
            latest_round = result.scalar_one_or_none()

            if not latest_round:
                return {"error": "No negotiation rounds found", "recommendation": None}

            # Calculate response rate based on strategy
            base_rate = latest_round.counter_rate or negotiation.current_proposed_rate

            if strategy == "aggressive":
                # Move toward customer max or margin target
                response_rate = (base_rate + negotiation.initial_proposed_rate) / 2
                confidence = 0.6
                tone = "firm"
            elif strategy == "candidate_friendly":
                # Move toward candidate desired or increase
                response_rate = base_rate * 1.05 if base_rate < (negotiation.candidate_desired_rate or float('inf')) else base_rate
                confidence = 0.8
                tone = "collaborative"
            else:  # balanced
                # Move gradually toward middle ground
                if negotiation.candidate_desired_rate:
                    response_rate = (base_rate + negotiation.candidate_desired_rate) / 2
                else:
                    response_rate = base_rate * 1.02
                confidence = 0.75
                tone = "professional"

            # Ensure customer max is respected
            if negotiation.customer_max_rate:
                response_rate = min(response_rate, negotiation.customer_max_rate)

            return {
                "suggested_response_rate": round(response_rate, 2),
                "rate_type": negotiation.rate_type,
                "strategy": strategy,
                "tone": tone,
                "confidence_score": confidence,
                "reasoning": f"Response calculated using {strategy} strategy",
                "recommendation": f"Propose rate of {response_rate} {negotiation.rate_type}",
                "next_action": "Submit counter offer or finalize agreement",
            }

        except Exception as e:
            logger.error(f"Error in auto-negotiation: {str(e)}")
            raise

    async def finalize_rate(
        self,
        db: AsyncSession,
        negotiation_id: int,
        agreed_rate: float,
        agreed_rate_type: str,
    ) -> RateNegotiation:
        """Finalize agreed rate.

        Args:
            db: Database session
            negotiation_id: Negotiation ID
            agreed_rate: Final agreed rate
            agreed_rate_type: Rate type

        Returns:
            Updated negotiation

        Raises:
            ValueError: If negotiation not found
        """
        try:
            service = RateNegotiationService(db)
            negotiation = await service.finalize_rate(negotiation_id, agreed_rate, agreed_rate_type)

            # Emit event
            await self.emit_event(
                event_type=EventType.RATE_AGREED,
                entity_type="RateNegotiation",
                entity_id=negotiation.id,
                payload={
                    "negotiation_id": negotiation_id,
                    "agreed_rate": agreed_rate,
                    "rate_type": agreed_rate_type,
                    "margin_percentage": negotiation.margin_percentage,
                },
            )

            logger.info(f"Finalized rate for negotiation {negotiation_id}: {agreed_rate}")
            return negotiation

        except Exception as e:
            logger.error(f"Error finalizing rate: {str(e)}")
            raise

    async def get_negotiation_analytics(self, db: AsyncSession) -> Dict[str, Any]:
        """Get negotiation analytics.

        Args:
            db: Database session

        Returns:
            Analytics data

        Raises:
            Exception: If database operation fails
        """
        try:
            service = RateNegotiationService(db)
            return await service.get_negotiation_analytics()

        except Exception as e:
            logger.error(f"Error getting analytics: {str(e)}")
            raise

    # ===== Interview Scheduling Methods =====

    async def schedule_interview(
        self,
        db: AsyncSession,
        schedule_data: InterviewScheduleCreate,
        scheduled_by_user_id: int,
    ) -> InterviewSchedule:
        """Schedule interview with conflict detection.

        Args:
            db: Database session
            schedule_data: Interview schedule data
            scheduled_by_user_id: User who scheduled

        Returns:
            Created interview schedule

        Raises:
            Exception: If database operation fails
        """
        try:
            service = InterviewSchedulingService(db)
            schedule = await service.schedule_interview(schedule_data)

            # Emit event
            await self.emit_event(
                event_type=EventType.INTERVIEW_SCHEDULED,
                entity_type="InterviewSchedule",
                entity_id=schedule.id,
                payload={
                    "schedule_id": schedule.id,
                    "candidate_id": schedule_data.candidate_id,
                    "interview_type": schedule_data.interview_type,
                    "scheduled_date": schedule_data.scheduled_date,
                    "scheduled_time": schedule_data.scheduled_time,
                },
                user_id=scheduled_by_user_id,
            )

            logger.info(f"Scheduled interview {schedule.id} for candidate {schedule_data.candidate_id}")
            return schedule

        except Exception as e:
            logger.error(f"Error scheduling interview: {str(e)}")
            raise

    async def reschedule_interview(
        self,
        db: AsyncSession,
        schedule_id: int,
        new_date: str,
        new_time: str,
        reason: str,
        rescheduled_by_user_id: int,
    ) -> InterviewSchedule:
        """Reschedule interview.

        Args:
            db: Database session
            schedule_id: Schedule ID
            new_date: New date (YYYY-MM-DD)
            new_time: New time (HH:MM)
            reason: Reschedule reason
            rescheduled_by_user_id: User who rescheduled

        Returns:
            Updated interview schedule

        Raises:
            ValueError: If schedule not found
        """
        try:
            service = InterviewSchedulingService(db)

            reschedule_data = InterviewRescheduleRequest(
                scheduled_date=new_date,
                scheduled_time=new_time,
                reason=reason,
            )

            schedule = await service.reschedule_interview(schedule_id, reschedule_data, rescheduled_by_user_id)

            # Emit event
            await self.emit_event(
                event_type=EventType.INTERVIEW_RESCHEDULED,
                entity_type="InterviewSchedule",
                entity_id=schedule.id,
                payload={
                    "schedule_id": schedule_id,
                    "new_date": new_date,
                    "new_time": new_time,
                    "reason": reason,
                    "reschedule_count": schedule.reschedule_count,
                },
                user_id=rescheduled_by_user_id,
            )

            logger.info(f"Rescheduled interview {schedule_id}: {reason}")
            return schedule

        except Exception as e:
            logger.error(f"Error rescheduling interview: {str(e)}")
            raise

    async def cancel_interview(
        self,
        db: AsyncSession,
        schedule_id: int,
        reason: str,
    ) -> InterviewSchedule:
        """Cancel interview.

        Args:
            db: Database session
            schedule_id: Schedule ID
            reason: Cancellation reason

        Returns:
            Updated interview schedule

        Raises:
            ValueError: If schedule not found
        """
        try:
            service = InterviewSchedulingService(db)

            cancel_data = InterviewCancelRequest(reason=reason)
            schedule = await service.cancel_interview(schedule_id, cancel_data)

            # Emit event
            await self.emit_event(
                event_type=EventType.INTERVIEW_CANCELLED,
                entity_type="InterviewSchedule",
                entity_id=schedule.id,
                payload={
                    "schedule_id": schedule_id,
                    "reason": reason,
                },
            )

            logger.info(f"Cancelled interview {schedule_id}: {reason}")
            return schedule

        except Exception as e:
            logger.error(f"Error cancelling interview: {str(e)}")
            raise

    async def send_reminders(
        self,
        db: AsyncSession,
        hours_before: int = 24,
    ) -> Dict[str, Any]:
        """Send reminders for upcoming interviews.

        Args:
            db: Database session
            hours_before: Hours before interview to send reminder

        Returns:
            Reminder status

        Raises:
            Exception: If database operation fails
        """
        try:
            service = InterviewSchedulingService(db)
            reminded_ids = await service.send_reminders(hours_before)

            return {
                "interviews_reminded": len(reminded_ids),
                "schedule_ids": reminded_ids,
                "status": "completed",
            }

        except Exception as e:
            logger.error(f"Error sending reminders: {str(e)}")
            raise

    async def get_scheduling_analytics(self, db: AsyncSession) -> Dict[str, Any]:
        """Get interview scheduling analytics.

        Args:
            db: Database session

        Returns:
            Analytics data

        Raises:
            Exception: If database operation fails
        """
        try:
            service = InterviewSchedulingService(db)
            return await service.get_scheduling_analytics()

        except Exception as e:
            logger.error(f"Error getting scheduling analytics: {str(e)}")
            raise
