"""Dashboard and analytics API endpoints."""

import logging
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from models.user import User
from models.enums import UserRole
from schemas.dashboard import (
    OverviewMetrics,
    PipelineMetrics,
    RecruiterPerformanceMetrics,
    RequirementAnalytics,
    SubmissionFunnel,
    OfferMetrics,
    SupplierLeaderboard,
    CandidateSourceMetrics,
    TimeSeriesMetrics,
    KPISummary,
    DashboardOverviewResponse,
)
from services.dashboard_service import DashboardService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def _parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse date string to datetime."""
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        return None


@router.get("/overview", response_model=OverviewMetrics, status_code=status.HTTP_200_OK)
async def get_dashboard_overview(
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD format"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OverviewMetrics:
    """Get executive summary dashboard metrics.

    Args:
        start_date: Filter start date
        end_date: Filter end date
        db: Database session
        current_user: Current authenticated user

    Returns:
        Overview metrics
    """
    try:
        service = DashboardService(db)
        start = _parse_date(start_date)
        end = _parse_date(end_date)

        metrics = await service.get_overview_metrics(start, end)
        return OverviewMetrics(**metrics)
    except Exception as e:
        logger.error(f"Error getting overview metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch overview metrics",
        )


@router.get("/pipeline", response_model=PipelineMetrics, status_code=status.HTTP_200_OK)
async def get_pipeline_metrics(
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD format"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PipelineMetrics:
    """Get full pipeline view with stages.

    Args:
        start_date: Filter start date
        end_date: Filter end date
        db: Database session
        current_user: Current authenticated user

    Returns:
        Pipeline metrics with stage breakdown
    """
    try:
        service = DashboardService(db)
        start = _parse_date(start_date)
        end = _parse_date(end_date)

        metrics = await service.get_pipeline_metrics(start, end)
        return PipelineMetrics(**metrics)
    except Exception as e:
        logger.error(f"Error getting pipeline metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch pipeline metrics",
        )


@router.get("/recruiter-performance", response_model=RecruiterPerformanceMetrics, status_code=status.HTTP_200_OK)
async def get_recruiter_performance(
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD format"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RecruiterPerformanceMetrics:
    """Get per-recruiter performance metrics.

    Args:
        start_date: Filter start date
        end_date: Filter end date
        db: Database session
        current_user: Current authenticated user

    Returns:
        Recruiter performance metrics
    """
    try:
        service = DashboardService(db)
        start = _parse_date(start_date)
        end = _parse_date(end_date)

        metrics = await service.get_recruiter_performance(start, end)
        return RecruiterPerformanceMetrics(**metrics)
    except Exception as e:
        logger.error(f"Error getting recruiter performance: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch recruiter performance",
        )


@router.get("/requirement-analytics", response_model=RequirementAnalytics, status_code=status.HTTP_200_OK)
async def get_requirement_analytics(
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD format"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RequirementAnalytics:
    """Get requirement analytics.

    Args:
        start_date: Filter start date
        end_date: Filter end date
        db: Database session
        current_user: Current authenticated user

    Returns:
        Requirement analytics
    """
    try:
        service = DashboardService(db)
        start = _parse_date(start_date)
        end = _parse_date(end_date)

        metrics = await service.get_requirement_analytics(start, end)
        return RequirementAnalytics(**metrics)
    except Exception as e:
        logger.error(f"Error getting requirement analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch requirement analytics",
        )


@router.get("/submission-funnel", response_model=SubmissionFunnel, status_code=status.HTTP_200_OK)
async def get_submission_funnel(
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD format"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SubmissionFunnel:
    """Get submission funnel conversion metrics.

    Args:
        start_date: Filter start date
        end_date: Filter end date
        db: Database session
        current_user: Current authenticated user

    Returns:
        Submission funnel data
    """
    try:
        service = DashboardService(db)
        start = _parse_date(start_date)
        end = _parse_date(end_date)

        metrics = await service.get_submission_funnel(start, end)
        return SubmissionFunnel(**metrics)
    except Exception as e:
        logger.error(f"Error getting submission funnel: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch submission funnel",
        )


@router.get("/offer-metrics", response_model=OfferMetrics, status_code=status.HTTP_200_OK)
async def get_offer_metrics(
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD format"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OfferMetrics:
    """Get offer metrics.

    Args:
        start_date: Filter start date
        end_date: Filter end date
        db: Database session
        current_user: Current authenticated user

    Returns:
        Offer metrics
    """
    try:
        service = DashboardService(db)
        start = _parse_date(start_date)
        end = _parse_date(end_date)

        metrics = await service.get_offer_metrics(start, end)
        return OfferMetrics(**metrics)
    except Exception as e:
        logger.error(f"Error getting offer metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch offer metrics",
        )


@router.get("/supplier-leaderboard", response_model=SupplierLeaderboard, status_code=status.HTTP_200_OK)
async def get_supplier_leaderboard(
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD format"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SupplierLeaderboard:
    """Get supplier performance leaderboard.

    Args:
        start_date: Filter start date
        end_date: Filter end date
        db: Database session
        current_user: Current authenticated user

    Returns:
        Ranked suppliers by performance
    """
    try:
        service = DashboardService(db)
        start = _parse_date(start_date)
        end = _parse_date(end_date)

        metrics = await service.get_supplier_leaderboard(start, end)
        return SupplierLeaderboard(**metrics)
    except Exception as e:
        logger.error(f"Error getting supplier leaderboard: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch supplier leaderboard",
        )


@router.get("/candidate-sources", response_model=CandidateSourceMetrics, status_code=status.HTTP_200_OK)
async def get_candidate_sources(
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD format"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CandidateSourceMetrics:
    """Get candidate volume by source.

    Args:
        start_date: Filter start date
        end_date: Filter end date
        db: Database session
        current_user: Current authenticated user

    Returns:
        Candidates by source breakdown
    """
    try:
        service = DashboardService(db)
        start = _parse_date(start_date)
        end = _parse_date(end_date)

        metrics = await service.get_candidate_source_breakdown(start, end)
        return CandidateSourceMetrics(**metrics)
    except Exception as e:
        logger.error(f"Error getting candidate sources: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch candidate sources",
        )


@router.get("/time-series/{metric}", response_model=TimeSeriesMetrics, status_code=status.HTTP_200_OK)
async def get_time_series(
    metric: str,
    interval: str = Query("daily", pattern="^(daily|weekly|monthly)$"),
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD format"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TimeSeriesMetrics:
    """Get historical time series data for a metric.

    Args:
        metric: Metric name
        interval: daily, weekly, or monthly
        start_date: Filter start date
        end_date: Filter end date
        db: Database session
        current_user: Current authenticated user

    Returns:
        Time series data
    """
    try:
        service = DashboardService(db)
        start = _parse_date(start_date)
        end = _parse_date(end_date)

        ts_data = await service.get_time_series(metric, interval, start, end)
        return TimeSeriesMetrics(**ts_data)
    except Exception as e:
        logger.error(f"Error getting time series: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch time series data",
        )


@router.get("/kpi-summary", response_model=KPISummary, status_code=status.HTTP_200_OK)
async def get_kpi_summary(
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD format"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> KPISummary:
    """Get key performance indicators summary.

    Args:
        start_date: Filter start date
        end_date: Filter end date
        db: Database session
        current_user: Current authenticated user

    Returns:
        KPI summary with targets and trends
    """
    try:
        service = DashboardService(db)
        start = _parse_date(start_date)
        end = _parse_date(end_date)

        kpis = await service.get_kpi_summary(start, end)
        return KPISummary(**kpis)
    except Exception as e:
        logger.error(f"Error getting KPI summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch KPI summary",
        )


@router.get("", response_model=DashboardOverviewResponse, status_code=status.HTTP_200_OK)
async def get_complete_dashboard(
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD format"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DashboardOverviewResponse:
    """Get complete dashboard with all metrics.

    This endpoint fetches all dashboard metrics in a single call for
    comprehensive overview display.

    Args:
        start_date: Filter start date
        end_date: Filter end date
        db: Database session
        current_user: Current authenticated user

    Returns:
        Complete dashboard overview
    """
    try:
        service = DashboardService(db)
        start = _parse_date(start_date)
        end = _parse_date(end_date)

        # Fetch all metrics in parallel
        overview = await service.get_overview_metrics(start, end)
        pipeline = await service.get_pipeline_metrics(start, end)
        recruiter_perf = await service.get_recruiter_performance(start, end)
        requirements = await service.get_requirement_analytics(start, end)
        funnel = await service.get_submission_funnel(start, end)
        offers = await service.get_offer_metrics(start, end)
        suppliers = await service.get_supplier_leaderboard(start, end)
        sources = await service.get_candidate_source_breakdown(start, end)
        kpis = await service.get_kpi_summary(start, end)

        return DashboardOverviewResponse(
            overview=OverviewMetrics(**overview),
            pipeline=PipelineMetrics(**pipeline),
            recruiter_performance=RecruiterPerformanceMetrics(**recruiter_perf),
            requirements=RequirementAnalytics(**requirements),
            submission_funnel=SubmissionFunnel(**funnel),
            offers=OfferMetrics(**offers),
            suppliers=SupplierLeaderboard(**suppliers),
            sources=CandidateSourceMetrics(**sources),
            kpis=KPISummary(**kpis),
            generated_at=datetime.utcnow(),
            period=f"custom_{start.strftime('%Y%m%d') if start else 'start'}_to_{end.strftime('%Y%m%d') if end else 'end'}",
        )
    except Exception as e:
        logger.error(f"Error getting complete dashboard: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch complete dashboard",
        )
