"""Supplier Portal API — supplier-facing endpoints for opportunities, submissions, performance."""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from api.dependencies import get_current_user, get_tenant_context_dep
from database.tenant_context import TenantContext
from models.user import User
from schemas.msp import (
    SupplierSubmitCandidateRequest, SupplierSubmissionResponse,
    SubmissionListResponse,
    PlacementListResponse, PlacementResponse,
    SupplierScorecard,
)
from services.msp_requirement_service import MSPRequirementService
from services.msp_submission_service import MSPSubmissionService
from services.msp_coordination_service import MSPCoordinationService
from services.msp_analytics_service import MSPAnalyticsService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/supplier", tags=["Supplier Portal"])


@router.get("/dashboard")
async def get_supplier_dashboard(
    user: User = Depends(get_current_user),
    ctx: TenantContext = Depends(get_tenant_context_dep),
    session: AsyncSession = Depends(get_db),
):
    """Get supplier dashboard with opportunities and performance."""
    req_svc = MSPRequirementService(session)
    analytics_svc = MSPAnalyticsService(session)
    coord_svc = MSPCoordinationService(session)

    opportunities = await req_svc.get_supplier_opportunities(ctx.organization_id)
    try:
        scorecard = await analytics_svc.get_supplier_scorecard(ctx.organization_id)
    except ValueError:
        scorecard = {}
    placements = await coord_svc.get_active_placements(ctx.organization_id, "supplier", 0, 5)

    return {
        "opportunities_count": len(opportunities),
        "scorecard": scorecard,
        "active_placements": placements["total"],
        "recent_opportunities": opportunities[:5],
    }


@router.get("/opportunities")
async def get_opportunities(
    status_filter: Optional[str] = None,
    user: User = Depends(get_current_user),
    ctx: TenantContext = Depends(get_tenant_context_dep),
    session: AsyncSession = Depends(get_db),
):
    """Get requirements distributed to this supplier (opportunities)."""
    svc = MSPRequirementService(session)
    opportunities = await svc.get_supplier_opportunities(
        ctx.organization_id, status_filter
    )

    return {
        "items": [
            {
                "distribution_id": o["distribution"].id,
                "requirement_id": o["distribution"].requirement_id,
                "status": str(o["distribution"].status),
                "distributed_at": o["distribution"].distributed_at,
                "expires_at": o["distribution"].expires_at,
                "max_submissions": o["distribution"].max_submissions,
                "my_submission_count": o["my_submission_count"],
                "remaining_submissions": o["remaining_submissions"],
                "notes": o["distribution"].notes_to_supplier,
                "requirement": {
                    "id": o["requirement"].id,
                    "title": getattr(o["requirement"], "title", "N/A"),
                } if o["requirement"] else None,
            }
            for o in opportunities
        ],
        "total": len(opportunities),
    }


@router.post("/submissions", response_model=SupplierSubmissionResponse, status_code=status.HTTP_201_CREATED)
async def submit_candidate(
    submission: SupplierSubmitCandidateRequest,
    user: User = Depends(get_current_user),
    ctx: TenantContext = Depends(get_tenant_context_dep),
    session: AsyncSession = Depends(get_db),
):
    """Submit a candidate for a distributed requirement."""
    svc = MSPSubmissionService(session)
    try:
        result = await svc.submit_candidate(
            supplier_org_id=ctx.organization_id,
            submitted_by_user_id=user.id,
            candidate_id=submission.candidate_id,
            requirement_distribution_id=submission.requirement_distribution_id,
            bill_rate=submission.bill_rate,
            pay_rate=submission.pay_rate,
            availability_date=submission.availability_date,
            supplier_notes=submission.supplier_notes,
            candidate_summary=submission.candidate_summary,
        )
        return SupplierSubmissionResponse(
            id=result.id,
            organization_id=result.organization_id,
            requirement_distribution_id=result.requirement_distribution_id,
            candidate_id=result.candidate_id,
            status=str(result.status),
            bill_rate=result.bill_rate,
            pay_rate=result.pay_rate,
            availability_date=result.availability_date,
            supplier_notes=result.supplier_notes,
            quality_score=result.quality_score,
            match_score=result.match_score,
            submitted_at=result.submitted_at,
            created_at=result.created_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/submissions", response_model=SubmissionListResponse)
async def get_my_submissions(
    status_filter: Optional[str] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    user: User = Depends(get_current_user),
    ctx: TenantContext = Depends(get_tenant_context_dep),
    session: AsyncSession = Depends(get_db),
):
    """Get this supplier's submissions and their status."""
    svc = MSPSubmissionService(session)
    result = await svc.get_supplier_submissions(
        ctx.organization_id, status_filter, offset, limit
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
            duplicate_flag=s.duplicate_flag,
            submitted_at=s.submitted_at,
            created_at=s.created_at,
        ) for s in result["items"]],
        total=result["total"],
        offset=result["offset"],
        limit=result["limit"],
    )


@router.get("/performance", response_model=SupplierScorecard)
async def get_my_performance(
    user: User = Depends(get_current_user),
    ctx: TenantContext = Depends(get_tenant_context_dep),
    session: AsyncSession = Depends(get_db),
):
    """Get this supplier's performance scorecard."""
    svc = MSPAnalyticsService(session)
    try:
        return SupplierScorecard(**await svc.get_supplier_scorecard(ctx.organization_id))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/placements", response_model=PlacementListResponse)
async def get_my_placements(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    user: User = Depends(get_current_user),
    ctx: TenantContext = Depends(get_tenant_context_dep),
    session: AsyncSession = Depends(get_db),
):
    """Get this supplier's active placements."""
    svc = MSPCoordinationService(session)
    result = await svc.get_active_placements(ctx.organization_id, "supplier", offset, limit)
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
