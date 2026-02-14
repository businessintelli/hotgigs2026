"""Timesheet API endpoints."""

import logging
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db
from schemas.timesheet import (
    TimesheetCreate,
    TimesheetUpdate,
    TimesheetResponse,
    TimesheetDetailResponse,
    TimesheetEntryCreate,
    TimesheetEntryUpdate,
    TimesheetEntryResponse,
    TimesheetApproveRequest,
    TimesheetRejectRequest,
    TimesheetCalendarResponse,
    TimesheetAnalyticsResponse,
    TimesheetBulkApproveRequest,
    TimesheetBulkApproveResponse,
    TimesheetAnomalyResponse,
    TimesheetListFilter,
)
from schemas.common import PaginatedResponse
from services.timesheet_service import TimesheetService
from agents.timesheet_agent import TimesheetAgent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/timesheets", tags=["timesheets"])
timesheet_agent = TimesheetAgent()


# ===== TIMESHEET ENDPOINTS =====


@router.post("", response_model=TimesheetResponse, status_code=status.HTTP_201_CREATED)
async def create_timesheet(
    timesheet_data: TimesheetCreate,
    db: AsyncSession = Depends(get_db),
) -> TimesheetResponse:
    """Create a new timesheet.

    Args:
        timesheet_data: Timesheet creation data
        db: Database session

    Returns:
        Created timesheet
    """
    try:
        timesheet = await timesheet_agent.create_timesheet(db, timesheet_data.model_dump())
        return TimesheetResponse.from_orm(timesheet)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating timesheet: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create timesheet",
        )


@router.get("", response_model=PaginatedResponse[TimesheetResponse])
async def list_timesheets(
    contractor_id: Optional[int] = Query(None),
    customer_id: Optional[int] = Query(None),
    placement_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    period_start: Optional[date] = Query(None),
    period_end: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[TimesheetResponse]:
    """Get timesheets with filters.

    Args:
        contractor_id: Filter by contractor
        customer_id: Filter by customer
        placement_id: Filter by placement
        status: Filter by status
        period_start: Filter by period start
        period_end: Filter by period end
        skip: Skip records
        limit: Limit records
        db: Database session

    Returns:
        Paginated timesheets
    """
    try:
        filters = TimesheetListFilter(
            contractor_id=contractor_id,
            customer_id=customer_id,
            placement_id=placement_id,
            status=status,
            period_start=period_start,
            period_end=period_end,
            skip=skip,
            limit=limit,
        )

        service = TimesheetService(db)
        timesheets, total = await service.get_timesheets(filters)

        items = [TimesheetResponse.from_orm(ts) for ts in timesheets]

        return PaginatedResponse(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
        )

    except Exception as e:
        logger.error(f"Error listing timesheets: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list timesheets",
        )


@router.get("/{timesheet_id}", response_model=TimesheetDetailResponse)
async def get_timesheet(
    timesheet_id: int,
    db: AsyncSession = Depends(get_db),
) -> TimesheetDetailResponse:
    """Get timesheet details.

    Args:
        timesheet_id: Timesheet ID
        db: Database session

    Returns:
        Timesheet with entries
    """
    try:
        service = TimesheetService(db)
        timesheet = await service.get_timesheet(timesheet_id)

        if not timesheet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Timesheet not found",
            )

        return TimesheetDetailResponse.from_orm(timesheet)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting timesheet: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get timesheet",
        )


@router.put("/{timesheet_id}", response_model=TimesheetResponse)
async def update_timesheet(
    timesheet_id: int,
    update_data: TimesheetUpdate,
    db: AsyncSession = Depends(get_db),
) -> TimesheetResponse:
    """Update timesheet.

    Args:
        timesheet_id: Timesheet ID
        update_data: Update data
        db: Database session

    Returns:
        Updated timesheet
    """
    try:
        service = TimesheetService(db)
        timesheet = await service.update_timesheet(timesheet_id, update_data)
        return TimesheetResponse.from_orm(timesheet)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating timesheet: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update timesheet",
        )


# ===== TIME ENTRY ENDPOINTS =====


@router.post("/{timesheet_id}/entries", response_model=TimesheetEntryResponse, status_code=status.HTTP_201_CREATED)
async def add_time_entry(
    timesheet_id: int,
    entry_data: TimesheetEntryCreate,
    db: AsyncSession = Depends(get_db),
) -> TimesheetEntryResponse:
    """Add time entry to timesheet.

    Args:
        timesheet_id: Timesheet ID
        entry_data: Entry data
        db: Database session

    Returns:
        Created entry
    """
    try:
        entry = await timesheet_agent.add_time_entry(db, timesheet_id, entry_data.model_dump())
        return TimesheetEntryResponse.from_orm(entry)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding time entry: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add time entry",
        )


@router.put("/{timesheet_id}/entries/{entry_id}", response_model=TimesheetEntryResponse)
async def update_time_entry(
    timesheet_id: int,
    entry_id: int,
    update_data: TimesheetEntryUpdate,
    db: AsyncSession = Depends(get_db),
) -> TimesheetEntryResponse:
    """Update time entry.

    Args:
        timesheet_id: Timesheet ID
        entry_id: Entry ID
        update_data: Update data
        db: Database session

    Returns:
        Updated entry
    """
    try:
        service = TimesheetService(db)
        entry = await service.update_time_entry(entry_id, update_data)
        return TimesheetEntryResponse.from_orm(entry)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating time entry: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update time entry",
        )


@router.delete("/{timesheet_id}/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_time_entry(
    timesheet_id: int,
    entry_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete time entry.

    Args:
        timesheet_id: Timesheet ID
        entry_id: Entry ID
        db: Database session
    """
    try:
        service = TimesheetService(db)
        await service.delete_time_entry(entry_id)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting time entry: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete time entry",
        )


# ===== TIMESHEET WORKFLOW ENDPOINTS =====


@router.post("/{timesheet_id}/submit", response_model=TimesheetResponse)
async def submit_timesheet(
    timesheet_id: int,
    db: AsyncSession = Depends(get_db),
) -> TimesheetResponse:
    """Submit timesheet for approval.

    Args:
        timesheet_id: Timesheet ID
        db: Database session

    Returns:
        Updated timesheet
    """
    try:
        timesheet = await timesheet_agent.submit_timesheet(db, timesheet_id)
        return TimesheetResponse.from_orm(timesheet)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error submitting timesheet: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit timesheet",
        )


@router.post("/{timesheet_id}/approve", response_model=TimesheetResponse)
async def approve_timesheet(
    timesheet_id: int,
    request: TimesheetApproveRequest,
    db: AsyncSession = Depends(get_db),
) -> TimesheetResponse:
    """Approve timesheet.

    Args:
        timesheet_id: Timesheet ID
        request: Approval request
        db: Database session

    Returns:
        Updated timesheet
    """
    try:
        timesheet = await timesheet_agent.approve_timesheet(
            db, timesheet_id, request.approver_id, request.notes
        )
        return TimesheetResponse.from_orm(timesheet)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error approving timesheet: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to approve timesheet",
        )


@router.post("/{timesheet_id}/reject", response_model=TimesheetResponse)
async def reject_timesheet(
    timesheet_id: int,
    request: TimesheetRejectRequest,
    db: AsyncSession = Depends(get_db),
) -> TimesheetResponse:
    """Reject timesheet.

    Args:
        timesheet_id: Timesheet ID
        request: Rejection request
        db: Database session

    Returns:
        Updated timesheet
    """
    try:
        timesheet = await timesheet_agent.reject_timesheet(
            db, timesheet_id, request.approver_id, request.reason
        )
        return TimesheetResponse.from_orm(timesheet)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error rejecting timesheet: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reject timesheet",
        )


@router.post("/{timesheet_id}/recall", response_model=TimesheetResponse)
async def recall_timesheet(
    timesheet_id: int,
    db: AsyncSession = Depends(get_db),
) -> TimesheetResponse:
    """Recall timesheet for editing.

    Args:
        timesheet_id: Timesheet ID
        db: Database session

    Returns:
        Updated timesheet
    """
    try:
        timesheet = await timesheet_agent.recall_timesheet(db, timesheet_id)
        return TimesheetResponse.from_orm(timesheet)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error recalling timesheet: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to recall timesheet",
        )


@router.post("/bulk-approve", response_model=TimesheetBulkApproveResponse)
async def bulk_approve_timesheets(
    request: TimesheetBulkApproveRequest,
    db: AsyncSession = Depends(get_db),
) -> TimesheetBulkApproveResponse:
    """Bulk approve timesheets.

    Args:
        request: Bulk approve request
        db: Database session

    Returns:
        Approval summary
    """
    try:
        result = await timesheet_agent.bulk_approve(db, request.timesheet_ids, request.approver_id)
        return TimesheetBulkApproveResponse(**result)

    except Exception as e:
        logger.error(f"Error in bulk approve: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to bulk approve timesheets",
        )


# ===== ANALYTICS ENDPOINTS =====


@router.get("/calendar/{contractor_id}", response_model=TimesheetCalendarResponse)
async def get_timesheet_calendar(
    contractor_id: int,
    month: int = Query(1, ge=1, le=12),
    year: int = Query(2024, ge=2020),
    db: AsyncSession = Depends(get_db),
) -> TimesheetCalendarResponse:
    """Get timesheet calendar view.

    Args:
        contractor_id: Contractor ID
        month: Month (1-12)
        year: Year
        db: Database session

    Returns:
        Calendar data
    """
    try:
        calendar = await timesheet_agent.get_timesheet_calendar(db, contractor_id, month, year)
        return TimesheetCalendarResponse(**calendar)

    except Exception as e:
        logger.error(f"Error getting calendar: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get calendar",
        )


@router.get("/missing", response_model=list)
async def get_missing_timesheets(
    db: AsyncSession = Depends(get_db),
) -> list:
    """Get missing timesheets.

    Args:
        db: Database session

    Returns:
        List of missing timesheet info
    """
    try:
        missing = await timesheet_agent.get_missing_timesheets(db)
        return missing

    except Exception as e:
        logger.error(f"Error getting missing timesheets: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get missing timesheets",
        )


@router.post("/send-reminders", response_model=dict)
async def send_timesheet_reminders(
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Send reminder notifications.

    Args:
        db: Database session

    Returns:
        Reminder summary
    """
    try:
        result = await timesheet_agent.send_timesheet_reminders(db)
        return result

    except Exception as e:
        logger.error(f"Error sending reminders: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send reminders",
        )


@router.post("/auto-generate", response_model=list)
async def auto_generate_timesheets(
    db: AsyncSession = Depends(get_db),
) -> list:
    """Auto-generate timesheets for active placements.

    Args:
        db: Database session

    Returns:
        List of created timesheets
    """
    try:
        timesheets = await timesheet_agent.auto_generate_timesheets(db)
        return [TimesheetResponse.from_orm(ts).model_dump() for ts in timesheets]

    except Exception as e:
        logger.error(f"Error auto-generating timesheets: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to auto-generate timesheets",
        )


@router.get("/{timesheet_id}/anomalies", response_model=TimesheetAnomalyResponse)
async def detect_anomalies(
    timesheet_id: int,
    db: AsyncSession = Depends(get_db),
) -> TimesheetAnomalyResponse:
    """Detect anomalies in timesheet.

    Args:
        timesheet_id: Timesheet ID
        db: Database session

    Returns:
        Anomaly detection result
    """
    try:
        result = await timesheet_agent.detect_timesheet_anomalies(db, timesheet_id)
        return TimesheetAnomalyResponse(**result)

    except Exception as e:
        logger.error(f"Error detecting anomalies: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to detect anomalies",
        )


@router.get("/analytics", response_model=TimesheetAnalyticsResponse)
async def get_analytics(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: AsyncSession = Depends(get_db),
) -> TimesheetAnalyticsResponse:
    """Get timesheet analytics.

    Args:
        start_date: Start date
        end_date: End date
        db: Database session

    Returns:
        Analytics data
    """
    try:
        analytics = await timesheet_agent.get_timesheet_analytics(db, start_date, end_date)
        return TimesheetAnalyticsResponse(**analytics)

    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get analytics",
        )


@router.get("/export/{placement_id}")
async def export_timesheets(
    placement_id: int,
    start_date: date = Query(...),
    end_date: date = Query(...),
    format: str = Query("csv", pattern="^(csv|excel|pdf)$"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Export timesheets.

    Args:
        placement_id: Placement ID
        start_date: Start date
        end_date: End date
        format: Export format
        db: Database session

    Returns:
        Export file info
    """
    try:
        file_path = await timesheet_agent.export_timesheets(
            db, placement_id, start_date, end_date, format
        )
        return {"file_path": file_path, "format": format}

    except Exception as e:
        logger.error(f"Error exporting timesheets: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export timesheets",
        )
