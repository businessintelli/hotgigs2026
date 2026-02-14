"""Submission API endpoints."""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db
from schemas.submission import (
    SubmissionCreate,
    SubmissionUpdate,
    SubmissionResponse,
)
from schemas.common import PaginatedResponse
from services.submission_service import SubmissionService
from agents.submission_workflow_agent import SubmissionWorkflowAgent
from models.enums import SubmissionStatus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/submissions", tags=["submissions"])
workflow_agent = SubmissionWorkflowAgent()


@router.post("", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
async def create_submission(
    submission_data: SubmissionCreate,
    db: AsyncSession = Depends(get_db),
) -> SubmissionResponse:
    """Create a new submission.

    Args:
        submission_data: Submission creation data
        db: Database session

    Returns:
        Created submission
    """
    try:
        service = SubmissionService(db)
        submission = await service.create_submission(submission_data)
        return SubmissionResponse.from_orm(submission)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error creating submission: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create submission",
        )


@router.get("/{submission_id}", response_model=SubmissionResponse)
async def get_submission(
    submission_id: int,
    db: AsyncSession = Depends(get_db),
) -> SubmissionResponse:
    """Get submission by ID.

    Args:
        submission_id: Submission ID
        db: Database session

    Returns:
        Submission data
    """
    try:
        service = SubmissionService(db)
        submission = await service.get_submission(submission_id)
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission not found",
            )
        return SubmissionResponse.from_orm(submission)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting submission: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get submission",
        )


@router.get("", response_model=PaginatedResponse[SubmissionResponse])
async def list_submissions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    requirement_id: Optional[int] = None,
    candidate_id: Optional[int] = None,
    status: Optional[SubmissionStatus] = None,
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[SubmissionResponse]:
    """List submissions with filtering and pagination.

    Args:
        skip: Skip count
        limit: Result limit
        requirement_id: Filter by requirement
        candidate_id: Filter by candidate
        status: Filter by status
        db: Database session

    Returns:
        Paginated submissions
    """
    try:
        service = SubmissionService(db)
        submissions, total = await service.get_submissions(
            skip=skip,
            limit=limit,
            requirement_id=requirement_id,
            candidate_id=candidate_id,
            status=status,
        )
        return PaginatedResponse(
            total=total,
            skip=skip,
            limit=limit,
            items=[SubmissionResponse.from_orm(s) for s in submissions],
        )
    except Exception as e:
        logger.error(f"Error listing submissions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list submissions",
        )


@router.put("/{submission_id}", response_model=SubmissionResponse)
async def update_submission(
    submission_id: int,
    submission_data: SubmissionUpdate,
    db: AsyncSession = Depends(get_db),
) -> SubmissionResponse:
    """Update submission.

    Args:
        submission_id: Submission ID
        submission_data: Update data
        db: Database session

    Returns:
        Updated submission
    """
    try:
        service = SubmissionService(db)
        submission = await service.update_submission(submission_id, submission_data)
        return SubmissionResponse.from_orm(submission)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error updating submission: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update submission",
        )


@router.delete("/{submission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_submission(
    submission_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Soft delete submission.

    Args:
        submission_id: Submission ID
        db: Database session
    """
    try:
        service = SubmissionService(db)
        await service.delete_submission(submission_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error deleting submission: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete submission",
        )


@router.post("/{submission_id}/review", response_model=SubmissionResponse)
async def submit_for_review(
    submission_id: int,
    db: AsyncSession = Depends(get_db),
) -> SubmissionResponse:
    """Submit submission for internal review.

    Args:
        submission_id: Submission ID
        db: Database session

    Returns:
        Updated submission
    """
    try:
        submission = await workflow_agent.submit_for_internal_review(db, submission_id)
        return SubmissionResponse.from_orm(submission)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error submitting for review: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit for review",
        )


@router.post("/{submission_id}/approve", response_model=SubmissionResponse)
async def approve_submission(
    submission_id: int,
    reviewer_id: int = Query(...),
    notes: str = Query(""),
    db: AsyncSession = Depends(get_db),
) -> SubmissionResponse:
    """Approve submission.

    Args:
        submission_id: Submission ID
        reviewer_id: Reviewer user ID
        notes: Reviewer notes
        db: Database session

    Returns:
        Updated submission
    """
    try:
        submission = await workflow_agent.process_approval(
            db, submission_id, True, reviewer_id, notes
        )
        return SubmissionResponse.from_orm(submission)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error approving submission: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to approve submission",
        )


@router.post("/{submission_id}/reject", response_model=SubmissionResponse)
async def reject_submission(
    submission_id: int,
    reviewer_id: int = Query(...),
    notes: str = Query(""),
    db: AsyncSession = Depends(get_db),
) -> SubmissionResponse:
    """Reject submission.

    Args:
        submission_id: Submission ID
        reviewer_id: Reviewer user ID
        notes: Rejection notes
        db: Database session

    Returns:
        Updated submission
    """
    try:
        submission = await workflow_agent.process_approval(
            db, submission_id, False, reviewer_id, notes
        )
        return SubmissionResponse.from_orm(submission)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error rejecting submission: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reject submission",
        )


@router.post("/{submission_id}/submit-to-customer", response_model=SubmissionResponse)
async def submit_to_customer(
    submission_id: int,
    db: AsyncSession = Depends(get_db),
) -> SubmissionResponse:
    """Submit approved submission to customer.

    Args:
        submission_id: Submission ID
        db: Database session

    Returns:
        Updated submission
    """
    try:
        submission = await workflow_agent.submit_to_customer(db, submission_id)
        return SubmissionResponse.from_orm(submission)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error submitting to customer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit to customer",
        )


@router.post("/{submission_id}/track-response", response_model=SubmissionResponse)
async def track_customer_response(
    submission_id: int,
    response: str = Query(...),
    shortlisted: bool = Query(...),
    feedback: str = Query(""),
    db: AsyncSession = Depends(get_db),
) -> SubmissionResponse:
    """Track customer response to submission.

    Args:
        submission_id: Submission ID
        response: Customer response text
        shortlisted: Whether candidate was shortlisted
        feedback: Customer feedback
        db: Database session

    Returns:
        Updated submission
    """
    try:
        submission = await workflow_agent.track_customer_response(
            db, submission_id, response, shortlisted, feedback
        )
        return SubmissionResponse.from_orm(submission)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error tracking response: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to track response",
        )


@router.post("/{submission_id}/withdraw", response_model=SubmissionResponse)
async def withdraw_submission(
    submission_id: int,
    reason: str = Query(...),
    db: AsyncSession = Depends(get_db),
) -> SubmissionResponse:
    """Withdraw submission.

    Args:
        submission_id: Submission ID
        reason: Withdrawal reason
        db: Database session

    Returns:
        Updated submission
    """
    try:
        submission = await workflow_agent.withdraw_submission(db, submission_id, reason)
        return SubmissionResponse.from_orm(submission)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error withdrawing submission: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to withdraw submission",
        )


@router.get("/requirement/{requirement_id}/analytics")
async def get_requirement_analytics(
    requirement_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get submission analytics for requirement.

    Args:
        requirement_id: Requirement ID
        db: Database session

    Returns:
        Analytics data
    """
    try:
        analytics = await workflow_agent.get_submission_analytics(
            db, requirement_id
        )
        return analytics
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get analytics",
        )


@router.get("/requirement/{requirement_id}/sla-compliance")
async def check_sla_compliance(
    requirement_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Check SLA compliance for requirement submissions.

    Args:
        requirement_id: Requirement ID
        db: Database session

    Returns:
        SLA compliance data
    """
    try:
        overdue = await workflow_agent.check_sla_compliance(db)
        overdue_for_requirement = [
            s for s in overdue if s.requirement_id == requirement_id
        ]
        return {
            "requirement_id": requirement_id,
            "overdue_count": len(overdue_for_requirement),
            "overdue_submissions": [
                {
                    "id": s.id,
                    "candidate_id": s.candidate_id,
                    "status": s.status.value,
                }
                for s in overdue_for_requirement
            ],
        }
    except Exception as e:
        logger.error(f"Error checking SLA: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check SLA compliance",
        )


@router.post("/bulk-submit")
async def bulk_submit_candidates(
    candidate_ids: List[int] = Query(...),
    requirement_id: int = Query(...),
    submitted_by: int = Query(...),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Bulk submit multiple candidates.

    Args:
        candidate_ids: List of candidate IDs
        requirement_id: Requirement ID
        submitted_by: User ID who submitted
        db: Database session

    Returns:
        Created submissions
    """
    try:
        submissions = await workflow_agent.bulk_submit(
            db, candidate_ids, requirement_id, submitted_by
        )
        return {
            "created_count": len(submissions),
            "submissions": [
                SubmissionResponse.from_orm(s).model_dump() for s in submissions
            ],
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error bulk submitting: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to bulk submit",
        )


@router.post("/{submission_id}/package")
async def package_candidate(
    submission_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get complete candidate package for submission.

    Args:
        submission_id: Submission ID
        db: Database session

    Returns:
        Candidate package
    """
    try:
        service = SubmissionService(db)
        submission = await service.get_submission(submission_id)
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission not found",
            )

        package = await workflow_agent.package_candidate(
            db, submission.candidate_id, submission.requirement_id
        )
        return package
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error packaging candidate: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to package candidate",
        )
