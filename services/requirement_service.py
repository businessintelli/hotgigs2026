"""Requirement management service."""

import logging
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.requirement import Requirement
from models.submission import Submission
from models.interview import Interview
from models.offer import Offer
from models.match import MatchScore
from models.enums import RequirementStatus, Priority, SubmissionStatus, OfferStatus

logger = logging.getLogger(__name__)


class RequirementService:
    """Service for requirement management operations."""

    def __init__(self, db: AsyncSession):
        """Initialize requirement service.

        Args:
            db: Async database session
        """
        self.db = db

    async def create_requirement(
        self,
        customer_id: int,
        title: str,
        description: Optional[str] = None,
        **kwargs,
    ) -> Requirement:
        """Create a new requirement.

        Args:
            customer_id: Customer ID
            title: Requirement title
            description: Job description
            **kwargs: Additional fields

        Returns:
            Created requirement

        Raises:
            ValueError: If customer not found
        """
        requirement = Requirement(
            customer_id=customer_id,
            title=title,
            description=description,
            status=RequirementStatus.DRAFT,
            **kwargs,
        )

        self.db.add(requirement)
        await self.db.commit()
        await self.db.refresh(requirement)

        logger.info(f"Requirement created: {requirement.id} - {title}")
        return requirement

    async def get_requirement_by_id(self, requirement_id: int) -> Optional[Requirement]:
        """Get requirement by ID with relationships.

        Args:
            requirement_id: Requirement ID

        Returns:
            Requirement object or None
        """
        stmt = (
            select(Requirement)
            .where(Requirement.id == requirement_id)
            .options(
                selectinload(Requirement.match_scores),
                selectinload(Requirement.submissions),
                selectinload(Requirement.interviews),
                selectinload(Requirement.offers),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def search_requirements(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        customer_id: Optional[int] = None,
        priority: Optional[str] = None,
        skills: Optional[List[str]] = None,
        recruiter_id: Optional[int] = None,
    ) -> Tuple[List[Requirement], int]:
        """Search requirements with filters.

        Args:
            skip: Number of records to skip
            limit: Maximum records to return
            status: Requirement status filter
            customer_id: Customer ID filter
            priority: Priority filter
            skills: Required skills filter
            recruiter_id: Recruiter ID filter

        Returns:
            Tuple of (requirements list, total count)
        """
        conditions = []

        if status:
            conditions.append(Requirement.status == status)

        if customer_id:
            conditions.append(Requirement.customer_id == customer_id)

        if priority:
            conditions.append(Requirement.priority == priority)

        if recruiter_id:
            conditions.append(Requirement.assigned_recruiter_id == recruiter_id)

        # Build query
        where_clause = and_(*conditions) if conditions else True

        # Count total
        count_stmt = select(func.count(Requirement.id)).where(where_clause)
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0

        # Get paginated results
        stmt = (
            select(Requirement)
            .where(where_clause)
            .order_by(desc(Requirement.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        requirements = result.scalars().all()

        # Filter by skills if provided
        if skills:
            filtered_requirements = []
            for req in requirements:
                if req.skills_required:
                    req_skills = [s.get("skill", "").lower() for s in req.skills_required]
                    if any(skill.lower() in req_skills for skill in skills):
                        filtered_requirements.append(req)
            requirements = filtered_requirements

        return requirements, total

    async def update_requirement(
        self,
        requirement_id: int,
        **kwargs,
    ) -> Requirement:
        """Update requirement information.

        Args:
            requirement_id: Requirement ID
            **kwargs: Fields to update

        Returns:
            Updated requirement

        Raises:
            ValueError: If requirement not found
        """
        requirement = await self.get_requirement_by_id(requirement_id)
        if not requirement:
            raise ValueError("Requirement not found")

        # Update allowed fields
        allowed_fields = {
            "title", "description", "skills_required", "skills_preferred",
            "experience_min", "experience_max", "education_level",
            "employment_type", "work_mode", "location_city", "location_state",
            "location_country", "rate_min", "rate_max", "rate_type",
            "duration_months", "positions_count", "priority", "notes", "metadata",
        }

        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                setattr(requirement, field, value)

        self.db.add(requirement)
        await self.db.commit()
        await self.db.refresh(requirement)

        logger.info(f"Requirement updated: {requirement_id}")
        return requirement

    async def activate_requirement(self, requirement_id: int) -> Requirement:
        """Activate a requirement.

        Args:
            requirement_id: Requirement ID

        Returns:
            Updated requirement

        Raises:
            ValueError: If requirement not found or invalid state
        """
        requirement = await self.get_requirement_by_id(requirement_id)
        if not requirement:
            raise ValueError("Requirement not found")

        if requirement.status not in [RequirementStatus.DRAFT, RequirementStatus.ON_HOLD]:
            raise ValueError(f"Cannot activate requirement in {requirement.status} status")

        requirement.status = RequirementStatus.ACTIVE
        requirement.start_date = datetime.utcnow().date()

        self.db.add(requirement)
        await self.db.commit()
        await self.db.refresh(requirement)

        logger.info(f"Requirement activated: {requirement_id}")
        return requirement

    async def close_requirement(
        self,
        requirement_id: int,
        close_reason: Optional[str] = None,
    ) -> Requirement:
        """Close a requirement.

        Args:
            requirement_id: Requirement ID
            close_reason: Reason for closing

        Returns:
            Updated requirement

        Raises:
            ValueError: If requirement not found
        """
        requirement = await self.get_requirement_by_id(requirement_id)
        if not requirement:
            raise ValueError("Requirement not found")

        requirement.status = RequirementStatus.CLOSED
        if requirement.extra_metadata is None:
            requirement.extra_metadata = {}
        requirement.extra_metadata["closed_at"] = datetime.utcnow().isoformat()
        if close_reason:
            requirement.extra_metadata["close_reason"] = close_reason

        self.db.add(requirement)
        await self.db.commit()
        await self.db.refresh(requirement)

        logger.info(f"Requirement closed: {requirement_id}")
        return requirement

    async def get_requirement_pipeline(
        self,
        requirement_id: int,
    ) -> Dict[str, Any]:
        """Get candidate pipeline for a requirement.

        Args:
            requirement_id: Requirement ID

        Returns:
            Pipeline data with candidates at each stage

        Raises:
            ValueError: If requirement not found
        """
        requirement = await self.get_requirement_by_id(requirement_id)
        if not requirement:
            raise ValueError("Requirement not found")

        # Get all submissions for this requirement
        submissions_stmt = (
            select(Submission)
            .where(Submission.requirement_id == requirement_id)
            .order_by(Submission.created_at)
        )
        submissions_result = await self.db.execute(submissions_stmt)
        submissions = submissions_result.scalars().all()

        # Group by status
        pipeline = {
            "requirement_id": requirement_id,
            "requirement_title": requirement.title,
            "stages": {},
        }

        for status in SubmissionStatus:
            stage_submissions = [s for s in submissions if s.status == status]
            pipeline["stages"][status.value] = {
                "count": len(stage_submissions),
                "submissions": [s.id for s in stage_submissions],
            }

        return pipeline

    async def get_requirement_submissions(
        self,
        requirement_id: int,
        status: Optional[str] = None,
    ) -> List[Submission]:
        """Get all submissions for a requirement.

        Args:
            requirement_id: Requirement ID
            status: Optional status filter

        Returns:
            List of submissions
        """
        conditions = [Submission.requirement_id == requirement_id]

        if status:
            conditions.append(Submission.status == status)

        stmt = (
            select(Submission)
            .where(and_(*conditions))
            .order_by(desc(Submission.created_at))
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_requirement_timeline(
        self,
        requirement_id: int,
    ) -> Dict[str, Any]:
        """Get activity timeline for a requirement.

        Args:
            requirement_id: Requirement ID

        Returns:
            Timeline events

        Raises:
            ValueError: If requirement not found
        """
        requirement = await self.get_requirement_by_id(requirement_id)
        if not requirement:
            raise ValueError("Requirement not found")

        timeline = {
            "requirement_id": requirement_id,
            "events": [],
        }

        # Add creation event
        timeline["events"].append({
            "type": "requirement_created",
            "timestamp": requirement.created_at,
            "description": f"Requirement created: {requirement.title}",
        })

        # Add activation event
        if requirement.status == RequirementStatus.ACTIVE:
            timeline["events"].append({
                "type": "requirement_activated",
                "timestamp": requirement.start_date if requirement.start_date else requirement.created_at,
                "description": "Requirement activated",
            })

        # Get submissions
        submissions_stmt = (
            select(Submission)
            .where(Submission.requirement_id == requirement_id)
            .order_by(Submission.created_at)
        )
        submissions_result = await self.db.execute(submissions_stmt)
        submissions = submissions_result.scalars().all()

        for submission in submissions:
            timeline["events"].append({
                "type": "submission",
                "timestamp": submission.created_at,
                "description": f"Submission received for candidate {submission.candidate_id}",
                "submission_id": submission.id,
                "status": submission.status.value,
            })

        # Get offers
        offers_stmt = (
            select(Offer)
            .where(Offer.requirement_id == requirement_id)
            .order_by(Offer.created_at)
        )
        offers_result = await self.db.execute(offers_stmt)
        offers = offers_result.scalars().all()

        for offer in offers:
            timeline["events"].append({
                "type": "offer",
                "timestamp": offer.created_at,
                "description": f"Offer extended to candidate {offer.candidate_id}",
                "offer_id": offer.id,
                "status": offer.status.value,
            })

        # Sort timeline
        timeline["events"] = sorted(timeline["events"], key=lambda x: x["timestamp"])

        return timeline

    async def get_requirement_stats(self) -> Dict[str, Any]:
        """Get requirement statistics.

        Returns:
            Requirement statistics
        """
        # Total requirements
        total_count = await self.db.execute(
            select(func.count(Requirement.id))
        )
        total = total_count.scalar() or 0

        # By status
        status_counts = {}
        for status in RequirementStatus:
            count = await self.db.execute(
                select(func.count(Requirement.id)).where(Requirement.status == status)
            )
            status_counts[status.value] = count.scalar() or 0

        # By priority
        priority_counts = {}
        for priority in Priority:
            count = await self.db.execute(
                select(func.count(Requirement.id)).where(Requirement.priority == priority)
            )
            priority_counts[priority.value] = count.scalar() or 0

        # Total positions
        total_positions = await self.db.execute(
            select(func.sum(Requirement.positions_count))
        )
        total_pos = total_positions.scalar() or 0

        # Filled positions
        filled_positions = await self.db.execute(
            select(func.sum(Requirement.positions_filled))
        )
        filled_pos = filled_positions.scalar() or 0

        return {
            "total_requirements": total,
            "by_status": status_counts,
            "by_priority": priority_counts,
            "total_positions_open": total_pos - filled_pos,
            "total_positions_filled": filled_pos,
            "fill_rate": round((filled_pos / total_pos * 100) if total_pos > 0 else 0, 2),
        }

    async def update_positions_filled(
        self,
        requirement_id: int,
        positions_filled: int,
    ) -> Requirement:
        """Update number of positions filled.

        Args:
            requirement_id: Requirement ID
            positions_filled: Number of positions filled

        Returns:
            Updated requirement

        Raises:
            ValueError: If requirement not found or invalid count
        """
        requirement = await self.get_requirement_by_id(requirement_id)
        if not requirement:
            raise ValueError("Requirement not found")

        if positions_filled > requirement.positions_count:
            raise ValueError(
                f"Cannot fill {positions_filled} positions, only {requirement.positions_count} open"
            )

        requirement.positions_filled = positions_filled

        # Auto-close if all positions filled
        if positions_filled >= requirement.positions_count:
            requirement.status = RequirementStatus.FILLED

        self.db.add(requirement)
        await self.db.commit()
        await self.db.refresh(requirement)

        logger.info(f"Requirement {requirement_id} positions filled updated to {positions_filled}")
        return requirement
