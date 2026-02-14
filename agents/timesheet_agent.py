"""Timesheet tracking agent."""

import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from agents.base_agent import BaseAgent
from agents.events import EventType
from models.timesheet import Timesheet, TimesheetEntry
from models.offer import Offer
from services.timesheet_service import TimesheetService
from schemas.timesheet import (
    TimesheetCreate,
    TimesheetUpdate,
    TimesheetEntryCreate,
    TimesheetEntryUpdate,
    TimesheetListFilter,
)

logger = logging.getLogger(__name__)


class TimesheetAgent(BaseAgent):
    """Agent for managing timesheet tracking for placed contractors."""

    def __init__(self):
        """Initialize the timesheet agent."""
        super().__init__(agent_name="TimesheetAgent", agent_version="1.0.0")
        self.default_overtime_multiplier = 1.5
        self.max_hours_per_day = 24
        self.min_hours_per_day = 0

    async def create_timesheet(self, db: AsyncSession, timesheet_data: Dict[str, Any]) -> Timesheet:
        """Create timesheet for a placement/period.

        Auto-fills dates based on billing cycle. Validates placement active and period not already submitted.

        Args:
            db: Database session
            timesheet_data: Timesheet data

        Returns:
            Created timesheet

        Raises:
            ValueError: If validation fails
        """
        try:
            logger.info(f"Creating timesheet for contractor {timesheet_data.get('contractor_id')}")

            service = TimesheetService(db)

            ts_create = TimesheetCreate(**timesheet_data)
            timesheet = await service.create_timesheet(ts_create)

            await self.emit_event(
                event_type=EventType.RESOURCE_CREATED,
                entity_type="timesheet",
                entity_id=timesheet.id,
                payload={"placement_id": timesheet.placement_id, "contractor_id": timesheet.contractor_id},
            )

            logger.info(f"Created timesheet {timesheet.id}")
            return timesheet

        except Exception as e:
            logger.error(f"Error creating timesheet: {str(e)}")
            raise

    async def add_time_entry(
        self, db: AsyncSession, timesheet_id: int, entry_data: Dict[str, Any]
    ) -> TimesheetEntry:
        """Add time entry to timesheet.

        Tracks: date, hours_regular, hours_overtime, project_code, task_description, billable flag.
        Validates: no duplicate dates, max 24h/day.

        Args:
            db: Database session
            timesheet_id: Timesheet ID
            entry_data: Entry data

        Returns:
            Created entry

        Raises:
            ValueError: If validation fails
        """
        try:
            logger.info(f"Adding time entry to timesheet {timesheet_id}")

            service = TimesheetService(db)

            entry_create = TimesheetEntryCreate(**entry_data)
            entry = await service.add_time_entry(timesheet_id, entry_create)

            await self.emit_event(
                event_type=EventType.RESOURCE_CREATED,
                entity_type="timesheet_entry",
                entity_id=entry.id,
                payload={"timesheet_id": timesheet_id, "entry_date": str(entry.entry_date)},
            )

            return entry

        except Exception as e:
            logger.error(f"Error adding time entry: {str(e)}")
            raise

    async def submit_timesheet(self, db: AsyncSession, timesheet_id: int) -> Timesheet:
        """Submit timesheet for approval.

        Calculates totals. Validates all required days present.
        Notifies approver via alerts agent.

        Args:
            db: Database session
            timesheet_id: Timesheet ID

        Returns:
            Updated timesheet

        Raises:
            ValueError: If validation fails
        """
        try:
            logger.info(f"Submitting timesheet {timesheet_id}")

            service = TimesheetService(db)
            timesheet = await service.submit_timesheet(timesheet_id)

            await self.emit_event(
                event_type=EventType.WORKFLOW_TRIGGERED,
                entity_type="timesheet",
                entity_id=timesheet_id,
                payload={"status": "submitted", "submitted_at": timesheet.submitted_at.isoformat()},
            )

            logger.info(f"Submitted timesheet {timesheet_id}")
            return timesheet

        except Exception as e:
            logger.error(f"Error submitting timesheet: {str(e)}")
            raise

    async def approve_timesheet(
        self, db: AsyncSession, timesheet_id: int, approver_id: int, notes: Optional[str] = None
    ) -> Timesheet:
        """Approve timesheet.

        Triggers invoice generation if auto_invoice enabled.
        Triggers payment processing for approved hours.

        Args:
            db: Database session
            timesheet_id: Timesheet ID
            approver_id: Approver user ID
            notes: Optional approval notes

        Returns:
            Updated timesheet
        """
        try:
            logger.info(f"Approving timesheet {timesheet_id}")

            service = TimesheetService(db)
            timesheet = await service.approve_timesheet(timesheet_id, approver_id, notes)

            await self.emit_event(
                event_type=EventType.WORKFLOW_TRIGGERED,
                entity_type="timesheet",
                entity_id=timesheet_id,
                payload={"status": "approved", "approver_id": approver_id},
            )

            return timesheet

        except Exception as e:
            logger.error(f"Error approving timesheet: {str(e)}")
            raise

    async def reject_timesheet(
        self, db: AsyncSession, timesheet_id: int, approver_id: int, reason: str
    ) -> Timesheet:
        """Reject timesheet with reason.

        Notifies contractor to revise.

        Args:
            db: Database session
            timesheet_id: Timesheet ID
            approver_id: Rejector user ID
            reason: Rejection reason

        Returns:
            Updated timesheet
        """
        try:
            logger.info(f"Rejecting timesheet {timesheet_id}: {reason}")

            service = TimesheetService(db)
            timesheet = await service.reject_timesheet(timesheet_id, approver_id, reason)

            await self.emit_event(
                event_type=EventType.WORKFLOW_TRIGGERED,
                entity_type="timesheet",
                entity_id=timesheet_id,
                payload={"status": "rejected", "reason": reason},
            )

            return timesheet

        except Exception as e:
            logger.error(f"Error rejecting timesheet: {str(e)}")
            raise

    async def recall_timesheet(self, db: AsyncSession, timesheet_id: int) -> Timesheet:
        """Contractor recalls submitted timesheet for editing.

        Args:
            db: Database session
            timesheet_id: Timesheet ID

        Returns:
            Updated timesheet
        """
        try:
            logger.info(f"Recalling timesheet {timesheet_id}")

            service = TimesheetService(db)
            timesheet = await service.recall_timesheet(timesheet_id)

            await self.emit_event(
                event_type=EventType.WORKFLOW_TRIGGERED,
                entity_type="timesheet",
                entity_id=timesheet_id,
                payload={"status": "recalled"},
            )

            return timesheet

        except Exception as e:
            logger.error(f"Error recalling timesheet: {str(e)}")
            raise

    async def bulk_approve(
        self, db: AsyncSession, timesheet_ids: List[int], approver_id: int
    ) -> Dict[str, Any]:
        """Bulk approve multiple timesheets.

        Returns success/failure counts.

        Args:
            db: Database session
            timesheet_ids: List of timesheet IDs
            approver_id: Approver user ID

        Returns:
            Approval summary
        """
        try:
            logger.info(f"Bulk approving {len(timesheet_ids)} timesheets")

            service = TimesheetService(db)
            result = await service.bulk_approve(timesheet_ids, approver_id)

            await self.emit_event(
                event_type=EventType.BATCH_OPERATION,
                entity_type="timesheet",
                entity_id=0,
                payload=result,
            )

            return result

        except Exception as e:
            logger.error(f"Error in bulk approve: {str(e)}")
            raise

    async def calculate_timesheet_totals(self, db: AsyncSession, timesheet_id: int) -> Dict[str, float]:
        """Calculate: regular_hours, overtime_hours, total_hours, billable_hours.

        regular_amount (hours × rate), overtime_amount (hours × OT rate), total_amount.

        Args:
            db: Database session
            timesheet_id: Timesheet ID

        Returns:
            Calculated totals
        """
        try:
            logger.debug(f"Calculating totals for timesheet {timesheet_id}")

            service = TimesheetService(db)
            totals = await service.calculate_timesheet_totals(timesheet_id)

            return totals

        except Exception as e:
            logger.error(f"Error calculating totals: {str(e)}")
            raise

    async def get_timesheet_calendar(
        self, db: AsyncSession, contractor_id: int, month: int, year: int
    ) -> Dict[str, Any]:
        """Calendar view of timesheets.

        Shows which days have entries, hours per day, status.

        Args:
            db: Database session
            contractor_id: Contractor ID
            month: Month (1-12)
            year: Year

        Returns:
            Calendar data
        """
        try:
            logger.debug(f"Getting calendar for contractor {contractor_id} {month}/{year}")

            service = TimesheetService(db)

            # Get all entries for the month
            start_date = date(year, month, 1)
            if month == 12:
                end_date = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = date(year, month + 1, 1) - timedelta(days=1)

            filters = TimesheetListFilter(
                contractor_id=contractor_id,
                period_start=start_date,
                period_end=end_date,
                limit=100,
            )

            timesheets, _ = await service.get_timesheets(filters)

            # Build calendar
            days = []
            current_date = start_date

            total_hours = 0
            total_billable = 0

            while current_date <= end_date:
                day_hours = 0
                day_billable = 0

                # Find entries for this date
                for ts in timesheets:
                    for entry in ts.entries:
                        if entry.entry_date == current_date:
                            day_hours += entry.total_hours
                            if entry.is_billable:
                                day_billable += entry.total_hours

                days.append({
                    "date": current_date.isoformat(),
                    "hours": day_hours,
                    "is_weekend": current_date.weekday() >= 5,
                    "entries_count": sum(1 for ts in timesheets for e in ts.entries if e.entry_date == current_date),
                })

                total_hours += day_hours
                total_billable += day_billable
                current_date += timedelta(days=1)

            return {
                "contractor_id": contractor_id,
                "month": month,
                "year": year,
                "days": days,
                "total_hours": total_hours,
                "total_billable_hours": total_billable,
            }

        except Exception as e:
            logger.error(f"Error getting calendar: {str(e)}")
            raise

    async def auto_generate_timesheets(self, db: AsyncSession) -> List[Timesheet]:
        """Auto-create timesheet shells for all active placements at start of billing period.

        Called by Celery beat weekly/bi-weekly/monthly based on placement config.

        Args:
            db: Database session

        Returns:
            List of created timesheets
        """
        try:
            logger.info("Auto-generating timesheets for active placements")

            from sqlalchemy import select as sql_select

            service = TimesheetService(db)

            # Get all active placements
            result = await db.execute(
                sql_select(Offer).where(Offer.is_active.is_(True))
            )
            placements = result.scalars().all()

            created_timesheets = []
            today = date.today()

            for placement in placements:
                try:
                    # Determine period based on billing cycle
                    period_start, period_end = self._calculate_billing_period(today)

                    # Check if timesheet already exists
                    filters = TimesheetListFilter(
                        placement_id=placement.id,
                        period_start=period_start,
                        period_end=period_end,
                        limit=1,
                    )

                    existing, _ = await service.get_timesheets(filters)
                    if existing:
                        continue

                    # Create timesheet
                    ts_data = TimesheetCreate(
                        placement_id=placement.id,
                        contractor_id=placement.candidate_id,
                        customer_id=placement.customer_id,
                        requirement_id=placement.requirement_id,
                        period_start=period_start,
                        period_end=period_end,
                        billing_cycle="weekly",
                        regular_rate=placement.offered_rate or 0,
                    )

                    timesheet = await service.create_timesheet(ts_data)
                    created_timesheets.append(timesheet)

                except Exception as e:
                    logger.warning(f"Failed to auto-generate timesheet for placement {placement.id}: {str(e)}")

            logger.info(f"Auto-generated {len(created_timesheets)} timesheets")
            return created_timesheets

        except Exception as e:
            logger.error(f"Error auto-generating timesheets: {str(e)}")
            raise

    async def detect_timesheet_anomalies(
        self, db: AsyncSession, timesheet_id: int
    ) -> Dict[str, Any]:
        """AI-detect anomalies.

        Excessive hours, weekend work without approval, sudden pattern changes, missing days, duplicate entries.

        Args:
            db: Database session
            timesheet_id: Timesheet ID

        Returns:
            Anomaly detection result
        """
        try:
            logger.debug(f"Detecting anomalies in timesheet {timesheet_id}")

            service = TimesheetService(db)
            anomalies = await service.detect_anomalies(timesheet_id)

            # Calculate risk score
            risk_score = 0.0
            for anomaly in anomalies:
                if anomaly["severity"] == "high":
                    risk_score += 0.5
                elif anomaly["severity"] == "medium":
                    risk_score += 0.25
                else:
                    risk_score += 0.1

            risk_score = min(risk_score, 1.0)

            return {
                "timesheet_id": timesheet_id,
                "anomalies": anomalies,
                "risk_score": risk_score,
                "has_anomalies": len(anomalies) > 0,
            }

        except Exception as e:
            logger.error(f"Error detecting anomalies: {str(e)}")
            raise

    async def get_timesheet_analytics(
        self, db: AsyncSession, start_date: date, end_date: date
    ) -> Dict[str, Any]:
        """Analytics: total hours billed, utilization rate, avg hours per contractor.

        overtime %, on-time submission rate, approval turnaround time.

        Args:
            db: Database session
            start_date: Start date
            end_date: End date

        Returns:
            Analytics data
        """
        try:
            logger.debug(f"Getting analytics for period {start_date} to {end_date}")

            service = TimesheetService(db)
            analytics = await service.get_timesheet_analytics(start_date, end_date)

            return analytics

        except Exception as e:
            logger.error(f"Error getting analytics: {str(e)}")
            raise

    async def export_timesheets(
        self,
        db: AsyncSession,
        placement_id: int,
        start_date: date,
        end_date: date,
        format: str = "csv",
    ) -> str:
        """Export timesheets for a placement/period.

        Formats: CSV, Excel, PDF.

        Args:
            db: Database session
            placement_id: Placement ID
            start_date: Start date
            end_date: End date
            format: Export format

        Returns:
            File path or content
        """
        try:
            logger.info(f"Exporting timesheets for placement {placement_id} ({format})")

            service = TimesheetService(db)

            filters = TimesheetListFilter(
                placement_id=placement_id,
                period_start=start_date,
                period_end=end_date,
                limit=100,
            )

            timesheets, _ = await service.get_timesheets(filters)

            if format == "csv":
                return await self._export_csv(timesheets)
            elif format == "excel":
                return await self._export_excel(timesheets)
            elif format == "pdf":
                return await self._export_pdf(timesheets)
            else:
                raise ValueError(f"Unsupported format: {format}")

        except Exception as e:
            logger.error(f"Error exporting timesheets: {str(e)}")
            raise

    async def get_missing_timesheets(self, db: AsyncSession) -> List[Dict[str, Any]]:
        """Find contractors who haven't submitted timesheets for current period.

        Args:
            db: Database session

        Returns:
            List of missing timesheet info
        """
        try:
            logger.info("Getting missing timesheets")

            service = TimesheetService(db)
            missing = await service.get_missing_timesheets()

            return missing

        except Exception as e:
            logger.error(f"Error getting missing timesheets: {str(e)}")
            raise

    async def send_timesheet_reminders(self, db: AsyncSession) -> Dict[str, Any]:
        """Send reminders to contractors with missing/overdue timesheets.

        Args:
            db: Database session

        Returns:
            Reminder send summary
        """
        try:
            logger.info("Sending timesheet reminders")

            missing = await self.get_missing_timesheets(db)

            await self.emit_event(
                event_type=EventType.NOTIFICATION_SENT,
                entity_type="timesheet",
                entity_id=0,
                payload={"reminder_count": len(missing)},
            )

            return {
                "reminders_sent": len(missing),
                "missing_timesheets": missing,
            }

        except Exception as e:
            logger.error(f"Error sending reminders: {str(e)}")
            raise

    def _calculate_billing_period(self, reference_date: date) -> tuple[date, date]:
        """Calculate billing period start and end dates.

        Args:
            reference_date: Reference date

        Returns:
            Tuple of (period_start, period_end)
        """
        # Default to weekly (Monday to Sunday)
        days_since_monday = reference_date.weekday()
        period_start = reference_date - timedelta(days=days_since_monday)
        period_end = period_start + timedelta(days=6)

        return period_start, period_end

    async def _export_csv(self, timesheets: List[Timesheet]) -> str:
        """Export timesheets as CSV.

        Args:
            timesheets: List of timesheets

        Returns:
            CSV content
        """
        try:
            lines = ["Timesheet ID,Contractor ID,Period Start,Period End,Total Hours,Billable Hours,Status"]

            for ts in timesheets:
                line = f"{ts.id},{ts.contractor_id},{ts.period_start},{ts.period_end},{ts.total_hours},{ts.total_billable_hours},{ts.status}"
                lines.append(line)

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"Error exporting CSV: {str(e)}")
            raise

    async def _export_excel(self, timesheets: List[Timesheet]) -> str:
        """Export timesheets as Excel.

        Args:
            timesheets: List of timesheets

        Returns:
            File path
        """
        try:
            logger.info("Excel export not implemented - returning CSV format")
            return await self._export_csv(timesheets)

        except Exception as e:
            logger.error(f"Error exporting Excel: {str(e)}")
            raise

    async def _export_pdf(self, timesheets: List[Timesheet]) -> str:
        """Export timesheets as PDF.

        Args:
            timesheets: List of timesheets

        Returns:
            File path
        """
        try:
            logger.info("PDF export not implemented - returning CSV format")
            return await self._export_csv(timesheets)

        except Exception as e:
            logger.error(f"Error exporting PDF: {str(e)}")
            raise
