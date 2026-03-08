"""Advanced search API endpoints."""

import logging
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from schemas.automation import (
    CandidateSearchRequest,
    CandidateSearchResponse,
    CandidateMatch,
    SavedSearchCreate,
    SavedSearchUpdate,
    SavedSearchResponse,
)
from schemas.common import PaginatedResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search")


# ===== CANDIDATE SEARCH ENDPOINTS =====

@router.post("/candidates", response_model=CandidateSearchResponse)
async def search_candidates(
    search_req: CandidateSearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
) -> CandidateSearchResponse:
    """
    Advanced candidate search with filters and relevance scoring.

    Returns candidates matching criteria with match scores and highlighted fields.
    """
    try:
        # Mock data: 10 candidates with varied match levels
        mock_candidates = [
            CandidateMatch(
                id=1,
                first_name="Alice",
                last_name="Johnson",
                email="alice.johnson@email.com",
                current_title="Senior Python Developer",
                location_city="San Francisco",
                location_country="USA",
                total_experience_years=8.5,
                match_score=95.0,
                matched_fields={
                    "skills": "Python, Django, FastAPI",
                    "experience": "8.5 years (exceeds 5+ requirement)",
                    "location": "San Francisco"
                },
                status="READY_FOR_SUBMISSION"
            ),
            CandidateMatch(
                id=2,
                first_name="Bob",
                last_name="Smith",
                email="bob.smith@email.com",
                current_title="Full Stack Developer",
                location_city="New York",
                location_country="USA",
                total_experience_years=6.0,
                match_score=85.0,
                matched_fields={
                    "skills": "Python, JavaScript, React",
                    "experience": "6.0 years"
                },
                status="MATCHED"
            ),
            CandidateMatch(
                id=3,
                first_name="Carol",
                last_name="Williams",
                email="carol.williams@email.com",
                current_title="Data Engineer",
                location_city="Seattle",
                location_country="USA",
                total_experience_years=7.2,
                match_score=92.0,
                matched_fields={
                    "skills": "Python, Spark, SQL",
                    "experience": "7+ years"
                },
                status="SCORED"
            ),
            CandidateMatch(
                id=4,
                first_name="Diana",
                last_name="Brown",
                email="diana.brown@email.com",
                current_title="Software Engineer",
                location_city="Austin",
                location_country="USA",
                total_experience_years=5.5,
                match_score=78.0,
                matched_fields={
                    "skills": "Java, Python, Microservices",
                },
                status="SCREENING"
            ),
            CandidateMatch(
                id=5,
                first_name="Edward",
                last_name="Davis",
                email="edward.davis@email.com",
                current_title="Backend Engineer",
                location_city="Boston",
                location_country="USA",
                total_experience_years=4.0,
                match_score=72.0,
                matched_fields={
                    "skills": "Python, Node.js",
                    "experience": "4 years"
                },
                status="PARSED"
            ),
            CandidateMatch(
                id=6,
                first_name="Fiona",
                last_name="Miller",
                email="fiona.miller@email.com",
                current_title="ML Engineer",
                location_city="Mountain View",
                location_country="USA",
                total_experience_years=6.5,
                match_score=88.0,
                matched_fields={
                    "skills": "Python, TensorFlow, Keras",
                    "experience": "6.5 years"
                },
                status="READY_FOR_SUBMISSION"
            ),
            CandidateMatch(
                id=7,
                first_name="George",
                last_name="Garcia",
                email="george.garcia@email.com",
                current_title="Full Stack Developer",
                location_city="Los Angeles",
                location_country="USA",
                total_experience_years=3.0,
                match_score=65.0,
                matched_fields={
                    "skills": "React, Python",
                },
                status="SOURCED"
            ),
            CandidateMatch(
                id=8,
                first_name="Hannah",
                last_name="Martinez",
                email="hannah.martinez@email.com",
                current_title="Senior DevOps Engineer",
                location_city="Denver",
                location_country="USA",
                total_experience_years=9.0,
                match_score=91.0,
                matched_fields={
                    "skills": "Kubernetes, Docker, Python, AWS",
                    "experience": "9 years"
                },
                status="MATCHED"
            ),
            CandidateMatch(
                id=9,
                first_name="Iris",
                last_name="Lee",
                email="iris.lee@email.com",
                current_title="Cloud Architect",
                location_city="Toronto",
                location_country="Canada",
                total_experience_years=10.0,
                match_score=87.0,
                matched_fields={
                    "skills": "AWS, Azure, Python, Terraform",
                    "experience": "10+ years"
                },
                status="SCORED"
            ),
            CandidateMatch(
                id=10,
                first_name="Jack",
                last_name="Wilson",
                email="jack.wilson@email.com",
                current_title="QA Engineer",
                location_city="Chicago",
                location_country="USA",
                total_experience_years=5.0,
                match_score=68.0,
                matched_fields={
                    "skills": "Python, Selenium, Testing",
                    "experience": "5 years"
                },
                status="SCREENING"
            ),
        ]

        # Filter by min_match_score if provided
        if search_req.min_match_score:
            mock_candidates = [c for c in mock_candidates if c.match_score >= search_req.min_match_score]

        # Apply limit and offset
        results = mock_candidates[search_req.skip:search_req.skip + search_req.limit]

        return CandidateSearchResponse(
            total=len(mock_candidates),
            results=results,
            filters_applied=search_req.model_dump(exclude_none=True)
        )

    except Exception as e:
        logger.error(f"Error searching candidates: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/candidates/quick", response_model=List[CandidateMatch])
async def quick_search_candidates(
    q: str = Query(..., min_length=1, description="Search query (name, email, skills)"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
) -> List[CandidateMatch]:
    """Quick search candidates by name, email, or skills."""
    try:
        # Mock data: 5 quick search results
        quick_results = [
            CandidateMatch(
                id=1,
                first_name="Alice",
                last_name="Johnson",
                email="alice.johnson@email.com",
                current_title="Senior Python Developer",
                location_city="San Francisco",
                location_country="USA",
                total_experience_years=8.5,
                match_score=95.0,
                matched_fields={"field": "name", "value": "Alice Johnson"},
                status="READY_FOR_SUBMISSION"
            ),
            CandidateMatch(
                id=3,
                first_name="Carol",
                last_name="Williams",
                email="carol.williams@email.com",
                current_title="Data Engineer",
                location_city="Seattle",
                location_country="USA",
                total_experience_years=7.2,
                match_score=92.0,
                matched_fields={"field": "skills", "value": "Python"},
                status="SCORED"
            ),
            CandidateMatch(
                id=6,
                first_name="Fiona",
                last_name="Miller",
                email="fiona.miller@email.com",
                current_title="ML Engineer",
                location_city="Mountain View",
                location_country="USA",
                total_experience_years=6.5,
                match_score=88.0,
                matched_fields={"field": "email", "value": "fiona.miller"},
                status="READY_FOR_SUBMISSION"
            ),
            CandidateMatch(
                id=8,
                first_name="Hannah",
                last_name="Martinez",
                email="hannah.martinez@email.com",
                current_title="Senior DevOps Engineer",
                location_city="Denver",
                location_country="USA",
                total_experience_years=9.0,
                match_score=91.0,
                matched_fields={"field": "name", "value": "Hannah Martinez"},
                status="MATCHED"
            ),
            CandidateMatch(
                id=9,
                first_name="Iris",
                last_name="Lee",
                email="iris.lee@email.com",
                current_title="Cloud Architect",
                location_city="Toronto",
                location_country="Canada",
                total_experience_years=10.0,
                match_score=87.0,
                matched_fields={"field": "skills", "value": "Python, AWS"},
                status="SCORED"
            ),
        ]

        return quick_results

    except Exception as e:
        logger.error(f"Error in quick search: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/requirements", response_model=dict)
async def search_requirements(
    body: dict,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
) -> dict:
    """Advanced requirement search with filters."""
    try:
        # Mock data
        mock_requirements = [
            {
                "id": 1,
                "title": "Senior Python Developer",
                "client": "TechCorp Inc",
                "location": "San Francisco, CA",
                "priority": "HIGH",
                "status": "ACTIVE",
                "min_rate": 100.0,
                "max_rate": 150.0,
                "candidate_count": 5,
                "match_count": 3
            },
            {
                "id": 2,
                "title": "Data Engineer",
                "client": "DataStream Analytics",
                "location": "New York, NY",
                "priority": "CRITICAL",
                "status": "ACTIVE",
                "min_rate": 110.0,
                "max_rate": 160.0,
                "candidate_count": 3,
                "match_count": 2
            },
            {
                "id": 3,
                "title": "DevOps Engineer",
                "client": "CloudNine Systems",
                "location": "Remote",
                "priority": "MEDIUM",
                "status": "ACTIVE",
                "min_rate": 90.0,
                "max_rate": 130.0,
                "candidate_count": 7,
                "match_count": 4
            },
        ]

        return {
            "total": len(mock_requirements),
            "results": mock_requirements,
            "filters_applied": body
        }

    except Exception as e:
        logger.error(f"Error searching requirements: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ===== SAVED SEARCH ENDPOINTS =====

@router.post("/saved", response_model=SavedSearchResponse, status_code=status.HTTP_201_CREATED)
async def save_search(
    search_data: SavedSearchCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
) -> SavedSearchResponse:
    """Save a search template."""
    try:
        # Mock response
        return SavedSearchResponse(
            id=1,
            name=search_data.name,
            search_type=search_data.search_type,
            filters=search_data.filters,
            sort_by=search_data.sort_by,
            sort_order=search_data.sort_order,
            is_default=search_data.is_default,
            result_count=0,
            last_run_at=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    except Exception as e:
        logger.error(f"Error saving search: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/saved", response_model=List[SavedSearchResponse])
async def list_saved_searches(
    search_type: Optional[str] = Query(None, description="Filter by search type"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
) -> List[SavedSearchResponse]:
    """List saved searches for current user."""
    try:
        # Mock data
        mock_searches = [
            SavedSearchResponse(
                id=1,
                name="Senior Developers",
                search_type="CANDIDATE",
                filters={"experience_min": 5, "skills": ["Python", "FastAPI"]},
                sort_by="experience",
                sort_order="desc",
                is_default=True,
                result_count=12,
                last_run_at=datetime.utcnow(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            SavedSearchResponse(
                id=2,
                name="Remote Cloud Engineers",
                search_type="CANDIDATE",
                filters={"location": "Remote", "skills": ["AWS", "Kubernetes"]},
                sort_by="match_score",
                sort_order="desc",
                is_default=False,
                result_count=8,
                last_run_at=datetime.utcnow(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            SavedSearchResponse(
                id=3,
                name="Tech Jobs",
                search_type="REQUIREMENT",
                filters={"client": "TechCorp Inc", "priority": "HIGH"},
                sort_by="created_at",
                sort_order="desc",
                is_default=False,
                result_count=5,
                last_run_at=datetime.utcnow(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
        ]

        return mock_searches

    except Exception as e:
        logger.error(f"Error listing saved searches: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/saved/{search_id}", response_model=SavedSearchResponse)
async def update_saved_search(
    search_id: int,
    search_update: SavedSearchUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
) -> SavedSearchResponse:
    """Update a saved search."""
    try:
        # Mock response
        return SavedSearchResponse(
            id=search_id,
            name=search_update.name or "Updated Search",
            search_type="CANDIDATE",
            filters=search_update.filters or {},
            sort_by=search_update.sort_by,
            sort_order=search_update.sort_order or "desc",
            is_default=search_update.is_default or False,
            result_count=0,
            last_run_at=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    except Exception as e:
        logger.error(f"Error updating saved search: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/saved/{search_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_saved_search(
    search_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Delete a saved search."""
    try:
        # Mock deletion
        return None

    except Exception as e:
        logger.error(f"Error deleting saved search: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/saved/{search_id}/run", response_model=CandidateSearchResponse)
async def run_saved_search(
    search_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
) -> CandidateSearchResponse:
    """Re-run a saved search."""
    try:
        # Mock response - return search results
        mock_candidates = [
            CandidateMatch(
                id=1,
                first_name="Alice",
                last_name="Johnson",
                email="alice.johnson@email.com",
                current_title="Senior Python Developer",
                location_city="San Francisco",
                location_country="USA",
                total_experience_years=8.5,
                match_score=95.0,
                matched_fields={"skills": "Python, Django"},
                status="READY_FOR_SUBMISSION"
            ),
        ]

        return CandidateSearchResponse(
            total=1,
            results=mock_candidates,
            filters_applied={"saved_search_id": search_id}
        )

    except Exception as e:
        logger.error(f"Error running saved search: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


logger.info("Search router initialized with 7 endpoints")
