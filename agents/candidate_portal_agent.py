import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from agents.base_agent import BaseAgent
from models.candidate_portal import (
    CandidateProfile,
    CandidateVideo,
    ResumeBuilderData,
)

logger = logging.getLogger(__name__)


class CandidatePortalAgent(BaseAgent):
    """Manages candidate self-service portal features including profiles, resumes, and videos."""

    def __init__(self):
        """Initialize candidate portal agent."""
        super().__init__("CandidatePortalAgent", "1.0.0")
        self.max_videos_per_candidate = 3
        self.max_video_duration_seconds = 15 * 60  # 15 minutes

    async def create_candidate_profile(
        self, db: AsyncSession, candidate_id: int, profile_data: Dict[str, Any]
    ) -> CandidateProfile:
        """Create or update candidate's public-facing profile.

        Args:
            db: Database session
            candidate_id: ID of candidate
            profile_data: Profile data dictionary

        Returns:
            Created/updated CandidateProfile

        Raises:
            ValueError: If candidate doesn't exist
        """
        try:
            # Check if profile exists
            query = select(CandidateProfile).where(
                CandidateProfile.candidate_id == candidate_id
            )
            result = await db.execute(query)
            profile = result.scalars().first()

            if profile:
                # Update existing profile
                for key, value in profile_data.items():
                    if hasattr(profile, key):
                        setattr(profile, key, value)
            else:
                # Create new profile
                profile = CandidateProfile(candidate_id=candidate_id, **profile_data)
                db.add(profile)

            # Calculate profile completeness
            profile.profile_completeness = self._calculate_profile_completeness(profile)
            profile.is_public = profile_data.get("is_public", True)

            await db.commit()
            logger.info(f"Created/updated profile for candidate {candidate_id}")

            await self.emit_event(
                event_type="candidate_profile_created",
                entity_type="candidate",
                entity_id=candidate_id,
                payload={"profile_completeness": profile.profile_completeness},
            )

            return profile

        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating candidate profile: {str(e)}")
            raise

    async def build_resume(
        self, db: AsyncSession, candidate_id: int, resume_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build professionally formatted resume from structured data.

        Args:
            db: Database session
            candidate_id: ID of candidate
            resume_data: Structured resume data

        Returns:
            Dictionary with resume info and generated file paths

        Raises:
            ValueError: If candidate or data invalid
        """
        try:
            # Check if resume exists
            query = select(ResumeBuilderData).where(
                ResumeBuilderData.candidate_id == candidate_id
            )
            result = await db.execute(query)
            resume = result.scalars().first()

            if resume:
                # Update existing resume
                for key, value in resume_data.items():
                    if hasattr(resume, key) and key != "version":
                        setattr(resume, key, value)
                resume.version += 1
            else:
                # Create new resume
                resume = ResumeBuilderData(
                    candidate_id=candidate_id,
                    template_name=resume_data.get("template_name", "professional"),
                    **resume_data,
                )
                db.add(resume)

            await db.flush()

            # Generate PDF and DOCX
            try:
                resume.generated_pdf_path = await self._generate_pdf(resume)
                resume.generated_docx_path = await self._generate_docx(resume)
                resume.last_generated_at = datetime.utcnow()
            except Exception as e:
                logger.warning(f"Could not generate resume files: {str(e)}")

            await db.commit()
            logger.info(f"Built resume for candidate {candidate_id}")

            await self.emit_event(
                event_type="resume_built",
                entity_type="candidate",
                entity_id=candidate_id,
                payload={
                    "version": resume.version,
                    "pdf_path": resume.generated_pdf_path,
                    "docx_path": resume.generated_docx_path,
                },
            )

            return {
                "resume_id": resume.id,
                "version": resume.version,
                "pdf_path": resume.generated_pdf_path,
                "docx_path": resume.generated_docx_path,
                "generated_at": resume.last_generated_at.isoformat(),
            }

        except Exception as e:
            await db.rollback()
            logger.error(f"Error building resume: {str(e)}")
            raise

    async def enhance_resume_section(
        self,
        db: AsyncSession,
        candidate_id: int,
        section_type: str,
        content: str,
        target_role: Optional[str] = None,
    ) -> str:
        """Use AI to improve a resume section.

        Args:
            db: Database session
            candidate_id: ID of candidate
            section_type: Type of section (summary, experience_bullet, etc)
            content: Original content
            target_role: Optional target role for context

        Returns:
            Enhanced content

        Raises:
            Exception: If enhancement fails
        """
        try:
            try:
                from anthropic import Anthropic

                client = Anthropic()

                prompt = f"""You are a professional resume writer and career coach.
Enhance the following resume section to make it more impactful and compelling.
Keep it concise but professional.

Section Type: {section_type}
Original Content: {content}
{"Target Role: " + target_role if target_role else ""}

Provide only the enhanced content without any explanation."""

                message = client.messages.create(
                    model="claude-opus-4-6",
                    max_tokens=1024,
                    messages=[{"role": "user", "content": prompt}],
                )

                enhanced = message.content[0].text.strip()

                logger.info(
                    f"Enhanced {section_type} section for candidate {candidate_id}"
                )
                return enhanced

            except ImportError:
                logger.warning("Anthropic SDK not available, returning original content")
                return content

        except Exception as e:
            logger.error(f"Error enhancing resume section: {str(e)}")
            raise

    async def upload_video_intro(
        self,
        db: AsyncSession,
        candidate_id: int,
        video_data: Dict[str, Any],
    ) -> CandidateVideo:
        """Upload video introduction for candidate.

        Args:
            db: Database session
            candidate_id: ID of candidate
            video_data: Video metadata and file info

        Returns:
            Created CandidateVideo

        Raises:
            ValueError: If validation fails
        """
        try:
            # Validate video count
            query = select(CandidateVideo).where(
                and_(
                    CandidateVideo.candidate_id == candidate_id,
                    CandidateVideo.is_active == True,
                )
            )
            result = await db.execute(query)
            existing_videos = result.scalars().all()

            if len(existing_videos) >= self.max_videos_per_candidate:
                raise ValueError(
                    f"Maximum {self.max_videos_per_candidate} active videos per candidate"
                )

            # Validate duration
            duration = video_data.get("duration_seconds", 0)
            if duration > self.max_video_duration_seconds:
                raise ValueError(
                    f"Video exceeds maximum duration of {self.max_video_duration_seconds} seconds"
                )

            # Create video record
            video = CandidateVideo(
                candidate_id=candidate_id,
                title=video_data.get("title"),
                description=video_data.get("description"),
                video_url=video_data.get("video_url"),
                storage_path=video_data.get("storage_path"),
                thumbnail_url=video_data.get("thumbnail_url"),
                duration_seconds=duration,
                file_size_bytes=video_data.get("file_size_bytes"),
                video_type=video_data.get("video_type", "intro"),
                is_active=True,
            )

            db.add(video)
            await db.flush()

            # Transcribe and summarize if available
            if video.video_url:
                try:
                    video.transcript = await self._transcribe_video(video.video_url)
                    if video.transcript:
                        video.ai_summary = await self._generate_video_summary(
                            video.transcript
                        )
                        video.skills_mentioned = (
                            await self._extract_skills_from_transcript(
                                video.transcript
                            )
                        )
                except Exception as e:
                    logger.warning(f"Could not transcribe video: {str(e)}")

            await db.commit()
            logger.info(f"Uploaded video {video.id} for candidate {candidate_id}")

            await self.emit_event(
                event_type="video_uploaded",
                entity_type="candidate",
                entity_id=candidate_id,
                payload={
                    "video_id": video.id,
                    "duration": duration,
                    "type": video.video_type,
                },
            )

            return video

        except Exception as e:
            await db.rollback()
            logger.error(f"Error uploading video: {str(e)}")
            raise

    async def transcribe_video(
        self, db: AsyncSession, video_id: int
    ) -> str:
        """Transcribe video intro using speech-to-text.

        Args:
            db: Database session
            video_id: ID of video

        Returns:
            Transcription text

        Raises:
            ValueError: If video not found
        """
        try:
            video = await db.get(CandidateVideo, video_id)
            if not video:
                raise ValueError(f"Video {video_id} not found")

            if video.transcript:
                return video.transcript

            transcript = await self._transcribe_video(video.video_url)
            video.transcript = transcript

            await db.commit()
            logger.info(f"Transcribed video {video_id}")

            return transcript

        except Exception as e:
            logger.error(f"Error transcribing video: {str(e)}")
            raise

    async def generate_video_summary(
        self, db: AsyncSession, video_id: int
    ) -> str:
        """Generate AI summary of video.

        Args:
            db: Database session
            video_id: ID of video

        Returns:
            AI-generated summary

        Raises:
            ValueError: If video not found
        """
        try:
            video = await db.get(CandidateVideo, video_id)
            if not video:
                raise ValueError(f"Video {video_id} not found")

            if video.ai_summary:
                return video.ai_summary

            if not video.transcript:
                transcript = await self._transcribe_video(video.video_url)
                video.transcript = transcript

            summary = await self._generate_video_summary(video.transcript)
            video.ai_summary = summary

            await db.commit()
            logger.info(f"Generated summary for video {video_id}")

            return summary

        except Exception as e:
            logger.error(f"Error generating video summary: {str(e)}")
            raise

    async def create_submission_package(
        self,
        db: AsyncSession,
        candidate_id: int,
        requirement_id: int,
    ) -> Dict[str, Any]:
        """Create complete submission package for requirement.

        Args:
            db: Database session
            candidate_id: ID of candidate
            requirement_id: ID of requirement

        Returns:
            Submission package dictionary

        Raises:
            ValueError: If candidate or requirement not found
        """
        try:
            # Fetch candidate profile
            query = select(CandidateProfile).where(
                CandidateProfile.candidate_id == candidate_id
            )
            result = await db.execute(query)
            profile = result.scalars().first()

            # Fetch latest resume
            resume_query = select(ResumeBuilderData).where(
                ResumeBuilderData.candidate_id == candidate_id
            )
            resume_result = await db.execute(resume_query)
            resume = resume_result.scalars().first()

            # Fetch videos
            videos_query = select(CandidateVideo).where(
                and_(
                    CandidateVideo.candidate_id == candidate_id,
                    CandidateVideo.is_active == True,
                )
            )
            videos_result = await db.execute(videos_query)
            videos = videos_result.scalars().all()

            # Calculate match score
            match_score = await self._calculate_match_score(
                db, candidate_id, requirement_id
            )

            package = {
                "candidate_id": candidate_id,
                "requirement_id": requirement_id,
                "profile": profile,
                "resume": resume,
                "videos": videos,
                "match_score": match_score,
                "created_at": datetime.utcnow().isoformat(),
            }

            logger.info(
                f"Created submission package for candidate {candidate_id} to requirement {requirement_id}"
            )

            await self.emit_event(
                event_type="submission_package_created",
                entity_type="candidate",
                entity_id=candidate_id,
                payload={
                    "requirement_id": requirement_id,
                    "match_score": match_score,
                },
            )

            return package

        except Exception as e:
            logger.error(f"Error creating submission package: {str(e)}")
            raise

    async def get_candidate_portal_data(
        self, db: AsyncSession, candidate_id: int
    ) -> Dict[str, Any]:
        """Get all portal data for candidate dashboard.

        Args:
            db: Database session
            candidate_id: ID of candidate

        Returns:
            Dashboard data dictionary

        Raises:
            ValueError: If candidate not found
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
            )
            resume_result = await db.execute(resume_query)
            resumes = resume_result.scalars().all()

            # Get videos
            video_query = select(CandidateVideo).where(
                CandidateVideo.candidate_id == candidate_id
            )
            video_result = await db.execute(video_query)
            videos = video_result.scalars().all()

            portal_data = {
                "candidate_id": candidate_id,
                "profile": profile,
                "resumes": resumes,
                "videos": videos,
                "profile_completeness": profile.profile_completeness if profile else 0,
                "resume_count": len(resumes),
                "video_count": len(videos),
            }

            logger.info(f"Retrieved portal data for candidate {candidate_id}")
            return portal_data

        except Exception as e:
            logger.error(f"Error getting portal data: {str(e)}")
            raise

    async def update_availability(
        self,
        db: AsyncSession,
        candidate_id: int,
        availability_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update candidate's availability and rate preferences.

        Args:
            db: Database session
            candidate_id: ID of candidate
            availability_data: Availability update data

        Returns:
            Updated availability data

        Raises:
            ValueError: If candidate not found
        """
        try:
            # Get profile
            query = select(CandidateProfile).where(
                CandidateProfile.candidate_id == candidate_id
            )
            result = await db.execute(query)
            profile = result.scalars().first()

            if not profile:
                # Create new profile with availability
                profile = CandidateProfile(
                    candidate_id=candidate_id,
                    **availability_data,
                )
                db.add(profile)
            else:
                # Update existing profile
                for key, value in availability_data.items():
                    if hasattr(profile, key):
                        setattr(profile, key, value)

            await db.commit()
            logger.info(f"Updated availability for candidate {candidate_id}")

            await self.emit_event(
                event_type="candidate_availability_updated",
                entity_type="candidate",
                entity_id=candidate_id,
                payload=availability_data,
            )

            return {
                "candidate_id": candidate_id,
                "availability_status": profile.availability_status,
                "desired_rate_min": profile.desired_rate_min,
                "desired_rate_max": profile.desired_rate_max,
            }

        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating availability: {str(e)}")
            raise

    # Helper methods

    def _calculate_profile_completeness(self, profile: CandidateProfile) -> float:
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

    async def _generate_pdf(self, resume: ResumeBuilderData) -> str:
        """Generate PDF from resume data."""
        # Placeholder: would use ReportLab or similar
        return f"/files/resumes/{resume.candidate_id}_{uuid.uuid4()}.pdf"

    async def _generate_docx(self, resume: ResumeBuilderData) -> str:
        """Generate DOCX from resume data."""
        # Placeholder: would use python-docx
        return f"/files/resumes/{resume.candidate_id}_{uuid.uuid4()}.docx"

    async def _transcribe_video(self, video_url: str) -> Optional[str]:
        """Transcribe video using speech-to-text API."""
        try:
            from anthropic import Anthropic

            client = Anthropic()
            # In real implementation, would fetch and process video file
            # For now, return placeholder
            logger.warning("Video transcription not fully implemented")
            return None

        except ImportError:
            logger.warning("Anthropic SDK not available for transcription")
            return None

    async def _generate_video_summary(self, transcript: str) -> str:
        """Generate summary from video transcript."""
        try:
            from anthropic import Anthropic

            client = Anthropic()

            prompt = f"""Summarize the following video introduction in 2-3 sentences,
highlighting key skills and experience:

{transcript}"""

            message = client.messages.create(
                model="claude-opus-4-6",
                max_tokens=256,
                messages=[{"role": "user", "content": prompt}],
            )

            return message.content[0].text.strip()

        except Exception as e:
            logger.warning(f"Could not generate video summary: {str(e)}")
            return None

    async def _extract_skills_from_transcript(
        self, transcript: str
    ) -> List[str]:
        """Extract mentioned skills from transcript."""
        try:
            from anthropic import Anthropic

            client = Anthropic()

            prompt = f"""Extract all technical and professional skills mentioned in this text.
Return as a comma-separated list only:

{transcript}"""

            message = client.messages.create(
                model="claude-opus-4-6",
                max_tokens=256,
                messages=[{"role": "user", "content": prompt}],
            )

            skills_text = message.content[0].text.strip()
            return [s.strip() for s in skills_text.split(",")]

        except Exception as e:
            logger.warning(f"Could not extract skills: {str(e)}")
            return []

    async def _calculate_match_score(
        self, db: AsyncSession, candidate_id: int, requirement_id: int
    ) -> float:
        """Calculate match score between candidate and requirement."""
        # Placeholder: would implement full matching algorithm
        return 75.0
