"""Tests for Matching Service."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from services.matching_service import MatchingService
from models.match import MatchScore
from models.enums import MatchStatus
from sqlalchemy import select


class TestMatchingService:
    """Test suite for MatchingService."""

    @pytest.fixture
    def matching_service(self):
        """Create matching service with mock agent."""
        mock_agent = AsyncMock()
        return MatchingService(matching_agent=mock_agent)

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_compute_skill_match_exact(self, matching_service):
        """Test exact skill match computation."""
        # Mock the agent method
        matching_service.agent.match_requirement_to_candidates = AsyncMock(
            return_value=[
                {
                    "candidate_id": 1,
                    "requirement_id": 1,
                    "overall_score": 0.95,
                    "skill_score": 1.0,
                    "reason": "Perfect match on all required skills",
                }
            ]
        )

        result = await matching_service.match_requirement_to_candidates(
            db_session=MagicMock(),
            requirement_id=1,
            limit=50,
            min_score=0.5,
        )

        assert result["requirement_id"] == 1
        assert result["matches_found"] == 1
        assert result["matches"][0]["overall_score"] == 0.95
        assert result["matches"][0]["skill_score"] == 1.0

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_compute_skill_match_partial(self, matching_service):
        """Test partial skill match computation."""
        matching_service.agent.match_requirement_to_candidates = AsyncMock(
            return_value=[
                {
                    "candidate_id": 2,
                    "requirement_id": 1,
                    "overall_score": 0.70,
                    "skill_score": 0.75,
                    "missing_skills": ["Docker", "Kubernetes"],
                }
            ]
        )

        result = await matching_service.match_requirement_to_candidates(
            db_session=MagicMock(),
            requirement_id=1,
            limit=50,
            min_score=0.5,
        )

        assert result["matches"][0]["skill_score"] == 0.75
        assert result["matches"][0]["missing_skills"] == ["Docker", "Kubernetes"]

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_compute_experience_score(self, matching_service):
        """Test experience score computation."""
        matching_service.agent.match_requirement_to_candidates = AsyncMock(
            return_value=[
                {
                    "candidate_id": 1,
                    "requirement_id": 1,
                    "overall_score": 0.85,
                    "experience_score": 0.90,
                }
            ]
        )

        result = await matching_service.match_requirement_to_candidates(
            db_session=MagicMock(),
            requirement_id=1,
        )

        assert result["matches"][0]["experience_score"] == 0.90

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_compute_overall_score(self, matching_service, sample_match_scores):
        """Test overall score computation."""
        matching_service.agent.match_requirement_to_candidates = AsyncMock(
            return_value=[
                {
                    "candidate_id": 1,
                    "requirement_id": 1,
                    **sample_match_scores,
                }
            ]
        )

        result = await matching_service.match_requirement_to_candidates(
            db_session=MagicMock(),
            requirement_id=1,
        )

        assert result["matches"][0]["overall_score"] == 0.85

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_bidirectional_matching(self, matching_service):
        """Test bidirectional matching (requirement to candidates)."""
        matching_service.agent.match_candidate_to_requirements = AsyncMock(
            return_value=[
                {
                    "candidate_id": 1,
                    "requirement_id": 1,
                    "overall_score": 0.82,
                },
                {
                    "candidate_id": 1,
                    "requirement_id": 2,
                    "overall_score": 0.65,
                },
            ]
        )

        result = await matching_service.match_candidate_to_requirements(
            db_session=MagicMock(),
            candidate_id=1,
            limit=50,
            min_score=0.5,
        )

        assert result["candidate_id"] == 1
        assert result["matches_found"] == 2
        assert len(result["matches"]) == 2

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_score_weights_configurable(self, matching_service):
        """Test that match weights are configurable."""
        new_weights = {
            "skill": 0.40,
            "experience": 0.30,
            "education": 0.10,
            "location": 0.10,
            "rate": 0.05,
            "availability": 0.05,
        }

        result = await matching_service.update_match_weights(
            session=MagicMock(),
            weights=new_weights,
        )

        assert result["weights"] == new_weights
        assert abs(result["total"] - 1.0) < 0.01

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_match_with_missing_skills(self, matching_service):
        """Test matching when candidate has missing skills."""
        matching_service.agent.match_requirement_to_candidates = AsyncMock(
            return_value=[
                {
                    "candidate_id": 2,
                    "requirement_id": 1,
                    "overall_score": 0.65,
                    "skill_score": 0.60,
                    "missing_skills": ["Docker", "Kubernetes", "RabbitMQ"],
                    "standout_qualities": ["Leadership", "System Design"],
                }
            ]
        )

        result = await matching_service.match_requirement_to_candidates(
            db_session=MagicMock(),
            requirement_id=1,
        )

        match = result["matches"][0]
        assert match["missing_skills"] == ["Docker", "Kubernetes", "RabbitMQ"]
        assert "Leadership" in match["standout_qualities"]

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_match_empty_candidate(self, matching_service):
        """Test matching with no candidates."""
        matching_service.agent.match_requirement_to_candidates = AsyncMock(
            return_value=[]
        )

        result = await matching_service.match_requirement_to_candidates(
            db_session=MagicMock(),
            requirement_id=1,
            min_score=0.9,  # High threshold
        )

        assert result["matches_found"] == 0
        assert result["matches"] == []

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_match_score(self, matching_service, db_session, sample_requirement, sample_candidate):
        """Test getting specific match score."""
        match_score = MatchScore(
            requirement_id=sample_requirement.id,
            candidate_id=sample_candidate.id,
            overall_score=0.85,
            skill_score=0.90,
            experience_score=0.85,
            education_score=0.80,
            location_score=0.70,
            rate_score=0.80,
            availability_score=0.95,
            culture_score=0.75,
            status=MatchStatus.MATCHED,
            matched_at=datetime.utcnow(),
        )

        db_session.add(match_score)
        db_session.commit()

        result = await matching_service.get_match_score(
            session=db_session,
            requirement_id=sample_requirement.id,
            candidate_id=sample_candidate.id,
        )

        assert result is not None
        assert result["overall_score"] == 0.85
        assert result["skill_score"] == 0.90

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_match_score_not_found(self, matching_service, db_session):
        """Test getting non-existent match score."""
        result = await matching_service.get_match_score(
            session=db_session,
            requirement_id=999,
            candidate_id=999,
        )

        assert result is None

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_weight_validation_sum_to_one(self, matching_service):
        """Test that weights must sum to 1.0."""
        invalid_weights = {
            "skill": 0.40,
            "experience": 0.30,
            "education": 0.10,
            "location": 0.10,
            "rate": 0.05,
            "availability": 0.03,  # Sums to 0.98
        }

        with pytest.raises(ValueError):
            await matching_service.update_match_weights(
                session=MagicMock(),
                weights=invalid_weights,
            )

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_batch_match_all(self, matching_service):
        """Test batch matching operation."""
        matching_service.agent.batch_match_all = AsyncMock(
            return_value={
                "requirements_processed": 5,
                "candidates_processed": 50,
                "matches_created": 120,
                "duration_seconds": 15.3,
            }
        )

        result = await matching_service.batch_match_all(
            session=MagicMock(),
            min_score=0.5,
        )

        assert result["requirements_processed"] == 5
        assert result["candidates_processed"] == 50
        assert result["matches_created"] == 120

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_recalculate_requirement_matches(self, matching_service):
        """Test recalculation of requirement matches."""
        matching_service.agent.recalculate_requirement_matches = AsyncMock(
            return_value={
                "matches_recalculated": 35,
                "new_matches": 5,
                "updated_matches": 30,
                "duration_seconds": 2.1,
            }
        )

        result = await matching_service.recalculate_requirement_matches(
            session=MagicMock(),
            requirement_id=1,
        )

        assert result["matches_recalculated"] == 35
        assert result["new_matches"] == 5

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_override_match(self, matching_service, db_session, sample_requirement, sample_candidate):
        """Test manual match score override."""
        match_score = MatchScore(
            requirement_id=sample_requirement.id,
            candidate_id=sample_candidate.id,
            overall_score=0.65,
            skill_score=0.70,
            status=MatchStatus.MATCHED,
            matched_at=datetime.utcnow(),
        )

        db_session.add(match_score)
        db_session.commit()

        result = await matching_service.override_match(
            session=db_session,
            requirement_id=sample_requirement.id,
            candidate_id=sample_candidate.id,
            override_score=0.92,
            notes="Manager override - strong soft skills",
        )

        assert result["overall_score"] == 0.92
        assert result["matched_by"] == "manual_override"
        assert result["notes"] == "Manager override - strong soft skills"

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_cache_match_results(self, matching_service, mock_redis_client):
        """Test caching match results."""
        matches = [
            {"candidate_id": 1, "overall_score": 0.85},
            {"candidate_id": 2, "overall_score": 0.78},
        ]

        result = await matching_service.cache_match_results(
            redis_client=mock_redis_client,
            requirement_id=1,
            matches=matches,
            ttl=3600,
        )

        assert result is True
        mock_redis_client.setex.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_cached_matches(self, matching_service, mock_redis_client):
        """Test retrieving cached matches."""
        import json

        cached_matches = [
            {"candidate_id": 1, "overall_score": 0.85},
            {"candidate_id": 2, "overall_score": 0.78},
        ]

        mock_redis_client.get = AsyncMock(
            return_value=json.dumps(cached_matches)
        )

        result = await matching_service.get_cached_matches(
            redis_client=mock_redis_client,
            requirement_id=1,
        )

        assert result == cached_matches

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_requirement_matches_paginated(self, matching_service, db_session, sample_requirement, sample_candidate):
        """Test paginated requirement matches."""
        for i in range(5):
            match = MatchScore(
                requirement_id=sample_requirement.id,
                candidate_id=sample_candidate.id + i,
                overall_score=0.80 - (i * 0.05),
                status=MatchStatus.MATCHED,
            )
            db_session.add(match)

        db_session.commit()

        result = await matching_service.get_requirement_matches(
            session=db_session,
            requirement_id=sample_requirement.id,
            limit=2,
            offset=0,
        )

        assert result["total"] == 5
        assert len(result["matches"]) == 2
        assert result["limit"] == 2
        assert result["offset"] == 0

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_match_error_handling(self, matching_service):
        """Test error handling in matching operations."""
        matching_service.agent.match_requirement_to_candidates = AsyncMock(
            side_effect=Exception("Database connection failed")
        )

        with pytest.raises(Exception):
            await matching_service.match_requirement_to_candidates(
                db_session=MagicMock(),
                requirement_id=1,
            )

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_score_breakdown(self, matching_service, sample_match_scores):
        """Test match score breakdown."""
        matching_service.agent.match_requirement_to_candidates = AsyncMock(
            return_value=[
                {
                    "candidate_id": 1,
                    "requirement_id": 1,
                    **sample_match_scores,
                }
            ]
        )

        result = await matching_service.match_requirement_to_candidates(
            db_session=MagicMock(),
            requirement_id=1,
        )

        match = result["matches"][0]
        assert match["skill_score"] == sample_match_scores["skill_score"]
        assert match["experience_score"] == sample_match_scores["experience_score"]
        assert match["education_score"] == sample_match_scores["education_score"]

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_standout_qualities_detection(self, matching_service):
        """Test detection of standout qualities."""
        matching_service.agent.match_requirement_to_candidates = AsyncMock(
            return_value=[
                {
                    "candidate_id": 1,
                    "requirement_id": 1,
                    "overall_score": 0.88,
                    "standout_qualities": ["Leadership", "System Design", "Mentoring"],
                }
            ]
        )

        result = await matching_service.match_requirement_to_candidates(
            db_session=MagicMock(),
            requirement_id=1,
        )

        assert "Leadership" in result["matches"][0]["standout_qualities"]
