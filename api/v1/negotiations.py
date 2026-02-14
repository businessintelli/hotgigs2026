"""Rate negotiation and interview scheduling API endpoints."""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db
from schemas.negotiation import (
    RateNegotiationCreate,
    RateNegotiationUpdate,
    RateNegotiationResponse,
    RateEvaluationResponse,
    AutoNegotiateResponse,
    NegotiationRoundCreate,
    NegotiationRoundUpdate,
    NegotiationRoundResponse,
    InterviewScheduleCreate,
    InterviewScheduleUpdate,
    InterviewScheduleResponse,
    InterviewRescheduleRequest,
    InterviewCancelRequest,
    AvailabilityCheckRequest,
    AvailabilityCheckResponse,
    SchedulingAnalyticsResponse,
)
from schemas.common import PaginatedResponse
from services.rate_negotiation_service import RateNegotiationService, InterviewSchedulingService
from agents.rate_negotiation_agent import RateNegotiationAgent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/negotiations", tags=["negotiations", "scheduling"])
negotiation_agent = RateNegotiationAgent()


# ===== RATE NEGOTIATION ENDPOINTS =====


@router.post("", response_model=RateNegotiationResponse, status_code=status.HTTP_201_CREATED)
async def create_negotiation(
    negotiation_data: RateNegotiationCreate,
    db: AsyncSession = Depends(get_db),
) -> RateNegotiationResponse:
    """Create new rate negotiation.

    Args:
        negotiation_data: Negotiation creation data
        db: Database session

    Returns:
        Created negotiation
    """
    try:
        negotiation = await negotiation_agent.initiate_negotiation(
            db,
            negotiation_data.submission_id,
            negotiation_data.initial_offer,
            negotiation_data.rate_type,
            negotiation_data.candidate_desired_rate,
            negotiation_data.customer_max_rate,
            negotiation_data.bill_rate,
            negotiation_data.pay_rate,
            negotiation_data.target_margin_percentage,
        )
        return RateNegotiationResponse.from_orm(negotiation)

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error creating negotiation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create negotiation",
        )


@router.get("/{negotiation_id}", response_model=RateNegotiationResponse)
async def get_negotiation(
    negotiation_id: int,
    db: AsyncSession = Depends(get_db),
) -> RateNegotiationResponse:
    """Get negotiation by ID.

    Args:
        negotiation_id: Negotiation ID
        db: Database session

    Returns:
        Negotiation data
    """
    try:
        service = RateNegotiationService(db)
        negotiation = await service.get_negotiation(negotiation_id)

        if not negotiation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Negotiation not found",
            )

        return RateNegotiationResponse.from_orm(negotiation)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting negotiation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get negotiation",
        )


@router.get("", response_model=PaginatedResponse)
async def get_negotiations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    submission_id: Optional[int] = None,
    status: Optional[str] = None,
    candidate_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse:
    """Get negotiations with filtering and pagination.

    Args:
        skip: Skip count
        limit: Result limit
        submission_id: Filter by submission
        status: Filter by status
        candidate_id: Filter by candidate
        db: Database session

    Returns:
        Paginated negotiations
    """
    try:
        service = RateNegotiationService(db)
        negotiations, total = await service.get_negotiations(
            skip=skip,
            limit=limit,
            submission_id=submission_id,
            status=status,
            candidate_id=candidate_id,
        )

        return PaginatedResponse(
            total=total,
            skip=skip,
            limit=limit,
            items=[RateNegotiationResponse.from_orm(n) for n in negotiations],
        )

    except Exception as e:
        logger.error(f"Error getting negotiations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get negotiations",
        )


@router.post("/{negotiation_id}/counter", response_model=NegotiationRoundResponse)
async def submit_counter_offer(
    negotiation_id: int,
    counter_data: NegotiationRoundUpdate,
    db: AsyncSession = Depends(get_db),
) -> NegotiationRoundResponse:
    """Submit counter offer.

    Args:
        negotiation_id: Negotiation ID
        counter_data: Counter offer data
        db: Database session

    Returns:
        Updated negotiation round
    """
    try:
        service = RateNegotiationService(db)
        round = await service.submit_counter_offer(negotiation_id, counter_data)
        return NegotiationRoundResponse.from_orm(round)

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error submitting counter offer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit counter offer",
        )


@router.post("/{negotiation_id}/suggest-rate", response_model=dict)
async def suggest_rate(
    negotiation_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get AI rate suggestion.

    Args:
        negotiation_id: Negotiation ID
        db: Database session

    Returns:
        Rate suggestion with reasoning
    """
    try:
        return await negotiation_agent.suggest_rate(db, negotiation_id)

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error suggesting rate: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to suggest rate",
        )


@router.post("/{negotiation_id}/evaluate-margin", response_model=RateEvaluationResponse)
async def evaluate_margin(
    negotiation_id: int,
    proposed_rate: float,
    db: AsyncSession = Depends(get_db),
) -> RateEvaluationResponse:
    """Evaluate margin at proposed rate.

    Args:
        negotiation_id: Negotiation ID
        proposed_rate: Rate to evaluate
        db: Database session

    Returns:
        Margin evaluation results
    """
    try:
        result = await negotiation_agent.evaluate_margin(db, negotiation_id, proposed_rate)
        return RateEvaluationResponse(**result)

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error evaluating margin: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to evaluate margin",
        )


@router.post("/{negotiation_id}/auto-negotiate", response_model=AutoNegotiateResponse)
async def auto_negotiate(
    negotiation_id: int,
    strategy: str = Query("balanced", pattern="^(aggressive|balanced|candidate_friendly)$"),
    db: AsyncSession = Depends(get_db),
) -> AutoNegotiateResponse:
    """AI auto-negotiation response.

    Args:
        negotiation_id: Negotiation ID
        strategy: Strategy (aggressive/balanced/candidate_friendly)
        db: Database session

    Returns:
        Auto-negotiation recommendation
    """
    try:
        result = await negotiation_agent.auto_negotiate(db, negotiation_id, strategy)
        return AutoNegotiateResponse(**result)

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error in auto-negotiation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to auto-negotiate",
        )


@router.post("/{negotiation_id}/finalize", response_model=RateNegotiationResponse)
async def finalize_rate(
    negotiation_id: int,
    agreed_rate: float,
    rate_type: str,
    db: AsyncSession = Depends(get_db),
) -> RateNegotiationResponse:
    """Finalize agreed rate.

    Args:
        negotiation_id: Negotiation ID
        agreed_rate: Final agreed rate
        rate_type: Rate type
        db: Database session

    Returns:
        Updated negotiation
    """
    try:
        negotiation = await negotiation_agent.finalize_rate(db, negotiation_id, agreed_rate, rate_type)
        return RateNegotiationResponse.from_orm(negotiation)

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error finalizing rate: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to finalize rate",
        )


@router.get("/analytics", response_model=dict)
async def get_negotiation_analytics(
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get negotiation analytics.

    Args:
        db: Database session

    Returns:
        Analytics data
    """
    try:
        return await negotiation_agent.get_negotiation_analytics(db)

    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get analytics",
        )


# ===== INTERVIEW SCHEDULING ENDPOINTS =====


@router.post("/interview-schedule", response_model=InterviewScheduleResponse, status_code=status.HTTP_201_CREATED)
async def schedule_interview(
    schedule_data: InterviewScheduleCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Query(...),
) -> InterviewScheduleResponse:
    """Schedule interview.

    Args:
        schedule_data: Interview schedule data
        db: Database session
        user_id: User scheduling the interview

    Returns:
        Created interview schedule
    """
    try:
        schedule = await negotiation_agent.schedule_interview(db, schedule_data, user_id)
        return InterviewScheduleResponse.from_orm(schedule)

    except Exception as e:
        logger.error(f"Error scheduling interview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to schedule interview",
        )


@router.get("/interview-schedule/{schedule_id}", response_model=InterviewScheduleResponse)
async def get_interview_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db),
) -> InterviewScheduleResponse:
    """Get interview schedule by ID.

    Args:
        schedule_id: Schedule ID
        db: Database session

    Returns:
        Interview schedule data
    """
    try:
        service = InterviewSchedulingService(db)
        schedule = await service.get_interview_schedule(schedule_id)

        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview schedule not found",
            )

        return InterviewScheduleResponse.from_orm(schedule)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting interview schedule: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get interview schedule",
        )


@router.get("/interview-schedule", response_model=PaginatedResponse)
async def get_interview_schedules(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    candidate_id: Optional[int] = None,
    requirement_id: Optional[int] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse:
    """Get interview schedules with filtering and pagination.

    Args:
        skip: Skip count
        limit: Result limit
        candidate_id: Filter by candidate
        requirement_id: Filter by requirement
        status: Filter by status
        db: Database session

    Returns:
        Paginated schedules
    """
    try:
        service = InterviewSchedulingService(db)
        schedules, total = await service.get_interview_schedules(
            skip=skip,
            limit=limit,
            candidate_id=candidate_id,
            requirement_id=requirement_id,
            status=status,
        )

        return PaginatedResponse(
            total=total,
            skip=skip,
            limit=limit,
            items=[InterviewScheduleResponse.from_orm(s) for s in schedules],
        )

    except Exception as e:
        logger.error(f"Error getting interview schedules: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get interview schedules",
        )


@router.put("/interview-schedule/{schedule_id}/reschedule", response_model=InterviewScheduleResponse)
async def reschedule_interview(
    schedule_id: int,
    reschedule_data: InterviewRescheduleRequest,
    db: AsyncSession = Depends(get_db),
    user_id: int = Query(...),
) -> InterviewScheduleResponse:
    """Reschedule interview.

    Args:
        schedule_id: Schedule ID
        reschedule_data: Reschedule request data
        db: Database session
        user_id: User rescheduling

    Returns:
        Updated interview schedule
    """
    try:
        schedule = await negotiation_agent.reschedule_interview(
            db,
            schedule_id,
            reschedule_data.scheduled_date,
            reschedule_data.scheduled_time,
            reschedule_data.reason,
            user_id,
        )
        return InterviewScheduleResponse.from_orm(schedule)

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error rescheduling interview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reschedule interview",
        )


@router.post("/interview-schedule/{schedule_id}/cancel", response_model=InterviewScheduleResponse)
async def cancel_interview(
    schedule_id: int,
    cancel_data: InterviewCancelRequest,
    db: AsyncSession = Depends(get_db),
) -> InterviewScheduleResponse:
    """Cancel interview.

    Args:
        schedule_id: Schedule ID
        cancel_data: Cancellation request data
        db: Database session

    Returns:
        Updated interview schedule
    """
    try:
        schedule = await negotiation_agent.cancel_interview(db, schedule_id, cancel_data.reason)
        return InterviewScheduleResponse.from_orm(schedule)

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error cancelling interview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel interview",
        )


@router.post("/interview-schedule/check-availability", response_model=AvailabilityCheckResponse)
async def check_availability(
    availability_data: AvailabilityCheckRequest,
    db: AsyncSession = Depends(get_db),
) -> AvailabilityCheckResponse:
    """Check availability of participants.

    Args:
        availability_data: Availability check request
        db: Database session

    Returns:
        Availability check results
    """
    try:
        # In production: Query calendar integrations
        return AvailabilityCheckResponse(
            participant_emails=availability_data.participant_emails,
            date_range_start=availability_data.date_range_start,
            date_range_end=availability_data.date_range_end,
            availability_status={email: True for email in availability_data.participant_emails},
            available_slots=[],
        )

    except Exception as e:
        logger.error(f"Error checking availability: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check availability",
        )


@router.post("/interview-schedule/send-reminders", response_model=dict)
async def send_reminders(
    hours_before: int = Query(24, ge=1),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Send reminders for upcoming interviews.

    Args:
        hours_before: Hours before interview
        db: Database session

    Returns:
        Reminder status
    """
    try:
        return await negotiation_agent.send_reminders(db, hours_before)

    except Exception as e:
        logger.error(f"Error sending reminders: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send reminders",
        )


@router.get("/interview-schedule/analytics", response_model=SchedulingAnalyticsResponse)
async def get_scheduling_analytics(
    db: AsyncSession = Depends(get_db),
) -> SchedulingAnalyticsResponse:
    """Get scheduling analytics.

    Args:
        db: Database session

    Returns:
        Analytics data
    """
    try:
        analytics = await negotiation_agent.get_scheduling_analytics(db)
        return SchedulingAnalyticsResponse(**analytics)

    except Exception as e:
        logger.error(f"Error getting scheduling analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get scheduling analytics",
        )
