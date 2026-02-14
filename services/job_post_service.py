"""Job post service for CRUD operations and management."""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from models.job_post import JobPost, JobPostAnalytics
from models.requirement import Requirement

logger = logging.getLogger(__name__)


class JobPostService:
    """Service for job post operations."""

    @staticmethod
    async def create_job_post(
        db: AsyncSession,
        requirement_id: int,
        title: str,
        content: str,
        summary: str,
        responsibilities: Optional[List[str]] = None,
        qualifications_required: Optional[List[str]] = None,
        qualifications_preferred: Optional[List[str]] = None,
        benefits: Optional[List[str]] = None,
        salary_range_min: Optional[float] = None,
        salary_range_max: Optional[float] = None,
        created_by: Optional[int] = None,
    ) -> JobPost:
        """Create a new job post.

        Args:
            db: Database session
            requirement_id: Requirement ID
            title: Job post title
            content: Full content
            summary: Summary
            responsibilities: List of responsibilities
            qualifications_required: Required qualifications
            qualifications_preferred: Preferred qualifications
            benefits: Benefits list
            salary_range_min: Minimum salary
            salary_range_max: Maximum salary
            created_by: User ID who created

        Returns:
            Created JobPost object
        """
        try:
            job_post = JobPost(
                requirement_id=requirement_id,
                title=title,
                content=content,
                summary=summary,
                responsibilities=responsibilities or [],
                qualifications_required=qualifications_required or [],
                qualifications_preferred=qualifications_preferred or [],
                benefits=benefits or [],
                salary_range_min=salary_range_min,
                salary_range_max=salary_range_max,
                status="draft",
                created_by=created_by,
            )
            db.add(job_post)
            await db.commit()
            await db.refresh(job_post)
            logger.info(f"Created job post: {job_post.id}")
            return job_post
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating job post: {str(e)}")
            raise

    @staticmethod
    async def get_job_post(db: AsyncSession, job_post_id: int) -> Optional[JobPost]:
        """Get job post by ID.

        Args:
            db: Database session
            job_post_id: Job post ID

        Returns:
            JobPost object or None
        """
        try:
            result = await db.execute(
                select(JobPost).where(JobPost.id == job_post_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting job post: {str(e)}")
            raise

    @staticmethod
    async def update_job_post(
        db: AsyncSession,
        job_post_id: int,
        **kwargs: Any,
    ) -> JobPost:
        """Update job post.

        Args:
            db: Database session
            job_post_id: Job post ID
            **kwargs: Fields to update

        Returns:
            Updated JobPost object
        """
        try:
            job_post = await JobPostService.get_job_post(db, job_post_id)
            if not job_post:
                raise ValueError(f"Job post {job_post_id} not found")

            for key, value in kwargs.items():
                if hasattr(job_post, key):
                    setattr(job_post, key, value)

            db.add(job_post)
            await db.commit()
            await db.refresh(job_post)
            logger.info(f"Updated job post: {job_post_id}")
            return job_post
        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating job post: {str(e)}")
            raise

    @staticmethod
    async def list_job_posts(
        db: AsyncSession,
        requirement_id: Optional[int] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[JobPost], int]:
        """List job posts.

        Args:
            db: Database session
            requirement_id: Filter by requirement
            status: Filter by status
            skip: Number to skip
            limit: Number to limit

        Returns:
            Tuple of (job posts list, total count)
        """
        try:
            query = select(JobPost)

            if requirement_id:
                query = query.where(JobPost.requirement_id == requirement_id)

            if status:
                query = query.where(JobPost.status == status)

            # Count total
            count_result = await db.execute(
                select(func.count(JobPost.id)).select_from(JobPost)
            )
            total = count_result.scalar() or 0

            # Get paginated results
            result = await db.execute(
                query.order_by(desc(JobPost.created_at))
                .offset(skip)
                .limit(limit)
            )
            job_posts = result.scalars().all()

            return job_posts, total
        except Exception as e:
            logger.error(f"Error listing job posts: {str(e)}")
            raise

    @staticmethod
    async def publish_job_post(
        db: AsyncSession,
        job_post_id: int,
        boards: List[str],
    ) -> JobPost:
        """Publish job post to boards.

        Args:
            db: Database session
            job_post_id: Job post ID
            boards: List of board names

        Returns:
            Updated JobPost object
        """
        try:
            job_post = await JobPostService.get_job_post(db, job_post_id)
            if not job_post:
                raise ValueError(f"Job post {job_post_id} not found")

            job_post.status = "published"
            job_post.published_at = datetime.utcnow()
            job_post.published_boards = boards

            db.add(job_post)
            await db.commit()
            await db.refresh(job_post)

            logger.info(f"Published job post {job_post_id} to {len(boards)} boards")
            return job_post
        except Exception as e:
            await db.rollback()
            logger.error(f"Error publishing job post: {str(e)}")
            raise

    @staticmethod
    async def update_seo_metrics(
        db: AsyncSession,
        job_post_id: int,
        seo_score: float,
    ) -> JobPost:
        """Update SEO metrics for job post.

        Args:
            db: Database session
            job_post_id: Job post ID
            seo_score: SEO score

        Returns:
            Updated JobPost object
        """
        try:
            job_post = await JobPostService.get_job_post(db, job_post_id)
            if not job_post:
                raise ValueError(f"Job post {job_post_id} not found")

            job_post.seo_score = seo_score
            db.add(job_post)
            await db.commit()
            await db.refresh(job_post)

            logger.info(f"Updated SEO metrics for job post {job_post_id}")
            return job_post
        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating SEO metrics: {str(e)}")
            raise

    @staticmethod
    async def update_inclusivity_metrics(
        db: AsyncSession,
        job_post_id: int,
        inclusivity_score: float,
    ) -> JobPost:
        """Update inclusivity metrics for job post.

        Args:
            db: Database session
            job_post_id: Job post ID
            inclusivity_score: Inclusivity score

        Returns:
            Updated JobPost object
        """
        try:
            job_post = await JobPostService.get_job_post(db, job_post_id)
            if not job_post:
                raise ValueError(f"Job post {job_post_id} not found")

            job_post.inclusivity_score = inclusivity_score
            db.add(job_post)
            await db.commit()
            await db.refresh(job_post)

            logger.info(f"Updated inclusivity metrics for job post {job_post_id}")
            return job_post
        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating inclusivity metrics: {str(e)}")
            raise

    @staticmethod
    async def record_analytics(
        db: AsyncSession,
        job_post_id: int,
        board_name: str,
        views: int = 0,
        clicks: int = 0,
        applications: int = 0,
        period_start: Optional[date] = None,
        period_end: Optional[date] = None,
    ) -> JobPostAnalytics:
        """Record job post analytics.

        Args:
            db: Database session
            job_post_id: Job post ID
            board_name: Board name
            views: View count
            clicks: Click count
            applications: Application count
            period_start: Period start date
            period_end: Period end date

        Returns:
            Created/updated JobPostAnalytics object
        """
        try:
            now = datetime.utcnow().date()

            # Check if analytics exists for this period
            analytics_result = await db.execute(
                select(JobPostAnalytics).where(
                    and_(
                        JobPostAnalytics.job_post_id == job_post_id,
                        JobPostAnalytics.board_name == board_name,
                        JobPostAnalytics.period_start == (period_start or now),
                    )
                )
            )
            analytics = analytics_result.scalar_one_or_none()

            if analytics:
                analytics.views += views
                analytics.clicks += clicks
                analytics.applications += applications
            else:
                analytics = JobPostAnalytics(
                    job_post_id=job_post_id,
                    board_name=board_name,
                    views=views,
                    clicks=clicks,
                    applications=applications,
                    period_start=period_start or now,
                    period_end=period_end or now,
                )

            db.add(analytics)
            await db.commit()
            await db.refresh(analytics)

            logger.info(f"Recorded analytics for job post {job_post_id}")
            return analytics
        except Exception as e:
            await db.rollback()
            logger.error(f"Error recording analytics: {str(e)}")
            raise

    @staticmethod
    async def get_analytics(
        db: AsyncSession,
        job_post_id: int,
    ) -> List[JobPostAnalytics]:
        """Get analytics for job post.

        Args:
            db: Database session
            job_post_id: Job post ID

        Returns:
            List of JobPostAnalytics objects
        """
        try:
            result = await db.execute(
                select(JobPostAnalytics)
                .where(JobPostAnalytics.job_post_id == job_post_id)
                .order_by(desc(JobPostAnalytics.period_end))
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting analytics: {str(e)}")
            raise

    @staticmethod
    async def archive_job_post(
        db: AsyncSession,
        job_post_id: int,
    ) -> JobPost:
        """Archive job post.

        Args:
            db: Database session
            job_post_id: Job post ID

        Returns:
            Updated JobPost object
        """
        try:
            job_post = await JobPostService.get_job_post(db, job_post_id)
            if not job_post:
                raise ValueError(f"Job post {job_post_id} not found")

            job_post.status = "archived"
            db.add(job_post)
            await db.commit()
            await db.refresh(job_post)

            logger.info(f"Archived job post {job_post_id}")
            return job_post
        except Exception as e:
            await db.rollback()
            logger.error(f"Error archiving job post: {str(e)}")
            raise

    @staticmethod
    async def get_jobs_for_requirement(
        db: AsyncSession,
        requirement_id: int,
    ) -> List[JobPost]:
        """Get all job posts for a requirement.

        Args:
            db: Database session
            requirement_id: Requirement ID

        Returns:
            List of JobPost objects
        """
        try:
            result = await db.execute(
                select(JobPost)
                .where(JobPost.requirement_id == requirement_id)
                .order_by(desc(JobPost.version))
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting job posts for requirement: {str(e)}")
            raise
