"""Enhanced ATS API endpoints."""

import logging
from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db
from schemas.ats import (
    JobOrderCreate,
    JobOrderUpdate,
    JobOrderResponse,
    OfferWorkflowCreate,
    OfferWorkflowUpdate,
    OfferWorkflowResponse,
    OnboardingTaskCreate,
    OnboardingTaskUpdate,
    OnboardingTaskResponse,
    InterviewFeedbackCreate,
    InterviewFeedbackUpdate,
    InterviewFeedbackResponse,
    FeedbackSummaryResponse,
    OnboardingDashboardResponse,
)
from schemas.common import PaginatedResponse
from models.ats import (
    JobOrder,
    OfferWorkflow,
    OnboardingTask,
    InterviewFeedback,
)
from models.enums import JobOrderStatus, OfferStatus, OnboardingTaskStatus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ats", tags=["ATS Enhancement"])


# ── Job Order Management ──

@router.post("/job-orders", response_model=JobOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_job_order(
    order_data: JobOrderCreate,
    db: AsyncSession = Depends(get_db),
) -> JobOrderResponse:
    """Create a job order from requirement.

    Args:
        order_data: Job order data
        db: Database session

    Returns:
        Created job order
    """
    try:
        order = JobOrder(
            requirement_id=order_data.requirement_id,
            client_org_id=order_data.client_org_id,
            priority=order_data.priority,
            target_fill_date=order_data.target_fill_date,
            max_submissions=order_data.max_submissions,
            distribution_type=order_data.distribution_type,
            distributed_to=order_data.distributed_to or [],
            status=JobOrderStatus.DRAFT,
        )
        db.add(order)
        await db.commit()
        await db.refresh(order)
        return JobOrderResponse.from_orm(order)
    except Exception as e:
        logger.error(f"Error creating job order: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create job order",
        )


@router.get("/job-orders", response_model=PaginatedResponse[JobOrderResponse])
async def list_job_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[JobOrderStatus] = Query(None, alias="status"),
    priority: Optional[str] = None,
    client_org_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[JobOrderResponse]:
    """List job orders with filtering.

    Args:
        skip: Skip count
        limit: Result limit
        status_filter: Filter by status
        priority: Filter by priority
        client_org_id: Filter by client org
        db: Database session

    Returns:
        Paginated job orders
    """
    try:
        from sqlalchemy import select, func

        query = select(JobOrder)

        if status_filter:
            query = query.where(JobOrder.status == status_filter)

        if priority:
            query = query.where(JobOrder.priority == priority)

        if client_org_id:
            query = query.where(JobOrder.client_org_id == client_org_id)

        # Get total
        count_query = select(func.count()).select_from(JobOrder)
        if status_filter:
            count_query = count_query.where(JobOrder.status == status_filter)
        if priority:
            count_query = count_query.where(JobOrder.priority == priority)
        if client_org_id:
            count_query = count_query.where(JobOrder.client_org_id == client_org_id)

        total = await db.scalar(count_query)

        # Execute query
        query = query.order_by(JobOrder.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        orders = result.scalars().all()

        return PaginatedResponse(
            total=total or 0,
            skip=skip,
            limit=limit,
            items=[JobOrderResponse.from_orm(o) for o in orders],
        )
    except Exception as e:
        logger.error(f"Error listing job orders: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list job orders",
        )


@router.put("/job-orders/{job_order_id}", response_model=JobOrderResponse)
async def update_job_order(
    job_order_id: int,
    order_data: JobOrderUpdate,
    db: AsyncSession = Depends(get_db),
) -> JobOrderResponse:
    """Update job order.

    Args:
        job_order_id: Job order ID
        order_data: Update data
        db: Database session

    Returns:
        Updated job order
    """
    try:
        from sqlalchemy import select

        query = select(JobOrder).where(JobOrder.id == job_order_id)
        result = await db.execute(query)
        order = result.scalar_one_or_none()

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job order not found",
            )

        if order_data.priority is not None:
            order.priority = order_data.priority
        if order_data.target_fill_date is not None:
            order.target_fill_date = order_data.target_fill_date
        if order_data.max_submissions is not None:
            order.max_submissions = order_data.max_submissions
        if order_data.status is not None:
            order.status = order_data.status
            if order_data.status == JobOrderStatus.FILLED:
                order.filled_at = datetime.utcnow()
        if order_data.cancelled_reason is not None:
            order.cancelled_reason = order_data.cancelled_reason

        await db.commit()
        await db.refresh(order)
        return JobOrderResponse.from_orm(order)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating job order: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update job order",
        )


@router.get("/job-orders/{job_order_id}/submissions", response_model=dict)
async def get_job_order_submissions(
    job_order_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """List submissions for a job order with scores.

    Args:
        job_order_id: Job order ID
        skip: Skip count
        limit: Result limit
        db: Database session

    Returns:
        Job order with submissions
    """
    try:
        from sqlalchemy import select

        # Get job order
        query = select(JobOrder).where(JobOrder.id == job_order_id)
        result = await db.execute(query)
        order = result.scalar_one_or_none()

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job order not found",
            )

        # Mock submission data
        return {
            "job_order_id": job_order_id,
            "requirement_id": order.requirement_id,
            "status": order.status.value,
            "total_submissions": 15,
            "submissions": [
                {
                    "id": i,
                    "candidate_id": 100 + i,
                    "candidate_name": f"Candidate {i}",
                    "match_score": 0.85 - (i * 0.05),
                    "status": "SUBMITTED",
                    "submitted_at": "2026-03-08T10:00:00Z",
                }
                for i in range(1, min(limit + 1, 6))
            ],
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting submissions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get submissions",
        )


# ── Offer Workflow Management ──

@router.post("/offers", response_model=OfferWorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_offer(
    offer_data: OfferWorkflowCreate,
    db: AsyncSession = Depends(get_db),
) -> OfferWorkflowResponse:
    """Create an offer for a submission.

    Args:
        offer_data: Offer data
        db: Database session

    Returns:
        Created offer
    """
    try:
        offer = OfferWorkflow(
            submission_id=offer_data.submission_id,
            candidate_id=offer_data.candidate_id,
            bill_rate=offer_data.bill_rate,
            pay_rate=offer_data.pay_rate,
            start_date=offer_data.start_date,
            end_date=offer_data.end_date,
            benefits_package=offer_data.benefits_package,
            offer_status=OfferStatus.DRAFT,
            expiry_date=offer_data.expiry_date,
        )
        db.add(offer)
        await db.commit()
        await db.refresh(offer)
        return OfferWorkflowResponse.from_orm(offer)
    except Exception as e:
        logger.error(f"Error creating offer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create offer",
        )


@router.put("/offers/{offer_id}", response_model=OfferWorkflowResponse)
async def update_offer(
    offer_id: int,
    offer_data: OfferWorkflowUpdate,
    db: AsyncSession = Depends(get_db),
) -> OfferWorkflowResponse:
    """Update offer status and details.

    Args:
        offer_id: Offer ID
        offer_data: Update data
        db: Database session

    Returns:
        Updated offer
    """
    try:
        from sqlalchemy import select

        query = select(OfferWorkflow).where(OfferWorkflow.id == offer_id)
        result = await db.execute(query)
        offer = result.scalar_one_or_none()

        if not offer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Offer not found",
            )

        if offer_data.offer_status is not None:
            offer.offer_status = offer_data.offer_status
            if offer_data.offer_status in [OfferStatus.ACCEPTED, OfferStatus.DECLINED]:
                offer.responded_at = datetime.utcnow()
            if offer_data.offer_status == OfferStatus.APPROVED:
                offer.approved_at = datetime.utcnow()
                offer.approved_by = offer_data.approved_by

        if offer_data.bill_rate is not None:
            offer.bill_rate = offer_data.bill_rate
        if offer_data.pay_rate is not None:
            offer.pay_rate = offer_data.pay_rate
        if offer_data.decline_reason is not None:
            offer.decline_reason = offer_data.decline_reason
        if offer_data.counter_offer_details is not None:
            offer.counter_offer_details = offer_data.counter_offer_details
        if offer_data.expiry_date is not None:
            offer.expiry_date = offer_data.expiry_date

        await db.commit()
        await db.refresh(offer)
        return OfferWorkflowResponse.from_orm(offer)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating offer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update offer",
        )


@router.get("/offers", response_model=PaginatedResponse[OfferWorkflowResponse])
async def list_offers(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[OfferStatus] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[OfferWorkflowResponse]:
    """List offers with filtering.

    Args:
        skip: Skip count
        limit: Result limit
        status_filter: Filter by status
        db: Database session

    Returns:
        Paginated offers
    """
    try:
        from sqlalchemy import select, func

        query = select(OfferWorkflow)

        if status_filter:
            query = query.where(OfferWorkflow.offer_status == status_filter)

        # Get total
        count_query = select(func.count()).select_from(OfferWorkflow)
        if status_filter:
            count_query = count_query.where(OfferWorkflow.offer_status == status_filter)

        total = await db.scalar(count_query)

        # Execute query
        query = query.order_by(OfferWorkflow.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        offers = result.scalars().all()

        return PaginatedResponse(
            total=total or 0,
            skip=skip,
            limit=limit,
            items=[OfferWorkflowResponse.from_orm(o) for o in offers],
        )
    except Exception as e:
        logger.error(f"Error listing offers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list offers",
        )


@router.get("/offers/{offer_id}", response_model=OfferWorkflowResponse)
async def get_offer(
    offer_id: int,
    db: AsyncSession = Depends(get_db),
) -> OfferWorkflowResponse:
    """Get offer details with full history.

    Args:
        offer_id: Offer ID
        db: Database session

    Returns:
        Offer details
    """
    try:
        from sqlalchemy import select

        query = select(OfferWorkflow).where(OfferWorkflow.id == offer_id)
        result = await db.execute(query)
        offer = result.scalar_one_or_none()

        if not offer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Offer not found",
            )

        return OfferWorkflowResponse.from_orm(offer)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting offer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get offer",
        )


# ── Onboarding Task Management ──

@router.post("/onboarding", response_model=OnboardingTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_onboarding_task(
    task_data: OnboardingTaskCreate,
    db: AsyncSession = Depends(get_db),
) -> OnboardingTaskResponse:
    """Create an onboarding task.

    Args:
        task_data: Task data
        db: Database session

    Returns:
        Created task
    """
    try:
        task = OnboardingTask(
            candidate_id=task_data.candidate_id,
            placement_id=task_data.placement_id,
            task_name=task_data.task_name,
            task_type=task_data.task_type,
            status=OnboardingTaskStatus.PENDING,
            assigned_to=task_data.assigned_to,
            due_date=task_data.due_date,
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return OnboardingTaskResponse.from_orm(task)
    except Exception as e:
        logger.error(f"Error creating onboarding task: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create onboarding task",
        )


@router.get("/onboarding/candidate/{candidate_id}", response_model=PaginatedResponse[OnboardingTaskResponse])
async def get_candidate_onboarding_tasks(
    candidate_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[OnboardingTaskResponse]:
    """List onboarding tasks for a candidate.

    Args:
        candidate_id: Candidate ID
        skip: Skip count
        limit: Result limit
        db: Database session

    Returns:
        Paginated tasks
    """
    try:
        from sqlalchemy import select, func

        query = select(OnboardingTask).where(OnboardingTask.candidate_id == candidate_id)

        # Get total
        count_query = select(func.count()).select_from(OnboardingTask).where(
            OnboardingTask.candidate_id == candidate_id
        )
        total = await db.scalar(count_query)

        # Execute query
        query = query.order_by(OnboardingTask.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        tasks = result.scalars().all()

        return PaginatedResponse(
            total=total or 0,
            skip=skip,
            limit=limit,
            items=[OnboardingTaskResponse.from_orm(t) for t in tasks],
        )
    except Exception as e:
        logger.error(f"Error getting onboarding tasks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get onboarding tasks",
        )


@router.put("/onboarding/{task_id}", response_model=OnboardingTaskResponse)
async def update_onboarding_task(
    task_id: int,
    task_data: OnboardingTaskUpdate,
    db: AsyncSession = Depends(get_db),
) -> OnboardingTaskResponse:
    """Update onboarding task status.

    Args:
        task_id: Task ID
        task_data: Update data
        db: Database session

    Returns:
        Updated task
    """
    try:
        from sqlalchemy import select

        query = select(OnboardingTask).where(OnboardingTask.id == task_id)
        result = await db.execute(query)
        task = result.scalar_one_or_none()

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        if task_data.status is not None:
            task.status = task_data.status
            if task_data.status == OnboardingTaskStatus.COMPLETED:
                task.completed_at = datetime.utcnow()

        if task_data.assigned_to is not None:
            task.assigned_to = task_data.assigned_to
        if task_data.due_date is not None:
            task.due_date = task_data.due_date
        if task_data.notes is not None:
            task.notes = task_data.notes

        await db.commit()
        await db.refresh(task)
        return OnboardingTaskResponse.from_orm(task)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating onboarding task: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update onboarding task",
        )


@router.get("/onboarding/dashboard", response_model=OnboardingDashboardResponse)
async def get_onboarding_dashboard(
    db: AsyncSession = Depends(get_db),
) -> OnboardingDashboardResponse:
    """Get onboarding overview dashboard.

    Args:
        db: Database session

    Returns:
        Dashboard data
    """
    try:
        from sqlalchemy import select, func

        # Get counts by status
        statuses = [
            OnboardingTaskStatus.PENDING,
            OnboardingTaskStatus.IN_PROGRESS,
            OnboardingTaskStatus.COMPLETED,
            OnboardingTaskStatus.BLOCKED,
            OnboardingTaskStatus.WAIVED,
        ]

        counts = {}
        for status in statuses:
            count_query = select(func.count()).select_from(OnboardingTask).where(
                OnboardingTask.status == status
            )
            counts[status.value] = await db.scalar(count_query) or 0

        # Get total
        total_query = select(func.count()).select_from(OnboardingTask)
        total = await db.scalar(total_query) or 0

        # Get overdue count (due_date < today)
        from datetime import date as date_type
        overdue_query = select(func.count()).select_from(OnboardingTask).where(
            OnboardingTask.due_date < date_type.today(),
            OnboardingTask.status.in_([OnboardingTaskStatus.PENDING, OnboardingTaskStatus.IN_PROGRESS]),
        )
        overdue = await db.scalar(overdue_query) or 0

        # Get upcoming due count (due_date = today to next 7 days)
        from datetime import timedelta
        today = date_type.today()
        upcoming_query = select(func.count()).select_from(OnboardingTask).where(
            OnboardingTask.due_date >= today,
            OnboardingTask.due_date <= today + timedelta(days=7),
            OnboardingTask.status.in_([OnboardingTaskStatus.PENDING, OnboardingTaskStatus.IN_PROGRESS]),
        )
        upcoming = await db.scalar(upcoming_query) or 0

        completed = counts.get("completed", 0)
        completion_rate = (completed / total * 100) if total > 0 else 0.0

        return OnboardingDashboardResponse(
            pending_count=counts.get("pending", 0),
            in_progress_count=counts.get("in_progress", 0),
            completed_count=completed,
            blocked_count=counts.get("blocked", 0),
            waived_count=counts.get("waived", 0),
            overdue_count=overdue,
            upcoming_due_count=upcoming,
            total_count=total,
            completion_rate=completion_rate,
        )
    except Exception as e:
        logger.error(f"Error getting onboarding dashboard: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get onboarding dashboard",
        )


# ── Interview Feedback Management ──

@router.post("/interview-feedback", response_model=InterviewFeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_interview_feedback(
    feedback_data: InterviewFeedbackCreate,
    db: AsyncSession = Depends(get_db),
) -> InterviewFeedbackResponse:
    """Submit interview feedback.

    Args:
        feedback_data: Feedback data
        db: Database session

    Returns:
        Created feedback
    """
    try:
        feedback = InterviewFeedback(
            interview_id=feedback_data.interview_id,
            submission_id=feedback_data.submission_id,
            candidate_id=feedback_data.candidate_id,
            interviewer_id=feedback_data.interviewer_id,
            overall_rating=feedback_data.overall_rating,
            technical_score=feedback_data.technical_score,
            communication_score=feedback_data.communication_score,
            culture_fit_score=feedback_data.culture_fit_score,
            problem_solving_score=feedback_data.problem_solving_score,
            strengths=feedback_data.strengths,
            weaknesses=feedback_data.weaknesses,
            recommendation=feedback_data.recommendation,
            detailed_notes=feedback_data.detailed_notes,
            is_anonymous=feedback_data.is_anonymous,
        )
        db.add(feedback)
        await db.commit()
        await db.refresh(feedback)
        return InterviewFeedbackResponse.from_orm(feedback)
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit feedback",
        )


@router.get("/interview-feedback/candidate/{candidate_id}", response_model=PaginatedResponse[InterviewFeedbackResponse])
async def get_candidate_feedback(
    candidate_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[InterviewFeedbackResponse]:
    """Get all feedback for a candidate.

    Args:
        candidate_id: Candidate ID
        skip: Skip count
        limit: Result limit
        db: Database session

    Returns:
        Paginated feedback
    """
    try:
        from sqlalchemy import select, func

        query = select(InterviewFeedback).where(InterviewFeedback.candidate_id == candidate_id)

        # Get total
        count_query = select(func.count()).select_from(InterviewFeedback).where(
            InterviewFeedback.candidate_id == candidate_id
        )
        total = await db.scalar(count_query)

        # Execute query
        query = query.order_by(InterviewFeedback.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        feedbacks = result.scalars().all()

        return PaginatedResponse(
            total=total or 0,
            skip=skip,
            limit=limit,
            items=[InterviewFeedbackResponse.from_orm(f) for f in feedbacks],
        )
    except Exception as e:
        logger.error(f"Error getting candidate feedback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get candidate feedback",
        )


@router.get("/interview-feedback/summary/{submission_id}", response_model=FeedbackSummaryResponse)
async def get_feedback_summary(
    submission_id: int,
    db: AsyncSession = Depends(get_db),
) -> FeedbackSummaryResponse:
    """Get aggregated feedback summary for a submission.

    Args:
        submission_id: Submission ID
        db: Database session

    Returns:
        Feedback summary
    """
    try:
        from sqlalchemy import select, func

        # Get all feedback for submission
        query = select(InterviewFeedback).where(InterviewFeedback.submission_id == submission_id)
        result = await db.execute(query)
        feedbacks = result.scalars().all()

        if not feedbacks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No feedback found for submission",
            )

        # Calculate averages
        avg_overall = sum(f.overall_rating for f in feedbacks) / len(feedbacks) if feedbacks else 0
        avg_technical = (
            sum(f.technical_score for f in feedbacks if f.technical_score)
            / len([f for f in feedbacks if f.technical_score])
            if [f for f in feedbacks if f.technical_score]
            else None
        )
        avg_communication = (
            sum(f.communication_score for f in feedbacks if f.communication_score)
            / len([f for f in feedbacks if f.communication_score])
            if [f for f in feedbacks if f.communication_score]
            else None
        )
        avg_culture_fit = (
            sum(f.culture_fit_score for f in feedbacks if f.culture_fit_score)
            / len([f for f in feedbacks if f.culture_fit_score])
            if [f for f in feedbacks if f.culture_fit_score]
            else None
        )
        avg_problem_solving = (
            sum(f.problem_solving_score for f in feedbacks if f.problem_solving_score)
            / len([f for f in feedbacks if f.problem_solving_score])
            if [f for f in feedbacks if f.problem_solving_score]
            else None
        )

        # Count recommendations
        recommendation_counts = {}
        for feedback in feedbacks:
            rec_key = feedback.recommendation.value
            recommendation_counts[rec_key] = recommendation_counts.get(rec_key, 0) + 1

        # Determine consensus (most frequent recommendation)
        consensus = max(recommendation_counts, key=recommendation_counts.get) if recommendation_counts else None

        return FeedbackSummaryResponse(
            submission_id=submission_id,
            candidate_id=feedbacks[0].candidate_id,
            total_feedback_count=len(feedbacks),
            avg_overall_rating=avg_overall,
            avg_technical_score=avg_technical,
            avg_communication_score=avg_communication,
            avg_culture_fit_score=avg_culture_fit,
            avg_problem_solving_score=avg_problem_solving,
            recommendation_counts=recommendation_counts,
            consensus_recommendation=consensus,
            last_feedback_at=max(f.created_at for f in feedbacks) if feedbacks else None,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting feedback summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get feedback summary",
        )
