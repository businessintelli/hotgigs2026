"""Timesheet service for tracking and management."""

import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func
from models.timesheet import Timesheet, TimesheetEntry
from models.offer import Offer
from models.candidate import Candidate
from models.customer import Customer
from schemas.timesheet import (
    TimesheetCreate,
    TimesheetUpdate,
    TimesheetEntryCreate,
    TimesheetEntryUpdate,
    TimesheetListFilter,
)

logger = logging.getLogger(__name__)


class TimesheetService:
    """Service for timesheet operations."""

    def __init__(self, db: AsyncSession):
        """Initialize timesheet service.

        Args:
            db: Database session
        """
        self.db = db

    async def create_timesheet(self, timesheet_data: TimesheetCreate) -> Timesheet:
        """Create a new timesheet.

        Args:
            timesheet_data: Timesheet creation data

        Returns:
            Created timesheet

        Raises:
            ValueError: If placement or period is invalid
            Exception: If database operation fails
        """
        try:
            # Verify placement exists and is active
            result = await self.db.execute(
                select(Offer).where(
                    and_(
                        Offer.id == timesheet_data.placement_id,
                        Offer.is_active.is_(True),
                    )
                )
            )
            placement = result.scalar_one_or_none()
            if not placement:
                raise ValueError(f"Active placement {timesheet_data.placement_id} not found")

            # Check for duplicate timesheet
            result = await self.db.execute(
                select(Timesheet).where(
                    and_(
                        Timesheet.contractor_id == timesheet_data.contractor_id,
                        Timesheet.period_start == timesheet_data.period_start,
                        Timesheet.period_end == timesheet_data.period_end,
                    )
                )
            )
            if result.scalar_one_or_none():
                raise ValueError("Timesheet for this period already exists")

            timesheet = Timesheet(**timesheet_data.model_dump())
            self.db.add(timesheet)
            await self.db.commit()
            await self.db.refresh(timesheet)

            logger.info(f"Created timesheet {timesheet.id} for contractor {timesheet_data.contractor_id}")
            return timesheet

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating timesheet: {str(e)}")
            raise

    async def get_timesheet(self, timesheet_id: int) -> Optional[Timesheet]:
        """Get timesheet by ID.

        Args:
            timesheet_id: Timesheet ID

        Returns:
            Timesheet or None
        """
        try:
            result = await self.db.execute(
                select(Timesheet).where(Timesheet.id == timesheet_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting timesheet: {str(e)}")
            raise

    async def get_timesheets(self, filters: TimesheetListFilter) -> Tuple[List[Timesheet], int]:
        """Get timesheets with filters.

        Args:
            filters: Filter criteria

        Returns:
            Tuple of (timesheets, total_count)
        """
        try:
            conditions = []

            if filters.contractor_id:
                conditions.append(Timesheet.contractor_id == filters.contractor_id)
            if filters.customer_id:
                conditions.append(Timesheet.customer_id == filters.customer_id)
            if filters.placement_id:
                conditions.append(Timesheet.placement_id == filters.placement_id)
            if filters.status:
                conditions.append(Timesheet.status == filters.status)
            if filters.period_start:
                conditions.append(Timesheet.period_start >= filters.period_start)
            if filters.period_end:
                conditions.append(Timesheet.period_end <= filters.period_end)

            query = select(Timesheet)
            if conditions:
                query = query.where(and_(*conditions))

            # Get total count
            count_result = await self.db.execute(select(func.count()).select_from(Timesheet).where(
                and_(*conditions) if conditions else True
            ))
            total = count_result.scalar()

            # Get paginated results
            query = query.order_by(desc(Timesheet.created_at))
            query = query.offset(filters.skip).limit(filters.limit)

            result = await self.db.execute(query)
            timesheets = result.scalars().all()

            logger.debug(f"Retrieved {len(timesheets)} timesheets")
            return timesheets, total

        except Exception as e:
            logger.error(f"Error getting timesheets: {str(e)}")
            raise

    async def update_timesheet(self, timesheet_id: int, update_data: TimesheetUpdate) -> Timesheet:
        """Update timesheet.

        Args:
            timesheet_id: Timesheet ID
            update_data: Update data

        Returns:
            Updated timesheet

        Raises:
            ValueError: If timesheet not found
        """
        try:
            timesheet = await self.get_timesheet(timesheet_id)
            if not timesheet:
                raise ValueError(f"Timesheet {timesheet_id} not found")

            update_dict = update_data.model_dump(exclude_unset=True)
            for key, value in update_dict.items():
                setattr(timesheet, key, value)

            await self.db.commit()
            await self.db.refresh(timesheet)

            logger.info(f"Updated timesheet {timesheet_id}")
            return timesheet

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating timesheet: {str(e)}")
            raise

    async def add_time_entry(
        self, timesheet_id: int, entry_data: TimesheetEntryCreate
    ) -> TimesheetEntry:
        """Add time entry to timesheet.

        Args:
            timesheet_id: Timesheet ID
            entry_data: Entry data

        Returns:
            Created entry

        Raises:
            ValueError: If validation fails
        """
        try:
            timesheet = await self.get_timesheet(timesheet_id)
            if not timesheet:
                raise ValueError(f"Timesheet {timesheet_id} not found")

            # Validate entry date is within timesheet period
            if not (timesheet.period_start <= entry_data.entry_date <= timesheet.period_end):
                raise ValueError("Entry date is outside timesheet period")

            # Check for duplicate entry
            result = await self.db.execute(
                select(TimesheetEntry).where(
                    and_(
                        TimesheetEntry.timesheet_id == timesheet_id,
                        TimesheetEntry.entry_date == entry_data.entry_date,
                    )
                )
            )
            if result.scalar_one_or_none():
                raise ValueError(f"Entry for {entry_data.entry_date} already exists")

            # Calculate total hours
            total_hours = entry_data.hours_regular + entry_data.hours_overtime

            # Get day of week
            day_of_week = entry_data.entry_date.strftime("%A")

            entry = TimesheetEntry(
                timesheet_id=timesheet_id,
                entry_date=entry_data.entry_date,
                day_of_week=day_of_week,
                hours_regular=entry_data.hours_regular,
                hours_overtime=entry_data.hours_overtime,
                total_hours=total_hours,
                is_billable=entry_data.is_billable,
                start_time=entry_data.start_time,
                end_time=entry_data.end_time,
                break_minutes=entry_data.break_minutes,
                project_code=entry_data.project_code,
                task_description=entry_data.task_description,
                is_holiday=entry_data.is_holiday,
                is_pto=entry_data.is_pto,
                is_sick_day=entry_data.is_sick_day,
                notes=entry_data.notes,
            )

            self.db.add(entry)
            await self.db.commit()
            await self.db.refresh(entry)

            # Recalculate timesheet totals
            await self._recalculate_timesheet_totals(timesheet_id)

            logger.info(f"Added time entry {entry.id} to timesheet {timesheet_id}")
            return entry

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error adding time entry: {str(e)}")
            raise

    async def update_time_entry(
        self, entry_id: int, update_data: TimesheetEntryUpdate
    ) -> TimesheetEntry:
        """Update time entry.

        Args:
            entry_id: Entry ID
            update_data: Update data

        Returns:
            Updated entry
        """
        try:
            result = await self.db.execute(
                select(TimesheetEntry).where(TimesheetEntry.id == entry_id)
            )
            entry = result.scalar_one_or_none()
            if not entry:
                raise ValueError(f"Entry {entry_id} not found")

            update_dict = update_data.model_dump(exclude_unset=True)

            # Recalculate total hours if hours changed
            if "hours_regular" in update_dict or "hours_overtime" in update_dict:
                regular = update_dict.get("hours_regular", entry.hours_regular)
                overtime = update_dict.get("hours_overtime", entry.hours_overtime)
                update_dict["total_hours"] = regular + overtime

            for key, value in update_dict.items():
                setattr(entry, key, value)

            await self.db.commit()
            await self.db.refresh(entry)

            # Recalculate timesheet totals
            await self._recalculate_timesheet_totals(entry.timesheet_id)

            logger.info(f"Updated time entry {entry_id}")
            return entry

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating time entry: {str(e)}")
            raise

    async def delete_time_entry(self, entry_id: int) -> None:
        """Delete time entry.

        Args:
            entry_id: Entry ID
        """
        try:
            result = await self.db.execute(
                select(TimesheetEntry).where(TimesheetEntry.id == entry_id)
            )
            entry = result.scalar_one_or_none()
            if not entry:
                raise ValueError(f"Entry {entry_id} not found")

            timesheet_id = entry.timesheet_id
            await self.db.delete(entry)
            await self.db.commit()

            # Recalculate timesheet totals
            await self._recalculate_timesheet_totals(timesheet_id)

            logger.info(f"Deleted time entry {entry_id}")

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting time entry: {str(e)}")
            raise

    async def submit_timesheet(self, timesheet_id: int) -> Timesheet:
        """Submit timesheet for approval.

        Args:
            timesheet_id: Timesheet ID

        Returns:
            Updated timesheet

        Raises:
            ValueError: If timesheet invalid or incomplete
        """
        try:
            timesheet = await self.get_timesheet(timesheet_id)
            if not timesheet:
                raise ValueError(f"Timesheet {timesheet_id} not found")

            if timesheet.status != "draft":
                raise ValueError(f"Cannot submit timesheet with status {timesheet.status}")

            # Validate all required days have entries
            result = await self.db.execute(
                select(func.count()).select_from(TimesheetEntry).where(
                    TimesheetEntry.timesheet_id == timesheet_id
                )
            )
            entry_count = result.scalar()

            if entry_count == 0:
                raise ValueError("Timesheet must have at least one entry")

            timesheet.status = "submitted"
            timesheet.submitted_at = datetime.utcnow()

            await self.db.commit()
            await self.db.refresh(timesheet)

            logger.info(f"Submitted timesheet {timesheet_id}")
            return timesheet

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error submitting timesheet: {str(e)}")
            raise

    async def approve_timesheet(
        self, timesheet_id: int, approver_id: int, notes: Optional[str] = None
    ) -> Timesheet:
        """Approve timesheet.

        Args:
            timesheet_id: Timesheet ID
            approver_id: Approver user ID
            notes: Optional approval notes

        Returns:
            Updated timesheet
        """
        try:
            timesheet = await self.get_timesheet(timesheet_id)
            if not timesheet:
                raise ValueError(f"Timesheet {timesheet_id} not found")

            if timesheet.status != "submitted":
                raise ValueError(f"Cannot approve timesheet with status {timesheet.status}")

            timesheet.status = "approved"
            timesheet.approved_by = approver_id
            timesheet.approved_at = datetime.utcnow()
            timesheet.approver_notes = notes

            await self.db.commit()
            await self.db.refresh(timesheet)

            logger.info(f"Approved timesheet {timesheet_id}")
            return timesheet

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error approving timesheet: {str(e)}")
            raise

    async def reject_timesheet(
        self, timesheet_id: int, approver_id: int, reason: str
    ) -> Timesheet:
        """Reject timesheet.

        Args:
            timesheet_id: Timesheet ID
            approver_id: Rejector user ID
            reason: Rejection reason

        Returns:
            Updated timesheet
        """
        try:
            timesheet = await self.get_timesheet(timesheet_id)
            if not timesheet:
                raise ValueError(f"Timesheet {timesheet_id} not found")

            if timesheet.status != "submitted":
                raise ValueError(f"Cannot reject timesheet with status {timesheet.status}")

            timesheet.status = "rejected"
            timesheet.rejected_by = approver_id
            timesheet.rejected_at = datetime.utcnow()
            timesheet.rejection_reason = reason

            await self.db.commit()
            await self.db.refresh(timesheet)

            logger.info(f"Rejected timesheet {timesheet_id}")
            return timesheet

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error rejecting timesheet: {str(e)}")
            raise

    async def recall_timesheet(self, timesheet_id: int) -> Timesheet:
        """Recall timesheet for editing.

        Args:
            timesheet_id: Timesheet ID

        Returns:
            Updated timesheet
        """
        try:
            timesheet = await self.get_timesheet(timesheet_id)
            if not timesheet:
                raise ValueError(f"Timesheet {timesheet_id} not found")

            if timesheet.status != "submitted":
                raise ValueError(f"Cannot recall timesheet with status {timesheet.status}")

            timesheet.status = "draft"
            timesheet.submitted_at = None

            await self.db.commit()
            await self.db.refresh(timesheet)

            logger.info(f"Recalled timesheet {timesheet_id}")
            return timesheet

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error recalling timesheet: {str(e)}")
            raise

    async def bulk_approve(self, timesheet_ids: List[int], approver_id: int) -> Dict[str, Any]:
        """Bulk approve timesheets.

        Args:
            timesheet_ids: List of timesheet IDs
            approver_id: Approver user ID

        Returns:
            Summary of approval results
        """
        approved_count = 0
        failed_ids = []

        try:
            for ts_id in timesheet_ids:
                try:
                    await self.approve_timesheet(ts_id, approver_id)
                    approved_count += 1
                except Exception as e:
                    logger.warning(f"Failed to approve timesheet {ts_id}: {str(e)}")
                    failed_ids.append(ts_id)

            return {
                "total_requested": len(timesheet_ids),
                "approved_count": approved_count,
                "failed_count": len(failed_ids),
                "failed_ids": failed_ids,
            }

        except Exception as e:
            logger.error(f"Error in bulk approve: {str(e)}")
            raise

    async def calculate_timesheet_totals(self, timesheet_id: int) -> Dict[str, float]:
        """Calculate timesheet totals.

        Args:
            timesheet_id: Timesheet ID

        Returns:
            Dictionary with calculated totals
        """
        try:
            timesheet = await self.get_timesheet(timesheet_id)
            if not timesheet:
                raise ValueError(f"Timesheet {timesheet_id} not found")

            # Get all entries
            result = await self.db.execute(
                select(TimesheetEntry).where(TimesheetEntry.timesheet_id == timesheet_id)
            )
            entries = result.scalars().all()

            # Calculate totals
            total_regular = sum(e.hours_regular for e in entries)
            total_overtime = sum(e.hours_overtime for e in entries)
            total_hours = sum(e.total_hours for e in entries)
            billable_hours = sum(e.total_hours for e in entries if e.is_billable)

            # Calculate amounts
            overtime_rate = timesheet.overtime_rate or (timesheet.regular_rate * 1.5)
            regular_amount = total_regular * timesheet.regular_rate
            overtime_amount = total_overtime * overtime_rate
            pay_amount = regular_amount + overtime_amount

            bill_rate = timesheet.bill_rate or timesheet.regular_rate
            bill_amount = billable_hours * bill_rate

            margin = bill_amount - pay_amount

            return {
                "total_regular_hours": total_regular,
                "total_overtime_hours": total_overtime,
                "total_hours": total_hours,
                "total_billable_hours": billable_hours,
                "regular_amount": regular_amount,
                "overtime_amount": overtime_amount,
                "total_pay_amount": pay_amount,
                "total_bill_amount": bill_amount,
                "margin_amount": margin,
            }

        except Exception as e:
            logger.error(f"Error calculating totals: {str(e)}")
            raise

    async def _recalculate_timesheet_totals(self, timesheet_id: int) -> None:
        """Recalculate and update timesheet totals.

        Args:
            timesheet_id: Timesheet ID
        """
        try:
            totals = await self.calculate_timesheet_totals(timesheet_id)
            timesheet = await self.get_timesheet(timesheet_id)

            for key, value in totals.items():
                setattr(timesheet, key, value)

            await self.db.commit()
            logger.debug(f"Recalculated totals for timesheet {timesheet_id}")

        except Exception as e:
            logger.error(f"Error recalculating totals: {str(e)}")
            await self.db.rollback()

    async def detect_anomalies(self, timesheet_id: int) -> List[Dict[str, Any]]:
        """Detect anomalies in timesheet.

        Args:
            timesheet_id: Timesheet ID

        Returns:
            List of detected anomalies
        """
        try:
            timesheet = await self.get_timesheet(timesheet_id)
            if not timesheet:
                raise ValueError(f"Timesheet {timesheet_id} not found")

            result = await self.db.execute(
                select(TimesheetEntry).where(TimesheetEntry.timesheet_id == timesheet_id)
                .order_by(TimesheetEntry.entry_date)
            )
            entries = result.scalars().all()

            anomalies = []

            for entry in entries:
                # Check for excessive hours
                if entry.total_hours > 16:
                    anomalies.append({
                        "type": "excessive_hours",
                        "severity": "high",
                        "entry_id": entry.id,
                        "description": f"Entry on {entry.entry_date} has {entry.total_hours} hours",
                    })

                # Check for weekend work without special flag
                if entry.entry_date.weekday() >= 5 and not entry.is_pto:
                    anomalies.append({
                        "type": "weekend_work",
                        "severity": "medium",
                        "entry_id": entry.id,
                        "description": f"Weekend work on {entry.entry_date}",
                    })

                # Check for missing hours after activity
                if entry.start_time and entry.end_time:
                    calculated_hours = (
                        (entry.end_time.hour - entry.start_time.hour)
                        - (entry.break_minutes / 60)
                    )
                    if abs(calculated_hours - entry.total_hours) > 0.5:
                        anomalies.append({
                            "type": "time_mismatch",
                            "severity": "medium",
                            "entry_id": entry.id,
                            "description": "Hours don't match start/end times",
                        })

            return anomalies

        except Exception as e:
            logger.error(f"Error detecting anomalies: {str(e)}")
            raise

    async def get_timesheet_analytics(
        self, start_date: date, end_date: date
    ) -> Dict[str, Any]:
        """Get timesheet analytics.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            Analytics data
        """
        try:
            # Get all timesheets in period
            result = await self.db.execute(
                select(Timesheet).where(
                    and_(
                        Timesheet.period_start >= start_date,
                        Timesheet.period_end <= end_date,
                    )
                )
            )
            timesheets = result.scalars().all()

            if not timesheets:
                return {
                    "total_hours_billed": 0,
                    "utilization_rate": 0,
                    "avg_hours_per_contractor": 0,
                    "overtime_percentage": 0,
                    "on_time_submission_rate": 0,
                    "avg_approval_turnaround_hours": 0,
                    "total_contractors": 0,
                    "submitted_timesheets": 0,
                    "approved_timesheets": 0,
                    "pending_timesheets": 0,
                    "total_payroll_amount": 0,
                    "total_bill_amount": 0,
                }

            total_hours = sum(t.total_hours for t in timesheets)
            total_billable = sum(t.total_billable_hours for t in timesheets)
            overtime_hours = sum(t.total_overtime_hours for t in timesheets)
            submitted = sum(1 for t in timesheets if t.status == "submitted")
            approved = sum(1 for t in timesheets if t.status == "approved")

            # Calculate turnaround times for approved
            turnaround_times = []
            for t in timesheets:
                if t.approved_at and t.submitted_at:
                    turnaround = (t.approved_at - t.submitted_at).total_seconds() / 3600
                    turnaround_times.append(turnaround)

            avg_turnaround = sum(turnaround_times) / len(turnaround_times) if turnaround_times else 0

            return {
                "total_hours_billed": total_billable,
                "utilization_rate": (total_billable / total_hours * 100) if total_hours > 0 else 0,
                "avg_hours_per_contractor": total_hours / len(set(t.contractor_id for t in timesheets)),
                "overtime_percentage": (overtime_hours / total_hours * 100) if total_hours > 0 else 0,
                "on_time_submission_rate": (submitted / len(timesheets) * 100) if timesheets else 0,
                "avg_approval_turnaround_hours": avg_turnaround,
                "total_contractors": len(set(t.contractor_id for t in timesheets)),
                "submitted_timesheets": submitted,
                "approved_timesheets": approved,
                "pending_timesheets": len(timesheets) - submitted - approved,
                "total_payroll_amount": sum(t.total_pay_amount for t in timesheets),
                "total_bill_amount": sum(t.total_bill_amount for t in timesheets),
            }

        except Exception as e:
            logger.error(f"Error getting analytics: {str(e)}")
            raise

    async def get_missing_timesheets(self) -> List[Dict[str, Any]]:
        """Get contractors missing timesheets for current period.

        Returns:
            List of missing timesheet info
        """
        try:
            # Get current period based on today
            today = date.today()
            period_start = today - timedelta(days=today.weekday())  # Start of week
            period_end = period_start + timedelta(days=6)  # End of week

            # Get active placements
            result = await self.db.execute(
                select(Offer).where(
                    and_(
                        Offer.is_active.is_(True),
                        Offer.start_date <= today,
                        or_(Offer.end_date.is_(None), Offer.end_date >= today),
                    )
                )
            )
            placements = result.scalars().all()

            missing = []

            for placement in placements:
                # Check if timesheet exists for this period
                result = await self.db.execute(
                    select(Timesheet).where(
                        and_(
                            Timesheet.placement_id == placement.id,
                            Timesheet.period_start == period_start,
                            Timesheet.period_end == period_end,
                        )
                    )
                )

                if not result.scalar_one_or_none():
                    missing.append({
                        "placement_id": placement.id,
                        "contractor_id": placement.candidate_id,
                        "customer_id": placement.customer_id,
                        "period_start": period_start,
                        "period_end": period_end,
                    })

            return missing

        except Exception as e:
            logger.error(f"Error getting missing timesheets: {str(e)}")
            raise
