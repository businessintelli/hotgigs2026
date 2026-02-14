import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Query
from pydantic import BaseModel, Field
from datetime import datetime
from pathlib import Path
import shutil
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from services.resume_service import ResumeService
from agents.resume_parser_agent import ResumeParserAgent
from agents.resume_tailoring_agent import ResumeTailoringAgent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resumes", tags=["resumes"])

# Initialize service
parser_agent = ResumeParserAgent()
tailoring_agent = ResumeTailoringAgent()
resume_service = ResumeService(parser_agent, tailoring_agent)


# Pydantic models
class ResumeUploadResponse(BaseModel):
    """Resume upload response."""

    id: int
    candidate_id: int
    file_name: str
    file_type: str
    file_size: int
    is_primary: bool
    uploaded_at: str


class ResumeParseResponse(BaseModel):
    """Resume parsing response."""

    resume_id: int
    parsed_resume_id: int
    parsing_confidence: float
    extraction_stats: Dict[str, int]
    parsed_at: str


class ParsedResumeData(BaseModel):
    """Parsed resume data."""

    id: int
    resume_id: int
    parsed_data: Dict[str, Any]
    skills_extracted: List[Dict[str, Any]]
    experience_extracted: List[Dict[str, Any]]
    education_extracted: List[Dict[str, Any]]
    certifications_extracted: List[Dict[str, Any]]
    parsing_confidence: float
    parser_version: str
    parsed_at: str


class ATSScoreResponse(BaseModel):
    """ATS compatibility score response."""

    resume_id: int
    overall_score: float
    max_score: int
    components: Dict[str, float]
    recommendations: List[str]


class TailoredResumeResponse(BaseModel):
    """Tailored resume response."""

    resume_id: int
    requirement_id: int
    requirement_title: str
    tailored_resume: Optional[str]
    tailoring_analysis: Optional[str]
    keywords_emphasized: Optional[str]
    gap_analysis: Dict[str, Any]
    ats_scores: Dict[str, float]
    ats_recommendations: List[str]
    generated_at: str


class ResumeSummaryResponse(BaseModel):
    """Resume summary response."""

    id: int
    candidate_id: int
    file_name: str
    file_type: str
    file_size: int
    is_primary: bool
    uploaded_at: str


class SkillSearchResponse(BaseModel):
    """Skill search response."""

    resume_id: int
    candidate_id: int
    matched_skills: List[str]
    all_skills: List[str]


@router.post(
    "/upload",
    response_model=ResumeUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload resume file",
    description="Upload a resume file (PDF or DOCX) for a candidate.",
)
async def upload_resume(
    candidate_id: int = Query(..., ge=1),
    file: UploadFile = File(...),
    is_primary: bool = Query(True),
    session: AsyncSession = Depends(get_db),
) -> ResumeUploadResponse:
    """
    Upload resume file for a candidate.

    Args:
        candidate_id: Candidate ID
        file: Resume file (PDF or DOCX)
        is_primary: Whether this is the primary resume
        session: Database session

    Returns:
        Uploaded resume details
    """
    try:
        # Validate file type
        allowed_types = {".pdf", ".docx", ".doc"}
        file_ext = Path(file.filename).suffix.lower()

        if file_ext not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file_ext} not supported. Allowed: {allowed_types}",
            )

        # Save file
        file_path = resume_service.upload_dir / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        file_size = len(content)

        # Store in database
        result = await resume_service.upload_resume(
            session,
            candidate_id,
            str(file_path),
            file.filename,
            file_size,
            is_primary,
        )

        await session.commit()

        return ResumeUploadResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading resume: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/{resume_id}/parse",
    response_model=ResumeParseResponse,
    status_code=status.HTTP_200_OK,
    summary="Parse resume file",
    description="Parse a resume file to extract structured information.",
)
async def parse_resume(
    resume_id: int,
    session: AsyncSession = Depends(get_db),
) -> ResumeParseResponse:
    """
    Parse resume and extract structured data.

    Args:
        resume_id: Resume ID
        session: Database session

    Returns:
        Parsing results and statistics
    """
    try:
        result = await resume_service.parse_resume(session, resume_id)

        return ResumeParseResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error parsing resume: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/{resume_id}/parsed",
    response_model=ParsedResumeData,
    status_code=status.HTTP_200_OK,
    summary="Get parsed resume data",
    description="Get structured data from a parsed resume.",
)
async def get_parsed_resume(
    resume_id: int,
    session: AsyncSession = Depends(get_db),
) -> ParsedResumeData:
    """
    Get parsed resume data.

    Args:
        resume_id: Resume ID
        session: Database session

    Returns:
        Parsed resume data with all extracted information
    """
    try:
        result = await resume_service.get_parsed_resume(session, resume_id)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parsed resume not found",
            )

        return ParsedResumeData(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting parsed resume: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/{resume_id}/tailor",
    response_model=TailoredResumeResponse,
    status_code=status.HTTP_200_OK,
    summary="Tailor resume for requirement",
    description="Generate a tailored version of resume for a specific job requirement.",
)
async def tailor_resume(
    resume_id: int,
    requirement_id: int = Query(..., ge=1),
    session: AsyncSession = Depends(get_db),
) -> TailoredResumeResponse:
    """
    Tailor resume for a specific job requirement.

    Args:
        resume_id: Resume ID
        requirement_id: Job requirement ID
        session: Database session

    Returns:
        Tailored resume and analysis
    """
    try:
        result = await resume_service.tailor_resume(session, resume_id, requirement_id)

        return TailoredResumeResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error tailoring resume: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/{resume_id}/ats-score",
    response_model=ATSScoreResponse,
    status_code=status.HTTP_200_OK,
    summary="Get ATS compatibility score",
    description="Get ATS (Applicant Tracking System) compatibility score for a resume.",
)
async def get_ats_score(
    resume_id: int,
    session: AsyncSession = Depends(get_db),
) -> ATSScoreResponse:
    """
    Get ATS compatibility score for a resume.

    Args:
        resume_id: Resume ID
        session: Database session

    Returns:
        ATS score with component breakdown and recommendations
    """
    try:
        result = await resume_service.get_ats_score(session, resume_id)

        return ATSScoreResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error getting ATS score: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/search",
    response_model=List[SkillSearchResponse],
    status_code=status.HTTP_200_OK,
    summary="Search resumes by skills",
    description="Search for resumes containing specific skills.",
)
async def search_resumes_by_skills(
    skills: List[str] = Query(..., description="Skills to search for"),
    match_all: bool = Query(False, description="Require all skills or any skill"),
    session: AsyncSession = Depends(get_db),
) -> List[SkillSearchResponse]:
    """
    Search resumes by skills.

    Args:
        skills: List of skills to search for
        match_all: If True, require all skills; if False, any skill match
        session: Database session

    Returns:
        List of matching resumes
    """
    try:
        results = await resume_service.search_resumes_by_skills(session, skills, match_all)

        return [SkillSearchResponse(**r) for r in results]

    except Exception as e:
        logger.error(f"Error searching resumes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/candidate/{candidate_id}",
    response_model=List[ResumeSummaryResponse],
    status_code=status.HTTP_200_OK,
    summary="Get candidate resumes",
    description="Get all resumes uploaded by a candidate.",
)
async def get_candidate_resumes(
    candidate_id: int,
    session: AsyncSession = Depends(get_db),
) -> List[ResumeSummaryResponse]:
    """
    Get all resumes for a candidate.

    Args:
        candidate_id: Candidate ID
        session: Database session

    Returns:
        List of candidate's resumes
    """
    try:
        results = await resume_service.get_candidate_resumes(session, candidate_id)

        return [ResumeSummaryResponse(**r) for r in results]

    except Exception as e:
        logger.error(f"Error getting candidate resumes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.delete(
    "/{resume_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete resume",
    description="Delete a resume file and its parsed data.",
)
async def delete_resume(
    resume_id: int,
    session: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete a resume and its parsed data.

    Args:
        resume_id: Resume ID
        session: Database session
    """
    try:
        await resume_service.delete_resume(session, resume_id)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error deleting resume: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
