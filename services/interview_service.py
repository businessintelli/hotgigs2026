"""Interview service for managing interviews and scheduling."""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from models.interview import Interview, InterviewFeedback
from models.interview_intelligence import (
    InterviewRecording,
    InterviewTranscript,
    InterviewNote,
    CompetencyScore,
    InterviewAnalytics,
    InterviewQuestion,
    InterviewResponse,
)
from models.candidate import Candidate
from models.requirement import Requirement
from models.enums import InterviewStatus, InterviewType
from schemas.interview import (
    InterviewCreate,
    InterviewUpdate,
    InterviewFeedbackCreate,
)
from agents.interview_agent import InterviewAgent
from agents.interview_intelligence_agent import InterviewIntelligenceAgent

logger = logging.getLogger(__name__)


class InterviewService:
    """Service for managing interview operations."""

    def __init__(self, db: AsyncSession, interview_agent: Optional[InterviewAgent] = None,
                 intelligence_agent: Optional[InterviewIntelligenceAgent] = None):
        """Initialize interview service.

        Args:
            db: Database session
            interview_agent: Interview agent instance
            intelligence_agent: Interview intelligence agent instance
        """
        self.db = db
        self.interview_agent = interview_agent
        self.intelligence_agent = intelligence_agent

    async def schedule_interview(
        self, interview_data: InterviewCreate, user_id: Optional[int] = None
    ) -> Interview:
        """Schedule a new interview.

        Args:
            interview_data: Interview creation data
            user_id: ID of user scheduling the interview

        Returns:
            Created interview
        """
        logger.info(
            f"Scheduling interview for candidate {interview_data.candidate_id}, "
            f"requirement {interview_data.requirement_id}"
        )

        try:
            # Verify candidate and requirement exist
            candidate = await self.db.get(Candidate, interview_data.candidate_id)
            requirement = await self.db.get(Requirement, interview_data.requirement_id)

            if not candidate or not requirement:
                raise ValueError("Invalid candidate or requirement ID")

            interview = Interview(
                candidate_id=interview_data.candidate_id,
                requirement_id=interview_data.requirement_id,
                interview_type=interview_data.interview_type,
                scheduled_at=interview_data.scheduled_at,
                duration_minutes=interview_data.duration_minutes,
                status=InterviewStatus.SCHEDULED,
                interviewer_name=interview_data.interviewer_name,
                interviewer_email=interview_data.interviewer_email,
                meeting_link=interview_data.meeting_link,
                notes=interview_data.notes,
                extra_metadata=interview_data.metadata,
            )

            self.db.add(interview)
            await self.db.flush()
            await self.db.commit()
            await self.db.refresh(interview)

            logger.info(f"Interview {interview.id} scheduled successfully")
            return interview

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error scheduling interview: {str(e)}")
            raise

    async def get_interview(self, interview_id: int) -> Optional[Interview]:
        """Get interview by ID.

        Args:
            interview_id: ID of the interview

        Returns:
            Interview object or None
        """
        return await self.db.get(Interview, interview_id)

    async def get_interviews_by_requirement(self, requirement_id: int) -> List[Interview]:
        """Get all interviews for a requirement.

        Args:
            requirement_id: ID of the requirement

        Returns:
            List of interviews
        """
        result = await self.db.execute(
            select(Interview)
            .where(Interview.requirement_id == requirement_id)
            .order_by(desc(Interview.created_at))
        )
        return result.scalars().all()

    async def get_interviews_by_candidate(self, candidate_id: int) -> List[Interview]:
        """Get all interviews for a candidate.

        Args:
            candidate_id: ID of the candidate

        Returns:
            List of interviews
        """
        result = await self.db.execute(
            select(Interview)
            .where(Interview.candidate_id == candidate_id)
            .order_by(desc(Interview.created_at))
        )
        return result.scalars().all()

    async def update_interview(
        self, interview_id: int, interview_data: InterviewUpdate
    ) -> Interview:
        """Update an interview.

        Args:
            interview_id: ID of the interview
            interview_data: Update data

        Returns:
            Updated interview
        """
        logger.info(f"Updating interview {interview_id}")

        try:
            interview = await self.get_interview(interview_id)
            if not interview:
                raise ValueError(f"Interview {interview_id} not found")

            update_data = interview_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(interview, field, value)

            await self.db.commit()
            await self.db.refresh(interview)

            logger.info(f"Interview {interview_id} updated successfully")
            return interview

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating interview: {str(e)}")
            raise

    async def start_chat_interview(
        self,
        interview_id: int,
        requirement_id: int,
        candidate_id: int,
        candidate_profile: Dict[str, Any],
        requirement_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Start an AI chat-based interview.

        Args:
            interview_id: ID of the interview
            requirement_id: ID of the requirement
            candidate_id: ID of the candidate
            candidate_profile: Candidate profile data
            requirement_context: Requirement context

        Returns:
            Interview start response
        """
        logger.info(f"Starting chat interview {interview_id}")

        try:
            interview = await self.update_interview(
                interview_id, InterviewUpdate(status=InterviewStatus.IN_PROGRESS)
            )

            if not self.interview_agent:
                raise RuntimeError("Interview agent not initialized")

            # Generate questions
            questions = await self.interview_agent.generate_questions(
                requirement_id=requirement_id,
                candidate_id=candidate_id,
                candidate_profile=candidate_profile,
                requirement_context=requirement_context,
                question_count=10,
            )

            # Store questions in database
            for question in questions:
                db_question = InterviewQuestion(
                    interview_id=interview_id,
                    question_text=question.question_text,
                    category=question.category,
                    difficulty=question.difficulty,
                    order=question.order,
                    context=question.context,
                )
                self.db.add(db_question)

            await self.db.commit()

            logger.info(f"Chat interview {interview_id} started with {len(questions)} questions")

            return {
                "interview_id": interview_id,
                "status": "in_progress",
                "questions_count": len(questions),
                "first_question": questions[0].to_dict() if questions else None,
            }

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error starting chat interview: {str(e)}")
            raise

    async def submit_response(
        self,
        interview_id: int,
        question_id: int,
        response_text: str,
        requirement_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Submit a response during chat interview.

        Args:
            interview_id: ID of the interview
            question_id: ID of the question
            response_text: Candidate's response
            requirement_context: Requirement context

        Returns:
            Response evaluation
        """
        logger.info(f"Submitting response to question {question_id}")

        try:
            # Get the question
            question_obj = await self.db.get(InterviewQuestion, question_id)
            if not question_obj or question_obj.interview_id != interview_id:
                raise ValueError("Question not found")

            if not self.interview_agent:
                raise RuntimeError("Interview agent not initialized")

            # Evaluate response
            from agents.interview_agent import InterviewQuestion as AgentQuestion

            agent_question = AgentQuestion(
                question_text=question_obj.question_text,
                category=question_obj.category,
                difficulty=question_obj.difficulty,
                order=question_obj.order,
                context=question_obj.context,
            )

            evaluation = await self.interview_agent.evaluate_response(
                agent_question, response_text, requirement_context
            )

            # Store response
            db_response = InterviewResponse(
                question_id=question_id,
                response_text=response_text,
                answered_at=datetime.utcnow(),
                ai_score=evaluation.ai_score,
                evaluation_notes=evaluation.evaluation_notes,
            )
            self.db.add(db_response)
            await self.db.commit()

            logger.info(f"Response stored with score {evaluation.ai_score}")

            return evaluation.to_dict()

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error submitting response: {str(e)}")
            raise

    async def complete_interview(self, interview_id: int) -> Interview:
        """Mark interview as completed.

        Args:
            interview_id: ID of the interview

        Returns:
            Updated interview
        """
        return await self.update_interview(
            interview_id, InterviewUpdate(status=InterviewStatus.COMPLETED)
        )

    async def process_recording(
        self,
        interview_id: int,
        recording_url: str,
        recording_type: str,
        duration_seconds: Optional[int] = None,
    ) -> InterviewRecording:
        """Process a recording.

        Args:
            interview_id: ID of the interview
            recording_url: URL of the recording
            recording_type: Type of recording (audio/video)
            duration_seconds: Duration in seconds

        Returns:
            Stored recording
        """
        logger.info(f"Processing recording for interview {interview_id}")

        try:
            recording = InterviewRecording(
                interview_id=interview_id,
                recording_url=recording_url,
                recording_type=recording_type,
                duration_seconds=duration_seconds,
                status="processing",
            )
            self.db.add(recording)
            await self.db.flush()
            await self.db.commit()

            if self.intelligence_agent:
                # Process recording asynchronously in background
                # For now, just update status
                recording.status = "completed"
                await self.db.commit()

            logger.info(f"Recording {recording.id} processed")
            return recording

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error processing recording: {str(e)}")
            raise

    async def generate_scorecard(
        self,
        interview_id: int,
        requirement_id: int,
        candidate_id: int,
        candidate_name: str,
        requirement_title: str,
        candidate_profile: Dict[str, Any],
    ) -> InterviewFeedback:
        """Generate a scorecard for an interview.

        Args:
            interview_id: ID of the interview
            requirement_id: ID of the requirement
            candidate_id: ID of the candidate
            candidate_name: Candidate's name
            requirement_title: Job title
            candidate_profile: Candidate profile

        Returns:
            Generated feedback with scorecard
        """
        logger.info(f"Generating scorecard for interview {interview_id}")

        try:
            if not self.interview_agent:
                raise RuntimeError("Interview agent not initialized")

            # Create a mock interview result
            from agents.interview_agent import InterviewResult

            interview_result = InterviewResult(
                interview_id=interview_id,
                status="completed",
                questions_asked=10,
                questions_answered=10,
                avg_response_score=75.0,
                completion_percentage=100.0,
                estimated_score=75.0,
            )

            # Generate scorecard
            scorecard = await self.interview_agent.generate_scorecard(
                interview_id=interview_id,
                requirement_id=requirement_id,
                candidate_id=candidate_id,
                candidate_name=candidate_name,
                requirement_title=requirement_title,
                interview_result=interview_result,
                candidate_profile=candidate_profile,
            )

            # Store as feedback
            feedback = InterviewFeedback(
                interview_id=interview_id,
                evaluator="AI Interview System",
                overall_rating=scorecard.overall_rating,
                technical_rating=3,
                communication_rating=3,
                culture_fit_rating=3,
                problem_solving_rating=3,
                strengths=scorecard.strengths,
                weaknesses=scorecard.weaknesses,
                recommendation=scorecard.recommendation,
                detailed_notes=scorecard.comments,
                scorecard_data=scorecard.to_dict(),
                ai_generated=True,
            )

            self.db.add(feedback)
            await self.db.commit()
            await self.db.refresh(feedback)

            logger.info(f"Scorecard generated for interview {interview_id}")
            return feedback

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error generating scorecard: {str(e)}")
            raise

    async def submit_feedback(
        self, interview_id: int, feedback_data: InterviewFeedbackCreate
    ) -> InterviewFeedback:
        """Submit feedback for an interview.

        Args:
            interview_id: ID of the interview
            feedback_data: Feedback data

        Returns:
            Stored feedback
        """
        logger.info(f"Submitting feedback for interview {interview_id}")

        try:
            feedback = InterviewFeedback(
                interview_id=interview_id,
                evaluator=feedback_data.evaluator,
                overall_rating=feedback_data.overall_rating,
                technical_rating=feedback_data.technical_rating,
                communication_rating=feedback_data.communication_rating,
                culture_fit_rating=feedback_data.culture_fit_rating,
                problem_solving_rating=feedback_data.problem_solving_rating,
                strengths=feedback_data.strengths,
                weaknesses=feedback_data.weaknesses,
                recommendation=feedback_data.recommendation,
                detailed_notes=feedback_data.detailed_notes,
                scorecard_data=feedback_data.scorecard_data,
                ai_generated=feedback_data.ai_generated,
            )

            self.db.add(feedback)
            await self.db.commit()
            await self.db.refresh(feedback)

            logger.info(f"Feedback submitted for interview {interview_id}")
            return feedback

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error submitting feedback: {str(e)}")
            raise

    async def get_feedback(self, interview_id: int) -> Optional[InterviewFeedback]:
        """Get feedback for an interview.

        Args:
            interview_id: ID of the interview

        Returns:
            Feedback or None
        """
        result = await self.db.execute(
            select(InterviewFeedback).where(InterviewFeedback.interview_id == interview_id)
        )
        return result.scalar_one_or_none()

    async def get_competency_scores(self, interview_id: int) -> List[CompetencyScore]:
        """Get competency scores for an interview.

        Args:
            interview_id: ID of the interview

        Returns:
            List of competency scores
        """
        result = await self.db.execute(
            select(CompetencyScore)
            .where(CompetencyScore.interview_id == interview_id)
            .order_by(desc(CompetencyScore.rating))
        )
        return result.scalars().all()

    async def get_analytics(self, interview_id: int) -> Optional[InterviewAnalytics]:
        """Get analytics for an interview.

        Args:
            interview_id: ID of the interview

        Returns:
            Analytics or None
        """
        result = await self.db.execute(
            select(InterviewAnalytics).where(InterviewAnalytics.interview_id == interview_id)
        )
        return result.scalar_one_or_none()

    async def get_notes(self, interview_id: int) -> List[InterviewNote]:
        """Get notes for an interview.

        Args:
            interview_id: ID of the interview

        Returns:
            List of notes
        """
        result = await self.db.execute(
            select(InterviewNote)
            .where(InterviewNote.interview_id == interview_id)
            .order_by(InterviewNote.created_at)
        )
        return result.scalars().all()

    async def get_requirement_summary(self, requirement_id: int) -> Dict[str, Any]:
        """Get interview summary for a requirement.

        Args:
            requirement_id: ID of the requirement

        Returns:
            Interview summary
        """
        logger.info(f"Getting interview summary for requirement {requirement_id}")

        try:
            interviews = await self.get_interviews_by_requirement(requirement_id)

            completed = [i for i in interviews if i.status == InterviewStatus.COMPLETED]
            feedback_list = []
            for interview in completed:
                feedback = await self.get_feedback(interview.id)
                if feedback:
                    feedback_list.append(feedback)

            avg_rating = (
                sum(f.overall_rating for f in feedback_list if f.overall_rating) / len(feedback_list)
                if feedback_list
                else 0
            )

            return {
                "requirement_id": requirement_id,
                "total_interviews": len(interviews),
                "completed_interviews": len(completed),
                "avg_rating": avg_rating,
                "interviews": [
                    {
                        "id": i.id,
                        "candidate_id": i.candidate_id,
                        "status": i.status,
                        "scheduled_at": i.scheduled_at,
                    }
                    for i in interviews
                ],
            }

        except Exception as e:
            logger.error(f"Error getting requirement summary: {str(e)}")
            raise
