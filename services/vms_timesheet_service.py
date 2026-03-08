"""VMS timesheet workflow service (supplier→MSP→client approval chain)."""
import logging
from datetime import date, datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from models.timesheet import Timesheet, TimesheetEntry
from models.msp_workflow import PlacementRecord

logger = logging.getLogger(__name__)


class VMSTimesheetService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_vms_timesheet(
        self, placement_id: int, period_start: date, period_end: date,
        entries: List[dict], submitted_by: int,
    ) -> Timesheet:
        # Verify placement
        result = await self.db.execute(
            select(PlacementRecord).where(PlacementRecord.id == placement_id, PlacementRecord.is_active == True)
        )
        placement = result.scalar_one_or_none()
        if not placement:
            raise ValueError(f"Placement {placement_id} not found")

        # Check duplicate
        dup = await self.db.execute(
            select(Timesheet).where(and_(
                Timesheet.placement_id == placement_id,
                Timesheet.period_start == period_start,
                Timesheet.period_end == period_end,
            ))
        )
        if dup.scalar_one_or_none():
            raise ValueError("Timesheet already exists for this period")

        total_regular = sum(e.get("hours_regular", 0) for e in entries)
        total_overtime = sum(e.get("hours_overtime", 0) for e in entries)
        total_hours = total_regular + total_overtime

        timesheet = Timesheet(
            placement_id=placement_id,
            contractor_id=placement.candidate_id,
            period_start=period_start,
            period_end=period_end,
            total_regular_hours=total_regular,
            total_overtime_hours=total_overtime,
            total_hours=total_hours,
            total_billable_hours=total_hours,
            bill_rate=placement.bill_rate,
            regular_rate=placement.pay_rate,
            overtime_rate=placement.pay_rate * 1.5 if placement.pay_rate else 0,
            regular_amount=total_regular * (placement.pay_rate or 0),
            overtime_amount=total_overtime * (placement.pay_rate or 0) * 1.5,
            total_pay_amount=total_regular * (placement.pay_rate or 0) + total_overtime * (placement.pay_rate or 0) * 1.5,
            total_bill_amount=total_hours * (placement.bill_rate or 0),
            margin_amount=(total_hours * (placement.bill_rate or 0)) - (total_regular * (placement.pay_rate or 0) + total_overtime * (placement.pay_rate or 0) * 1.5),
            status="SUBMITTED",
        )
        self.db.add(timesheet)
        await self.db.flush()

        for entry_data in entries:
            entry = TimesheetEntry(timesheet_id=timesheet.id, **entry_data)
            self.db.add(entry)

        await self.db.commit()
        await self.db.refresh(timesheet)
        return timesheet

    async def msp_review_timesheet(
        self, timesheet_id: int, reviewer_id: int, decision: str, notes: Optional[str] = None,
    ) -> Timesheet:
        result = await self.db.execute(select(Timesheet).where(Timesheet.id == timesheet_id))
        ts = result.scalar_one_or_none()
        if not ts:
            raise ValueError(f"Timesheet {timesheet_id} not found")

        if decision == "approve":
            ts.status = "APPROVED"
            ts.approved_by = reviewer_id
            ts.approved_at = datetime.utcnow()
        elif decision == "reject":
            ts.status = "REJECTED"
            ts.rejected_by = reviewer_id
            ts.rejection_reason = notes

        await self.db.commit()
        await self.db.refresh(ts)
        return ts

    async def client_approve_timesheet(
        self, timesheet_id: int, approver_id: int, decision: str, notes: Optional[str] = None,
    ) -> Timesheet:
        return await self.msp_review_timesheet(timesheet_id, approver_id, decision, notes)

    async def check_timesheet_compliance(self, timesheet_id: int) -> Dict[str, Any]:
        result = await self.db.execute(select(Timesheet).where(Timesheet.id == timesheet_id))
        ts = result.scalar_one_or_none()
        if not ts:
            raise ValueError(f"Timesheet {timesheet_id} not found")

        issues = []
        if ts.total_overtime_hours and ts.total_overtime_hours > 20:
            issues.append({"type": "overtime_limit", "message": f"Overtime {ts.total_overtime_hours}h exceeds 20h weekly limit"})
        if ts.total_hours and ts.total_hours > 60:
            issues.append({"type": "max_hours", "message": f"Total {ts.total_hours}h exceeds 60h weekly limit"})

        return {"timesheet_id": timesheet_id, "is_compliant": len(issues) == 0, "issues": issues}

    async def get_pending_timesheets(self, status: str = "SUBMITTED") -> List[Timesheet]:
        result = await self.db.execute(
            select(Timesheet).where(Timesheet.status == status).order_by(Timesheet.created_at.desc())
        )
        return list(result.scalars().all())
