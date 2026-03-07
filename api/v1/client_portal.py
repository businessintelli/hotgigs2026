"""Client Portal API — client-facing endpoints for requirements, submissions, feedback."""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from api.dependencies import get_current_user, require_org_type, get_tenant_context_dep
from database.tenant_context import TenantContext
from models.user import User
from schemas.msp import (
    SubmissionListResponse, SupplierSubmissionResponse,
    ClientFeedbackRequest, ClientFeedbackResponse,
    PlacementListResponse, PlacementResponse,
    ClientMetrics,
)
from services.msp_submission_service import MSPSubmissionService
from services.msp_coordination_service import MSPCoordinationService
from services.msp_analytics_service import MSPAnalyticsService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/client", tags=["Client Portal"])


@router.get("/dashboard")
async def get_client_dashboard(
    user: User = Depends(get_current_user),
    ctx: TenantContext = Depends(get_tenant_context_dep),
    session: AsyncSession = Depends(get_db),
):
    """Get client dashboard with key metrics."""
    analytics_svc = MSPAnalyticsService(session)
    coord_svc = MSPCoordinationService(session)

    metrics = await analytics_svc.get_client_metrics(ctx.organization_id)
    placements = await coord_svc.get_active_placements(ctx.organization_id, "client", 0, 5)

    return {
        "metrics": metrics,
        "recent_placements": [
            PlacementResponse(
                id=p.id,
                organization_id=p.organization_id,
                requirement_id=p.requirement_id,
                candidate_id=p.candidate_id,
                supplier_org_id=p.supplier_org_id,
                client_org_id=p.client_org_id,
                start_date=p.start_date,
                end_date=p.end_date,
                bill_rate=p.bill_rate,
                pay_rate=p.pay_rate,
                msp_margin=p.msp_margin,
                status=str(p.status),
                work_location=p.work_location,
                job_title=p.job_title,
                created_at=p.created_at,
            ) for p in placements["items"]
        ],
    }


@router.get("/submissions", response_model=SubmissionListResponse)
async def get_client_submissions(
    status_filter: Optional[str] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    user: User = Depends(get_current_user),
    ctx: TenantContext = Depends(get_tenant_context_dep),
    session: AsyncSession = Depends(get_db),
):
    """Get submissions forwarded to this client by MSP."""
    svc = MSPSubmissionService(session)
    # Client sees only submissions that have been forwarded to them
    effective_status = status_filter or "submitted_to_client"
    result = await svc.get_submission_pipeline(
        status_filter=effective_status,
        offset=offset,
        limit=limit,
    )
    return SubmissionListResponse(
        items=[SupplierSubmissionResponse(
            id=s.id,
            organization_id=s.organization_id,
            requirement_distribution_id=s.requirement_distribution_id,
            candidate_id=s.candidate_id,
            status=str(s.status),
            bill_rate=s.bill_rate,
            pay_rate=s.pay_rate,
            availability_date=s.availability_date,
            supplier_notes=s.supplier_notes,
            quality_score=s.quality_score,
            match_score=s.match_score,
            submitted_at=s.submitted_at,
            created_at=s.created_at,
        ) for s in result["items"]],
        total=result["total"],
        offset=result["offset"],
        limit=result["limit"],
    )


@router.post("/submissions/{sub_id}/feedback", response_model=ClientFeedbackResponse)
async def provide_feedback(
    sub_id: int,
    feedback: ClientFeedbackRequest,
    user: User = Depends(get_current_user),
    ctx: TenantContext = Depends(get_tenant_context_dep),
    session: AsyncSession = Depends(get_db),
):
    """Provide feedback (shortlist/reject/interview) on a submitted candidate."""
    svc = MSPSubmissionService(session)
    try:
        result = await svc.record_client_feedback(
            submission_id=sub_id,
            client_org_id=ctx.organization_id,
            client_user_id=user.id,
            decision=feedback.decision,
            feedback_notes=feedback.feedback_notes,
            rating=feedback.rating,
            preferred_interview_date=feedback.preferred_interview_date,
            interview_type=feedback.interview_type,
        )
        return ClientFeedbackResponse(
            id=result.id,
            supplier_submission_id=result.supplier_submission_id,
            client_user_id=result.client_user_id,
            decision=str(result.decision),
            feedback_notes=result.feedback_notes,
            rating=result.rating,
            feedback_at=result.feedback_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/placements", response_model=PlacementListResponse)
async def get_client_placements(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    user: User = Depends(get_current_user),
    ctx: TenantContext = Depends(get_tenant_context_dep),
    session: AsyncSession = Depends(get_db),
):
    """Get active placements at this client."""
    svc = MSPCoordinationService(session)
    result = await svc.get_active_placements(ctx.organization_id, "client", offset, limit)
    return PlacementListResponse(
        items=[PlacementResponse(
            id=p.id,
            organization_id=p.organization_id,
            requirement_id=p.requirement_id,
            candidate_id=p.candidate_id,
            supplier_org_id=p.supplier_org_id,
            client_org_id=p.client_org_id,
            start_date=p.start_date,
            end_date=p.end_date,
            bill_rate=p.bill_rate,
            pay_rate=p.pay_rate,
            status=str(p.status),
            work_location=p.work_location,
            job_title=p.job_title,
            created_at=p.created_at,
        ) for p in result["items"]],
        total=result["total"],
        offset=result["offset"],
        limit=result["limit"],
    )


@router.get("/analytics", response_model=ClientMetrics)
async def get_my_analytics(
    user: User = Depends(get_current_user),
    ctx: TenantContext = Depends(get_tenant_context_dep),
    session: AsyncSession = Depends(get_db),
):
    """Get analytics for this client organization."""
    svc = MSPAnalyticsService(session)
    try:
        return ClientMetrics(**await svc.get_client_metrics(ctx.organization_id))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
