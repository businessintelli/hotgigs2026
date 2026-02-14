"""Resume harvesting API endpoints."""

import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db
from schemas.harvest import (
    HarvestSourceCreate,
    HarvestSourceUpdate,
    HarvestSourceResponse,
    HarvestJobCreate,
    HarvestJobResponse,
    HarvestResultResponse,
    HarvestSearchRequest,
    HarvestSearchResponse,
    CandidateSourceMappingResponse,
    HarvestAnalyticsResponse,
)
from schemas.common import PaginatedResponse
from services.harvest_service import HarvestService
from agents.resume_harvesting_agent import ResumeHarvestingAgent
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/harvest", tags=["harvest"])
harvesting_agent = ResumeHarvestingAgent(anthropic_api_key=settings.anthropic_api_key)


# ===== HARVEST SOURCE ENDPOINTS =====


@router.post("/sources", response_model=HarvestSourceResponse, status_code=status.HTTP_201_CREATED)
async def configure_source(
    source_config: HarvestSourceCreate,
    db: AsyncSession = Depends(get_db),
) -> HarvestSourceResponse:
    """Configure a harvesting source with API credentials and search parameters."""
    try:
        source = await harvesting_agent.configure_source(db, source_config.model_dump())
        await db.commit()
        return source

    except Exception as e:
        logger.error(f"Error configuring source: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/sources", response_model=PaginatedResponse[HarvestSourceResponse])
async def list_sources(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[HarvestSourceResponse]:
    """List configured harvest sources."""
    try:
        service = HarvestService(db)
        sources, total = await service.get_sources(skip=skip, limit=limit)

        return PaginatedResponse(
            total=total,
            skip=skip,
            limit=limit,
            items=sources,
        )

    except Exception as e:
        logger.error(f"Error listing sources: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/sources/{source_id}", response_model=HarvestSourceResponse)
async def update_source(
    source_id: int,
    source_update: HarvestSourceUpdate,
    db: AsyncSession = Depends(get_db),
) -> HarvestSourceResponse:
    """Update harvest source configuration."""
    try:
        service = HarvestService(db)
        source = await service.update_source(source_id, source_update.model_dump(exclude_unset=True))

        if not source:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")

        await db.commit()
        return source

    except Exception as e:
        logger.error(f"Error updating source: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ===== HARVEST SEARCH ENDPOINTS =====


@router.post("/search", response_model=HarvestSearchResponse)
async def search_candidates(
    search_request: HarvestSearchRequest,
    db: AsyncSession = Depends(get_db),
) -> HarvestSearchResponse:
    """Search for candidates on a specific source."""
    try:
        candidates = await harvesting_agent.search_candidates(
            db, search_request.source_name, search_request.search_criteria
        )

        return HarvestSearchResponse(
            candidates=candidates,
            total_count=len(candidates),
            source_name=search_request.source_name,
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error searching candidates: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ===== HARVEST JOB ENDPOINTS =====


@router.post("/jobs", response_model=HarvestJobResponse, status_code=status.HTTP_201_CREATED)
async def create_harvest_job(
    job_data: HarvestJobCreate,
    db: AsyncSession = Depends(get_db),
) -> HarvestJobResponse:
    """Create harvest job (one-time or scheduled)."""
    try:
        service = HarvestService(db)
        source = await service.get_source_by_id(job_data.source_id)

        if not source:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")

        job = await harvesting_agent.schedule_harvest(
            db, source.name, job_data.search_criteria, job_data.frequency or "once"
        )

        await db.commit()
        return job

    except Exception as e:
        logger.error(f"Error creating harvest job: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/jobs", response_model=PaginatedResponse[HarvestJobResponse])
async def list_harvest_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[HarvestJobResponse]:
    """List harvest jobs."""
    try:
        service = HarvestService(db)
        jobs, total = await service.get_jobs(skip=skip, limit=limit)

        return PaginatedResponse(
            total=total,
            skip=skip,
            limit=limit,
            items=jobs,
        )

    except Exception as e:
        logger.error(f"Error listing harvest jobs: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/jobs/{job_id}", response_model=HarvestJobResponse)
async def get_harvest_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
) -> HarvestJobResponse:
    """Get harvest job details."""
    try:
        service = HarvestService(db)
        job = await service.get_job_by_id(job_id)

        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

        return job

    except Exception as e:
        logger.error(f"Error getting harvest job: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/jobs/{job_id}/run", response_model=HarvestJobResponse)
async def run_harvest_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
) -> HarvestJobResponse:
    """Execute/re-run harvest job."""
    try:
        service = HarvestService(db)
        job = await service.get_job_by_id(job_id)

        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

        await service.mark_job_running(job_id)
        await db.commit()

        # Execute harvest (in production, would be async task)
        source = await service.get_source_by_id(job.source_id)
        candidates = await harvesting_agent.search_candidates(db, source.name, job.search_criteria)
        await harvesting_agent.process_harvest_results(db, job_id, candidates)
        await service.mark_job_completed(job_id)
        await db.commit()

        return await service.get_job_by_id(job_id)

    except Exception as e:
        logger.error(f"Error running harvest job: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ===== HARVEST RESULTS ENDPOINTS =====


@router.get("/jobs/{job_id}/results", response_model=PaginatedResponse[HarvestResultResponse])
async def get_harvest_results(
    job_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[HarvestResultResponse]:
    """Get harvest results for a job."""
    try:
        service = HarvestService(db)
        job = await service.get_job_by_id(job_id)

        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

        results, total = await service.get_job_results(job_id, skip=skip, limit=limit)

        return PaginatedResponse(
            total=total,
            skip=skip,
            limit=limit,
            items=results,
        )

    except Exception as e:
        logger.error(f"Error getting harvest results: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ===== CANDIDATE ENRICHMENT ENDPOINTS =====


@router.post("/enrich/{candidate_id}")
async def enrich_candidate(
    candidate_id: int,
    sources: Optional[List[int]] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Enrich candidate from multiple sources."""
    try:
        enrichment = await harvesting_agent.enrich_candidate(db, candidate_id, sources)
        return enrichment

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error enriching candidate: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/candidate/{candidate_id}/sources", response_model=List[CandidateSourceMappingResponse])
async def get_candidate_sources(
    candidate_id: int,
    db: AsyncSession = Depends(get_db),
) -> List[CandidateSourceMappingResponse]:
    """Get all source profiles for a candidate."""
    try:
        service = HarvestService(db)
        sources = await service.get_candidate_sources(candidate_id)
        return sources

    except Exception as e:
        logger.error(f"Error getting candidate sources: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ===== DEDUPLICATION ENDPOINTS =====


@router.post("/deduplicate")
async def run_deduplication(
    candidates: List[dict],
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Run deduplication on candidate list."""
    try:
        deduped = await harvesting_agent.deduplicate_candidates(db, candidates)

        return {
            "original_count": len(candidates),
            "deduped_count": len(deduped),
            "duplicates_found": len(candidates) - len(deduped),
            "candidates": deduped,
        }

    except Exception as e:
        logger.error(f"Error deduplicating candidates: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ===== ANALYTICS ENDPOINTS =====


@router.get("/analytics", response_model=HarvestAnalyticsResponse)
async def get_harvest_analytics(
    db: AsyncSession = Depends(get_db),
) -> HarvestAnalyticsResponse:
    """Get harvesting analytics."""
    try:
        analytics = await harvesting_agent.get_harvest_analytics(db)
        return analytics

    except Exception as e:
        logger.error(f"Error getting harvest analytics: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
