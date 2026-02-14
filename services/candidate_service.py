"""Candidate management service."""

import logging
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.candidate import Candidate
from models.resume import Resume
from models.submission import Submission
from models.interview import Interview
from models.offer import Offer
from models.enums import CandidateStatus, SubmissionStatus

logger = logging.getLogger(__name__)


class CandidateService:
    """Service for candidate management operations."""

    def __init__(self, db: AsyncSession):
        """Initialize candidate service.

        Args:
            db: Async database session
        """
        self.db = db

    async def create_candidate(
        self,
        first_name: str,
        last_name: str,
        email: str,
        phone: Optional[str] = None,
        **kwargs,
    ) -> Candidate:
        """Create a new candidate.

        Args:
            first_name: Candidate first name
            last_name: Candidate last name
            email: Candidate email
            phone: Candidate phone
            **kwargs: Additional fields

        Returns:
            Created candidate

        Raises:
            ValueError: If email already exists
        """
        # Check if email already exists
        existing = await self.get_candidate_by_email(email)
        if existing:
            raise ValueError(f"Candidate with email {email} already exists")

        candidate = Candidate(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            status=CandidateStatus.SOURCED,
            **kwargs,
        )

        self.db.add(candidate)
        await self.db.commit()
        await self.db.refresh(candidate)

        logger.info(f"Candidate created: {candidate.id} - {email}")
        return candidate

    async def get_candidate_by_id(self, candidate_id: int) -> Optional[Candidate]:
        """Get candidate by ID with relationships.

        Args:
            candidate_id: Candidate ID

        Returns:
            Candidate object or None
        """
        stmt = (
            select(Candidate)
            .where(Candidate.id == candidate_id)
            .options(
                selectinload(Candidate.resumes),
                selectinload(Candidate.submissions),
                selectinload(Candidate.interviews),
                selectinload(Candidate.offers),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_candidate_by_email(self, email: str) -> Optional[Candidate]:
        """Get candidate by email.

        Args:
            email: Candidate email

        Returns:
            Candidate object or None
        """
        stmt = select(Candidate).where(Candidate.email == email.lower())
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def search_candidates(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        skills: Optional[List[str]] = None,
        location: Optional[str] = None,
        experience_min: Optional[float] = None,
        experience_max: Optional[float] = None,
        availability: Optional[str] = None,
        source: Optional[str] = None,
    ) -> Tuple[List[Candidate], int]:
        """Search candidates with filters.

        Args:
            skip: Number of records to skip
            limit: Maximum records to return
            status: Candidate status filter
            skills: List of required skills
            location: Location filter
            experience_min: Minimum experience in years
            experience_max: Maximum experience in years
            availability: Availability filter
            source: Source filter

        Returns:
            Tuple of (candidates list, total count)
        """
        conditions = []

        if status:
            conditions.append(Candidate.status == status)

        if location:
            conditions.append(
                or_(
                    Candidate.location_city.ilike(f"%{location}%"),
                    Candidate.location_state.ilike(f"%{location}%"),
                    Candidate.location_country.ilike(f"%{location}%"),
                )
            )

        if experience_min is not None:
            conditions.append(Candidate.total_experience_years >= experience_min)

        if experience_max is not None:
            conditions.append(Candidate.total_experience_years <= experience_max)

        if source:
            conditions.append(Candidate.source == source)

        # Build query
        where_clause = and_(*conditions) if conditions else True

        # Count total
        count_stmt = select(func.count(Candidate.id)).where(where_clause)
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0

        # Get paginated results
        stmt = (
            select(Candidate)
            .where(where_clause)
            .order_by(desc(Candidate.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        candidates = result.scalars().all()

        # Filter by skills if provided
        if skills:
            filtered_candidates = []
            for candidate in candidates:
                if candidate.skills:
                    candidate_skills = [s.get("skill", "").lower() for s in candidate.skills]
                    if any(skill.lower() in candidate_skills for skill in skills):
                        filtered_candidates.append(candidate)
            candidates = filtered_candidates

        return candidates, total

    async def update_candidate(
        self,
        candidate_id: int,
        **kwargs,
    ) -> Candidate:
        """Update candidate information.

        Args:
            candidate_id: Candidate ID
            **kwargs: Fields to update

        Returns:
            Updated candidate

        Raises:
            ValueError: If candidate not found
        """
        candidate = await self.get_candidate_by_id(candidate_id)
        if not candidate:
            raise ValueError("Candidate not found")

        # Update allowed fields
        allowed_fields = {
            "first_name", "last_name", "phone", "linkedin_url",
            "current_title", "current_company", "total_experience_years",
            "skills", "education", "desired_rate", "desired_rate_type",
            "availability_date", "work_authorization", "willing_to_relocate",
            "notes", "metadata",
        }

        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                setattr(candidate, field, value)

        self.db.add(candidate)
        await self.db.commit()
        await self.db.refresh(candidate)

        logger.info(f"Candidate updated: {candidate_id}")
        return candidate

    async def update_candidate_status(
        self,
        candidate_id: int,
        new_status: str,
    ) -> Candidate:
        """Update candidate status.

        Args:
            candidate_id: Candidate ID
            new_status: New status

        Returns:
            Updated candidate

        Raises:
            ValueError: If candidate not found
        """
        candidate = await self.get_candidate_by_id(candidate_id)
        if not candidate:
            raise ValueError("Candidate not found")

        old_status = candidate.status
        candidate.status = CandidateStatus(new_status)
        self.db.add(candidate)
        await self.db.commit()
        await self.db.refresh(candidate)

        logger.info(f"Candidate {candidate_id} status updated: {old_status} → {new_status}")
        return candidate

    async def get_candidate_timeline(self, candidate_id: int) -> Dict[str, Any]:
        """Get full activity timeline for a candidate.

        Args:
            candidate_id: Candidate ID

        Returns:
            Dictionary with timeline events

        Raises:
            ValueError: If candidate not found
        """
        candidate = await self.get_candidate_by_id(candidate_id)
        if not candidate:
            raise ValueError("Candidate not found")

        timeline = {
            "candidate_id": candidate_id,
            "events": [],
        }

        # Add creation event
        timeline["events"].append({
            "type": "candidate_created",
            "timestamp": candidate.created_at,
            "description": f"Candidate added to system",
        })

        # Get submissions
        submissions_stmt = (
            select(Submission)
            .where(Submission.candidate_id == candidate_id)
            .order_by(Submission.created_at)
        )
        submissions_result = await self.db.execute(submissions_stmt)
        submissions = submissions_result.scalars().all()

        for submission in submissions:
            timeline["events"].append({
                "type": "submission",
                "timestamp": submission.created_at,
                "description": f"Submitted for requirement {submission.requirement_id}",
                "submission_id": submission.id,
            })

        # Get interviews
        interviews_stmt = (
            select(Interview)
            .where(Interview.candidate_id == candidate_id)
            .order_by(Interview.created_at)
        )
        interviews_result = await self.db.execute(interviews_stmt)
        interviews = interviews_result.scalars().all()

        for interview in interviews:
            timeline["events"].append({
                "type": "interview",
                "timestamp": interview.created_at,
                "description": f"{interview.interview_type} interview scheduled",
                "interview_id": interview.id,
                "status": interview.status,
            })

        # Get offers
        offers_stmt = (
            select(Offer)
            .where(Offer.candidate_id == candidate_id)
            .order_by(Offer.created_at)
        )
        offers_result = await self.db.execute(offers_stmt)
        offers = offers_result.scalars().all()

        for offer in offers:
            timeline["events"].append({
                "type": "offer",
                "timestamp": offer.created_at,
                "description": f"Offer extended for requirement {offer.requirement_id}",
                "offer_id": offer.id,
                "status": offer.status,
            })

        # Sort timeline by timestamp
        timeline["events"] = sorted(timeline["events"], key=lambda x: x["timestamp"])

        return timeline

    async def add_candidate_note(
        self,
        candidate_id: int,
        note: str,
        user_id: int,
    ) -> Dict[str, Any]:
        """Add internal note to candidate.

        Args:
            candidate_id: Candidate ID
            note: Note text
            user_id: User ID who added the note

        Returns:
            Note object

        Raises:
            ValueError: If candidate not found
        """
        candidate = await self.get_candidate_by_id(candidate_id)
        if not candidate:
            raise ValueError("Candidate not found")

        # Store note in metadata
        candidate.extra_metadata = candidate.extra_metadata or {}
        if "notes" not in candidate.extra_metadata:
            candidate.extra_metadata["notes"] = []

        candidate.extra_metadata["notes"].append({
            "text": note,
            "added_by": user_id,
            "timestamp": datetime.utcnow().isoformat(),
        })

        self.db.add(candidate)
        await self.db.commit()

        logger.info(f"Note added to candidate {candidate_id}")
        return candidate.extra_metadata["notes"][-1]

    async def get_candidate_stats(self) -> Dict[str, Any]:
        """Get candidate pool statistics.

        Returns:
            Candidate statistics
        """
        # Total candidates
        total_count = await self.db.execute(
            select(func.count(Candidate.id))
        )
        total = total_count.scalar() or 0

        # By status
        status_counts = {}
        for status in CandidateStatus:
            count = await self.db.execute(
                select(func.count(Candidate.id)).where(Candidate.status == status)
            )
            status_counts[status.value] = count.scalar() or 0

        # By source
        source_counts = {}
        sources = await self.db.execute(
            select(Candidate.source).distinct().where(Candidate.source.isnot(None))
        )
        for source in sources.scalars().all():
            count = await self.db.execute(
                select(func.count(Candidate.id)).where(Candidate.source == source)
            )
            source_counts[source] = count.scalar() or 0

        # Average experience
        avg_exp = await self.db.execute(
            select(func.avg(Candidate.total_experience_years))
        )
        average_experience = float(avg_exp.scalar() or 0)

        return {
            "total_candidates": total,
            "by_status": status_counts,
            "by_source": source_counts,
            "average_experience_years": round(average_experience, 2),
        }

    async def bulk_update_status(
        self,
        candidate_ids: List[int],
        new_status: str,
    ) -> int:
        """Bulk update candidate status.

        Args:
            candidate_ids: List of candidate IDs
            new_status: New status

        Returns:
            Number of candidates updated
        """
        # Update candidates
        stmt = (
            select(Candidate)
            .where(Candidate.id.in_(candidate_ids))
        )
        result = await self.db.execute(stmt)
        candidates = result.scalars().all()

        for candidate in candidates:
            candidate.status = CandidateStatus(new_status)

        self.db.add_all(candidates)
        await self.db.commit()

        logger.info(f"Bulk updated {len(candidates)} candidates to status {new_status}")
        return len(candidates)

    async def delete_candidate(self, candidate_id: int) -> bool:
        """Delete a candidate (soft or hard delete based on business logic).

        Args:
            candidate_id: Candidate ID

        Returns:
            True if deleted, False otherwise
        """
        candidate = await self.get_candidate_by_id(candidate_id)
        if not candidate:
            return False

        # For now, do soft delete by deactivating
        candidate.is_active = False
        self.db.add(candidate)
        await self.db.commit()

        logger.info(f"Candidate deactivated: {candidate_id}")
        return True
