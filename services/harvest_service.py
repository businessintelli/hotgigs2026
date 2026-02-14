"""Resume harvesting service."""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy import select, and_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from models.harvest import HarvestSource, HarvestJob, HarvestResult, CandidateSourceMapping
from models.candidate import Candidate

logger = logging.getLogger(__name__)


class HarvestService:
    """Service for harvest operations."""

    def __init__(self, db: AsyncSession):
        """Initialize harvest service."""
        self.db = db

    async def get_sources(self, skip: int = 0, limit: int = 20) -> tuple[List[HarvestSource], int]:
        """Get all harvest sources with pagination."""
        try:
            stmt = select(func.count(HarvestSource.id))
            result = await self.db.execute(stmt)
            total = result.scalar() or 0

            stmt = select(HarvestSource).offset(skip).limit(limit).order_by(HarvestSource.created_at.desc())
            result = await self.db.execute(stmt)
            sources = result.scalars().all()

            return sources, total

        except Exception as e:
            logger.error(f"Error getting harvest sources: {str(e)}")
            raise

    async def get_source_by_id(self, source_id: int) -> Optional[HarvestSource]:
        """Get harvest source by ID."""
        try:
            stmt = select(HarvestSource).where(HarvestSource.id == source_id)
            result = await self.db.execute(stmt)
            return result.scalars().first()

        except Exception as e:
            logger.error(f"Error getting harvest source: {str(e)}")
            raise

    async def get_source_by_name(self, name: str) -> Optional[HarvestSource]:
        """Get harvest source by name."""
        try:
            stmt = select(HarvestSource).where(HarvestSource.name == name)
            result = await self.db.execute(stmt)
            return result.scalars().first()

        except Exception as e:
            logger.error(f"Error getting harvest source by name: {str(e)}")
            raise

    async def update_source(self, source_id: int, update_data: Dict[str, Any]) -> Optional[HarvestSource]:
        """Update harvest source."""
        try:
            source = await self.get_source_by_id(source_id)
            if not source:
                return None

            for key, value in update_data.items():
                if hasattr(source, key) and value is not None:
                    setattr(source, key, value)

            await self.db.flush()
            logger.info(f"Updated harvest source {source_id}")
            return source

        except Exception as e:
            logger.error(f"Error updating harvest source: {str(e)}")
            raise

    async def get_jobs(self, skip: int = 0, limit: int = 20) -> tuple[List[HarvestJob], int]:
        """Get all harvest jobs with pagination."""
        try:
            stmt = select(func.count(HarvestJob.id))
            result = await self.db.execute(stmt)
            total = result.scalar() or 0

            stmt = select(HarvestJob).offset(skip).limit(limit).order_by(HarvestJob.created_at.desc())
            result = await self.db.execute(stmt)
            jobs = result.scalars().all()

            return jobs, total

        except Exception as e:
            logger.error(f"Error getting harvest jobs: {str(e)}")
            raise

    async def get_job_by_id(self, job_id: int) -> Optional[HarvestJob]:
        """Get harvest job by ID."""
        try:
            stmt = select(HarvestJob).where(HarvestJob.id == job_id)
            result = await self.db.execute(stmt)
            return result.scalars().first()

        except Exception as e:
            logger.error(f"Error getting harvest job: {str(e)}")
            raise

    async def get_job_results(self, job_id: int, skip: int = 0, limit: int = 50) -> tuple[List[HarvestResult], int]:
        """Get harvest results for a job."""
        try:
            stmt = select(func.count(HarvestResult.id)).where(HarvestResult.job_id == job_id)
            result = await self.db.execute(stmt)
            total = result.scalar() or 0

            stmt = (
                select(HarvestResult)
                .where(HarvestResult.job_id == job_id)
                .offset(skip)
                .limit(limit)
                .order_by(HarvestResult.created_at.desc())
            )
            result = await self.db.execute(stmt)
            results = result.scalars().all()

            return results, total

        except Exception as e:
            logger.error(f"Error getting harvest results: {str(e)}")
            raise

    async def get_candidate_sources(self, candidate_id: int) -> List[CandidateSourceMapping]:
        """Get all source mappings for a candidate."""
        try:
            stmt = select(CandidateSourceMapping).where(CandidateSourceMapping.candidate_id == candidate_id)
            result = await self.db.execute(stmt)
            return result.scalars().all()

        except Exception as e:
            logger.error(f"Error getting candidate sources: {str(e)}")
            raise

    async def update_source_sync(self, source_id: int) -> None:
        """Update last harvested timestamp for source."""
        try:
            source = await self.get_source_by_id(source_id)
            if source:
                source.last_harvested_at = datetime.utcnow()
                await self.db.flush()
                logger.info(f"Updated sync time for source {source_id}")

        except Exception as e:
            logger.error(f"Error updating source sync: {str(e)}")
            raise

    async def get_scheduled_jobs(self) -> List[HarvestJob]:
        """Get harvest jobs that are due for execution."""
        try:
            stmt = select(HarvestJob).where(
                and_(
                    HarvestJob.status == "scheduled",
                    HarvestJob.next_run_at <= datetime.utcnow(),
                )
            )
            result = await self.db.execute(stmt)
            return result.scalars().all()

        except Exception as e:
            logger.error(f"Error getting scheduled jobs: {str(e)}")
            raise

    async def mark_job_running(self, job_id: int) -> None:
        """Mark harvest job as running."""
        try:
            job = await self.get_job_by_id(job_id)
            if job:
                job.status = "running"
                job.started_at = datetime.utcnow()
                await self.db.flush()
                logger.info(f"Marked job {job_id} as running")

        except Exception as e:
            logger.error(f"Error marking job running: {str(e)}")
            raise

    async def mark_job_completed(self, job_id: int) -> None:
        """Mark harvest job as completed."""
        try:
            job = await self.get_job_by_id(job_id)
            if job:
                job.status = "completed"
                job.completed_at = datetime.utcnow()

                # Schedule next run if recurring
                if job.frequency:
                    if job.frequency == "daily":
                        job.next_run_at = datetime.utcnow() + timedelta(days=1)
                    elif job.frequency == "weekly":
                        job.next_run_at = datetime.utcnow() + timedelta(weeks=1)
                    elif job.frequency == "monthly":
                        job.next_run_at = datetime.utcnow() + timedelta(days=30)

                    job.status = "scheduled"

                await self.db.flush()
                logger.info(f"Marked job {job_id} as completed")

        except Exception as e:
            logger.error(f"Error marking job completed: {str(e)}")
            raise

    async def mark_job_failed(self, job_id: int, error_message: str) -> None:
        """Mark harvest job as failed."""
        try:
            job = await self.get_job_by_id(job_id)
            if job:
                job.status = "failed"
                job.error_message = error_message
                job.completed_at = datetime.utcnow()
                await self.db.flush()
                logger.error(f"Marked job {job_id} as failed: {error_message}")

        except Exception as e:
            logger.error(f"Error marking job failed: {str(e)}")
            raise

    async def get_candidate_by_id(self, candidate_id: int) -> Optional[Candidate]:
        """Get candidate by ID."""
        try:
            stmt = select(Candidate).where(Candidate.id == candidate_id)
            result = await self.db.execute(stmt)
            return result.scalars().first()

        except Exception as e:
            logger.error(f"Error getting candidate: {str(e)}")
            raise

    async def get_harvest_source_mapping(
        self, candidate_id: int, source_id: int
    ) -> Optional[CandidateSourceMapping]:
        """Get source mapping for candidate."""
        try:
            stmt = select(CandidateSourceMapping).where(
                and_(
                    CandidateSourceMapping.candidate_id == candidate_id,
                    CandidateSourceMapping.source_id == source_id,
                )
            )
            result = await self.db.execute(stmt)
            return result.scalars().first()

        except Exception as e:
            logger.error(f"Error getting source mapping: {str(e)}")
            raise
