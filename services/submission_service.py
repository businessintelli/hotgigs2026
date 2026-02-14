"""Submission service for managing candidate submissions."""

import logging
from datetime import datetime
from typing import List, Dict, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from models.submission import Submission
from models.candidate import Candidate
from models.requirement import Requirement
from models.match import MatchScore
from models.enums import SubmissionStatus, CandidateStatus
from schemas.submission import SubmissionCreate, SubmissionUpdate

logger = logging.getLogger(__name__)


class SubmissionService:
    """Service for submission CRUD and business logic."""

    def __init__(self, db: AsyncSession):
        """Initialize submission service.

        Args:
            db: Database session
        """
        self.db = db

    async def create_submission(
        self,
        submission_data: SubmissionCreate,
    ) -> Submission:
        """Create a new submission.

        Args:
            submission_data: Submission creation data

        Returns:
            Created submission

        Raises:
            ValueError: If candidate or requirement not found
        """
        try:
            # Verify candidate exists
            result = await self.db.execute(
                select(Candidate).where(Candidate.id == submission_data.candidate_id)
            )
            if not result.scalar_one_or_none():
                raise ValueError(f"Candidate {submission_data.candidate_id} not found")

            # Verify requirement exists
            result = await self.db.execute(
                select(Requirement).where(Requirement.id == submission_data.requirement_id)
            )
            if not result.scalar_one_or_none():
                raise ValueError(f"Requirement {submission_data.requirement_id} not found")

            # Create submission
            submission = Submission(**submission_data.model_dump())
            self.db.add(submission)
            await self.db.commit()
            await self.db.refresh(submission)

            logger.info(f"Created submission {submission.id}")
            return submission

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating submission: {str(e)}")
            raise

    async def get_submission(self, submission_id: int) -> Optional[Submission]:
        """Get submission by ID.

        Args:
            submission_id: Submission ID

        Returns:
            Submission or None

        Raises:
            Exception: If database operation fails
        """
        try:
            result = await self.db.execute(
                select(Submission).where(Submission.id == submission_id)
            )
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"Error getting submission: {str(e)}")
            raise

    async def get_submissions(
        self,
        skip: int = 0,
        limit: int = 20,
        requirement_id: Optional[int] = None,
        candidate_id: Optional[int] = None,
        status: Optional[SubmissionStatus] = None,
    ) -> tuple[List[Submission], int]:
        """Get submissions with filtering and pagination.

        Args:
            skip: Skip count
            limit: Result limit
            requirement_id: Filter by requirement
            candidate_id: Filter by candidate
            status: Filter by status

        Returns:
            Tuple of submissions list and total count

        Raises:
            Exception: If database operation fails
        """
        try:
            query = select(Submission)
            count_query = select(func.count(Submission.id))

            # Apply filters
            filters = []
            if requirement_id:
                filters.append(Submission.requirement_id == requirement_id)
            if candidate_id:
                filters.append(Submission.candidate_id == candidate_id)
            if status:
                filters.append(Submission.status == status)

            if filters:
                query = query.where(and_(*filters))
                count_query = count_query.where(and_(*filters))

            # Get total count
            result = await self.db.execute(count_query)
            total = result.scalar() or 0

            # Get paginated results
            result = await self.db.execute(
                query.order_by(desc(Submission.created_at))
                .offset(skip)
                .limit(limit)
            )
            submissions = result.scalars().all()

            logger.info(f"Retrieved {len(submissions)} submissions")
            return submissions, total

        except Exception as e:
            logger.error(f"Error getting submissions: {str(e)}")
            raise

    async def update_submission(
        self,
        submission_id: int,
        submission_data: SubmissionUpdate,
    ) -> Submission:
        """Update submission.

        Args:
            submission_id: Submission ID
            submission_data: Update data

        Returns:
            Updated submission

        Raises:
            ValueError: If submission not found
        """
        try:
            # Fetch submission
            result = await self.db.execute(
                select(Submission).where(Submission.id == submission_id)
            )
            submission = result.scalar_one_or_none()

            if not submission:
                raise ValueError(f"Submission {submission_id} not found")

            # Update fields
            update_data = submission_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(submission, field, value)

            self.db.add(submission)
            await self.db.commit()
            await self.db.refresh(submission)

            logger.info(f"Updated submission {submission_id}")
            return submission

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating submission: {str(e)}")
            raise

    async def delete_submission(self, submission_id: int) -> bool:
        """Soft delete submission.

        Args:
            submission_id: Submission ID

        Returns:
            True if successful

        Raises:
            ValueError: If submission not found
        """
        try:
            # Fetch submission
            result = await self.db.execute(
                select(Submission).where(Submission.id == submission_id)
            )
            submission = result.scalar_one_or_none()

            if not submission:
                raise ValueError(f"Submission {submission_id} not found")

            # Soft delete
            submission.is_active = False
            self.db.add(submission)
            await self.db.commit()

            logger.info(f"Deleted submission {submission_id}")
            return True

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting submission: {str(e)}")
            raise

    async def get_submissions_by_requirement(
        self,
        requirement_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[Submission], int]:
        """Get all submissions for a requirement.

        Args:
            requirement_id: Requirement ID
            skip: Skip count
            limit: Result limit

        Returns:
            Tuple of submissions and count

        Raises:
            Exception: If database operation fails
        """
        return await self.get_submissions(
            skip=skip,
            limit=limit,
            requirement_id=requirement_id,
        )

    async def get_submissions_by_candidate(
        self,
        candidate_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[Submission], int]:
        """Get all submissions for a candidate.

        Args:
            candidate_id: Candidate ID
            skip: Skip count
            limit: Result limit

        Returns:
            Tuple of submissions and count

        Raises:
            Exception: If database operation fails
        """
        return await self.get_submissions(
            skip=skip,
            limit=limit,
            candidate_id=candidate_id,
        )

    async def get_submissions_by_status(
        self,
        status: SubmissionStatus,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[Submission], int]:
        """Get submissions by status.

        Args:
            status: Submission status
            skip: Skip count
            limit: Result limit

        Returns:
            Tuple of submissions and count

        Raises:
            Exception: If database operation fails
        """
        return await self.get_submissions(
            skip=skip,
            limit=limit,
            status=status,
        )

    async def get_pending_approvals(
        self,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[Submission], int]:
        """Get submissions pending internal review.

        Args:
            skip: Skip count
            limit: Result limit

        Returns:
            Tuple of submissions and count

        Raises:
            Exception: If database operation fails
        """
        try:
            query = select(Submission).where(
                Submission.status == SubmissionStatus.PENDING_REVIEW
            )
            count_query = select(func.count(Submission.id)).where(
                Submission.status == SubmissionStatus.PENDING_REVIEW
            )

            # Get total
            result = await self.db.execute(count_query)
            total = result.scalar() or 0

            # Get paginated
            result = await self.db.execute(
                query.order_by(desc(Submission.created_at))
                .offset(skip)
                .limit(limit)
            )
            submissions = result.scalars().all()

            logger.info(f"Retrieved {len(submissions)} pending approvals")
            return submissions, total

        except Exception as e:
            logger.error(f"Error getting pending approvals: {str(e)}")
            raise

    async def get_shortlisted_candidates(
        self,
        requirement_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[Submission], int]:
        """Get shortlisted submissions for requirement.

        Args:
            requirement_id: Requirement ID
            skip: Skip count
            limit: Result limit

        Returns:
            Tuple of submissions and count

        Raises:
            Exception: If database operation fails
        """
        try:
            query = select(Submission).where(
                and_(
                    Submission.requirement_id == requirement_id,
                    Submission.status == SubmissionStatus.SHORTLISTED,
                )
            )
            count_query = select(func.count(Submission.id)).where(
                and_(
                    Submission.requirement_id == requirement_id,
                    Submission.status == SubmissionStatus.SHORTLISTED,
                )
            )

            # Get total
            result = await self.db.execute(count_query)
            total = result.scalar() or 0

            # Get paginated
            result = await self.db.execute(
                query.order_by(desc(Submission.created_at))
                .offset(skip)
                .limit(limit)
            )
            submissions = result.scalars().all()

            logger.info(f"Retrieved {len(submissions)} shortlisted submissions")
            return submissions, total

        except Exception as e:
            logger.error(f"Error getting shortlisted: {str(e)}")
            raise

    async def get_submission_pipeline_stats(
        self,
        requirement_id: int,
    ) -> Dict[str, Any]:
        """Get pipeline statistics for requirement.

        Args:
            requirement_id: Requirement ID

        Returns:
            Pipeline statistics

        Raises:
            Exception: If database operation fails
        """
        try:
            # Get all submissions for requirement
            result = await self.db.execute(
                select(Submission).where(
                    Submission.requirement_id == requirement_id
                )
            )
            submissions = result.scalars().all()

            # Count by status
            status_counts = {}
            for submission in submissions:
                status = submission.status.value
                status_counts[status] = status_counts.get(status, 0) + 1

            # Calculate time metrics
            approved_with_response = [
                s for s in submissions
                if s.status == SubmissionStatus.APPROVED
                and s.reviewed_at
                and s.submitted_to_customer_at
            ]
            avg_time_to_approval = 0
            if approved_with_response:
                times = [
                    (s.submitted_to_customer_at - s.reviewed_at).days
                    for s in approved_with_response
                ]
                avg_time_to_approval = sum(times) / len(times)

            # Conversion rates
            total = len(submissions)
            conversion_rates = {
                status: (count / total * 100) if total > 0 else 0
                for status, count in status_counts.items()
            }

            stats = {
                "total_submissions": total,
                "status_distribution": status_counts,
                "conversion_rates": conversion_rates,
                "average_days_to_approval": avg_time_to_approval,
                "shortlist_rate": (
                    status_counts.get(SubmissionStatus.SHORTLISTED.value, 0)
                    / total
                    * 100
                    if total > 0
                    else 0
                ),
                "rejection_rate": (
                    status_counts.get(SubmissionStatus.REJECTED.value, 0)
                    / total
                    * 100
                    if total > 0
                    else 0
                ),
            }

            logger.info(f"Generated pipeline stats for requirement {requirement_id}")
            return stats

        except Exception as e:
            logger.error(f"Error getting pipeline stats: {str(e)}")
            raise

    async def search_submissions(
        self,
        query: str,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[Submission], int]:
        """Search submissions by candidate name or email.

        Args:
            query: Search query
            skip: Skip count
            limit: Result limit

        Returns:
            Tuple of submissions and count

        Raises:
            Exception: If database operation fails
        """
        try:
            search_query = select(Submission).join(Candidate).where(
                or_(
                    Candidate.first_name.contains(query),
                    Candidate.last_name.contains(query),
                    Candidate.email.contains(query),
                )
            )

            count_query = select(func.count(Submission.id)).select_from(
                Submission
            ).join(Candidate).where(
                or_(
                    Candidate.first_name.contains(query),
                    Candidate.last_name.contains(query),
                    Candidate.email.contains(query),
                )
            )

            # Get total
            result = await self.db.execute(count_query)
            total = result.scalar() or 0

            # Get paginated
            result = await self.db.execute(
                search_query.order_by(desc(Submission.created_at))
                .offset(skip)
                .limit(limit)
            )
            submissions = result.scalars().all()

            logger.info(f"Found {len(submissions)} submissions matching '{query}'")
            return submissions, total

        except Exception as e:
            logger.error(f"Error searching submissions: {str(e)}")
            raise

    async def bulk_update_status(
        self,
        submission_ids: List[int],
        status: SubmissionStatus,
    ) -> int:
        """Update status for multiple submissions.

        Args:
            submission_ids: List of submission IDs
            status: New status

        Returns:
            Number of updated submissions

        Raises:
            Exception: If database operation fails
        """
        try:
            result = await self.db.execute(
                select(Submission).where(Submission.id.in_(submission_ids))
            )
            submissions = result.scalars().all()

            for submission in submissions:
                submission.status = status
                self.db.add(submission)

            await self.db.commit()

            logger.info(f"Updated {len(submissions)} submissions to {status}")
            return len(submissions)

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error bulk updating submissions: {str(e)}")
            raise
