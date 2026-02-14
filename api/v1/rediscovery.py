"""Candidate rediscovery API endpoints."""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db
from schemas.rediscovery import (
    RediscoveryCandidateListResponse,
    CandidateRediscoveryResponse,
    CompetencyProfileResponse,
    RediscoveryAnalyticsResponse,
)
from schemas.common import PaginatedResponse
from services.rediscovery_service import RediscoveryService
from agents.candidate_rediscovery_agent import CandidateRediscoveryAgent
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/rediscovery", tags=["rediscovery"]
)

# Initialize agent
rediscovery_agent = CandidateRediscoveryAgent(
    anthropic_api_key=settings.anthropic_api_key
)


@router.post(
    "/find/{requirement_id}",
    response_model=List[RediscoveryCandidateListResponse],
)
async def find_silver_medalists(
    requirement_id: int,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> List[RediscoveryCandidateListResponse]:
    """Find silver medalist candidates for requirement.

    Args:
        requirement_id: Requirement ID
        limit: Maximum candidates to return
        db: Database session

    Returns:
        List of ranked candidates
    """
    try:
        candidates = await rediscovery_agent.find_silver_medalists(
            db, requirement_id, limit=limit
        )

        return [
            RediscoveryCandidateListResponse.model_validate(c) for c in candidates
        ]
    except Exception as e:
        logger.error(f"Error finding silver medalists: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/candidates",
    response_model=PaginatedResponse[CandidateRediscoveryResponse],
)
async def list_rediscovery_candidates(
    requirement_id: Optional[int] = None,
    candidate_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[CandidateRediscoveryResponse]:
    """List rediscovery candidates.

    Args:
        requirement_id: Filter by requirement
        candidate_id: Filter by candidate
        status: Filter by status
        skip: Number to skip
        limit: Number to limit
        db: Database session

    Returns:
        Paginated rediscovery list
    """
    try:
        rediscoveries, total = await RediscoveryService.list_rediscoveries(
            db,
            requirement_id=requirement_id,
            candidate_id=candidate_id,
            status=status,
            skip=skip,
            limit=limit,
        )

        items = [
            CandidateRediscoveryResponse.model_validate(r) for r in rediscoveries
        ]
        return PaginatedResponse(
            total=total,
            skip=skip,
            limit=limit,
            items=items,
        )
    except Exception as e:
        logger.error(f"Error listing rediscoveries: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/candidate/{candidate_id}/competency-profile",
    response_model=CompetencyProfileResponse,
)
async def get_competency_profile(
    candidate_id: int,
    db: AsyncSession = Depends(get_db),
) -> CompetencyProfileResponse:
    """Get candidate competency profile.

    Args:
        candidate_id: Candidate ID
        db: Database session

    Returns:
        Competency profile
    """
    try:
        profile = await RediscoveryService.get_competency_profile(db, candidate_id)

        if not profile:
            raise HTTPException(
                status_code=404, detail="Competency profile not found"
            )

        return CompetencyProfileResponse.model_validate(profile)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting competency profile: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/candidate/{candidate_id}/build-profile",
    response_model=CompetencyProfileResponse,
)
async def build_competency_profile(
    candidate_id: int,
    db: AsyncSession = Depends(get_db),
) -> CompetencyProfileResponse:
    """Build or rebuild competency profile from interview feedback.

    Args:
        candidate_id: Candidate ID
        db: Database session

    Returns:
        Competency profile
    """
    try:
        profile_data = await rediscovery_agent.build_competency_index(
            db, candidate_id
        )

        profile = await RediscoveryService.update_competency_profile(
            db, candidate_id, **profile_data
        )

        return CompetencyProfileResponse.model_validate(profile)
    except Exception as e:
        logger.error(f"Error building competency profile: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/reengagement-opportunities")
async def get_reengagement_opportunities(
    days_inactive: int = Query(90, ge=1),
    db: AsyncSession = Depends(get_db),
):
    """Find candidates with reengagement opportunities.

    Args:
        days_inactive: Days inactive threshold
        db: Database session

    Returns:
        List of reengagement opportunities
    """
    try:
        opportunities = (
            await rediscovery_agent.detect_reengagement_opportunities(
                db, days_inactive=days_inactive
            )
        )

        return {"opportunities": opportunities}
    except Exception as e:
        logger.error(f"Error getting reengagement opportunities: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/candidate/{candidate_id}/reengage")
async def send_reengagement_message(
    candidate_id: int,
    requirement_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Generate and send reengagement message to candidate.

    Args:
        candidate_id: Candidate ID
        requirement_id: Requirement ID
        db: Database session

    Returns:
        Generated message
    """
    try:
        message = await rediscovery_agent.generate_reengagement_message(
            db, candidate_id, requirement_id
        )

        # Update rediscovery record
        rediscoveries, _ = await RediscoveryService.list_rediscoveries(
            db, candidate_id=candidate_id, requirement_id=requirement_id, limit=1
        )

        if rediscoveries:
            await RediscoveryService.update_rediscovery(
                db,
                rediscoveries[0].id,
                status="contacted",
                contacted_at=__import__("datetime").datetime.utcnow(),
            )

        return {
            "candidate_id": candidate_id,
            "requirement_id": requirement_id,
            "message": message,
        }
    except Exception as e:
        logger.error(f"Error sending reengagement message: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/analytics", response_model=RediscoveryAnalyticsResponse)
async def get_rediscovery_analytics(
    db: AsyncSession = Depends(get_db),
) -> RediscoveryAnalyticsResponse:
    """Get rediscovery analytics.

    Args:
        db: Database session

    Returns:
        Analytics data
    """
    try:
        analytics = await rediscovery_agent.get_rediscovery_analytics(db)

        return RediscoveryAnalyticsResponse.model_validate(analytics)
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/candidate/{candidate_id}/score", status_code=status.HTTP_200_OK)
async def calculate_rediscovery_score(
    candidate_id: int,
    requirement_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Calculate rediscovery match score for candidate and requirement.

    Args:
        candidate_id: Candidate ID
        requirement_id: Requirement ID
        db: Database session

    Returns:
        Score breakdown
    """
    try:
        score_data = await rediscovery_agent.score_rediscovery_match(
            db, candidate_id, requirement_id
        )

        return score_data
    except Exception as e:
        logger.error(f"Error calculating rediscovery score: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
