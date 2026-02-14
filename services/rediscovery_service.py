"""Rediscovery service for candidate talent pool management."""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from models.candidate import Candidate
from models.rediscovery import CandidateRediscovery, CompetencyProfile
from models.enums import CandidateStatus

logger = logging.getLogger(__name__)


class RediscoveryService:
    """Service for candidate rediscovery operations."""

    @staticmethod
    async def create_rediscovery(
        db: AsyncSession,
        candidate_id: int,
        requirement_id: int,
        rediscovery_score: float,
        skill_match_score: float,
        interview_history_score: float,
        recency_score: float,
        engagement_score: float,
        score_breakdown: Dict[str, Any],
        original_requirement_id: Optional[int] = None,
    ) -> CandidateRediscovery:
        """Create rediscovery record.

        Args:
            db: Database session
            candidate_id: Candidate ID
            requirement_id: Requirement ID
            rediscovery_score: Overall rediscovery score
            skill_match_score: Skill match score
            interview_history_score: Interview history score
            recency_score: Recency score
            engagement_score: Engagement score
            score_breakdown: Score breakdown dictionary
            original_requirement_id: Original requirement ID

        Returns:
            Created CandidateRediscovery object
        """
        try:
            rediscovery = CandidateRediscovery(
                candidate_id=candidate_id,
                requirement_id=requirement_id,
                original_requirement_id=original_requirement_id,
                rediscovery_score=rediscovery_score,
                skill_match_score=skill_match_score,
                interview_history_score=interview_history_score,
                recency_score=recency_score,
                engagement_score=engagement_score,
                score_breakdown=score_breakdown,
                status="identified",
            )
            db.add(rediscovery)
            await db.commit()
            await db.refresh(rediscovery)
            logger.info(f"Created rediscovery record for candidate {candidate_id}")
            return rediscovery
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating rediscovery: {str(e)}")
            raise

    @staticmethod
    async def get_rediscovery(
        db: AsyncSession, rediscovery_id: int
    ) -> Optional[CandidateRediscovery]:
        """Get rediscovery record.

        Args:
            db: Database session
            rediscovery_id: Rediscovery ID

        Returns:
            CandidateRediscovery object or None
        """
        try:
            result = await db.execute(
                select(CandidateRediscovery).where(
                    CandidateRediscovery.id == rediscovery_id
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting rediscovery: {str(e)}")
            raise

    @staticmethod
    async def update_rediscovery(
        db: AsyncSession,
        rediscovery_id: int,
        **kwargs: Any,
    ) -> CandidateRediscovery:
        """Update rediscovery record.

        Args:
            db: Database session
            rediscovery_id: Rediscovery ID
            **kwargs: Fields to update

        Returns:
            Updated CandidateRediscovery object
        """
        try:
            rediscovery = await RediscoveryService.get_rediscovery(db, rediscovery_id)
            if not rediscovery:
                raise ValueError(f"Rediscovery {rediscovery_id} not found")

            for key, value in kwargs.items():
                if hasattr(rediscovery, key):
                    setattr(rediscovery, key, value)

            db.add(rediscovery)
            await db.commit()
            await db.refresh(rediscovery)
            logger.info(f"Updated rediscovery: {rediscovery_id}")
            return rediscovery
        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating rediscovery: {str(e)}")
            raise

    @staticmethod
    async def list_rediscoveries(
        db: AsyncSession,
        requirement_id: Optional[int] = None,
        candidate_id: Optional[int] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[CandidateRediscovery], int]:
        """List rediscovery records.

        Args:
            db: Database session
            requirement_id: Filter by requirement
            candidate_id: Filter by candidate
            status: Filter by status
            skip: Number to skip
            limit: Number to limit

        Returns:
            Tuple of (rediscoveries list, total count)
        """
        try:
            query = select(CandidateRediscovery)

            if requirement_id:
                query = query.where(
                    CandidateRediscovery.requirement_id == requirement_id
                )

            if candidate_id:
                query = query.where(CandidateRediscovery.candidate_id == candidate_id)

            if status:
                query = query.where(CandidateRediscovery.status == status)

            # Count total
            count_result = await db.execute(
                select(func.count(CandidateRediscovery.id)).select_from(
                    query.select_from(CandidateRediscovery)
                )
            )
            total = count_result.scalar() or 0

            # Get paginated results
            result = await db.execute(
                query.order_by(desc(CandidateRediscovery.rediscovery_score))
                .offset(skip)
                .limit(limit)
            )
            rediscoveries = result.scalars().all()

            return rediscoveries, total
        except Exception as e:
            logger.error(f"Error listing rediscoveries: {str(e)}")
            raise

    @staticmethod
    async def create_competency_profile(
        db: AsyncSession,
        candidate_id: int,
    ) -> CompetencyProfile:
        """Create competency profile.

        Args:
            db: Database session
            candidate_id: Candidate ID

        Returns:
            Created CompetencyProfile object
        """
        try:
            profile = CompetencyProfile(
                candidate_id=candidate_id,
                competency_details={},
                assessment_count=0,
            )
            db.add(profile)
            await db.commit()
            await db.refresh(profile)
            logger.info(f"Created competency profile for candidate {candidate_id}")
            return profile
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating competency profile: {str(e)}")
            raise

    @staticmethod
    async def get_competency_profile(
        db: AsyncSession, candidate_id: int
    ) -> Optional[CompetencyProfile]:
        """Get competency profile.

        Args:
            db: Database session
            candidate_id: Candidate ID

        Returns:
            CompetencyProfile object or None
        """
        try:
            result = await db.execute(
                select(CompetencyProfile).where(
                    CompetencyProfile.candidate_id == candidate_id
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting competency profile: {str(e)}")
            raise

    @staticmethod
    async def update_competency_profile(
        db: AsyncSession,
        candidate_id: int,
        **kwargs: Any,
    ) -> CompetencyProfile:
        """Update competency profile.

        Args:
            db: Database session
            candidate_id: Candidate ID
            **kwargs: Fields to update

        Returns:
            Updated CompetencyProfile object
        """
        try:
            profile = await RediscoveryService.get_competency_profile(
                db, candidate_id
            )

            if not profile:
                profile = await RediscoveryService.create_competency_profile(
                    db, candidate_id
                )

            for key, value in kwargs.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)

            db.add(profile)
            await db.commit()
            await db.refresh(profile)
            logger.info(f"Updated competency profile for candidate {candidate_id}")
            return profile
        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating competency profile: {str(e)}")
            raise

    @staticmethod
    async def get_talent_pool_candidates(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[Candidate], int]:
        """Get candidates in talent pool.

        Args:
            db: Database session
            skip: Number to skip
            limit: Number to limit

        Returns:
            Tuple of (candidates list, total count)
        """
        try:
            query = select(Candidate).where(
                Candidate.status == CandidateStatus.TALENT_POOL
            )

            # Count total
            count_result = await db.execute(
                select(func.count(Candidate.id)).where(
                    Candidate.status == CandidateStatus.TALENT_POOL
                )
            )
            total = count_result.scalar() or 0

            # Get paginated results
            result = await db.execute(
                query.order_by(desc(Candidate.engagement_score))
                .offset(skip)
                .limit(limit)
            )
            candidates = result.scalars().all()

            return candidates, total
        except Exception as e:
            logger.error(f"Error getting talent pool candidates: {str(e)}")
            raise

    @staticmethod
    async def search_rediscovery_candidates(
        db: AsyncSession,
        requirement_id: int,
        min_score: float = 0.0,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[CandidateRediscovery], int]:
        """Search rediscovery candidates for requirement.

        Args:
            db: Database session
            requirement_id: Requirement ID
            min_score: Minimum rediscovery score
            skip: Number to skip
            limit: Number to limit

        Returns:
            Tuple of (rediscoveries list, total count)
        """
        try:
            query = select(CandidateRediscovery).where(
                and_(
                    CandidateRediscovery.requirement_id == requirement_id,
                    CandidateRediscovery.rediscovery_score >= min_score,
                )
            )

            # Count total
            count_result = await db.execute(
                select(func.count(CandidateRediscovery.id)).where(
                    and_(
                        CandidateRediscovery.requirement_id == requirement_id,
                        CandidateRediscovery.rediscovery_score >= min_score,
                    )
                )
            )
            total = count_result.scalar() or 0

            # Get paginated results
            result = await db.execute(
                query.order_by(desc(CandidateRediscovery.rediscovery_score))
                .offset(skip)
                .limit(limit)
            )
            rediscoveries = result.scalars().all()

            return rediscoveries, total
        except Exception as e:
            logger.error(f"Error searching rediscovery candidates: {str(e)}")
            raise
