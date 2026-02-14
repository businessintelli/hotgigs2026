import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import shutil
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from models.resume import Resume, ParsedResume
from models.candidate import Candidate
from agents.resume_parser_agent import ResumeParserAgent
from agents.resume_tailoring_agent import ResumeTailoringAgent
from config import settings

logger = logging.getLogger(__name__)


class ResumeService:
    """Service layer for resume management and processing."""

    def __init__(
        self,
        parser_agent: Optional[ResumeParserAgent] = None,
        tailoring_agent: Optional[ResumeTailoringAgent] = None,
        upload_dir: str = "/tmp/resumes",
    ):
        """Initialize resume service.

        Args:
            parser_agent: Optional pre-initialized parser agent
            tailoring_agent: Optional pre-initialized tailoring agent
            upload_dir: Directory for storing uploaded resumes
        """
        self.parser = parser_agent or ResumeParserAgent()
        self.tailor = tailoring_agent or ResumeTailoringAgent()
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def upload_resume(
        self,
        session: AsyncSession,
        candidate_id: int,
        file_path: str,
        file_name: str,
        file_size: int,
        is_primary: bool = True,
    ) -> Dict[str, Any]:
        """
        Upload resume file and store in database.

        Args:
            session: Database session
            candidate_id: Candidate ID
            file_path: Path to uploaded file
            file_name: Original file name
            file_size: File size in bytes
            is_primary: Whether this is primary resume

        Returns:
            Resume record details
        """
        try:
            logger.info(f"Uploading resume for candidate {candidate_id}: {file_name}")

            # If this is primary, unset other primaries
            if is_primary:
                stmt = select(Resume).where(
                    and_(
                        Resume.candidate_id == candidate_id,
                        Resume.is_primary == True,
                    )
                )
                result = await session.execute(stmt)
                existing_primary = result.scalar_one_or_none()
                if existing_primary:
                    existing_primary.is_primary = False

            # Determine file type
            file_ext = Path(file_name).suffix.lower()
            file_type = file_ext.lstrip(".")

            # Create resume record
            resume = Resume(
                candidate_id=candidate_id,
                file_path=file_path,
                file_name=file_name,
                file_type=file_type,
                file_size=file_size,
                is_primary=is_primary,
            )

            session.add(resume)
            await session.flush()  # Get the ID

            logger.info(f"Resume uploaded: {resume.id}")

            return {
                "id": resume.id,
                "candidate_id": candidate_id,
                "file_name": file_name,
                "file_type": file_type,
                "file_size": file_size,
                "is_primary": is_primary,
                "uploaded_at": resume.uploaded_at.isoformat(),
            }

        except Exception as e:
            logger.error(f"Error uploading resume: {str(e)}")
            await session.rollback()
            raise

    async def parse_resume(
        self,
        session: AsyncSession,
        resume_id: int,
    ) -> Dict[str, Any]:
        """
        Parse resume file and extract structured data.

        Args:
            session: Database session
            resume_id: Resume ID

        Returns:
            Parsed resume data
        """
        try:
            logger.info(f"Parsing resume {resume_id}")

            # Get resume record
            stmt = select(Resume).where(Resume.id == resume_id)
            result = await session.execute(stmt)
            resume = result.scalar_one_or_none()

            if not resume:
                raise ValueError(f"Resume {resume_id} not found")

            # Extract text from file
            text = await self.parser.extract_text_from_file(resume.file_path)

            # Parse resume
            parsed_data = await self.parser.parse_resume(text, resume.file_name)

            # Check if parsed resume already exists
            stmt = select(ParsedResume).where(ParsedResume.resume_id == resume_id)
            result = await session.execute(stmt)
            existing_parsed = result.scalar_one_or_none()

            if existing_parsed:
                # Update existing
                existing_parsed.raw_text = text
                existing_parsed.parsed_data = parsed_data["parsed_data"]
                existing_parsed.skills_extracted = parsed_data["parsed_data"].get("skills", [])
                existing_parsed.experience_extracted = parsed_data["parsed_data"].get("experience", [])
                existing_parsed.education_extracted = parsed_data["parsed_data"].get("education", [])
                existing_parsed.certifications_extracted = parsed_data["parsed_data"].get("certifications", [])
                existing_parsed.parsing_confidence = parsed_data["parsing_confidence"]
                existing_parsed.parser_version = parsed_data["parser_version"]
            else:
                # Create new
                existing_parsed = ParsedResume(
                    resume_id=resume_id,
                    raw_text=text,
                    parsed_data=parsed_data["parsed_data"],
                    skills_extracted=parsed_data["parsed_data"].get("skills", []),
                    experience_extracted=parsed_data["parsed_data"].get("experience", []),
                    education_extracted=parsed_data["parsed_data"].get("education", []),
                    certifications_extracted=parsed_data["parsed_data"].get("certifications", []),
                    parsing_confidence=parsed_data["parsing_confidence"],
                    parser_version=parsed_data["parser_version"],
                )
                session.add(existing_parsed)

            await session.flush()

            # Update candidate skills and education from parsed data
            stmt = select(Candidate).where(Candidate.id == resume.candidate_id)
            result = await session.execute(stmt)
            candidate = result.scalar_one_or_none()

            if candidate:
                if parsed_data["parsed_data"].get("skills"):
                    candidate.skills = parsed_data["parsed_data"]["skills"]
                if parsed_data["parsed_data"].get("education"):
                    candidate.education = parsed_data["parsed_data"]["education"]

            await session.commit()

            logger.info(f"Resume {resume_id} parsed successfully")

            return {
                "resume_id": resume_id,
                "parsed_resume_id": existing_parsed.id,
                "parsing_confidence": parsed_data["parsing_confidence"],
                "extraction_stats": parsed_data["extraction_stats"],
                "parsed_at": parsed_data["parsed_at"],
            }

        except Exception as e:
            logger.error(f"Error parsing resume {resume_id}: {str(e)}")
            await session.rollback()
            raise

    async def get_parsed_resume(
        self,
        session: AsyncSession,
        resume_id: int,
    ) -> Optional[Dict[str, Any]]:
        """
        Get parsed resume data.

        Args:
            session: Database session
            resume_id: Resume ID

        Returns:
            Parsed data or None
        """
        try:
            stmt = select(ParsedResume).where(ParsedResume.resume_id == resume_id)
            result = await session.execute(stmt)
            parsed = result.scalar_one_or_none()

            if not parsed:
                return None

            return {
                "id": parsed.id,
                "resume_id": parsed.resume_id,
                "parsed_data": parsed.parsed_data,
                "skills_extracted": parsed.skills_extracted,
                "experience_extracted": parsed.experience_extracted,
                "education_extracted": parsed.education_extracted,
                "certifications_extracted": parsed.certifications_extracted,
                "parsing_confidence": parsed.parsing_confidence,
                "parser_version": parsed.parser_version,
                "parsed_at": parsed.parsed_at.isoformat(),
            }

        except Exception as e:
            logger.error(f"Error getting parsed resume: {str(e)}")
            raise

    async def tailor_resume(
        self,
        session: AsyncSession,
        resume_id: int,
        requirement_id: int,
    ) -> Dict[str, Any]:
        """
        Tailor resume for a specific requirement.

        Args:
            session: Database session
            resume_id: Resume ID
            requirement_id: Requirement ID

        Returns:
            Tailored resume and analysis
        """
        try:
            logger.info(f"Tailoring resume {resume_id} for requirement {requirement_id}")

            # Get resume
            stmt = select(Resume).where(Resume.id == resume_id)
            result = await session.execute(stmt)
            resume = result.scalar_one_or_none()

            if not resume:
                raise ValueError(f"Resume {resume_id} not found")

            # Get requirement
            from models.requirement import Requirement

            stmt = select(Requirement).where(Requirement.id == requirement_id)
            result = await session.execute(stmt)
            requirement = result.scalar_one_or_none()

            if not requirement:
                raise ValueError(f"Requirement {requirement_id} not found")

            # Get candidate name
            stmt = select(Candidate).where(Candidate.id == resume.candidate_id)
            result = await session.execute(stmt)
            candidate = result.scalar_one_or_none()

            # Extract resume text
            resume_text = await self.parser.extract_text_from_file(resume.file_path)

            # Tailor resume
            tailoring_result = await self.tailor.tailor_resume_for_requirement(
                resume_text,
                requirement.title,
                requirement.description or "",
                candidate.full_name if candidate else None,
            )

            return {
                "resume_id": resume_id,
                "requirement_id": requirement_id,
                "requirement_title": requirement.title,
                "tailored_resume": tailoring_result["tailored_resume"],
                "tailoring_analysis": tailoring_result["tailoring_analysis"],
                "keywords_emphasized": tailoring_result["keywords_emphasized"],
                "gap_analysis": tailoring_result["gap_analysis"],
                "ats_scores": tailoring_result["ats_scores"],
                "ats_recommendations": tailoring_result["ats_recommendations"],
                "generated_at": tailoring_result["generated_at"],
            }

        except Exception as e:
            logger.error(f"Error tailoring resume: {str(e)}")
            raise

    async def get_ats_score(
        self,
        session: AsyncSession,
        resume_id: int,
    ) -> Dict[str, Any]:
        """
        Get ATS compatibility score for a resume.

        Args:
            session: Database session
            resume_id: Resume ID

        Returns:
            ATS score details
        """
        try:
            # Get resume
            stmt = select(Resume).where(Resume.id == resume_id)
            result = await session.execute(stmt)
            resume = result.scalar_one_or_none()

            if not resume:
                raise ValueError(f"Resume {resume_id} not found")

            # Extract text
            resume_text = await self.parser.extract_text_from_file(resume.file_path)

            # Calculate ATS score
            ats_result = await self.tailor.get_ats_score(resume_text)

            return {
                "resume_id": resume_id,
                "overall_score": ats_result["overall_score"],
                "max_score": ats_result["max_score"],
                "components": ats_result["components"],
                "recommendations": ats_result["recommendations"],
            }

        except Exception as e:
            logger.error(f"Error getting ATS score: {str(e)}")
            raise

    async def search_resumes_by_skills(
        self,
        session: AsyncSession,
        skills: List[str],
        match_all: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Search resumes by skills.

        Args:
            session: Database session
            skills: List of skills to search for
            match_all: If True, require all skills; if False, any skill

        Returns:
            List of matching resumes
        """
        try:
            logger.info(f"Searching resumes by skills: {skills}")

            stmt = select(ParsedResume)
            result = await session.execute(stmt)
            parsed_resumes = result.scalars().all()

            matches = []

            for parsed in parsed_resumes:
                extracted_skills = [s.get("skill", "").lower() for s in (parsed.skills_extracted or [])]

                # Check skill matches
                matching_skills = []
                for search_skill in skills:
                    if any(search_skill.lower() in es for es in extracted_skills):
                        matching_skills.append(search_skill)

                if match_all:
                    if len(matching_skills) == len(skills):
                        matches.append(
                            {
                                "resume_id": parsed.resume_id,
                                "candidate_id": parsed.resume.candidate_id,
                                "matched_skills": matching_skills,
                                "all_skills": extracted_skills,
                            }
                        )
                else:
                    if matching_skills:
                        matches.append(
                            {
                                "resume_id": parsed.resume_id,
                                "candidate_id": parsed.resume.candidate_id,
                                "matched_skills": matching_skills,
                                "all_skills": extracted_skills,
                            }
                        )

            logger.info(f"Found {len(matches)} resumes matching skills")

            return matches

        except Exception as e:
            logger.error(f"Error searching resumes by skills: {str(e)}")
            raise

    async def get_candidate_resumes(
        self,
        session: AsyncSession,
        candidate_id: int,
    ) -> List[Dict[str, Any]]:
        """
        Get all resumes for a candidate.

        Args:
            session: Database session
            candidate_id: Candidate ID

        Returns:
            List of resume records
        """
        try:
            stmt = select(Resume).where(Resume.candidate_id == candidate_id).order_by(Resume.uploaded_at.desc())
            result = await session.execute(stmt)
            resumes = result.scalars().all()

            return [
                {
                    "id": r.id,
                    "candidate_id": r.candidate_id,
                    "file_name": r.file_name,
                    "file_type": r.file_type,
                    "file_size": r.file_size,
                    "is_primary": r.is_primary,
                    "uploaded_at": r.uploaded_at.isoformat(),
                }
                for r in resumes
            ]

        except Exception as e:
            logger.error(f"Error getting candidate resumes: {str(e)}")
            raise

    async def delete_resume(
        self,
        session: AsyncSession,
        resume_id: int,
    ) -> bool:
        """
        Delete a resume and its parsed data.

        Args:
            session: Database session
            resume_id: Resume ID

        Returns:
            Success flag
        """
        try:
            stmt = select(Resume).where(Resume.id == resume_id)
            result = await session.execute(stmt)
            resume = result.scalar_one_or_none()

            if not resume:
                raise ValueError(f"Resume {resume_id} not found")

            # Delete file if it exists
            try:
                if Path(resume.file_path).exists():
                    Path(resume.file_path).unlink()
            except Exception as e:
                logger.warning(f"Could not delete resume file: {str(e)}")

            # Delete from database (cascade will delete ParsedResume)
            await session.delete(resume)
            await session.commit()

            logger.info(f"Resume {resume_id} deleted")

            return True

        except Exception as e:
            logger.error(f"Error deleting resume: {str(e)}")
            await session.rollback()
            raise

    async def create_resume_version(
        self,
        session: AsyncSession,
        resume_id: int,
        version_content: str,
        version_name: str,
    ) -> Dict[str, Any]:
        """
        Create a tailored version of a resume.

        Stores as a separate file with metadata.

        Args:
            session: Database session
            resume_id: Original resume ID
            version_content: Content of tailored resume
            version_name: Name/description of version

        Returns:
            Version metadata
        """
        try:
            stmt = select(Resume).where(Resume.id == resume_id)
            result = await session.execute(stmt)
            resume = result.scalar_one_or_none()

            if not resume:
                raise ValueError(f"Resume {resume_id} not found")

            # Create version file path
            base_name = Path(resume.file_name).stem
            version_file_name = f"{base_name}__{version_name}.txt"
            version_file_path = self.upload_dir / version_file_name

            # Write version file
            with open(version_file_path, "w") as f:
                f.write(version_content)

            file_size = version_file_path.stat().st_size

            # Store version metadata
            version_metadata = {
                "original_resume_id": resume_id,
                "version_name": version_name,
                "file_path": str(version_file_path),
                "file_size": file_size,
                "created_at": datetime.utcnow().isoformat(),
            }

            logger.info(f"Created resume version: {version_name}")

            return version_metadata

        except Exception as e:
            logger.error(f"Error creating resume version: {str(e)}")
            raise
