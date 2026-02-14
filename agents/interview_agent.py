"""Interview Agent for AI-powered screening and scorecard generation."""

import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from anthropic import Anthropic
from agents.base_agent import BaseAgent
from agents.events import (
    InterviewScheduledEvent,
    InterviewCompletedEvent,
    FeedbackGeneratedEvent,
    EventType,
)

logger = logging.getLogger(__name__)


class InterviewQuestion:
    """Represents an interview question."""

    def __init__(
        self,
        question_text: str,
        category: str,
        difficulty: str = "medium",
        order: int = 1,
        context: Optional[Dict[str, Any]] = None,
    ):
        self.question_text = question_text
        self.category = category
        self.difficulty = difficulty
        self.order = order
        self.context = context or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "question_text": self.question_text,
            "category": self.category,
            "difficulty": self.difficulty,
            "order": self.order,
            "context": self.context,
        }


class ResponseEvaluation:
    """Represents evaluation of a candidate response."""

    def __init__(
        self,
        response_text: str,
        ai_score: float,
        evaluation_notes: str = "",
        strengths: Optional[List[str]] = None,
        areas_for_improvement: Optional[List[str]] = None,
    ):
        self.response_text = response_text
        self.ai_score = ai_score
        self.evaluation_notes = evaluation_notes
        self.strengths = strengths or []
        self.areas_for_improvement = areas_for_improvement or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "response_text": self.response_text,
            "ai_score": self.ai_score,
            "evaluation_notes": self.evaluation_notes,
            "strengths": self.strengths,
            "areas_for_improvement": self.areas_for_improvement,
        }


class ScorecardCompetency:
    """Represents a competency rating in a scorecard."""

    def __init__(
        self,
        name: str,
        rating: int,
        evidence: Optional[List[str]] = None,
        comments: str = "",
    ):
        self.name = name
        self.rating = rating
        self.evidence = evidence or []
        self.comments = comments

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "rating": self.rating,
            "evidence": self.evidence,
            "comments": self.comments,
        }


class Scorecard:
    """Represents an interview scorecard."""

    def __init__(
        self,
        interview_id: int,
        candidate_id: int,
        candidate_name: str,
        requirement_id: int,
        requirement_title: str,
        competencies: List[ScorecardCompetency],
        overall_rating: int,
        recommendation: str,
        strengths: List[str],
        weaknesses: List[str],
        interviewer_name: Optional[str] = None,
        next_steps: Optional[List[str]] = None,
        comments: str = "",
    ):
        self.interview_id = interview_id
        self.candidate_id = candidate_id
        self.candidate_name = candidate_name
        self.requirement_id = requirement_id
        self.requirement_title = requirement_title
        self.competencies = competencies
        self.overall_rating = overall_rating
        self.recommendation = recommendation
        self.strengths = strengths
        self.weaknesses = weaknesses
        self.interviewer_name = interviewer_name or "AI Interview Assistant"
        self.interview_date = datetime.utcnow()
        self.next_steps = next_steps or []
        self.comments = comments
        self.generated_by_ai = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "interview_id": self.interview_id,
            "candidate_id": self.candidate_id,
            "candidate_name": self.candidate_name,
            "requirement_id": self.requirement_id,
            "requirement_title": self.requirement_title,
            "interview_date": self.interview_date.isoformat(),
            "interviewer_name": self.interviewer_name,
            "competencies": [c.to_dict() for c in self.competencies],
            "overall_rating": self.overall_rating,
            "recommendation": self.recommendation,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "next_steps": self.next_steps,
            "comments": self.comments,
            "generated_by_ai": self.generated_by_ai,
        }


class FeedbackSummary:
    """Represents a summary of interview feedback."""

    def __init__(
        self,
        interview_id: int,
        candidates_interviewed: int,
        avg_rating: float,
        competency_highlights: Dict[str, List[str]],
        common_strengths: List[str],
        areas_needing_improvement: List[str],
        overall_recommendation: str,
    ):
        self.interview_id = interview_id
        self.candidates_interviewed = candidates_interviewed
        self.avg_rating = avg_rating
        self.competency_highlights = competency_highlights
        self.common_strengths = common_strengths
        self.areas_needing_improvement = areas_needing_improvement
        self.overall_recommendation = overall_recommendation

    def to_dict(self) -> Dict[str, Any]:
        return {
            "interview_id": self.interview_id,
            "candidates_interviewed": self.candidates_interviewed,
            "avg_rating": self.avg_rating,
            "competency_highlights": self.competency_highlights,
            "common_strengths": self.common_strengths,
            "areas_needing_improvement": self.areas_needing_improvement,
            "overall_recommendation": self.overall_recommendation,
        }


class InterviewResult:
    """Represents the result of an interview."""

    def __init__(
        self,
        interview_id: int,
        status: str,
        questions_asked: int,
        questions_answered: int,
        avg_response_score: Optional[float] = None,
        completion_percentage: float = 100.0,
        estimated_score: Optional[float] = None,
    ):
        self.interview_id = interview_id
        self.status = status
        self.questions_asked = questions_asked
        self.questions_answered = questions_answered
        self.avg_response_score = avg_response_score
        self.completion_percentage = completion_percentage
        self.estimated_score = estimated_score or avg_response_score

    def to_dict(self) -> Dict[str, Any]:
        return {
            "interview_id": self.interview_id,
            "status": self.status,
            "questions_asked": self.questions_asked,
            "questions_answered": self.questions_answered,
            "avg_response_score": self.avg_response_score,
            "completion_percentage": self.completion_percentage,
            "estimated_score": self.estimated_score,
        }


class InterviewAgent(BaseAgent):
    """AI Interview Agent for automated screening and evaluation."""

    # Question templates by job category
    QUESTION_TEMPLATES = {
        "technical": [
            "Describe your experience with {specific_skill}. How did you use it in {context}?",
            "Walk me through a recent project where you used {specific_skill}.",
            "What is your proficiency level with {specific_skill} and can you provide examples?",
            "How do you stay current with {specific_skill} technology/practices?",
            "Describe a technical challenge you faced with {specific_skill} and how you solved it.",
        ],
        "behavioral": [
            "Tell me about a time you {relevant_scenario} in a professional setting.",
            "Can you share an example of when you demonstrated {competency}?",
            "Describe a situation where you had to work with a difficult team member.",
            "Tell me about a time you failed and what you learned from it.",
            "Give an example of when you had to meet a tight deadline.",
        ],
        "situational": [
            "If you were faced with {role_specific_challenge}, how would you approach it?",
            "How would you handle {challenging_scenario}?",
            "What would you do if {hypothetical_situation}?",
            "How would you prioritize if {competing_demands}?",
            "Imagine {scenario}, how would you respond?",
        ],
        "culture_fit": [
            "What type of work environment do you thrive in?",
            "How do you handle feedback and criticism?",
            "Tell me about your ideal team dynamic.",
            "How do you contribute to a positive team culture?",
            "What values are most important to you in a workplace?",
        ],
    }

    # Core competencies for evaluation
    CORE_COMPETENCIES = {
        "technical_proficiency": "Technical skill and domain expertise",
        "problem_solving": "Ability to solve complex problems",
        "communication": "Clear and effective communication",
        "leadership": "Leadership and team collaboration",
        "adaptability": "Ability to adapt to new situations",
        "customer_focus": "Customer and stakeholder focus",
        "analytical": "Analytical and data-driven thinking",
        "time_management": "Time and priority management",
    }

    def __init__(self, anthropic_api_key: str):
        """Initialize the Interview Agent.

        Args:
            anthropic_api_key: API key for Anthropic Claude API
        """
        super().__init__(agent_name="InterviewAgent", agent_version="1.0.0")
        self.client = Anthropic(api_key=anthropic_api_key)
        self.conversation_history: Dict[int, List[Dict[str, str]]] = {}

    async def generate_questions(
        self,
        requirement_id: int,
        candidate_id: int,
        candidate_profile: Dict[str, Any],
        requirement_context: Dict[str, Any],
        question_count: int = 10,
    ) -> List[InterviewQuestion]:
        """Generate role-specific interview questions.

        Args:
            requirement_id: ID of the job requirement
            candidate_id: ID of the candidate
            candidate_profile: Candidate's profile data
            requirement_context: Job requirement details
            question_count: Number of questions to generate

        Returns:
            List of interview questions
        """
        logger.info(
            f"Generating {question_count} questions for candidate {candidate_id}, requirement {requirement_id}"
        )

        try:
            prompt = self._build_question_generation_prompt(
                candidate_profile, requirement_context, question_count
            )

            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}],
            )

            questions_data = self._parse_questions_response(response.content[0].text)
            questions = [
                InterviewQuestion(
                    question_text=q["text"],
                    category=q["category"],
                    difficulty=q.get("difficulty", "medium"),
                    order=i + 1,
                    context={"requirement_id": requirement_id, "candidate_id": candidate_id},
                )
                for i, q in enumerate(questions_data)
            ]

            logger.info(f"Generated {len(questions)} questions successfully")
            return questions

        except Exception as e:
            logger.error(f"Error generating questions: {str(e)}")
            raise

    async def evaluate_response(
        self,
        question: InterviewQuestion,
        response: str,
        requirement_context: Dict[str, Any],
    ) -> ResponseEvaluation:
        """Evaluate a candidate's response to a question.

        Args:
            question: The interview question
            response: Candidate's response text
            requirement_context: Job requirement context

        Returns:
            Evaluation of the response
        """
        logger.info(f"Evaluating response to question: {question.question_text[:50]}...")

        try:
            prompt = self._build_evaluation_prompt(question, response, requirement_context)

            response_obj = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )

            evaluation_data = self._parse_evaluation_response(response_obj.content[0].text)

            evaluation = ResponseEvaluation(
                response_text=response,
                ai_score=evaluation_data["score"],
                evaluation_notes=evaluation_data.get("notes", ""),
                strengths=evaluation_data.get("strengths", []),
                areas_for_improvement=evaluation_data.get("improvements", []),
            )

            logger.info(f"Evaluated response with score: {evaluation.ai_score}")
            return evaluation

        except Exception as e:
            logger.error(f"Error evaluating response: {str(e)}")
            raise

    async def conduct_chat_interview(
        self,
        interview_id: int,
        candidate_profile: Dict[str, Any],
        requirement_context: Dict[str, Any],
    ) -> InterviewResult:
        """Conduct a chat-based interview.

        Args:
            interview_id: ID of the interview
            candidate_profile: Candidate's profile
            requirement_context: Job requirement context

        Returns:
            Interview result
        """
        logger.info(f"Conducting chat interview {interview_id}")

        try:
            self.conversation_history[interview_id] = []

            # Generate questions
            questions = await self.generate_questions(
                requirement_context["id"],
                candidate_profile["id"],
                candidate_profile,
                requirement_context,
            )

            scores = []
            for question in questions:
                # In a real implementation, this would interact with the candidate
                # through the chat interface. For now, we simulate a response.
                simulated_response = await self._get_simulated_response(question)

                evaluation = await self.evaluate_response(
                    question, simulated_response, requirement_context
                )
                scores.append(evaluation.ai_score)

                self.conversation_history[interview_id].append(
                    {
                        "role": "assistant",
                        "content": question.question_text,
                    }
                )
                self.conversation_history[interview_id].append(
                    {
                        "role": "user",
                        "content": simulated_response,
                    }
                )

            avg_score = sum(scores) / len(scores) if scores else 0

            result = InterviewResult(
                interview_id=interview_id,
                status="completed",
                questions_asked=len(questions),
                questions_answered=len(scores),
                avg_response_score=avg_score,
                completion_percentage=100.0,
                estimated_score=avg_score,
            )

            await self.emit_event(
                event_type=EventType.INTERVIEW_COMPLETED,
                entity_type="interview",
                entity_id=interview_id,
                payload={"average_score": avg_score, "questions_count": len(questions)},
            )

            logger.info(f"Interview {interview_id} completed with score {avg_score}")
            return result

        except Exception as e:
            logger.error(f"Error conducting chat interview: {str(e)}")
            raise

    async def generate_scorecard(
        self,
        interview_id: int,
        requirement_id: int,
        candidate_id: int,
        candidate_name: str,
        requirement_title: str,
        interview_result: InterviewResult,
        candidate_profile: Dict[str, Any],
    ) -> Scorecard:
        """Generate a structured interview scorecard.

        Args:
            interview_id: ID of the interview
            requirement_id: ID of the job requirement
            candidate_id: ID of the candidate
            candidate_name: Candidate's full name
            requirement_title: Job title
            interview_result: Result from the interview
            candidate_profile: Candidate's profile data

        Returns:
            Generated scorecard
        """
        logger.info(f"Generating scorecard for interview {interview_id}")

        try:
            prompt = self._build_scorecard_prompt(
                candidate_name, requirement_title, interview_result, candidate_profile
            )

            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}],
            )

            scorecard_data = self._parse_scorecard_response(response.content[0].text)

            competencies = [
                ScorecardCompetency(
                    name=comp["name"],
                    rating=comp["rating"],
                    evidence=comp.get("evidence", []),
                    comments=comp.get("comments", ""),
                )
                for comp in scorecard_data.get("competencies", [])
            ]

            scorecard = Scorecard(
                interview_id=interview_id,
                candidate_id=candidate_id,
                candidate_name=candidate_name,
                requirement_id=requirement_id,
                requirement_title=requirement_title,
                competencies=competencies,
                overall_rating=scorecard_data.get("overall_rating", 3),
                recommendation=scorecard_data.get("recommendation", "consider"),
                strengths=scorecard_data.get("strengths", []),
                weaknesses=scorecard_data.get("weaknesses", []),
                next_steps=scorecard_data.get("next_steps", []),
                comments=scorecard_data.get("comments", ""),
            )

            await self.emit_event(
                event_type=EventType.FEEDBACK_GENERATED,
                entity_type="interview",
                entity_id=interview_id,
                payload={
                    "scorecard_id": interview_id,
                    "recommendation": scorecard.recommendation,
                },
            )

            logger.info(f"Scorecard generated with recommendation: {scorecard.recommendation}")
            return scorecard

        except Exception as e:
            logger.error(f"Error generating scorecard: {str(e)}")
            raise

    async def generate_feedback_summary(
        self, interview_id: int, interview_result: InterviewResult
    ) -> FeedbackSummary:
        """Generate a feedback summary for the interview.

        Args:
            interview_id: ID of the interview
            interview_result: Result from the interview

        Returns:
            Feedback summary
        """
        logger.info(f"Generating feedback summary for interview {interview_id}")

        try:
            # In a real implementation, this would aggregate feedback from multiple
            # sources. For now, we generate a summary based on the interview result.

            summary = FeedbackSummary(
                interview_id=interview_id,
                candidates_interviewed=1,
                avg_rating=interview_result.estimated_score / 20,  # Convert 0-100 to 1-5
                competency_highlights={
                    "problem_solving": ["Demonstrated strong analytical skills"],
                    "communication": ["Clear and articulate responses"],
                    "technical": ["Good technical foundation"],
                },
                common_strengths=[
                    "Good communication",
                    "Problem-solving ability",
                    "Technical knowledge",
                ],
                areas_needing_improvement=[
                    "Deeper technical expertise needed",
                    "More specific examples required",
                ],
                overall_recommendation="Consider for next round" if interview_result.estimated_score >= 70 else "Needs improvement",
            )

            logger.info(f"Feedback summary generated")
            return summary

        except Exception as e:
            logger.error(f"Error generating feedback summary: {str(e)}")
            raise

    async def calculate_interview_score(self, interview_id: int) -> float:
        """Calculate overall interview score.

        Args:
            interview_id: ID of the interview

        Returns:
            Overall interview score (0-100)
        """
        logger.info(f"Calculating interview score for {interview_id}")

        try:
            # In a real implementation, this would aggregate scores from all responses
            # For now, return a placeholder
            return 75.0

        except Exception as e:
            logger.error(f"Error calculating interview score: {str(e)}")
            raise

    # Helper methods

    def _build_question_generation_prompt(
        self,
        candidate_profile: Dict[str, Any],
        requirement_context: Dict[str, Any],
        question_count: int,
    ) -> str:
        """Build prompt for question generation."""
        skills = ", ".join(requirement_context.get("skills_required", [])[:5])
        candidate_skills = ", ".join(
            [s.get("skill", "") for s in candidate_profile.get("skills", [])][:5]
        )

        return f"""
Generate {question_count} interview questions for the following job opening and candidate:

Job Title: {requirement_context.get("title", "Unknown")}
Required Skills: {skills}
Experience Required: {requirement_context.get("experience_min", 0)}-{requirement_context.get("experience_max", 10)} years

Candidate Background:
Name: {candidate_profile.get("first_name", "")} {candidate_profile.get("last_name", "")}
Current Title: {candidate_profile.get("current_title", "Not specified")}
Skills: {candidate_skills}
Experience: {candidate_profile.get("total_experience_years", 0)} years

Generate a mix of:
- 3-4 technical questions about their specific skills and experience
- 3-4 behavioral questions about work approach and past experiences
- 2-3 situational questions relevant to the role
- 1 culture fit question

Format the response as a JSON array with objects containing:
{{
  "text": "question text",
  "category": "technical|behavioral|situational|culture_fit",
  "difficulty": "easy|medium|hard"
}}

Only return the JSON array, no other text.
"""

    def _build_evaluation_prompt(
        self, question: InterviewQuestion, response: str, requirement_context: Dict[str, Any]
    ) -> str:
        """Build prompt for response evaluation."""
        return f"""
Evaluate this interview response on a scale of 0-100.

Question Category: {question.category}
Question: {question.question_text}

Candidate Response: {response}

Job Context: {requirement_context.get("title", "Unknown")}

Consider:
- Relevance to the question
- Technical accuracy (if applicable)
- Completeness of answer
- Communication clarity
- Examples or evidence provided

Respond with a JSON object:
{{
  "score": (0-100),
  "notes": "evaluation notes",
  "strengths": ["strength1", "strength2"],
  "improvements": ["area1", "area2"]
}}

Only return the JSON, no other text.
"""

    def _build_scorecard_prompt(
        self,
        candidate_name: str,
        requirement_title: str,
        interview_result: InterviewResult,
        candidate_profile: Dict[str, Any],
    ) -> str:
        """Build prompt for scorecard generation."""
        return f"""
Generate an interview scorecard for:

Candidate: {candidate_name}
Position: {requirement_title}
Interview Score: {interview_result.avg_response_score:.1f}/100
Questions Asked: {interview_result.questions_asked}
Questions Answered: {interview_result.questions_answered}

Candidate Background:
- Current Title: {candidate_profile.get("current_title", "Not specified")}
- Experience: {candidate_profile.get("total_experience_years", 0)} years
- Skills: {', '.join([s.get('skill', '') for s in candidate_profile.get('skills', [])])}

Generate a comprehensive scorecard including:
1. Rating for each core competency (1-5 scale):
   - Technical Proficiency
   - Problem Solving
   - Communication
   - Leadership/Teamwork
   - Adaptability

2. Overall rating (1-5)
3. Recommendation (hire/consider/no_hire)
4. Top 3 strengths
5. Top 2 weaknesses
6. Next steps

Respond with JSON:
{{
  "competencies": [
    {{"name": "competency", "rating": 1-5, "evidence": ["evidence"], "comments": "notes"}}
  ],
  "overall_rating": 1-5,
  "recommendation": "hire|consider|no_hire",
  "strengths": ["strength1", "strength2", "strength3"],
  "weaknesses": ["weakness1", "weakness2"],
  "next_steps": ["step1", "step2"],
  "comments": "additional notes"
}}

Only return the JSON, no other text.
"""

    def _parse_questions_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse questions from Claude response."""
        try:
            # Clean response text
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            questions = json.loads(response_text)
            return questions if isinstance(questions, list) else [questions]
        except json.JSONDecodeError:
            logger.warning("Failed to parse questions JSON, returning default questions")
            return [
                {
                    "text": "Tell me about your experience with the required technologies.",
                    "category": "technical",
                    "difficulty": "medium",
                }
            ]

    def _parse_evaluation_response(self, response_text: str) -> Dict[str, Any]:
        """Parse evaluation from Claude response."""
        try:
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            return json.loads(response_text)
        except json.JSONDecodeError:
            logger.warning("Failed to parse evaluation JSON, returning default")
            return {
                "score": 70,
                "notes": "Response provides relevant information",
                "strengths": ["Clear communication"],
                "improvements": ["More specific examples needed"],
            }

    def _parse_scorecard_response(self, response_text: str) -> Dict[str, Any]:
        """Parse scorecard from Claude response."""
        try:
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            return json.loads(response_text)
        except json.JSONDecodeError:
            logger.warning("Failed to parse scorecard JSON, returning default")
            return {
                "competencies": [
                    {
                        "name": "Technical Proficiency",
                        "rating": 3,
                        "evidence": [],
                        "comments": "Adequate technical knowledge",
                    }
                ],
                "overall_rating": 3,
                "recommendation": "consider",
                "strengths": ["Communication"],
                "weaknesses": ["Technical depth"],
                "next_steps": ["Schedule second interview"],
                "comments": "Candidate shows potential",
            }

    async def _get_simulated_response(self, question: InterviewQuestion) -> str:
        """Get a simulated candidate response for testing."""
        # In a real implementation, this would get the actual candidate's response
        # through the chat interface. For now, return a placeholder.
        return f"Based on my experience, I have worked with {question.context.get('requirement_id')} in various projects."

    async def on_start(self) -> None:
        """Called when the agent starts."""
        logger.info(f"{self.agent_name} started successfully")

    async def on_stop(self) -> None:
        """Called when the agent stops."""
        logger.info(f"{self.agent_name} stopped")
        self.conversation_history.clear()
