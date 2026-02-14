import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db, get_current_user
from agents.candidate_portal_agent import CandidatePortalAgent
from services.candidate_portal_service import CandidatePortalService
from schemas.candidate_portal import (
    CandidateProfileSchema,
    CandidateProfileCreateSchema,
    CandidateProfileUpdateSchema,
    CandidateVideoSchema,
    CandidateVideoCreateSchema,
    ResumeBuilderDataSchema,
    ResumeBuilderDataCreateSchema,
    ResumeEnhancementSchema,
    AvailabilityUpdateSchema,
    CandidatePortalDashboardSchema,
    SubmissionPackageSchema,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/portal", tags=["candidate_portal"])
agent = CandidatePortalAgent()


@router.get("/profile", response_model=CandidateProfileSchema)
async def get_profile(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> CandidateProfileSchema:
    """Get candidate's own profile."""
    try:
        candidate_id = current_user.get("candidate_id")
        if not candidate_id:
            raise HTTPException(status_code=403, detail="Not a candidate account")

        profile = await CandidatePortalService.get_or_create_profile(db, candidate_id)
        return profile
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/profile", response_model=CandidateProfileSchema)
async def update_profile(
    profile_data: CandidateProfileUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> CandidateProfileSchema:
    """Update candidate profile."""
    try:
        candidate_id = current_user.get("candidate_id")
        if not candidate_id:
            raise HTTPException(status_code=403, detail="Not a candidate account")

        profile = await CandidatePortalService.update_profile(
            db, candidate_id, profile_data.dict(exclude_unset=True)
        )
        return profile
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/resume/build", response_model=ResumeBuilderDataSchema, status_code=201)
async def build_resume(
    resume_data: ResumeBuilderDataCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> ResumeBuilderDataSchema:
    """Build resume from structured data."""
    try:
        candidate_id = current_user.get("candidate_id")
        if not candidate_id:
            raise HTTPException(status_code=403, detail="Not a candidate account")

        result = await agent.build_resume(db, candidate_id, resume_data.dict())
        return ResumeBuilderDataSchema(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error building resume: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/resume", response_model=List[ResumeBuilderDataSchema])
async def list_resumes(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> List[ResumeBuilderDataSchema]:
    """List candidate's resumes."""
    try:
        candidate_id = current_user.get("candidate_id")
        if not candidate_id:
            raise HTTPException(status_code=403, detail="Not a candidate account")

        resumes = await CandidatePortalService.list_resumes(db, candidate_id)
        return resumes
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing resumes: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/resume/enhance-section", response_model=dict)
async def enhance_resume_section(
    enhancement: ResumeEnhancementSchema,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict:
    """AI-enhance a resume section."""
    try:
        candidate_id = current_user.get("candidate_id")
        if not candidate_id:
            raise HTTPException(status_code=403, detail="Not a candidate account")

        enhanced = await agent.enhance_resume_section(
            db,
            candidate_id,
            enhancement.section_type,
            enhancement.content,
            enhancement.target_role,
        )

        return {"original": enhancement.content, "enhanced": enhanced}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enhancing section: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/resume/{resume_id}/download")
async def download_resume(
    resume_id: int,
    format: str = Query("pdf", pattern="^(pdf|docx)$"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Download resume in specified format."""
    try:
        # Placeholder: would stream file from storage
        return {"status": "download_ready", "format": format}
    except Exception as e:
        logger.error(f"Error downloading resume: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/videos", response_model=CandidateVideoSchema, status_code=201)
async def upload_video(
    title: str = Query(..., min_length=1),
    description: Optional[str] = None,
    video_type: str = Query(..., min_length=1),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> CandidateVideoSchema:
    """Upload video introduction."""
    try:
        candidate_id = current_user.get("candidate_id")
        if not candidate_id:
            raise HTTPException(status_code=403, detail="Not a candidate account")

        # Placeholder: would handle file upload to S3
        video_data = {
            "title": title,
            "description": description,
            "video_type": video_type,
            "video_url": f"s3://bucket/videos/{candidate_id}/{file.filename}",
            "duration_seconds": 0,  # Would be calculated
        }

        video = await agent.upload_video_intro(db, candidate_id, video_data)
        return CandidateVideoSchema.from_orm(video)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error uploading video: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/videos", response_model=List[CandidateVideoSchema])
async def list_videos(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> List[CandidateVideoSchema]:
    """List candidate's videos."""
    try:
        candidate_id = current_user.get("candidate_id")
        if not candidate_id:
            raise HTTPException(status_code=403, detail="Not a candidate account")

        videos = await CandidatePortalService.list_videos(db, candidate_id)
        return videos
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing videos: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/videos/{video_id}")
async def delete_video(
    video_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Delete a video."""
    try:
        await CandidatePortalService.delete_video(db, video_id)
        return {"status": "deleted", "video_id": video_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting video: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/videos/{video_id}/summary", response_model=dict)
async def get_video_summary(
    video_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Get AI summary of video."""
    try:
        summary = await agent.generate_video_summary(db, video_id)
        return {"video_id": video_id, "summary": summary}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting video summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/applications", response_model=List[dict])
async def get_applications(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> List[dict]:
    """Get candidate's applications."""
    try:
        candidate_id = current_user.get("candidate_id")
        if not candidate_id:
            raise HTTPException(status_code=403, detail="Not a candidate account")

        # Placeholder: would fetch from submissions table
        return []
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting applications: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/availability", response_model=dict)
async def update_availability(
    availability: AvailabilityUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Update candidate availability."""
    try:
        candidate_id = current_user.get("candidate_id")
        if not candidate_id:
            raise HTTPException(status_code=403, detail="Not a candidate account")

        result = await agent.update_availability(db, candidate_id, availability.dict())
        return result
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating availability: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/submit/{requirement_id}", response_model=SubmissionPackageSchema, status_code=201)
async def submit_for_requirement(
    requirement_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> SubmissionPackageSchema:
    """Submit profile and materials for requirement."""
    try:
        candidate_id = current_user.get("candidate_id")
        if not candidate_id:
            raise HTTPException(status_code=403, detail="Not a candidate account")

        package = await agent.create_submission_package(db, candidate_id, requirement_id)
        return package
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error submitting for requirement: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/dashboard", response_model=CandidatePortalDashboardSchema)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> CandidatePortalDashboardSchema:
    """Get candidate dashboard."""
    try:
        candidate_id = current_user.get("candidate_id")
        if not candidate_id:
            raise HTTPException(status_code=403, detail="Not a candidate account")

        dashboard = await CandidatePortalService.get_portal_dashboard(db, candidate_id)
        return dashboard
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
