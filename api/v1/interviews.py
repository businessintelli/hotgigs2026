"""Interview API endpoints."""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from api.dependencies import get_db
from schemas.interview import (
    InterviewCreate,
    InterviewUpdate,
    InterviewResponse,
    InterviewFeedbackCreate,
    InterviewFeedbackResponse,
)
from schemas.interview_intelligence import (
    RecordingCreate,
    RecordingResponse,
    TranscriptResponse,
    NoteResponse,
    AnalyticsResponse,
    BiasReport,
    CandidateComparisonSchema,
)
from schemas.common import BaseResponse
from services.interview_service import InterviewService
from agents.interview_agent import InterviewAgent
from agents.interview_intelligence_agent import InterviewIntelligenceAgent
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/interviews", tags=["interviews"])

# Initialize agents
interview_agent = InterviewAgent(anthropic_api_key=settings.anthropic_api_key)
intelligence_agent = InterviewIntelligenceAgent(anthropic_api_key=settings.anthropic_api_key)


@router.post("/schedule", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
async def schedule_interview(
    interview_data: InterviewCreate,
    db: AsyncSession = Depends(get_db),
    user_id: Optional[int] = None,
) -> InterviewResponse:
    """Schedule a new interview.

    Args:
        interview_data: Interview creation data
        db: Database session
        user_id: User ID

    Returns:
        Created interview
    """
    try:
        service = InterviewService(db, interview_agent, intelligence_agent)
        interview = await service.schedule_interview(interview_data, user_id)
        return InterviewResponse.from_orm(interview)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error scheduling interview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to schedule interview",
        )


@router.get("/{interview_id}", response_model=InterviewResponse)
async def get_interview(
    interview_id: int, db: AsyncSession = Depends(get_db)
) -> InterviewResponse:
    """Get interview by ID.

    Args:
        interview_id: ID of the interview
        db: Database session

    Returns:
        Interview details
    """
    service = InterviewService(db, interview_agent, intelligence_agent)
    interview = await service.get_interview(interview_id)

    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found"
        )

    return InterviewResponse.from_orm(interview)


@router.put("/{interview_id}", response_model=InterviewResponse)
async def update_interview(
    interview_id: int, interview_data: InterviewUpdate, db: AsyncSession = Depends(get_db)
) -> InterviewResponse:
    """Update an interview.

    Args:
        interview_id: ID of the interview
        interview_data: Update data
        db: Database session

    Returns:
        Updated interview
    """
    try:
        service = InterviewService(db, interview_agent, intelligence_agent)
        interview = await service.update_interview(interview_id, interview_data)
        return InterviewResponse.from_orm(interview)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating interview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update interview",
        )


@router.post("/{interview_id}/start-chat", response_model=dict)
async def start_chat_interview(
    interview_id: int, db: AsyncSession = Depends(get_db)
) -> dict:
    """Start an AI chat interview.

    Args:
        interview_id: ID of the interview
        db: Database session

    Returns:
        Interview start response
    """
    try:
        service = InterviewService(db, interview_agent, intelligence_agent)
        interview = await service.get_interview(interview_id)

        if not interview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found"
            )

        # Get candidate and requirement data
        from models.candidate import Candidate
        from models.requirement import Requirement

        candidate = await db.get(Candidate, interview.candidate_id)
        requirement = await db.get(Requirement, interview.requirement_id)

        if not candidate or not requirement:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid candidate or requirement",
            )

        # Convert ORM objects to dicts
        candidate_profile = {
            "id": candidate.id,
            "first_name": candidate.first_name,
            "last_name": candidate.last_name,
            "current_title": candidate.current_title,
            "total_experience_years": candidate.total_experience_years,
            "skills": candidate.skills or [],
        }

        requirement_context = {
            "id": requirement.id,
            "title": requirement.title,
            "description": requirement.description,
            "skills_required": requirement.skills_required or [],
            "experience_min": requirement.experience_min,
            "experience_max": requirement.experience_max,
        }

        result = await service.start_chat_interview(
            interview_id, requirement.id, candidate.id, candidate_profile, requirement_context
        )
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting chat interview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start chat interview",
        )


@router.post("/{interview_id}/submit-response", response_model=dict)
async def submit_response(
    interview_id: int,
    question_id: int,
    response_text: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Submit a response during chat interview.

    Args:
        interview_id: ID of the interview
        question_id: ID of the question
        response_text: Candidate's response
        db: Database session

    Returns:
        Evaluation result
    """
    try:
        from models.requirement import Requirement

        service = InterviewService(db, interview_agent, intelligence_agent)
        interview = await service.get_interview(interview_id)

        if not interview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found"
            )

        requirement = await db.get(Requirement, interview.requirement_id)

        requirement_context = {
            "title": requirement.title,
            "skills_required": requirement.skills_required or [],
        }

        result = await service.submit_response(
            interview_id, question_id, response_text, requirement_context
        )
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting response: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit response",
        )


@router.get("/{interview_id}/questions", response_model=List[dict])
async def get_questions(interview_id: int, db: AsyncSession = Depends(get_db)) -> List[dict]:
    """Get interview questions.

    Args:
        interview_id: ID of the interview
        db: Database session

    Returns:
        List of interview questions
    """
    try:
        from models.interview_intelligence import InterviewQuestion
        from sqlalchemy import select

        result = await db.execute(
            select(InterviewQuestion).where(InterviewQuestion.interview_id == interview_id)
        )
        questions = result.scalars().all()

        return [
            {
                "id": q.id,
                "question_text": q.question_text,
                "category": q.category,
                "difficulty": q.difficulty,
                "order": q.order,
                "context": q.context,
            }
            for q in questions
        ]

    except Exception as e:
        logger.error(f"Error getting questions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get questions",
        )


@router.get("/{interview_id}/scorecard", response_model=dict)
async def get_scorecard(interview_id: int, db: AsyncSession = Depends(get_db)) -> dict:
    """Get interview scorecard.

    Args:
        interview_id: ID of the interview
        db: Database session

    Returns:
        Scorecard data
    """
    try:
        service = InterviewService(db, interview_agent, intelligence_agent)
        feedback = await service.get_feedback(interview_id)

        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Scorecard not found"
            )

        return feedback.scorecard_data or {}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting scorecard: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get scorecard",
        )


@router.post("/{interview_id}/process-recording", response_model=RecordingResponse, status_code=status.HTTP_201_CREATED)
async def process_recording(
    interview_id: int,
    recording_data: RecordingCreate,
    db: AsyncSession = Depends(get_db),
) -> RecordingResponse:
    """Process a recording.

    Args:
        interview_id: ID of the interview
        recording_data: Recording data
        db: Database session

    Returns:
        Stored recording
    """
    try:
        service = InterviewService(db, interview_agent, intelligence_agent)
        recording = await service.process_recording(
            interview_id,
            recording_data.recording_url,
            recording_data.recording_type,
            recording_data.duration_seconds,
        )
        return RecordingResponse.from_orm(recording)

    except Exception as e:
        logger.error(f"Error processing recording: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process recording",
        )


@router.get("/{interview_id}/transcript", response_model=dict)
async def get_transcript(interview_id: int, db: AsyncSession = Depends(get_db)) -> dict:
    """Get interview transcript.

    Args:
        interview_id: ID of the interview
        db: Database session

    Returns:
        Transcript data
    """
    try:
        from models.interview_intelligence import InterviewRecording, InterviewTranscript
        from sqlalchemy import select

        # Get recording
        result = await db.execute(
            select(InterviewRecording).where(InterviewRecording.interview_id == interview_id)
        )
        recording = result.scalar_one_or_none()

        if not recording:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Recording not found"
            )

        # Get transcript
        transcript = await db.get(InterviewTranscript, recording.id)

        if not transcript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Transcript not found"
            )

        return TranscriptResponse.from_orm(transcript).model_dump()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting transcript: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get transcript",
        )


@router.get("/{interview_id}/notes", response_model=List[dict])
async def get_notes(interview_id: int, db: AsyncSession = Depends(get_db)) -> List[dict]:
    """Get interview notes.

    Args:
        interview_id: ID of the interview
        db: Database session

    Returns:
        List of notes
    """
    try:
        service = InterviewService(db, interview_agent, intelligence_agent)
        notes = await service.get_notes(interview_id)

        return [
            {
                "id": n.id,
                "note_type": n.note_type,
                "category": n.category,
                "content": n.content,
                "timestamp_start": n.timestamp_start,
                "timestamp_end": n.timestamp_end,
                "confidence": n.confidence,
                "source": n.source,
            }
            for n in notes
        ]

    except Exception as e:
        logger.error(f"Error getting notes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get notes",
        )


@router.get("/{interview_id}/analytics", response_model=dict)
async def get_analytics(interview_id: int, db: AsyncSession = Depends(get_db)) -> dict:
    """Get interview analytics.

    Args:
        interview_id: ID of the interview
        db: Database session

    Returns:
        Analytics data
    """
    try:
        service = InterviewService(db, interview_agent, intelligence_agent)
        analytics = await service.get_analytics(interview_id)

        if not analytics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Analytics not found"
            )

        return AnalyticsResponse.from_orm(analytics).model_dump()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get analytics",
        )


@router.get("/{interview_id}/feedback", response_model=Optional[InterviewFeedbackResponse])
async def get_feedback(interview_id: int, db: AsyncSession = Depends(get_db)) -> Optional[InterviewFeedbackResponse]:
    """Get all feedback for an interview.

    Args:
        interview_id: ID of the interview
        db: Database session

    Returns:
        Feedback data or None
    """
    try:
        service = InterviewService(db, interview_agent, intelligence_agent)
        feedback = await service.get_feedback(interview_id)

        if feedback:
            return InterviewFeedbackResponse.from_orm(feedback)
        return None

    except Exception as e:
        logger.error(f"Error getting feedback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get feedback",
        )


@router.post("/{interview_id}/feedback", response_model=InterviewFeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    interview_id: int,
    feedback_data: InterviewFeedbackCreate,
    db: AsyncSession = Depends(get_db),
) -> InterviewFeedbackResponse:
    """Submit feedback for an interview.

    Args:
        interview_id: ID of the interview
        feedback_data: Feedback data
        db: Database session

    Returns:
        Stored feedback
    """
    try:
        service = InterviewService(db, interview_agent, intelligence_agent)
        feedback = await service.submit_feedback(interview_id, feedback_data)
        return InterviewFeedbackResponse.from_orm(feedback)

    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit feedback",
        )


@router.post("/{interview_id}/generate-scorecard", response_model=InterviewFeedbackResponse, status_code=status.HTTP_201_CREATED)
async def generate_scorecard(
    interview_id: int, db: AsyncSession = Depends(get_db)
) -> InterviewFeedbackResponse:
    """Generate an AI scorecard for an interview.

    Args:
        interview_id: ID of the interview
        db: Database session

    Returns:
        Generated scorecard as feedback
    """
    try:
        from models.candidate import Candidate
        from models.requirement import Requirement

        service = InterviewService(db, interview_agent, intelligence_agent)
        interview = await service.get_interview(interview_id)

        if not interview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found"
            )

        candidate = await db.get(Candidate, interview.candidate_id)
        requirement = await db.get(Requirement, interview.requirement_id)

        if not candidate or not requirement:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid candidate or requirement",
            )

        candidate_profile = {
            "id": candidate.id,
            "first_name": candidate.first_name,
            "last_name": candidate.last_name,
            "current_title": candidate.current_title,
            "total_experience_years": candidate.total_experience_years,
            "skills": candidate.skills or [],
        }

        feedback = await service.generate_scorecard(
            interview_id,
            requirement.id,
            candidate.id,
            candidate.full_name,
            requirement.title,
            candidate_profile,
        )

        return InterviewFeedbackResponse.from_orm(feedback)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating scorecard: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate scorecard",
        )


@router.get("/requirement/{requirement_id}/summary", response_model=dict)
async def get_requirement_summary(
    requirement_id: int, db: AsyncSession = Depends(get_db)
) -> dict:
    """Get interview summary for a requirement.

    Args:
        requirement_id: ID of the requirement
        db: Database session

    Returns:
        Interview summary
    """
    try:
        service = InterviewService(db, interview_agent, intelligence_agent)
        summary = await service.get_requirement_summary(requirement_id)
        return summary

    except Exception as e:
        logger.error(f"Error getting requirement summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get summary",
        )


@router.post("/compare", response_model=CandidateComparisonSchema)
async def compare_candidates(
    interview_ids: List[int], db: AsyncSession = Depends(get_db)
) -> CandidateComparisonSchema:
    """Compare multiple candidates.

    Args:
        interview_ids: List of interview IDs
        db: Database session

    Returns:
        Comparison report
    """
    try:
        service = InterviewService(db, interview_agent, intelligence_agent)

        # Get interviews and candidate data
        candidate_data = []
        for interview_id in interview_ids:
            from models.candidate import Candidate

            interview = await service.get_interview(interview_id)
            if interview:
                candidate = await db.get(Candidate, interview.candidate_id)
                if candidate:
                    candidate_data.append(
                        {
                            "name": candidate.full_name,
                            "id": candidate.id,
                            "current_title": candidate.current_title,
                        }
                    )

        if not intelligence_agent:
            raise RuntimeError("Intelligence agent not initialized")

        comparison = await intelligence_agent.compare_candidates(
            interview_ids, candidate_data
        )

        return CandidateComparisonSchema(
            candidate_ids=comparison.interview_ids,
            candidate_names=comparison.candidate_names,
            metrics=[],
            overall_rankings=comparison.rankings,
            strengths_by_candidate={
                int(k): v for k, v in comparison.strengths_by_candidate.items()
            },
            weaknesses_by_candidate={
                int(k): v for k, v in comparison.weaknesses_by_candidate.items()
            },
            recommendations="See detailed rankings above",
        )

    except Exception as e:
        logger.error(f"Error comparing candidates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to compare candidates",
        )
