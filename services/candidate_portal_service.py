import logging
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from models.candidate_portal import (
    CandidateProfile,
    CandidateVideo,
    ResumeBuilderData,
)
from schemas.candidate_portal import (
    CandidateProfileSchema,
    CandidateVideoSchema,
    ResumeBuilderDataSchema,
    CandidatePortalDashboardSchema,
)

logger = logging.getLogger(__name__)


class CandidatePortalService:
    """Service layer for candidate portal operations."""

    @staticmethod
    async def get_or_create_profile(
        db: AsyncSession, candidate_id: int
    ) -> CandidateProfileSchema:
        """Get or create candidate profile.

        Args:
            db: Database session
            candidate_id: ID of candidate

        Returns:
            CandidateProfileSchema

        Raises:
            Exception: If database error occurs
        """
        try:
            query = select(CandidateProfile).where(
                CandidateProfile.candidate_id == candidate_id
            )
            result = await db.execute(query)
            profile = result.scalars().first()

            if not profile:
                profile = CandidateProfile(
                    candidate_id=candidate_id,
                    is_public=True,
                    profile_completeness=0.0,
                )
                db.add(profile)
                await db.commit()

            return CandidateProfileSchema.from_orm(profile)

        except Exception as e:
            await db.rollback()
            logger.error(f"Error getting/creating profile: {str(e)}")
            raise

    @staticmethod
    async def update_profile(
        db: AsyncSession,
        candidate_id: int,
        profile_data: Dict[str, Any],
    ) -> CandidateProfileSchema:
        """Update candidate profile.

        Args:
            db: Database session
            candidate_id: ID of candidate
            profile_data: Profile update data

        Returns:
            Updated CandidateProfileSchema

        Raises:
            ValueError: If profile not found
        """
        try:
            query = select(CandidateProfile).where(
                CandidateProfile.candidate_id == candidate_id
            )
            result = await db.execute(query)
            profile = result.scalars().first()

            if not profile:
                raise ValueError(f"Profile for candidate {candidate_id} not found")

            for key, value in profile_data.items():
                if hasattr(profile, key) and value is not None:
                    setattr(profile, key, value)

            # Recalculate completeness
            profile.profile_completeness = CandidatePortalService._calculate_completeness(
                profile
            )

            await db.commit()
            logger.info(f"Updated profile for candidate {candidate_id}")

            return CandidateProfileSchema.from_orm(profile)

        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating profile: {str(e)}")
            raise

    @staticmethod
    async def create_resume(
        db: AsyncSession,
        candidate_id: int,
        resume_data: Dict[str, Any],
    ) -> ResumeBuilderDataSchema:
        """Create resume for candidate.

        Args:
            db: Database session
            candidate_id: ID of candidate
            resume_data: Resume data

        Returns:
            ResumeBuilderDataSchema

        Raises:
            Exception: If error occurs
        """
        try:
            resume = ResumeBuilderData(
                candidate_id=candidate_id,
                template_name=resume_data.get("template_name", "professional"),
                personal_info=resume_data.get("personal_info", {}),
                summary=resume_data.get("summary"),
                experience=resume_data.get("experience", []),
                education=resume_data.get("education", []),
                skills=resume_data.get("skills", {}),
                certifications=resume_data.get("certifications", []),
                projects=resume_data.get("projects", []),
                languages=resume_data.get("languages", []),
                custom_sections=resume_data.get("custom_sections", []),
            )

            db.add(resume)
            await db.commit()

            logger.info(f"Created resume {resume.id} for candidate {candidate_id}")

            return ResumeBuilderDataSchema.from_orm(resume)

        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating resume: {str(e)}")
            raise

    @staticmethod
    async def update_resume(
        db: AsyncSession,
        resume_id: int,
        resume_data: Dict[str, Any],
    ) -> ResumeBuilderDataSchema:
        """Update resume.

        Args:
            db: Database session
            resume_id: ID of resume
            resume_data: Resume update data

        Returns:
            Updated ResumeBuilderDataSchema

        Raises:
            ValueError: If resume not found
        """
        try:
            resume = await db.get(ResumeBuilderData, resume_id)
            if not resume:
                raise ValueError(f"Resume {resume_id} not found")

            for key, value in resume_data.items():
                if hasattr(resume, key) and value is not None and key != "version":
                    setattr(resume, key, value)

            resume.version += 1
            await db.commit()

            logger.info(f"Updated resume {resume_id}")

            return ResumeBuilderDataSchema.from_orm(resume)

        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating resume: {str(e)}")
            raise

    @staticmethod
    async def list_resumes(
        db: AsyncSession, candidate_id: int
    ) -> List[ResumeBuilderDataSchema]:
        """List resumes for candidate.

        Args:
            db: Database session
            candidate_id: ID of candidate

        Returns:
            List of resumes

        Raises:
            Exception: If database error occurs
        """
        try:
            query = select(ResumeBuilderData).where(
                ResumeBuilderData.candidate_id == candidate_id
            ).order_by(ResumeBuilderData.created_at.desc())

            result = await db.execute(query)
            resumes = result.scalars().all()

            return [ResumeBuilderDataSchema.from_orm(r) for r in resumes]

        except Exception as e:
            logger.error(f"Error listing resumes: {str(e)}")
            raise

    @staticmethod
    async def upload_video(
        db: AsyncSession,
        candidate_id: int,
        video_data: Dict[str, Any],
    ) -> CandidateVideoSchema:
        """Upload video for candidate.

        Args:
            db: Database session
            candidate_id: ID of candidate
            video_data: Video data

        Returns:
            CandidateVideoSchema

        Raises:
            ValueError: If validation fails
        """
        try:
            # Check active video count
            query = select(CandidateVideo).where(
                and_(
                    CandidateVideo.candidate_id == candidate_id,
                    CandidateVideo.is_active == True,
                )
            )
            result = await db.execute(query)
            active_videos = result.scalars().all()

            if len(active_videos) >= 3:
                raise ValueError("Maximum 3 active videos per candidate")

            video = CandidateVideo(
                candidate_id=candidate_id,
                title=video_data.get("title"),
                description=video_data.get("description"),
                video_url=video_data.get("video_url"),
                storage_path=video_data.get("storage_path"),
                thumbnail_url=video_data.get("thumbnail_url"),
                duration_seconds=video_data.get("duration_seconds", 0),
                file_size_bytes=video_data.get("file_size_bytes"),
                video_type=video_data.get("video_type", "intro"),
                is_active=True,
            )

            db.add(video)
            await db.commit()

            logger.info(f"Uploaded video {video.id} for candidate {candidate_id}")

            return CandidateVideoSchema.from_orm(video)

        except Exception as e:
            await db.rollback()
            logger.error(f"Error uploading video: {str(e)}")
            raise

    @staticmethod
    async def get_video(db: AsyncSession, video_id: int) -> Optional[CandidateVideoSchema]:
        """Get video by ID.

        Args:
            db: Database session
            video_id: ID of video

        Returns:
            CandidateVideoSchema or None

        Raises:
            Exception: If database error occurs
        """
        try:
            video = await db.get(CandidateVideo, video_id)
            if not video:
                return None

            return CandidateVideoSchema.from_orm(video)

        except Exception as e:
            logger.error(f"Error getting video: {str(e)}")
            raise

    @staticmethod
    async def list_videos(
        db: AsyncSession, candidate_id: int, active_only: bool = True
    ) -> List[CandidateVideoSchema]:
        """List videos for candidate.

        Args:
            db: Database session
            candidate_id: ID of candidate
            active_only: Only return active videos

        Returns:
            List of videos

        Raises:
            Exception: If database error occurs
        """
        try:
            filters = [CandidateVideo.candidate_id == candidate_id]
            if active_only:
                filters.append(CandidateVideo.is_active == True)

            query = select(CandidateVideo).where(and_(*filters)).order_by(
                CandidateVideo.uploaded_at.desc()
            )

            result = await db.execute(query)
            videos = result.scalars().all()

            return [CandidateVideoSchema.from_orm(v) for v in videos]

        except Exception as e:
            logger.error(f"Error listing videos: {str(e)}")
            raise

    @staticmethod
    async def delete_video(db: AsyncSession, video_id: int) -> None:
        """Soft delete video.

        Args:
            db: Database session
            video_id: ID of video

        Raises:
            ValueError: If video not found
        """
        try:
            video = await db.get(CandidateVideo, video_id)
            if not video:
                raise ValueError(f"Video {video_id} not found")

            video.is_active = False
            await db.commit()

            logger.info(f"Deactivated video {video_id}")

        except Exception as e:
            await db.rollback()
            logger.error(f"Error deleting video: {str(e)}")
            raise

    @staticmethod
    async def increment_video_views(db: AsyncSession, video_id: int) -> None:
        """Increment video view count.

        Args:
            db: Database session
            video_id: ID of video

        Raises:
            ValueError: If video not found
        """
        try:
            video = await db.get(CandidateVideo, video_id)
            if not video:
                raise ValueError(f"Video {video_id} not found")

            video.view_count += 1
            await db.commit()

        except Exception as e:
            await db.rollback()
            logger.error(f"Error incrementing video views: {str(e)}")
            raise

    @staticmethod
    async def get_portal_dashboard(
        db: AsyncSession, candidate_id: int
    ) -> Dict[str, Any]:
        """Get complete portal dashboard.

        Args:
            db: Database session
            candidate_id: ID of candidate

        Returns:
            Dashboard dictionary

        Raises:
            Exception: If error occurs
        """
        try:
            # Get profile
            profile_query = select(CandidateProfile).where(
                CandidateProfile.candidate_id == candidate_id
            )
            profile_result = await db.execute(profile_query)
            profile = profile_result.scalars().first()

            # Get resumes
            resume_query = select(ResumeBuilderData).where(
                ResumeBuilderData.candidate_id == candidate_id
            ).order_by(ResumeBuilderData.created_at.desc())
            resume_result = await db.execute(resume_query)
            resumes = resume_result.scalars().all()

            # Get videos
            video_query = select(CandidateVideo).where(
                and_(
                    CandidateVideo.candidate_id == candidate_id,
                    CandidateVideo.is_active == True,
                )
            ).order_by(CandidateVideo.uploaded_at.desc())
            video_result = await db.execute(video_query)
            videos = video_result.scalars().all()

            dashboard = {
                "profile": CandidateProfileSchema.from_orm(profile) if profile else None,
                "resumes": [ResumeBuilderDataSchema.from_orm(r) for r in resumes],
                "videos": [CandidateVideoSchema.from_orm(v) for v in videos],
                "profile_completeness": profile.profile_completeness if profile else 0,
                "resume_count": len(resumes),
                "video_count": len(videos),
            }

            return dashboard

        except Exception as e:
            logger.error(f"Error getting portal dashboard: {str(e)}")
            raise

    @staticmethod
    def _calculate_completeness(profile: CandidateProfile) -> float:
        """Calculate profile completeness percentage."""
        fields = [
            profile.headline,
            profile.bio,
            profile.portfolio_url,
            profile.github_url,
            profile.linkedin_url,
            profile.desired_roles,
            profile.availability_status,
        ]

        completed = sum(1 for field in fields if field)
        return round((completed / len(fields) * 100), 2)
