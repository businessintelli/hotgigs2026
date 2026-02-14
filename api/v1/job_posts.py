"""Job post generation and management API endpoints."""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db
from schemas.job_post import (
    JobPostCreate,
    JobPostUpdate,
    JobPostResponse,
    JobPostGenerateRequest,
    JobPostAnalyticsResponse,
    SEOOptimizationResponse,
    InclusivityCheckResponse,
    SalaryRangeSuggestionResponse,
    JobPostVersionResponse,
    JobPostGenerateFromTextRequest,
    MultiboardPublishRequest,
)
from schemas.common import PaginatedResponse
from services.job_post_service import JobPostService
from agents.job_post_agent import JobPostAgent
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/job-posts", tags=["job_posts"])

# Initialize agent
job_post_agent = JobPostAgent(anthropic_api_key=settings.anthropic_api_key)


@router.post(
    "/generate/{requirement_id}",
    response_model=JobPostResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_job_post(
    requirement_id: int,
    request: JobPostGenerateRequest,
    db: AsyncSession = Depends(get_db),
) -> JobPostResponse:
    """Generate job post from requirement.

    Args:
        requirement_id: Requirement ID
        request: Generation parameters
        db: Database session

    Returns:
        Generated job post
    """
    try:
        post_data = await job_post_agent.generate_job_post(
            db, requirement_id, style=request.style
        )

        job_post = await JobPostService.create_job_post(db, **post_data)

        return JobPostResponse.model_validate(job_post)
    except Exception as e:
        logger.error(f"Error generating job post: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/generate-from-text", response_model=JobPostResponse)
async def generate_from_freeform_text(
    request: JobPostGenerateFromTextRequest,
    db: AsyncSession = Depends(get_db),
) -> JobPostResponse:
    """Generate job post from freeform text.

    Args:
        request: Freeform text and parameters
        db: Database session

    Returns:
        Generated job post
    """
    try:
        parsed = await job_post_agent.generate_from_text(request.freeform_text)

        # Create requirement (simplified - in real world would be more complex)
        from models.requirement import Requirement

        requirement = Requirement(
            customer_id=1,  # Default customer
            title=parsed.get("title", "Job Posting"),
            description=parsed.get("description"),
            skills_required=parsed.get("skills_required", []),
            skills_preferred=parsed.get("skills_preferred", []),
            experience_min=parsed.get("experience_min"),
            experience_max=parsed.get("experience_max"),
            location_city=parsed.get("location", "").split(",")[0] if parsed.get("location") else None,
            employment_type=parsed.get("employment_type"),
            work_mode=parsed.get("work_mode"),
            rate_min=parsed.get("salary_min"),
            rate_max=parsed.get("salary_max"),
            rate_type=parsed.get("salary_type", "annual"),
        )
        db.add(requirement)
        await db.flush()

        job_post = await JobPostService.create_job_post(
            db,
            requirement_id=requirement.id,
            title=parsed.get("title", "Job Posting"),
            summary=parsed.get("summary", ""),
            content=parsed.get("description", ""),
        )

        await db.commit()
        await db.refresh(job_post)

        return JobPostResponse.model_validate(job_post)
    except Exception as e:
        await db.rollback()
        logger.error(f"Error generating from text: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{job_post_id}", response_model=JobPostResponse)
async def get_job_post(
    job_post_id: int,
    db: AsyncSession = Depends(get_db),
) -> JobPostResponse:
    """Get job post details.

    Args:
        job_post_id: Job post ID
        db: Database session

    Returns:
        Job post details
    """
    try:
        job_post = await JobPostService.get_job_post(db, job_post_id)

        if not job_post:
            raise HTTPException(status_code=404, detail="Job post not found")

        return JobPostResponse.model_validate(job_post)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job post: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{job_post_id}", response_model=JobPostResponse)
async def update_job_post(
    job_post_id: int,
    job_post_data: JobPostUpdate,
    db: AsyncSession = Depends(get_db),
) -> JobPostResponse:
    """Update job post.

    Args:
        job_post_id: Job post ID
        job_post_data: Update data
        db: Database session

    Returns:
        Updated job post
    """
    try:
        job_post = await JobPostService.update_job_post(
            db, job_post_id, **job_post_data.model_dump(exclude_unset=True)
        )

        return JobPostResponse.model_validate(job_post)
    except Exception as e:
        logger.error(f"Error updating job post: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{job_post_id}/optimize-seo", response_model=SEOOptimizationResponse)
async def optimize_for_seo(
    job_post_id: int,
    db: AsyncSession = Depends(get_db),
) -> SEOOptimizationResponse:
    """Optimize job post for SEO.

    Args:
        job_post_id: Job post ID
        db: Database session

    Returns:
        SEO optimization result
    """
    try:
        job_post = await JobPostService.get_job_post(db, job_post_id)

        if not job_post:
            raise HTTPException(status_code=404, detail="Job post not found")

        # Get requirement for keywords
        from models.requirement import Requirement

        requirement = await db.get(Requirement, job_post.requirement_id)

        target_keywords = (requirement.skills_required or [])[:5] if requirement else []

        optimization = await job_post_agent.optimize_for_seo(
            job_post.content, target_keywords
        )

        # Update SEO score
        await JobPostService.update_seo_metrics(
            db, job_post_id, optimization["seo_score"]
        )

        return SEOOptimizationResponse.model_validate(optimization)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error optimizing for SEO: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/{job_post_id}/check-inclusivity",
    response_model=InclusivityCheckResponse,
)
async def check_inclusive_language(
    job_post_id: int,
    db: AsyncSession = Depends(get_db),
) -> InclusivityCheckResponse:
    """Check job post for biased/exclusive language.

    Args:
        job_post_id: Job post ID
        db: Database session

    Returns:
        Inclusivity check result
    """
    try:
        job_post = await JobPostService.get_job_post(db, job_post_id)

        if not job_post:
            raise HTTPException(status_code=404, detail="Job post not found")

        check_result = await job_post_agent.check_inclusive_language(
            job_post.content
        )

        # Update inclusivity score
        await JobPostService.update_inclusivity_metrics(
            db, job_post_id, check_result["inclusivity_score"]
        )

        return InclusivityCheckResponse.model_validate(check_result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking inclusive language: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{job_post_id}/publish", response_model=JobPostResponse)
async def publish_job_post(
    job_post_id: int,
    request: MultiboardPublishRequest,
    db: AsyncSession = Depends(get_db),
) -> JobPostResponse:
    """Publish job post to job boards.

    Args:
        job_post_id: Job post ID
        request: Publish request with board names
        db: Database session

    Returns:
        Published job post
    """
    try:
        job_post = await JobPostService.publish_job_post(
            db, job_post_id, request.boards
        )

        return JobPostResponse.model_validate(job_post)
    except Exception as e:
        logger.error(f"Error publishing job post: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{job_post_id}/multi-board")
async def create_multiboard_versions(
    job_post_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Create optimized versions for multiple job boards.

    Args:
        job_post_id: Job post ID
        db: Database session

    Returns:
        Board-specific versions
    """
    try:
        versions = await job_post_agent.create_multi_board_versions(db, job_post_id)

        return {"versions": versions}
    except Exception as e:
        logger.error(f"Error creating multiboard versions: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/suggest-salary", response_model=SalaryRangeSuggestionResponse)
async def suggest_salary_range(
    skills: List[str],
    location: str,
    experience_years: int = 5,
    db: AsyncSession = Depends(get_db),
) -> SalaryRangeSuggestionResponse:
    """Suggest competitive salary range.

    Args:
        skills: Required skills
        location: Job location
        experience_years: Years of experience
        db: Database session

    Returns:
        Salary suggestion
    """
    try:
        suggestion = await job_post_agent.suggest_salary_range(
            db, skills, location, experience_years
        )

        return SalaryRangeSuggestionResponse.model_validate(suggestion)
    except Exception as e:
        logger.error(f"Error suggesting salary: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/requirement/{requirement_id}",
    response_model=PaginatedResponse[JobPostResponse],
)
async def get_job_posts_for_requirement(
    requirement_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[JobPostResponse]:
    """Get all job posts for a requirement.

    Args:
        requirement_id: Requirement ID
        skip: Number to skip
        limit: Number to limit
        db: Database session

    Returns:
        Paginated job posts
    """
    try:
        posts, total = await JobPostService.list_job_posts(
            db, requirement_id=requirement_id, skip=skip, limit=limit
        )

        items = [JobPostResponse.model_validate(p) for p in posts]

        return PaginatedResponse(
            total=total,
            skip=skip,
            limit=limit,
            items=items,
        )
    except Exception as e:
        logger.error(f"Error getting job posts: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{job_post_id}/analytics", response_model=List[JobPostAnalyticsResponse])
async def get_job_post_analytics(
    job_post_id: int,
    db: AsyncSession = Depends(get_db),
) -> List[JobPostAnalyticsResponse]:
    """Get analytics for job post.

    Args:
        job_post_id: Job post ID
        db: Database session

    Returns:
        Analytics records
    """
    try:
        analytics = await JobPostService.get_analytics(db, job_post_id)

        return [JobPostAnalyticsResponse.model_validate(a) for a in analytics]
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
