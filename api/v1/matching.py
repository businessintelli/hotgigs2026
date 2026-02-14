import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from datetime import datetime
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from services.matching_service import MatchingService
from agents.matching_agent import MatchingAgent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/matching", tags=["matching"])

# Initialize service
matching_agent = MatchingAgent()
matching_service = MatchingService(matching_agent)


# Pydantic models
class MatchWeights(BaseModel):
    """Matching weight configuration."""

    skill: float = Field(default=0.35, ge=0.0, le=1.0)
    experience: float = Field(default=0.25, ge=0.0, le=1.0)
    education: float = Field(default=0.15, ge=0.0, le=1.0)
    location: float = Field(default=0.10, ge=0.0, le=1.0)
    rate: float = Field(default=0.10, ge=0.0, le=1.0)
    availability: float = Field(default=0.05, ge=0.0, le=1.0)
    culture: float = Field(default=0.0, ge=0.0, le=1.0)

    class Config:
        json_schema_extra = {
            "example": {
                "skill": 0.35,
                "experience": 0.25,
                "education": 0.15,
                "location": 0.10,
                "rate": 0.10,
                "availability": 0.05,
                "culture": 0.0,
            }
        }


class ScoreBreakdown(BaseModel):
    """Score component breakdown."""

    skill: float
    experience: float
    education: float
    location: float
    rate: float
    availability: float
    culture: float


class MatchScoreResponse(BaseModel):
    """Match score response model."""

    candidate_id: int
    candidate_name: str
    candidate_email: str
    overall_score: float
    skill_score: float
    experience_score: float
    education_score: float
    location_score: float
    rate_score: float
    availability_score: float
    culture_score: float
    missing_skills: List[str]
    standout_qualities: List[str]
    score_breakdown: ScoreBreakdown


class MatchResultsResponse(BaseModel):
    """Match results response."""

    requirement_id: Optional[int] = None
    candidate_id: Optional[int] = None
    matches_found: int
    matches: List[Dict[str, Any]]
    timestamp: datetime


class SingleMatchResponse(BaseModel):
    """Single match score response."""

    requirement_id: int
    candidate_id: int
    overall_score: float
    skill_score: float
    experience_score: float
    education_score: float
    location_score: float
    rate_score: float
    availability_score: float
    culture_score: float
    missing_skills: List[str]
    standout_qualities: List[str]
    score_breakdown: ScoreBreakdown
    matched_at: Optional[str]


class RequirementMatchesResponse(BaseModel):
    """Paginated requirement matches."""

    requirement_id: int
    total: int
    limit: int
    offset: int
    matches: List[Dict[str, Any]]


class BatchMatchResponse(BaseModel):
    """Batch matching operation response."""

    total_requirements: int
    total_candidates: int
    matches_created: int
    matches_updated: int
    errors: int
    timestamp: datetime


class MatchOverrideRequest(BaseModel):
    """Request to override match score."""

    overall_score: float = Field(ge=0.0, le=1.0)
    notes: Optional[str] = None


class MatchOverrideResponse(BaseModel):
    """Override response."""

    requirement_id: int
    candidate_id: int
    overall_score: float
    matched_by: str
    notes: Optional[str]
    timestamp: datetime


@router.post(
    "/requirement/{requirement_id}/match",
    response_model=MatchResultsResponse,
    status_code=status.HTTP_200_OK,
    summary="Match candidates for requirement",
    description="Find all candidates matching a specific job requirement, ranked by match score.",
)
async def match_requirement_to_candidates(
    requirement_id: int,
    limit: int = Query(50, ge=1, le=500),
    min_score: float = Query(0.5, ge=0.0, le=1.0),
    session: AsyncSession = Depends(get_db),
) -> MatchResultsResponse:
    """
    Match candidates for a specific requirement.

    Args:
        requirement_id: Job requirement ID
        limit: Maximum number of results (default: 50)
        min_score: Minimum match score threshold (default: 0.5)
        session: Database session

    Returns:
        Ranked list of matching candidates
    """
    try:
        result = await matching_service.match_requirement_to_candidates(
            session,
            requirement_id,
            limit,
            min_score,
        )

        return MatchResultsResponse(
            requirement_id=requirement_id,
            matches_found=result["matches_found"],
            matches=result["matches"],
            timestamp=datetime.fromisoformat(result["timestamp"]),
        )

    except Exception as e:
        logger.error(f"Error matching requirement: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/candidate/{candidate_id}/match",
    response_model=MatchResultsResponse,
    status_code=status.HTTP_200_OK,
    summary="Match requirements for candidate",
    description="Find all job requirements matching a specific candidate, ranked by match score.",
)
async def match_candidate_to_requirements(
    candidate_id: int,
    limit: int = Query(50, ge=1, le=500),
    min_score: float = Query(0.5, ge=0.0, le=1.0),
    session: AsyncSession = Depends(get_db),
) -> MatchResultsResponse:
    """
    Match requirements for a specific candidate.

    Args:
        candidate_id: Candidate ID
        limit: Maximum number of results (default: 50)
        min_score: Minimum match score threshold (default: 0.5)
        session: Database session

    Returns:
        Ranked list of matching requirements
    """
    try:
        result = await matching_service.match_candidate_to_requirements(
            session,
            candidate_id,
            limit,
            min_score,
        )

        return MatchResultsResponse(
            candidate_id=candidate_id,
            matches_found=result["matches_found"],
            matches=result["matches"],
            timestamp=datetime.fromisoformat(result["timestamp"]),
        )

    except Exception as e:
        logger.error(f"Error matching candidate: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/scores/{requirement_id}/{candidate_id}",
    response_model=SingleMatchResponse,
    status_code=status.HTTP_200_OK,
    summary="Get specific match score",
    description="Get detailed match score between a candidate and requirement.",
)
async def get_match_score(
    requirement_id: int,
    candidate_id: int,
    session: AsyncSession = Depends(get_db),
) -> SingleMatchResponse:
    """
    Get match score for specific candidate-requirement pair.

    Args:
        requirement_id: Requirement ID
        candidate_id: Candidate ID
        session: Database session

    Returns:
        Detailed match score with breakdown
    """
    try:
        match = await matching_service.get_match_score(session, requirement_id, candidate_id)

        if not match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Match not found",
            )

        return SingleMatchResponse(
            requirement_id=match["requirement_id"],
            candidate_id=match["candidate_id"],
            overall_score=match["overall_score"],
            skill_score=match["skill_score"],
            experience_score=match["experience_score"],
            education_score=match["education_score"],
            location_score=match["location_score"],
            rate_score=match["rate_score"],
            availability_score=match["availability_score"],
            culture_score=match["culture_score"],
            missing_skills=match["missing_skills"],
            standout_qualities=match["standout_qualities"],
            score_breakdown=ScoreBreakdown(**match["score_breakdown"]),
            matched_at=match.get("matched_at"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting match score: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/scores/{requirement_id}",
    response_model=RequirementMatchesResponse,
    status_code=status.HTTP_200_OK,
    summary="Get all match scores for requirement",
    description="Get paginated list of all match scores for a specific requirement.",
)
async def get_requirement_matches(
    requirement_id: int,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db),
) -> RequirementMatchesResponse:
    """
    Get all match scores for a requirement.

    Args:
        requirement_id: Requirement ID
        limit: Results limit (default: 50)
        offset: Results offset (default: 0)
        session: Database session

    Returns:
        Paginated match results
    """
    try:
        result = await matching_service.get_requirement_matches(
            session,
            requirement_id,
            limit,
            offset,
        )

        return RequirementMatchesResponse(
            requirement_id=result["requirement_id"],
            total=result["total"],
            limit=result["limit"],
            offset=result["offset"],
            matches=result["matches"],
        )

    except Exception as e:
        logger.error(f"Error getting requirement matches: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.put(
    "/config",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Update matching weights",
    description="Update the matching algorithm weight configuration.",
)
async def update_matching_weights(
    weights: MatchWeights,
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Update matching algorithm weights.

    Args:
        weights: New weight configuration
        session: Database session

    Returns:
        Updated configuration
    """
    try:
        weights_dict = weights.model_dump()
        result = await matching_service.update_match_weights(session, weights_dict)

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error updating weights: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/batch",
    response_model=BatchMatchResponse,
    status_code=status.HTTP_200_OK,
    summary="Batch match all requirements and candidates",
    description="Execute batch matching operation for all active requirements and candidates.",
)
async def batch_match_all(
    min_score: float = Query(0.5, ge=0.0, le=1.0),
    session: AsyncSession = Depends(get_db),
) -> BatchMatchResponse:
    """
    Execute batch matching for all active requirements and candidates.

    Args:
        min_score: Minimum match score to save (default: 0.5)
        session: Database session

    Returns:
        Batch operation statistics
    """
    try:
        result = await matching_service.batch_match_all(session, min_score)

        return BatchMatchResponse(
            total_requirements=result["total_requirements"],
            total_candidates=result["total_candidates"],
            matches_created=result["matches_created"],
            matches_updated=result["matches_updated"],
            errors=result["errors"],
            timestamp=datetime.fromisoformat(result["timestamp"]),
        )

    except Exception as e:
        logger.error(f"Error in batch matching: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/recalculate/{requirement_id}",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Recalculate matches for requirement",
    description="Recalculate all match scores for a specific requirement.",
)
async def recalculate_requirement_matches(
    requirement_id: int,
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Recalculate all matches for a specific requirement.

    Args:
        requirement_id: Requirement ID
        session: Database session

    Returns:
        Recalculation statistics
    """
    try:
        result = await matching_service.recalculate_requirement_matches(session, requirement_id)

        return result

    except Exception as e:
        logger.error(f"Error recalculating matches: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.put(
    "/override/{requirement_id}/{candidate_id}",
    response_model=MatchOverrideResponse,
    status_code=status.HTTP_200_OK,
    summary="Override match score",
    description="Manually override a match score.",
)
async def override_match_score(
    requirement_id: int,
    candidate_id: int,
    override_data: MatchOverrideRequest,
    session: AsyncSession = Depends(get_db),
) -> MatchOverrideResponse:
    """
    Manually override a match score.

    Args:
        requirement_id: Requirement ID
        candidate_id: Candidate ID
        override_data: Override data with new score and notes
        session: Database session

    Returns:
        Override confirmation
    """
    try:
        result = await matching_service.override_match(
            session,
            requirement_id,
            candidate_id,
            override_data.overall_score,
            override_data.notes,
        )

        return MatchOverrideResponse(
            requirement_id=result["requirement_id"],
            candidate_id=result["candidate_id"],
            overall_score=result["overall_score"],
            matched_by=result["matched_by"],
            notes=result["notes"],
            timestamp=datetime.fromisoformat(result["timestamp"]),
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error overriding match: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
