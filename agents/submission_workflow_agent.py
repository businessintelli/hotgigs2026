"""Submission workflow agent for managing candidate submissions."""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from agents.base_agent import BaseAgent
from agents.events import EventType
from models.submission import Submission
from models.candidate import Candidate
from models.requirement import Requirement
from models.user import User
from models.interview import InterviewFeedback
from models.match import MatchScore
from models.resume import Resume
from models.enums import (
    SubmissionStatus,
    CandidateStatus,
    RequirementStatus,
)

logger = logging.getLogger(__name__)


class SubmissionWorkflowAgent(BaseAgent):
    """Agent for managing submission workflow and candidate submissions to customers."""

    def __init__(self):
        """Initialize the submission workflow agent."""
        super().__init__(
            agent_name="SubmissionWorkflowAgent",
            agent_version="1.0.0",
        )
        self.sla_days = 7  # Default SLA is 7 days

    async def package_candidate(
        self,
        db: AsyncSession,
        candidate_id: int,
        requirement_id: int,
    ) -> Dict[str, Any]:
        """Assemble full candidate package for submission.

        Fetches candidate, resume, match scores, interview feedback,
        and generates AI recommendation summary.

        Args:
            db: Database session
            candidate_id: Candidate ID
            requirement_id: Requirement ID

        Returns:
            Dictionary with complete candidate package data

        Raises:
            ValueError: If candidate or requirement not found
        """
        try:
            # Fetch candidate
            result = await db.execute(
                select(Candidate).where(Candidate.id == candidate_id)
            )
            candidate = result.scalar_one_or_none()

            if not candidate:
                raise ValueError(f"Candidate {candidate_id} not found")

            # Fetch requirement
            result = await db.execute(
                select(Requirement).where(Requirement.id == requirement_id)
            )
            requirement = result.scalar_one_or_none()

            if not requirement:
                raise ValueError(f"Requirement {requirement_id} not found")

            # Fetch latest resume
            result = await db.execute(
                select(Resume)
                .where(Resume.candidate_id == candidate_id)
                .order_by(Resume.created_at.desc())
            )
            resume = result.scalar_one_or_none()

            # Fetch match score
            result = await db.execute(
                select(MatchScore).where(
                    and_(
                        MatchScore.candidate_id == candidate_id,
                        MatchScore.requirement_id == requirement_id,
                    )
                )
            )
            match_score = result.scalar_one_or_none()

            # Fetch interview feedback
            result = await db.execute(
                select(InterviewFeedback)
                .where(InterviewFeedback.candidate_id == candidate_id)
                .order_by(InterviewFeedback.created_at.desc())
                .limit(5)
            )
            interview_feedback = result.scalars().all()

            # Build package
            package = {
                "candidate": {
                    "id": candidate.id,
                    "name": candidate.full_name,
                    "email": candidate.email,
                    "phone": candidate.phone,
                    "current_title": candidate.current_title,
                    "current_company": candidate.current_company,
                    "total_experience_years": candidate.total_experience_years,
                    "location": {
                        "city": candidate.location_city,
                        "state": candidate.location_state,
                        "country": candidate.location_country,
                    },
                    "skills": candidate.skills,
                    "education": candidate.education,
                    "certifications": candidate.certifications,
                    "desired_rate": candidate.desired_rate,
                    "availability_date": candidate.availability_date.isoformat()
                    if candidate.availability_date
                    else None,
                    "work_authorization": candidate.work_authorization,
                    "willing_to_relocate": candidate.willing_to_relocate,
                    "linkedin_url": candidate.linkedin_url,
                },
                "resume": {
                    "id": resume.id if resume else None,
                    "url": resume.file_path if resume else None,
                    "parsed_text": resume.parsed_text[:500] if resume and resume.parsed_text else None,
                    "uploaded_at": resume.created_at.isoformat() if resume else None,
                },
                "match_score": {
                    "overall_score": match_score.overall_score if match_score else None,
                    "skill_score": match_score.skill_score if match_score else None,
                    "experience_score": match_score.experience_score if match_score else None,
                    "education_score": match_score.education_score if match_score else None,
                    "location_score": match_score.location_score if match_score else None,
                    "rate_score": match_score.rate_score if match_score else None,
                    "matching_reason": match_score.matching_reason if match_score else None,
                },
                "interview_feedback": [
                    {
                        "id": fb.id,
                        "score": fb.overall_score,
                        "feedback": fb.feedback[:200],
                        "date": fb.created_at.isoformat(),
                    }
                    for fb in interview_feedback
                ],
                "requirement": {
                    "id": requirement.id,
                    "title": requirement.title,
                    "skills_required": requirement.skills_required,
                    "experience_min": requirement.experience_min,
                    "experience_max": requirement.experience_max,
                    "rate_min": requirement.rate_min,
                    "rate_max": requirement.rate_max,
                },
                "recommendation_summary": self._generate_recommendation_summary(
                    candidate, match_score, interview_feedback, requirement
                ),
            }

            logger.info(f"Packaged candidate {candidate_id} for requirement {requirement_id}")
            return package

        except Exception as e:
            logger.error(f"Error packaging candidate: {str(e)}")
            raise

    async def submit_for_internal_review(
        self,
        db: AsyncSession,
        submission_id: int,
    ) -> Submission:
        """Submit submission for internal review.

        Changes status to PENDING_REVIEW, assigns reviewer based on
        requirement's assigned recruiter's manager, sends notification event.

        Args:
            db: Database session
            submission_id: Submission ID

        Returns:
            Updated submission

        Raises:
            ValueError: If submission not found or invalid state
        """
        try:
            # Fetch submission with relations
            result = await db.execute(
                select(Submission)
                .where(Submission.id == submission_id)
            )
            submission = result.scalar_one_or_none()

            if not submission:
                raise ValueError(f"Submission {submission_id} not found")

            if submission.status != SubmissionStatus.DRAFT:
                raise ValueError(
                    f"Can only submit DRAFT submissions for review. Current status: {submission.status}"
                )

            # Fetch requirement to get assigned recruiter
            result = await db.execute(
                select(Requirement).where(Requirement.id == submission.requirement_id)
            )
            requirement = result.scalar_one_or_none()

            if requirement and requirement.assigned_recruiter_id:
                # In production, would fetch recruiter's manager
                submission.reviewed_by = requirement.assigned_recruiter_id

            # Update submission status
            submission.status = SubmissionStatus.PENDING_REVIEW
            db.add(submission)
            await db.commit()
            await db.refresh(submission)

            # Emit event
            await self.emit_event(
                event_type=EventType.SUBMISSION_CREATED,
                entity_type="Submission",
                entity_id=submission.id,
                payload={
                    "submission_id": submission.id,
                    "candidate_id": submission.candidate_id,
                    "status": SubmissionStatus.PENDING_REVIEW.value,
                },
                user_id=submission.submitted_by,
            )

            logger.info(f"Submitted submission {submission_id} for internal review")
            return submission

        except Exception as e:
            await db.rollback()
            logger.error(f"Error submitting for review: {str(e)}")
            raise

    async def process_approval(
        self,
        db: AsyncSession,
        submission_id: int,
        approved: bool,
        reviewer_id: int,
        notes: str,
    ) -> Submission:
        """Process submission approval or rejection.

        If approved → APPROVED status. If rejected → back to DRAFT with feedback.
        Records reviewer and timestamp.

        Args:
            db: Database session
            submission_id: Submission ID
            approved: Whether submission is approved
            reviewer_id: User ID of reviewer
            notes: Reviewer notes/feedback

        Returns:
            Updated submission

        Raises:
            ValueError: If submission not found or invalid state
        """
        try:
            # Fetch submission
            result = await db.execute(
                select(Submission).where(Submission.id == submission_id)
            )
            submission = result.scalar_one_or_none()

            if not submission:
                raise ValueError(f"Submission {submission_id} not found")

            # Update submission
            submission.reviewed_by = reviewer_id
            submission.reviewed_at = datetime.utcnow()

            if approved:
                submission.status = SubmissionStatus.APPROVED
                event_type = EventType.SUBMISSION_APPROVED
            else:
                submission.status = SubmissionStatus.DRAFT
                submission.rejection_reason = notes
                event_type = EventType.SUBMISSION_REJECTED

            submission.internal_notes = notes
            db.add(submission)
            await db.commit()
            await db.refresh(submission)

            # Emit event
            await self.emit_event(
                event_type=event_type,
                entity_type="Submission",
                entity_id=submission.id,
                payload={
                    "submission_id": submission.id,
                    "candidate_id": submission.candidate_id,
                    "approved": approved,
                    "notes": notes,
                },
                user_id=reviewer_id,
            )

            logger.info(
                f"Processed submission {submission_id}: {'APPROVED' if approved else 'REJECTED'}"
            )
            return submission

        except Exception as e:
            await db.rollback()
            logger.error(f"Error processing approval: {str(e)}")
            raise

    async def submit_to_customer(
        self,
        db: AsyncSession,
        submission_id: int,
    ) -> Submission:
        """Submit approved submission to customer.

        Validates status is APPROVED, changes to SUBMITTED, sets submitted_to_customer_at,
        emits event for notification.

        Args:
            db: Database session
            submission_id: Submission ID

        Returns:
            Updated submission

        Raises:
            ValueError: If submission not found or not approved
        """
        try:
            # Fetch submission
            result = await db.execute(
                select(Submission).where(Submission.id == submission_id)
            )
            submission = result.scalar_one_or_none()

            if not submission:
                raise ValueError(f"Submission {submission_id} not found")

            if submission.status != SubmissionStatus.APPROVED:
                raise ValueError(
                    f"Can only submit APPROVED submissions. Current status: {submission.status}"
                )

            # Update submission
            submission.status = SubmissionStatus.SUBMITTED
            submission.submitted_to_customer_at = datetime.utcnow()
            db.add(submission)
            await db.commit()
            await db.refresh(submission)

            # Emit event
            await self.emit_event(
                event_type=EventType.SUBMISSION_SENT,
                entity_type="Submission",
                entity_id=submission.id,
                payload={
                    "submission_id": submission.id,
                    "candidate_id": submission.candidate_id,
                    "customer_id": submission.customer_id,
                    "submitted_at": submission.submitted_to_customer_at.isoformat(),
                },
                user_id=submission.submitted_by,
            )

            logger.info(f"Submitted submission {submission_id} to customer")
            return submission

        except Exception as e:
            await db.rollback()
            logger.error(f"Error submitting to customer: {str(e)}")
            raise

    async def track_customer_response(
        self,
        db: AsyncSession,
        submission_id: int,
        response: str,
        shortlisted: bool,
        feedback: str,
    ) -> Submission:
        """Track customer response to submission.

        Updates status to SHORTLISTED or REJECTED, records response.

        Args:
            db: Database session
            submission_id: Submission ID
            response: Customer response text
            shortlisted: Whether candidate was shortlisted
            feedback: Customer feedback

        Returns:
            Updated submission

        Raises:
            ValueError: If submission not found
        """
        try:
            # Fetch submission
            result = await db.execute(
                select(Submission).where(Submission.id == submission_id)
            )
            submission = result.scalar_one_or_none()

            if not submission:
                raise ValueError(f"Submission {submission_id} not found")

            # Update submission
            submission.customer_response = response
            submission.customer_response_at = datetime.utcnow()
            submission.customer_notes = feedback

            if shortlisted:
                submission.status = SubmissionStatus.SHORTLISTED
                # Update candidate status
                result = await db.execute(
                    select(Candidate).where(Candidate.id == submission.candidate_id)
                )
                candidate = result.scalar_one_or_none()
                if candidate:
                    candidate.status = CandidateStatus.CUSTOMER_REVIEW
                    db.add(candidate)
            else:
                submission.status = SubmissionStatus.REJECTED
                submission.rejection_reason = feedback

            db.add(submission)
            await db.commit()
            await db.refresh(submission)

            # Emit event
            await self.emit_event(
                event_type=EventType.SUBMISSION_REJECTED if not shortlisted else EventType.MATCH_SHORTLISTED,
                entity_type="Submission",
                entity_id=submission.id,
                payload={
                    "submission_id": submission.id,
                    "candidate_id": submission.candidate_id,
                    "shortlisted": shortlisted,
                    "feedback": feedback,
                },
            )

            logger.info(f"Tracked customer response for submission {submission_id}")
            return submission

        except Exception as e:
            await db.rollback()
            logger.error(f"Error tracking customer response: {str(e)}")
            raise

    async def withdraw_submission(
        self,
        db: AsyncSession,
        submission_id: int,
        reason: str,
    ) -> Submission:
        """Withdraw submission from consideration.

        Sets WITHDRAWN status and stores reason.

        Args:
            db: Database session
            submission_id: Submission ID
            reason: Withdrawal reason

        Returns:
            Updated submission

        Raises:
            ValueError: If submission not found
        """
        try:
            # Fetch submission
            result = await db.execute(
                select(Submission).where(Submission.id == submission_id)
            )
            submission = result.scalar_one_or_none()

            if not submission:
                raise ValueError(f"Submission {submission_id} not found")

            # Update submission
            submission.status = SubmissionStatus.WITHDRAWN
            submission.rejection_reason = reason
            db.add(submission)
            await db.commit()
            await db.refresh(submission)

            # Emit event
            await self.emit_event(
                event_type=EventType.SUBMISSION_WITHDRAWN,
                entity_type="Submission",
                entity_id=submission.id,
                payload={
                    "submission_id": submission.id,
                    "candidate_id": submission.candidate_id,
                    "reason": reason,
                },
            )

            logger.info(f"Withdrawn submission {submission_id}")
            return submission

        except Exception as e:
            await db.rollback()
            logger.error(f"Error withdrawing submission: {str(e)}")
            raise

    async def check_sla_compliance(
        self,
        db: AsyncSession,
    ) -> List[Submission]:
        """Find submissions past SLA deadlines.

        Returns list of overdue submissions based on submission_deadline.

        Args:
            db: Database session

        Returns:
            List of overdue submissions
        """
        try:
            # Find submissions with overdue requirements
            result = await db.execute(
                select(Submission)
                .join(Requirement)
                .where(
                    and_(
                        Requirement.submission_deadline.isnot(None),
                        Requirement.submission_deadline < datetime.utcnow().date(),
                        Submission.status.in_(
                            [
                                SubmissionStatus.DRAFT,
                                SubmissionStatus.PENDING_REVIEW,
                            ]
                        ),
                    )
                )
            )
            overdue_submissions = result.scalars().all()

            logger.info(f"Found {len(overdue_submissions)} overdue submissions")
            return overdue_submissions

        except Exception as e:
            logger.error(f"Error checking SLA compliance: {str(e)}")
            raise

    async def get_submission_analytics(
        self,
        db: AsyncSession,
        requirement_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get submission analytics and conversion metrics.

        Calculates conversion rates by stage, avg time per stage,
        rejection reasons breakdown.

        Args:
            db: Database session
            requirement_id: Optional requirement ID to filter by

        Returns:
            Dictionary with analytics

        Raises:
            ValueError: If requirement not found
        """
        try:
            # Build query
            query = select(Submission)
            if requirement_id:
                query = query.where(Submission.requirement_id == requirement_id)
                # Verify requirement exists
                result = await db.execute(
                    select(Requirement).where(Requirement.id == requirement_id)
                )
                if not result.scalar_one_or_none():
                    raise ValueError(f"Requirement {requirement_id} not found")

            # Fetch all submissions
            result = await db.execute(query)
            submissions = result.scalars().all()

            # Calculate metrics
            total = len(submissions)
            status_counts = {}
            rejection_reasons = {}
            stage_times = {}

            for submission in submissions:
                # Count by status
                status = submission.status.value
                status_counts[status] = status_counts.get(status, 0) + 1

                # Track rejection reasons
                if submission.rejection_reason:
                    reason = submission.rejection_reason[:50]
                    rejection_reasons[reason] = rejection_reasons.get(reason, 0) + 1

                # Calculate time in stage
                if submission.submitted_to_customer_at and submission.reviewed_at:
                    time_delta = (
                        submission.submitted_to_customer_at - submission.reviewed_at
                    ).days
                    stage = f"{submission.status.value}_days"
                    if stage not in stage_times:
                        stage_times[stage] = []
                    stage_times[stage].append(time_delta)

            # Calculate averages
            avg_stage_times = {
                stage: sum(times) / len(times)
                for stage, times in stage_times.items()
            }

            # Calculate conversion rates
            conversion_rates = {
                status: (count / total * 100) if total > 0 else 0
                for status, count in status_counts.items()
            }

            analytics = {
                "total_submissions": total,
                "status_distribution": status_counts,
                "conversion_rates": conversion_rates,
                "average_stage_times_days": avg_stage_times,
                "rejection_reasons_breakdown": rejection_reasons,
                "shortlist_rate": (
                    status_counts.get(SubmissionStatus.SHORTLISTED.value, 0) / total * 100
                    if total > 0
                    else 0
                ),
                "rejection_rate": (
                    status_counts.get(SubmissionStatus.REJECTED.value, 0) / total * 100
                    if total > 0
                    else 0
                ),
            }

            logger.info(f"Generated analytics for {total} submissions")
            return analytics

        except Exception as e:
            logger.error(f"Error generating analytics: {str(e)}")
            raise

    async def bulk_submit(
        self,
        db: AsyncSession,
        candidate_ids: List[int],
        requirement_id: int,
        submitted_by: int,
    ) -> List[Submission]:
        """Create multiple submissions at once.

        Args:
            db: Database session
            candidate_ids: List of candidate IDs
            requirement_id: Requirement ID
            submitted_by: User ID who submitted

        Returns:
            List of created submissions

        Raises:
            ValueError: If requirement not found or invalid candidates
        """
        try:
            # Verify requirement exists
            result = await db.execute(
                select(Requirement).where(Requirement.id == requirement_id)
            )
            requirement = result.scalar_one_or_none()
            if not requirement:
                raise ValueError(f"Requirement {requirement_id} not found")

            # Verify all candidates exist
            result = await db.execute(
                select(Candidate).where(Candidate.id.in_(candidate_ids))
            )
            candidates = result.scalars().all()
            if len(candidates) != len(candidate_ids):
                raise ValueError("Some candidates not found")

            # Create submissions
            submissions = []
            for candidate_id in candidate_ids:
                submission = Submission(
                    requirement_id=requirement_id,
                    candidate_id=candidate_id,
                    customer_id=requirement.customer_id,
                    submitted_by=submitted_by,
                    status=SubmissionStatus.DRAFT,
                )
                submissions.append(submission)
                db.add(submission)

            await db.commit()

            # Refresh all
            for submission in submissions:
                await db.refresh(submission)

            logger.info(f"Created {len(submissions)} bulk submissions")
            return submissions

        except Exception as e:
            await db.rollback()
            logger.error(f"Error bulk submitting: {str(e)}")
            raise

    def _generate_recommendation_summary(
        self,
        candidate: Candidate,
        match_score: Optional[MatchScore],
        interview_feedback: List[InterviewFeedback],
        requirement: Requirement,
    ) -> str:
        """Generate AI recommendation summary for candidate.

        Args:
            candidate: Candidate object
            match_score: Match score object
            interview_feedback: List of interview feedback
            requirement: Requirement object

        Returns:
            Recommendation summary string
        """
        summary_parts = []

        # Experience fit
        if candidate.total_experience_years:
            if (
                requirement.experience_min
                and candidate.total_experience_years >= requirement.experience_min
            ):
                summary_parts.append(
                    f"Strong experience fit ({candidate.total_experience_years:.1f} years meets requirement)"
                )

        # Match score
        if match_score and match_score.overall_score:
            if match_score.overall_score >= 0.8:
                summary_parts.append("Excellent overall match")
            elif match_score.overall_score >= 0.6:
                summary_parts.append("Good overall match")

        # Interview feedback
        if interview_feedback:
            avg_score = sum(fb.overall_score for fb in interview_feedback) / len(
                interview_feedback
            )
            if avg_score >= 4.0:
                summary_parts.append("Strong interview performance")

        # Location
        if candidate.location_city == requirement.location_city:
            summary_parts.append("Same location as requirement")
        elif candidate.willing_to_relocate:
            summary_parts.append("Willing to relocate")

        return " | ".join(summary_parts) if summary_parts else "Candidate meets basic requirements"
