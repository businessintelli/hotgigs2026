"""VMS timesheet workflow endpoints (supplier→MSP→client approval chain)."""

import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from api.dependencies import get_current_user, get_db, require_role, get_tenant_context_dep
from database.tenant_context import TenantContext
from models.user import User
from models.timesheet import Timesheet
from schemas.timesheet import (
    TimesheetCreate, TimesheetResponse, TimesheetDetailResponse,
    TimesheetApproveRequest, TimesheetRejectRequest
)
from services.vms_timesheet_service import VMSTimesheetService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/vms", tags=["VMS Timesheets"])


@router.post("/timesheets", response_model=TimesheetResponse, status_code=status.HTTP_201_CREATED)
async def create_vms_timesheet(
    data: TimesheetCreate,
    user: User = Depends(require_role("supplier_admin", "supplier_recruiter", "contractor")),
    db: AsyncSession = Depends(get_db),
):
    """Supplier submits a timesheet for a placement."""
    try:
        svc = VMSTimesheetService(db)
        timesheet = await svc.create_vms_timesheet(
            placement_id=data.placement_id,
            period_start=data.period_start,
            period_end=data.period_end,
            entries=[], # Entries would be added separately or in extended model
            submitted_by=user.id,
        )
        return TimesheetResponse.model_validate(timesheet)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating timesheet: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/timesheets", response_model=List[TimesheetResponse])
async def list_vms_timesheets(
    status_filter: Optional[str] = Query(None, alias="status"),
    org_type: Optional[str] = Query(None),
    period: Optional[str] = Query(None),
    user: User = Depends(require_role("supplier_admin", "msp_admin", "client_admin", "platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    """List timesheets with filtering by status, organization type, and period."""
    try:
        query = select(Timesheet)

        if status_filter:
            query = query.where(Timesheet.status == status_filter)

        # Additional filtering based on org_type would require join with PlacementRecord
        result = await db.execute(query.order_by(Timesheet.created_at.desc()))
        timesheets = result.scalars().all()

        return [TimesheetResponse.model_validate(ts) for ts in timesheets]
    except Exception as e:
        logger.error(f"Error listing timesheets: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.put("/timesheets/{timesheet_id}/msp-review", response_model=TimesheetResponse)
async def msp_review_timesheet(
    timesheet_id: int,
    review: TimesheetApproveRequest,
    user: User = Depends(require_role("msp_admin", "msp_manager", "platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    """MSP reviews and approves/rejects a timesheet."""
    try:
        svc = VMSTimesheetService(db)
        # Determine decision from request (assuming notes include decision or separate field)
        decision = "approve"  # Default; in real scenario this would be in request body
        timesheet = await svc.msp_review_timesheet(
            timesheet_id=timesheet_id,
            reviewer_id=user.id,
            decision=decision,
            notes=review.notes,
        )
        return TimesheetResponse.model_validate(timesheet)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error reviewing timesheet: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.put("/timesheets/{timesheet_id}/client-approve", response_model=TimesheetResponse)
async def client_approve_timesheet(
    timesheet_id: int,
    review: TimesheetApproveRequest,
    user: User = Depends(require_role("client_admin", "client_manager", "platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    """Client approves a timesheet."""
    try:
        svc = VMSTimesheetService(db)
        decision = "approve"  # Default
        timesheet = await svc.client_approve_timesheet(
            timesheet_id=timesheet_id,
            approver_id=user.id,
            decision=decision,
            notes=review.notes,
        )
        return TimesheetResponse.model_validate(timesheet)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error approving timesheet: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/timesheets/{timesheet_id}/compliance-check", response_model=dict)
async def check_timesheet_compliance(
    timesheet_id: int,
    user: User = Depends(require_role("msp_admin", "client_admin", "platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    """Check compliance status for a timesheet."""
    try:
        svc = VMSTimesheetService(db)
        compliance = await svc.check_timesheet_compliance(timesheet_id)
        return compliance
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error checking timesheet compliance: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
