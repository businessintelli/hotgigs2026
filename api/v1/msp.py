"""MSP Admin Portal API — manage clients, suppliers, distributions, submissions."""

import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from api.dependencies import get_current_user, require_role, require_org_type, get_tenant_context_dep
from database.tenant_context import TenantContext
from models.user import User
from models.organization import Organization
from schemas.organization import (
    OrganizationCreate, OrganizationUpdate, OrganizationResponse, OrganizationListResponse,
)
from schemas.msp import (
    DistributeRequirementRequest, DistributionResponse, DistributionListResponse,
    SubmissionListResponse, SupplierSubmissionResponse,
    MSPReviewRequest, MSPReviewResponse,
    PlacementCreateRequest, PlacementResponse, PlacementListResponse,
    MSPDashboardMetrics, SupplierScorecard, ClientMetrics,
)
from services.msp_onboarding_service import MSPOnboardingService
from services.msp_requirement_service import MSPRequirementService
from services.msp_submission_service import MSPSubmissionService
from services.msp_coordination_service import MSPCoordinationService
from services.msp_analytics_service import MSPAnalyticsService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/msp", tags=["MSP Admin"])


# --- Dashboard ---

@router.get("/dashboard", response_model=MSPDashboardMetrics)
async def get_msp_dashboard(
    user: User = Depends(require_role("msp_admin", "msp_manager", "msp_recruiter", "platform_admin", "admin")),
    ctx: TenantContext = Depends(get_tenant_context_dep),
    session: AsyncSession = Depends(get_db),
):
    """Get MSP dashboard aggregate metrics."""
    svc = MSPAnalyticsService(session)
    metrics = await svc.get_msp_dashboard_metrics(ctx.organization_id)
    return MSPDashboardMetrics(**metrics)


# --- Organization Management ---

@router.get("/organizations", response_model=OrganizationListResponse)
async def list_organizations(
    org_type: Optional[str] = Query(None, pattern="^(client|supplier)$"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    user: User = Depends(require_role("msp_admin", "msp_manager", "msp_recruiter", "platform_admin", "admin")),
    ctx: TenantContext = Depends(get_tenant_context_dep),
    session: AsyncSession = Depends(get_db),
):
    """List all client and supplier organizations under this MSP."""
    svc = MSPOnboardingService(session)
    if org_type == "client":
        orgs = await svc.get_clients(ctx.organization_id)
    elif org_type == "supplier":
        orgs = await svc.get_suppliers(ctx.organization_id)
    else:
        clients = await svc.get_clients(ctx.organization_id)
        suppliers = await svc.get_suppliers(ctx.organization_id)
        orgs = clients + suppliers

    # Manual pagination
    total = len(orgs)
    paginated = orgs[offset:offset + limit]

    return OrganizationListResponse(
        items=[OrganizationResponse.model_validate(o) for o in paginated],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.post("/organizations", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def onboard_organization(
    org_data: OrganizationCreate,
    user: User = Depends(require_role("msp_admin", "platform_admin", "admin")),
    ctx: TenantContext = Depends(get_tenant_context_dep),
    session: AsyncSession = Depends(get_db),
):
    """Onboard a new client or supplier organization."""
    svc = MSPOnboardingService(session)

    try:
        if org_data.org_type == "client":
            result = await svc.onboard_client(
                msp_org_id=ctx.organization_id,
                name=org_data.name,
                primary_contact_email=org_data.primary_contact_email or f"admin@{org_data.slug or 'org'}.com",
                primary_contact_name=org_data.primary_contact_name,
                industry=org_data.industry,
                website=org_data.website,
                description=org_data.description,
                address=org_data.address,
                city=org_data.city,
                state=org_data.state,
                country=org_data.country,
                contract_start=org_data.contract_start,
                contract_end=org_data.contract_end,
            )
        elif org_data.org_type == "supplier":
            result = await svc.onboard_supplier(
                msp_org_id=ctx.organization_id,
                name=org_data.name,
                primary_contact_email=org_data.primary_contact_email or f"admin@{org_data.slug or 'org'}.com",
                primary_contact_name=org_data.primary_contact_name,
                tier=org_data.tier or "standard",
                commission_rate=org_data.commission_rate,
                specializations=org_data.specializations,
                industry=org_data.industry,
                website=org_data.website,
                description=org_data.description,
                address=org_data.address,
                city=org_data.city,
                state=org_data.state,
                country=org_data.country,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="org_type must be 'client' or 'supplier'",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return OrganizationResponse.model_validate(result["organization"])


@router.post("/organizations/{org_id}/activate", response_model=OrganizationResponse)
async def activate_organization(
    org_id: int,
    user: User = Depends(require_role("msp_admin", "platform_admin", "admin")),
    session: AsyncSession = Depends(get_db),
):
    """Activate an organization (move from pending to active)."""
    svc = MSPOnboardingService(session)
    try:
        org = await svc.activate_organization(org_id)
        return OrganizationResponse.model_validate(org)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/organizations/{org_id}/suspend", response_model=OrganizationResponse)
async def suspend_organization(
    org_id: int,
    reason: Optional[str] = None,
    user: User = Depends(require_role("msp_admin", "platform_admin", "admin")),
    session: AsyncSession = Depends(get_db),
):
    """Suspend an organization."""
    svc = MSPOnboardingService(session)
    try:
        org = await svc.suspend_organization(org_id, reason)
        return OrganizationResponse.model_validate(org)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# --- Requirement Distribution ---

@router.post("/requirements/{req_id}/distribute", response_model=List[DistributionResponse])
async def distribute_requirement(
    req_id: int,
    request: DistributeRequirementRequest,
    user: User = Depends(require_role("msp_admin", "msp_manager", "msp_recruiter", "platform_admin", "admin")),
    ctx: TenantContext = Depends(get_tenant_context_dep),
    session: AsyncSession = Depends(get_db),
):
    """Distribute a requirement to one or more suppliers."""
    svc = MSPRequirementService(session)
    try:
        distributions = await svc.distribute_requirement(
            msp_org_id=ctx.organization_id,
            requirement_id=req_id,
            supplier_org_ids=request.supplier_org_ids,
            distributed_by_user_id=user.id,
            expires_at=request.expires_at,
            max_submissions=request.max_submissions,
            notes_to_supplier=request.notes_to_supplier,
        )
        return [DistributionResponse(
            id=d.id,
            organization_id=d.organization_id,
            requirement_id=d.requirement_id,
            supplier_org_id=d.supplier_org_id,
            status=str(d.status),
            distributed_at=d.distributed_at,
            expires_at=d.expires_at,
            max_submissions=d.max_submissions,
            notes_to_supplier=d.notes_to_supplier,
        ) for d in distributions]
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/requirements/{req_id}/distributions", response_model=DistributionListResponse)
async def get_requirement_distributions(
    req_id: int,
    user: User = Depends(require_role("msp_admin", "msp_manager", "msp_recruiter", "platform_admin", "admin")),
    session: AsyncSession = Depends(get_db),
):
    """Get all distributions for a requirement."""
    svc = MSPRequirementService(session)
    enriched = await svc.get_distributions_for_requirement(req_id)

    items = []
    for e in enriched:
        d = e["distribution"]
        items.append(DistributionResponse(
            id=d.id,
            organization_id=d.organization_id,
            requirement_id=d.requirement_id,
            supplier_org_id=d.supplier_org_id,
            supplier_org_name=e["supplier_org_name"],
            status=str(d.status),
            distributed_at=d.distributed_at,
            expires_at=d.expires_at,
            max_submissions=d.max_submissions,
            submission_count=e["submission_count"],
            notes_to_supplier=d.notes_to_supplier,
        ))

    return DistributionListResponse(items=items, total=len(items))


# --- Submissions Pipeline ---

@router.get("/submissions", response_model=SubmissionListResponse)
async def get_submissions_pipeline(
    status_filter: Optional[str] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    user: User = Depends(require_role("msp_admin", "msp_manager", "msp_recruiter", "platform_admin", "admin")),
    ctx: TenantContext = Depends(get_tenant_context_dep),
    session: AsyncSession = Depends(get_db),
):
    """Get the full submissions pipeline for the MSP."""
    svc = MSPSubmissionService(session)
    result = await svc.get_submission_pipeline(
        msp_org_id=ctx.organization_id,
        status_filter=status_filter,
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
            duplicate_flag=s.duplicate_flag,
            submitted_at=s.submitted_at,
            created_at=s.created_at,
        ) for s in result["items"]],
        total=result["total"],
        offset=result["offset"],
        limit=result["limit"],
    )


@router.post("/submissions/{sub_id}/review", response_model=MSPReviewResponse)
async def review_submission(
    sub_id: int,
    review: MSPReviewRequest,
    user: User = Depends(require_role("msp_admin", "msp_manager", "msp_recruiter", "platform_admin", "admin")),
    ctx: TenantContext = Depends(get_tenant_context_dep),
    session: AsyncSession = Depends(get_db),
):
    """MSP reviews a supplier submission."""
    svc = MSPSubmissionService(session)
    try:
        result = await svc.review_submission(
            msp_org_id=ctx.organization_id,
            submission_id=sub_id,
            reviewer_id=user.id,
            decision=review.decision,
            match_score=review.match_score,
            quality_rating=review.quality_rating,
            screening_notes=review.screening_notes,
            strengths=review.strengths,
            concerns=review.concerns,
            recommendation=review.recommendation,
        )
        return MSPReviewResponse(
            id=result.id,
            supplier_submission_id=result.supplier_submission_id,
            reviewer_id=result.reviewer_id,
            decision=str(result.decision),
            match_score=result.match_score,
            quality_rating=result.quality_rating,
            screening_notes=result.screening_notes,
            strengths=result.strengths,
            concerns=result.concerns,
            recommendation=result.recommendation,
            reviewed_at=result.reviewed_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/submissions/{sub_id}/forward")
async def forward_to_client(
    sub_id: int,
    notes: Optional[str] = None,
    user: User = Depends(require_role("msp_admin", "msp_manager", "msp_recruiter", "platform_admin", "admin")),
    session: AsyncSession = Depends(get_db),
):
    """Forward an approved submission to the client."""
    svc = MSPSubmissionService(session)
    try:
        await svc.forward_to_client(sub_id, notes)
        return {"status": "forwarded", "submission_id": sub_id}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# --- Analytics ---

@router.get("/analytics/suppliers/{supplier_org_id}", response_model=SupplierScorecard)
async def get_supplier_scorecard(
    supplier_org_id: int,
    user: User = Depends(require_role("msp_admin", "msp_manager", "platform_admin", "admin")),
    session: AsyncSession = Depends(get_db),
):
    """Get supplier performance scorecard."""
    svc = MSPAnalyticsService(session)
    try:
        return SupplierScorecard(**await svc.get_supplier_scorecard(supplier_org_id))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/analytics/clients/{client_org_id}", response_model=ClientMetrics)
async def get_client_metrics(
    client_org_id: int,
    user: User = Depends(require_role("msp_admin", "msp_manager", "platform_admin", "admin")),
    session: AsyncSession = Depends(get_db),
):
    """Get client-specific metrics."""
    svc = MSPAnalyticsService(session)
    try:
        return ClientMetrics(**await svc.get_client_metrics(client_org_id))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# --- Placements ---

@router.get("/placements", response_model=PlacementListResponse)
async def list_placements(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    user: User = Depends(require_role("msp_admin", "msp_manager", "msp_recruiter", "platform_admin", "admin")),
    ctx: TenantContext = Depends(get_tenant_context_dep),
    session: AsyncSession = Depends(get_db),
):
    """List active placements managed by this MSP."""
    svc = MSPCoordinationService(session)
    result = await svc.get_active_placements(ctx.organization_id, "msp", offset, limit)
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
            msp_margin=p.msp_margin,
            status=str(p.status),
            work_location=p.work_location,
            job_title=p.job_title,
            created_at=p.created_at,
        ) for p in result["items"]],
        total=result["total"],
        offset=result["offset"],
        limit=result["limit"],
    )


@router.get("/sla-breaches")
async def check_sla_breaches(
    user: User = Depends(require_role("msp_admin", "msp_manager", "platform_admin", "admin")),
    ctx: TenantContext = Depends(get_tenant_context_dep),
    session: AsyncSession = Depends(get_db),
):
    """Check for SLA breaches across active workflows."""
    svc = MSPCoordinationService(session)
    breaches = await svc.check_sla_breaches(ctx.organization_id)
    return {"breaches": breaches, "total": len(breaches)}
