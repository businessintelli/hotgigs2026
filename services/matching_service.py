import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from models.match import MatchScore
from models.requirement import Requirement
from models.candidate import Candidate
from agents.matching_agent import MatchingAgent
from agents.events import EventType
from config import settings

logger = logging.getLogger(__name__)


class MatchingService:
    """Service layer for candidate-requirement matching operations."""

    def __init__(self, matching_agent: Optional[MatchingAgent] = None):
        """Initialize matching service.

        Args:
            matching_agent: Optional pre-initialized matching agent
        """
        self.agent = matching_agent or MatchingAgent()

    async def match_requirement_to_candidates(
        self,
        session: AsyncSession,
        requirement_id: int,
        limit: int = 50,
        min_score: float = 0.5,
    ) -> Dict[str, Any]:
        """
        Match a requirement against all candidates.

        Args:
            session: Database session
            requirement_id: Requirement ID
            limit: Maximum results
            min_score: Minimum match score

        Returns:
            Match results with metadata
        """
        try:
            logger.info(f"Matching requirement {requirement_id} to candidates")

            matches = await self.agent.match_requirement_to_candidates(
                session,
                requirement_id,
                limit,
                min_score,
            )

            return {
                "requirement_id": requirement_id,
                "matches_found": len(matches),
                "matches": matches,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error matching requirement {requirement_id}: {str(e)}")
            raise

    async def match_candidate_to_requirements(
        self,
        session: AsyncSession,
        candidate_id: int,
        limit: int = 50,
        min_score: float = 0.5,
    ) -> Dict[str, Any]:
        """
        Match a candidate against all requirements.

        Args:
            session: Database session
            candidate_id: Candidate ID
            limit: Maximum results
            min_score: Minimum match score

        Returns:
            Match results with metadata
        """
        try:
            logger.info(f"Matching candidate {candidate_id} to requirements")

            matches = await self.agent.match_candidate_to_requirements(
                session,
                candidate_id,
                limit,
                min_score,
            )

            return {
                "candidate_id": candidate_id,
                "matches_found": len(matches),
                "matches": matches,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error matching candidate {candidate_id}: {str(e)}")
            raise

    async def get_match_score(
        self,
        session: AsyncSession,
        requirement_id: int,
        candidate_id: int,
    ) -> Optional[Dict[str, Any]]:
        """
        Get specific match score.

        Args:
            session: Database session
            requirement_id: Requirement ID
            candidate_id: Candidate ID

        Returns:
            Match score details or None
        """
        try:
            stmt = select(MatchScore).where(
                and_(
                    MatchScore.requirement_id == requirement_id,
                    MatchScore.candidate_id == candidate_id,
                )
            )
            result = await session.execute(stmt)
            match = result.scalar_one_or_none()

            if not match:
                return None

            return {
                "requirement_id": match.requirement_id,
                "candidate_id": match.candidate_id,
                "overall_score": match.overall_score,
                "skill_score": match.skill_score,
                "experience_score": match.experience_score,
                "education_score": match.education_score,
                "location_score": match.location_score,
                "rate_score": match.rate_score,
                "availability_score": match.availability_score,
                "culture_score": match.culture_score,
                "missing_skills": match.missing_skills,
                "standout_qualities": match.standout_qualities,
                "score_breakdown": match.score_breakdown,
                "matched_at": match.matched_at.isoformat() if match.matched_at else None,
            }

        except Exception as e:
            logger.error(
                f"Error getting match score for requirement {requirement_id}, "
                f"candidate {candidate_id}: {str(e)}"
            )
            raise

    async def get_requirement_matches(
        self,
        session: AsyncSession,
        requirement_id: int,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get all match scores for a requirement.

        Args:
            session: Database session
            requirement_id: Requirement ID
            limit: Results limit
            offset: Results offset

        Returns:
            Paginated match results
        """
        try:
            # Get total count
            count_stmt = select(MatchScore).where(MatchScore.requirement_id == requirement_id)
            count_result = await session.execute(count_stmt)
            total = len(count_result.scalars().all())

            # Get paginated results
            stmt = (
                select(MatchScore)
                .where(MatchScore.requirement_id == requirement_id)
                .order_by(MatchScore.overall_score.desc())
                .offset(offset)
                .limit(limit)
            )
            result = await session.execute(stmt)
            matches = result.scalars().all()

            matches_data = [
                {
                    "id": m.id,
                    "requirement_id": m.requirement_id,
                    "candidate_id": m.candidate_id,
                    "overall_score": m.overall_score,
                    "skill_score": m.skill_score,
                    "experience_score": m.experience_score,
                    "education_score": m.education_score,
                    "location_score": m.location_score,
                    "rate_score": m.rate_score,
                    "availability_score": m.availability_score,
                    "culture_score": m.culture_score,
                    "status": m.status,
                    "matched_at": m.matched_at.isoformat() if m.matched_at else None,
                }
                for m in matches
            ]

            return {
                "requirement_id": requirement_id,
                "total": total,
                "limit": limit,
                "offset": offset,
                "matches": matches_data,
            }

        except Exception as e:
            logger.error(f"Error getting requirement matches: {str(e)}")
            raise

    async def update_match_weights(
        self,
        session: AsyncSession,
        weights: Dict[str, float],
    ) -> Dict[str, Any]:
        """
        Update matching weights.

        Args:
            session: Database session
            weights: New weight configuration

        Returns:
            Updated weights
        """
        try:
            # Validate weights sum to 1.0
            total_weight = sum(weights.values())
            if abs(total_weight - 1.0) > 0.01:
                raise ValueError(f"Weights must sum to 1.0, got {total_weight}")

            # Update agent weights
            self.agent.weights = weights

            logger.info(f"Updated matching weights: {weights}")

            return {
                "weights": weights,
                "total": total_weight,
                "valid": True,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error updating match weights: {str(e)}")
            raise

    async def batch_match_all(
        self,
        session: AsyncSession,
        min_score: float = 0.5,
    ) -> Dict[str, Any]:
        """
        Execute batch matching for all active requirements and candidates.

        Args:
            session: Database session
            min_score: Minimum match score to save

        Returns:
            Batch operation statistics
        """
        try:
            logger.info("Starting batch matching operation")

            stats = await self.agent.batch_match_all(session, min_score)

            logger.info(f"Batch matching completed: {stats}")

            return {
                **stats,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error in batch matching: {str(e)}")
            raise

    async def recalculate_requirement_matches(
        self,
        session: AsyncSession,
        requirement_id: int,
    ) -> Dict[str, Any]:
        """
        Recalculate all matches for a requirement.

        Args:
            session: Database session
            requirement_id: Requirement ID

        Returns:
            Recalculation statistics
        """
        try:
            logger.info(f"Recalculating matches for requirement {requirement_id}")

            stats = await self.agent.recalculate_requirement_matches(
                session,
                requirement_id,
            )

            logger.info(f"Recalculation completed: {stats}")

            return {
                **stats,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error recalculating matches: {str(e)}")
            raise

    async def override_match(
        self,
        session: AsyncSession,
        requirement_id: int,
        candidate_id: int,
        override_score: float,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Manually override a match score.

        Args:
            session: Database session
            requirement_id: Requirement ID
            candidate_id: Candidate ID
            override_score: New override score
            notes: Override reason notes

        Returns:
            Updated match details
        """
        try:
            stmt = select(MatchScore).where(
                and_(
                    MatchScore.requirement_id == requirement_id,
                    MatchScore.candidate_id == candidate_id,
                )
            )
            result = await session.execute(stmt)
            match = result.scalar_one_or_none()

            if not match:
                raise ValueError(f"Match not found for requirement {requirement_id}, candidate {candidate_id}")

            match.overall_score = override_score
            match.matched_by = "manual_override"
            match.notes = notes
            match.matched_at = datetime.utcnow()

            await session.commit()

            logger.info(
                f"Overrode match score for requirement {requirement_id}, "
                f"candidate {candidate_id}: {override_score}"
            )

            return {
                "requirement_id": requirement_id,
                "candidate_id": candidate_id,
                "overall_score": override_score,
                "matched_by": "manual_override",
                "notes": notes,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error overriding match: {str(e)}")
            await session.rollback()
            raise

    async def cache_match_results(
        self,
        redis_client,
        requirement_id: int,
        matches: List[Dict[str, Any]],
        ttl: int = 3600,
    ) -> bool:
        """
        Cache match results in Redis.

        Args:
            redis_client: Redis client
            requirement_id: Requirement ID
            matches: Match results to cache
            ttl: Cache TTL in seconds

        Returns:
            Success flag
        """
        try:
            import json

            cache_key = f"matches:requirement:{requirement_id}"
            cache_value = json.dumps(matches)

            await redis_client.setex(cache_key, ttl, cache_value)

            logger.debug(f"Cached matches for requirement {requirement_id}")

            return True

        except Exception as e:
            logger.warning(f"Error caching match results: {str(e)}")
            return False

    async def get_cached_matches(
        self,
        redis_client,
        requirement_id: int,
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get cached match results from Redis.

        Args:
            redis_client: Redis client
            requirement_id: Requirement ID

        Returns:
            Cached matches or None
        """
        try:
            import json

            cache_key = f"matches:requirement:{requirement_id}"
            cached = await redis_client.get(cache_key)

            if cached:
                matches = json.loads(cached)
                logger.debug(f"Retrieved cached matches for requirement {requirement_id}")
                return matches

            return None

        except Exception as e:
            logger.warning(f"Error retrieving cached matches: {str(e)}")
            return None
