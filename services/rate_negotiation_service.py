"""Rate negotiation and interview scheduling service."""

import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from models.negotiation import RateNegotiation, NegotiationRound, InterviewSchedule
from models.submission import Submission
from models.candidate import Candidate
from models.requirement import Requirement
from models.customer import Customer
from schemas.negotiation import (
    RateNegotiationCreate,
    RateNegotiationUpdate,
    NegotiationRoundCreate,
    NegotiationRoundUpdate,
    InterviewScheduleCreate,
    InterviewScheduleUpdate,
    InterviewRescheduleRequest,
    InterviewCancelRequest,
    AvailabilityCheckRequest,
)

logger = logging.getLogger(__name__)


class RateNegotiationService:
    """Service for rate negotiation lifecycle management."""

    def __init__(self, db: AsyncSession):
        """Initialize service.

        Args:
            db: Database session
        """
        self.db = db

    async def create_negotiation(
        self,
        negotiation_data: RateNegotiationCreate,
    ) -> RateNegotiation:
        """Create new rate negotiation.

        Args:
            negotiation_data: Negotiation creation data

        Returns:
            Created negotiation

        Raises:
            Exception: If database operation fails
        """
        try:
            # Fetch submission to get all IDs
            result = await self.db.execute(
                select(Submission).where(Submission.id == negotiation_data.submission_id)
            )
            submission = result.scalar_one_or_none()

            if not submission:
                raise ValueError(f"Submission {negotiation_data.submission_id} not found")

            negotiation = RateNegotiation(
                submission_id=submission.id,
                candidate_id=submission.candidate_id,
                requirement_id=submission.requirement_id,
                customer_id=submission.requirement.customer_id,
                initial_proposed_rate=negotiation_data.initial_offer,
                current_proposed_rate=negotiation_data.initial_offer,
                rate_type=negotiation_data.rate_type,
                candidate_desired_rate=negotiation_data.candidate_desired_rate,
                customer_max_rate=negotiation_data.customer_max_rate,
                bill_rate=negotiation_data.bill_rate,
                pay_rate=negotiation_data.pay_rate,
                target_margin_percentage=negotiation_data.target_margin_percentage,
                status="initiated",
            )

            self.db.add(negotiation)
            await self.db.commit()
            await self.db.refresh(negotiation)

            logger.info(f"Created rate negotiation {negotiation.id} for submission {negotiation_data.submission_id}")
            return negotiation

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating negotiation: {str(e)}")
            raise

    async def get_negotiation(self, negotiation_id: int) -> Optional[RateNegotiation]:
        """Get negotiation by ID.

        Args:
            negotiation_id: Negotiation ID

        Returns:
            Negotiation or None

        Raises:
            Exception: If database operation fails
        """
        try:
            result = await self.db.execute(
                select(RateNegotiation).where(RateNegotiation.id == negotiation_id)
            )
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"Error getting negotiation: {str(e)}")
            raise

    async def get_negotiations(
        self,
        skip: int = 0,
        limit: int = 20,
        submission_id: Optional[int] = None,
        status: Optional[str] = None,
        candidate_id: Optional[int] = None,
    ) -> Tuple[List[RateNegotiation], int]:
        """Get negotiations with filtering and pagination.

        Args:
            skip: Skip count
            limit: Result limit
            submission_id: Filter by submission
            status: Filter by status
            candidate_id: Filter by candidate

        Returns:
            Tuple of negotiations and total count

        Raises:
            Exception: If database operation fails
        """
        try:
            query = select(RateNegotiation)
            count_query = select(func.count(RateNegotiation.id))

            filters = []
            if submission_id:
                filters.append(RateNegotiation.submission_id == submission_id)
            if status:
                filters.append(RateNegotiation.status == status)
            if candidate_id:
                filters.append(RateNegotiation.candidate_id == candidate_id)

            if filters:
                query = query.where(and_(*filters))
                count_query = count_query.where(and_(*filters))

            # Get total count
            count_result = await self.db.execute(count_query)
            total = count_result.scalar() or 0

            # Get paginated results
            result = await self.db.execute(
                query.order_by(desc(RateNegotiation.started_at)).offset(skip).limit(limit)
            )
            negotiations = result.scalars().all()

            return negotiations, total

        except Exception as e:
            logger.error(f"Error getting negotiations: {str(e)}")
            raise

    async def submit_counter_offer(
        self,
        negotiation_id: int,
        round_data: NegotiationRoundUpdate,
    ) -> NegotiationRound:
        """Submit counter offer in negotiation.

        Args:
            negotiation_id: Negotiation ID
            round_data: Counter offer data

        Returns:
            Updated negotiation round

        Raises:
            Exception: If database operation fails
        """
        try:
            # Get latest round
            result = await self.db.execute(
                select(NegotiationRound)
                .where(NegotiationRound.negotiation_id == negotiation_id)
                .order_by(desc(NegotiationRound.round_number))
                .limit(1)
            )
            latest_round = result.scalar_one_or_none()

            if not latest_round:
                raise ValueError(f"No rounds found for negotiation {negotiation_id}")

            # Update round with counter
            latest_round.counter_rate = round_data.counter_rate
            latest_round.counter_notes = round_data.counter_notes
            latest_round.status = "countered"
            latest_round.responded_at = datetime.utcnow()

            # Update negotiation
            negotiation = await self.get_negotiation(negotiation_id)
            if negotiation:
                negotiation.current_proposed_rate = round_data.counter_rate or negotiation.current_proposed_rate
                negotiation.status = "in_progress"

            await self.db.commit()
            await self.db.refresh(latest_round)

            logger.info(f"Submitted counter offer for negotiation {negotiation_id}")
            return latest_round

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error submitting counter offer: {str(e)}")
            raise

    async def add_negotiation_round(
        self,
        negotiation_id: int,
        round_data: NegotiationRoundCreate,
    ) -> NegotiationRound:
        """Add new negotiation round.

        Args:
            negotiation_id: Negotiation ID
            round_data: Round creation data

        Returns:
            Created negotiation round

        Raises:
            Exception: If database operation fails
        """
        try:
            # Get negotiation
            negotiation = await self.get_negotiation(negotiation_id)
            if not negotiation:
                raise ValueError(f"Negotiation {negotiation_id} not found")

            # Check max rounds
            if negotiation.total_rounds >= negotiation.max_rounds:
                raise ValueError(f"Maximum negotiation rounds ({negotiation.max_rounds}) reached")

            # Create round
            round_number = negotiation.total_rounds + 1
            negotiation_round = NegotiationRound(
                negotiation_id=negotiation_id,
                round_number=round_number,
                proposed_by=round_data.proposed_by,
                proposed_rate=round_data.proposed_rate,
                rate_type=round_data.rate_type,
                notes=round_data.notes,
                status="proposed",
            )

            # Update negotiation
            negotiation.total_rounds = round_number
            negotiation.current_proposed_rate = round_data.proposed_rate
            if round_number == 1:
                negotiation.status = "in_progress"

            self.db.add(negotiation_round)
            await self.db.commit()
            await self.db.refresh(negotiation_round)

            logger.info(f"Added negotiation round {round_number} for negotiation {negotiation_id}")
            return negotiation_round

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error adding negotiation round: {str(e)}")
            raise

    async def evaluate_margin(
        self,
        negotiation_id: int,
        proposed_rate: float,
    ) -> Dict[str, Any]:
        """Evaluate margin at proposed rate.

        Args:
            negotiation_id: Negotiation ID
            proposed_rate: Proposed rate

        Returns:
            Margin evaluation results

        Raises:
            Exception: If database operation fails
        """
        try:
            negotiation = await self.get_negotiation(negotiation_id)
            if not negotiation:
                raise ValueError(f"Negotiation {negotiation_id} not found")

            # Calculate margin
            bill_rate = negotiation.bill_rate or proposed_rate * 1.3
            pay_rate = proposed_rate
            margin = bill_rate - pay_rate
            margin_percentage = (margin / bill_rate * 100) if bill_rate > 0 else 0

            is_acceptable = margin_percentage >= negotiation.target_margin_percentage

            return {
                "proposed_rate": proposed_rate,
                "bill_rate": bill_rate,
                "pay_rate": pay_rate,
                "margin_amount": margin,
                "margin_percentage": margin_percentage,
                "target_margin_percentage": negotiation.target_margin_percentage,
                "is_acceptable": is_acceptable,
                "feedback": (
                    "Margin meets target"
                    if is_acceptable
                    else f"Margin below target by {negotiation.target_margin_percentage - margin_percentage:.1f}%"
                ),
                "recommendations": [
                    "Consider counter-offer" if not is_acceptable else "Proceed with rate",
                    f"Current margin: {margin_percentage:.1f}%",
                ],
            }

        except Exception as e:
            logger.error(f"Error evaluating margin: {str(e)}")
            raise

    async def finalize_rate(
        self,
        negotiation_id: int,
        agreed_rate: float,
        agreed_rate_type: str,
    ) -> RateNegotiation:
        """Finalize agreed rate.

        Args:
            negotiation_id: Negotiation ID
            agreed_rate: Agreed rate
            agreed_rate_type: Rate type

        Returns:
            Updated negotiation

        Raises:
            Exception: If database operation fails
        """
        try:
            negotiation = await self.get_negotiation(negotiation_id)
            if not negotiation:
                raise ValueError(f"Negotiation {negotiation_id} not found")

            negotiation.agreed_rate = agreed_rate
            negotiation.rate_type = agreed_rate_type
            negotiation.status = "agreed"
            negotiation.closed_at = datetime.utcnow()
            negotiation.closed_reason = "Rate agreed"

            await self.db.commit()
            await self.db.refresh(negotiation)

            logger.info(f"Finalized rate for negotiation {negotiation_id}: {agreed_rate} {agreed_rate_type}")
            return negotiation

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error finalizing rate: {str(e)}")
            raise

    async def get_negotiation_analytics(self) -> Dict[str, Any]:
        """Get negotiation analytics.

        Returns:
            Analytics data

        Raises:
            Exception: If database operation fails
        """
        try:
            # Get all negotiations
            result = await self.db.execute(select(RateNegotiation))
            negotiations = result.scalars().all()

            if not negotiations:
                return {
                    "total_negotiations": 0,
                    "average_rounds_to_close": 0,
                    "average_margin_achieved": 0,
                    "success_rate": 0,
                    "average_time_to_close_days": 0,
                    "status_distribution": {},
                }

            total = len(negotiations)
            agreed = [n for n in negotiations if n.status == "agreed"]
            failed = [n for n in negotiations if n.status == "failed"]

            # Calculate metrics
            avg_rounds = sum(n.total_rounds for n in negotiations) / total if total > 0 else 0
            avg_margin = sum(n.margin_percentage or 0 for n in agreed) / len(agreed) if agreed else 0
            success_rate = len(agreed) / total * 100 if total > 0 else 0

            # Calculate time to close
            times_to_close = []
            for n in agreed:
                if n.closed_at and n.started_at:
                    days = (n.closed_at - n.started_at).days
                    times_to_close.append(days)

            avg_time_to_close = sum(times_to_close) / len(times_to_close) if times_to_close else 0

            return {
                "total_negotiations": total,
                "agreed_count": len(agreed),
                "failed_count": len(failed),
                "average_rounds_to_close": round(avg_rounds, 2),
                "average_margin_achieved": round(avg_margin, 2),
                "success_rate": round(success_rate, 2),
                "average_time_to_close_days": round(avg_time_to_close, 2),
                "status_distribution": {
                    "initiated": len([n for n in negotiations if n.status == "initiated"]),
                    "in_progress": len([n for n in negotiations if n.status == "in_progress"]),
                    "agreed": len(agreed),
                    "failed": len(failed),
                    "cancelled": len([n for n in negotiations if n.status == "cancelled"]),
                },
            }

        except Exception as e:
            logger.error(f"Error getting negotiation analytics: {str(e)}")
            raise


class InterviewSchedulingService:
    """Service for interview scheduling."""

    def __init__(self, db: AsyncSession):
        """Initialize service.

        Args:
            db: Database session
        """
        self.db = db

    async def schedule_interview(
        self,
        schedule_data: InterviewScheduleCreate,
    ) -> InterviewSchedule:
        """Schedule interview.

        Args:
            schedule_data: Interview schedule data

        Returns:
            Created interview schedule

        Raises:
            Exception: If database operation fails
        """
        try:
            interview_schedule = InterviewSchedule(
                interview_id=schedule_data.interview_id,
                candidate_id=schedule_data.candidate_id,
                requirement_id=schedule_data.requirement_id,
                interview_type=schedule_data.interview_type,
                scheduled_date=schedule_data.scheduled_date,
                scheduled_time=schedule_data.scheduled_time,
                timezone=schedule_data.timezone,
                duration_minutes=schedule_data.duration_minutes,
                interviewer_name=schedule_data.interviewer_name,
                interviewer_email=schedule_data.interviewer_email,
                additional_participants=schedule_data.additional_participants,
                meeting_link=schedule_data.meeting_link,
                meeting_id=schedule_data.meeting_id,
                location=schedule_data.location,
                notes=schedule_data.notes,
                status="scheduled",
                confirmation_status={"candidate": "pending", "interviewer": "pending"},
            )

            self.db.add(interview_schedule)
            await self.db.commit()
            await self.db.refresh(interview_schedule)

            logger.info(f"Scheduled interview {interview_schedule.id} for candidate {schedule_data.candidate_id}")
            return interview_schedule

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error scheduling interview: {str(e)}")
            raise

    async def get_interview_schedule(self, schedule_id: int) -> Optional[InterviewSchedule]:
        """Get interview schedule by ID.

        Args:
            schedule_id: Schedule ID

        Returns:
            Interview schedule or None

        Raises:
            Exception: If database operation fails
        """
        try:
            result = await self.db.execute(
                select(InterviewSchedule).where(InterviewSchedule.id == schedule_id)
            )
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"Error getting interview schedule: {str(e)}")
            raise

    async def get_interview_schedules(
        self,
        skip: int = 0,
        limit: int = 20,
        candidate_id: Optional[int] = None,
        requirement_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> Tuple[List[InterviewSchedule], int]:
        """Get interview schedules with filtering and pagination.

        Args:
            skip: Skip count
            limit: Result limit
            candidate_id: Filter by candidate
            requirement_id: Filter by requirement
            status: Filter by status

        Returns:
            Tuple of schedules and total count

        Raises:
            Exception: If database operation fails
        """
        try:
            query = select(InterviewSchedule)
            count_query = select(func.count(InterviewSchedule.id))

            filters = []
            if candidate_id:
                filters.append(InterviewSchedule.candidate_id == candidate_id)
            if requirement_id:
                filters.append(InterviewSchedule.requirement_id == requirement_id)
            if status:
                filters.append(InterviewSchedule.status == status)

            if filters:
                query = query.where(and_(*filters))
                count_query = count_query.where(and_(*filters))

            count_result = await self.db.execute(count_query)
            total = count_result.scalar() or 0

            result = await self.db.execute(
                query.order_by(desc(InterviewSchedule.scheduled_date)).offset(skip).limit(limit)
            )
            schedules = result.scalars().all()

            return schedules, total

        except Exception as e:
            logger.error(f"Error getting interview schedules: {str(e)}")
            raise

    async def reschedule_interview(
        self,
        schedule_id: int,
        reschedule_data: InterviewRescheduleRequest,
        rescheduled_by: int,
    ) -> InterviewSchedule:
        """Reschedule interview.

        Args:
            schedule_id: Schedule ID
            reschedule_data: New schedule data
            rescheduled_by: User ID who rescheduled

        Returns:
            Updated interview schedule

        Raises:
            Exception: If database operation fails
        """
        try:
            schedule = await self.get_interview_schedule(schedule_id)
            if not schedule:
                raise ValueError(f"Interview schedule {schedule_id} not found")

            # Store old values in history
            old_entry = {
                "old_date": schedule.scheduled_date,
                "old_time": schedule.scheduled_time,
                "new_date": reschedule_data.scheduled_date,
                "new_time": reschedule_data.scheduled_time,
                "reason": reschedule_data.reason,
                "rescheduled_by": rescheduled_by,
                "rescheduled_at": datetime.utcnow().isoformat(),
            }

            # Update schedule
            schedule.scheduled_date = reschedule_data.scheduled_date
            schedule.scheduled_time = reschedule_data.scheduled_time
            schedule.status = "rescheduled"
            schedule.reschedule_count += 1

            # Add to history
            if not schedule.reschedule_history:
                schedule.reschedule_history = []
            schedule.reschedule_history.append(old_entry)

            await self.db.commit()
            await self.db.refresh(schedule)

            logger.info(f"Rescheduled interview {schedule_id}: {reschedule_data.reason}")
            return schedule

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error rescheduling interview: {str(e)}")
            raise

    async def cancel_interview(
        self,
        schedule_id: int,
        cancel_data: InterviewCancelRequest,
    ) -> InterviewSchedule:
        """Cancel interview.

        Args:
            schedule_id: Schedule ID
            cancel_data: Cancellation data

        Returns:
            Updated interview schedule

        Raises:
            Exception: If database operation fails
        """
        try:
            schedule = await self.get_interview_schedule(schedule_id)
            if not schedule:
                raise ValueError(f"Interview schedule {schedule_id} not found")

            schedule.status = "cancelled"
            schedule.cancellation_reason = cancel_data.reason

            await self.db.commit()
            await self.db.refresh(schedule)

            logger.info(f"Cancelled interview {schedule_id}: {cancel_data.reason}")
            return schedule

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error cancelling interview: {str(e)}")
            raise

    async def send_reminders(self, hours_before: int = 24) -> List[int]:
        """Send reminders for upcoming interviews.

        Args:
            hours_before: Hours before interview to send reminder

        Returns:
            List of schedule IDs reminded

        Raises:
            Exception: If database operation fails
        """
        try:
            # Calculate time window
            now = datetime.utcnow()
            reminder_start = now + timedelta(hours=hours_before - 1)
            reminder_end = now + timedelta(hours=hours_before + 1)

            # Find interviews without reminders in time window
            result = await self.db.execute(
                select(InterviewSchedule).where(
                    and_(
                        InterviewSchedule.reminder_sent == False,
                        InterviewSchedule.status != "cancelled",
                    )
                )
            )
            schedules = result.scalars().all()

            reminded_ids = []
            for schedule in schedules:
                # Check if in time window (simplified - would need proper datetime conversion)
                if schedule.scheduled_date:
                    schedule.reminder_sent = True
                    schedule.reminder_sent_at = now
                    reminded_ids.append(schedule.id)

            if reminded_ids:
                await self.db.commit()

            logger.info(f"Sent reminders for {len(reminded_ids)} interviews")
            return reminded_ids

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error sending reminders: {str(e)}")
            raise

    async def get_scheduling_analytics(self) -> Dict[str, Any]:
        """Get scheduling analytics.

        Returns:
            Analytics data

        Raises:
            Exception: If database operation fails
        """
        try:
            result = await self.db.execute(select(InterviewSchedule))
            schedules = result.scalars().all()

            if not schedules:
                return {
                    "total_interviews_scheduled": 0,
                    "rescheduled_count": 0,
                    "rescheduled_percentage": 0,
                    "no_show_count": 0,
                    "no_show_percentage": 0,
                    "average_days_to_schedule": 0,
                    "popular_time_slots": {},
                    "popular_interview_types": {},
                    "average_reschedules_per_interview": 0,
                    "cancellation_reasons": {},
                }

            total = len(schedules)
            rescheduled = [s for s in schedules if s.reschedule_count > 0]
            no_shows = [s for s in schedules if s.status == "no_show"]
            completed = [s for s in schedules if s.status == "completed"]

            # Count by interview type
            type_counts = {}
            for s in schedules:
                type_counts[s.interview_type] = type_counts.get(s.interview_type, 0) + 1

            # Count by time slot (hour)
            time_slot_counts = {}
            for s in schedules:
                if s.scheduled_time:
                    hour = s.scheduled_time.split(":")[0]
                    time_slot_counts[f"{hour}:00"] = time_slot_counts.get(f"{hour}:00", 0) + 1

            return {
                "total_interviews_scheduled": total,
                "completed_count": len(completed),
                "rescheduled_count": len(rescheduled),
                "rescheduled_percentage": round(len(rescheduled) / total * 100, 2) if total > 0 else 0,
                "no_show_count": len(no_shows),
                "no_show_percentage": round(len(no_shows) / total * 100, 2) if total > 0 else 0,
                "average_reschedules_per_interview": round(sum(s.reschedule_count for s in schedules) / total, 2) if total > 0 else 0,
                "popular_time_slots": dict(sorted(time_slot_counts.items(), key=lambda x: x[1], reverse=True)[:5]),
                "popular_interview_types": dict(sorted(type_counts.items(), key=lambda x: x[1], reverse=True)),
            }

        except Exception as e:
            logger.error(f"Error getting scheduling analytics: {str(e)}")
            raise
