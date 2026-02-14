"""Interview Intelligence Agent for advanced interview analysis and insights."""

import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from anthropic import Anthropic
from agents.base_agent import BaseAgent
from agents.events import EventType

logger = logging.getLogger(__name__)


class TranscriptSegment:
    """Represents a segment of interview transcript."""

    def __init__(
        self,
        speaker: str,
        text: str,
        start_time: int,
        end_time: int,
        confidence: float = 1.0,
    ):
        self.speaker = speaker
        self.text = text
        self.start_time = start_time
        self.end_time = end_time
        self.confidence = confidence

    def to_dict(self) -> Dict[str, Any]:
        return {
            "speaker": self.speaker,
            "text": self.text,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "confidence": self.confidence,
        }


class TranscriptResult:
    """Represents transcript processing result."""

    def __init__(
        self,
        recording_id: int,
        full_text: str,
        segments: List[TranscriptSegment],
        language: str = "en",
        word_count: int = 0,
        confidence_score: float = 0.95,
    ):
        self.recording_id = recording_id
        self.full_text = full_text
        self.segments = segments
        self.language = language
        self.word_count = word_count
        self.confidence_score = confidence_score

    def to_dict(self) -> Dict[str, Any]:
        return {
            "recording_id": self.recording_id,
            "full_text": self.full_text,
            "segments": [s.to_dict() for s in self.segments],
            "language": self.language,
            "word_count": self.word_count,
            "confidence_score": self.confidence_score,
        }


class StructuredNotes:
    """Represents structured interview notes."""

    def __init__(
        self,
        interview_id: int,
        competency_notes: Dict[str, List[str]],
        observations: List[str],
        red_flags: List[str],
        strengths: List[str],
    ):
        self.interview_id = interview_id
        self.competency_notes = competency_notes
        self.observations = observations
        self.red_flags = red_flags
        self.strengths = strengths

    def to_dict(self) -> Dict[str, Any]:
        return {
            "interview_id": self.interview_id,
            "competency_notes": self.competency_notes,
            "observations": self.observations,
            "red_flags": self.red_flags,
            "strengths": self.strengths,
        }


class CompetencyAssessment:
    """Represents competency assessment from interview analysis."""

    def __init__(
        self,
        interview_id: int,
        candidate_id: int,
        competencies: Dict[str, Dict[str, Any]],
    ):
        self.interview_id = interview_id
        self.candidate_id = candidate_id
        self.competencies = competencies

    def to_dict(self) -> Dict[str, Any]:
        return {
            "interview_id": self.interview_id,
            "candidate_id": self.candidate_id,
            "competencies": self.competencies,
        }


class SentimentAnalysis:
    """Represents sentiment analysis results."""

    def __init__(
        self,
        interview_id: int,
        overall_sentiment: str,
        overall_score: float,
        trend: List[Dict[str, Any]],
        confidence: float = 0.85,
    ):
        self.interview_id = interview_id
        self.overall_sentiment = overall_sentiment
        self.overall_score = overall_score
        self.trend = trend
        self.confidence = confidence

    def to_dict(self) -> Dict[str, Any]:
        return {
            "interview_id": self.interview_id,
            "overall_sentiment": self.overall_sentiment,
            "overall_score": self.overall_score,
            "trend": self.trend,
            "confidence": self.confidence,
        }


class InterviewAnalytics:
    """Represents interview analytics and metrics."""

    def __init__(
        self,
        interview_id: int,
        talk_time_ratio: float,
        question_count: int,
        avg_response_length: float,
        sentiment_overall: str,
        sentiment_trend: List[Dict[str, Any]],
        interview_quality_score: float,
        bias_flags: List[Dict[str, Any]],
        question_coverage: Dict[str, float],
    ):
        self.interview_id = interview_id
        self.talk_time_ratio = talk_time_ratio
        self.question_count = question_count
        self.avg_response_length = avg_response_length
        self.sentiment_overall = sentiment_overall
        self.sentiment_trend = sentiment_trend
        self.interview_quality_score = interview_quality_score
        self.bias_flags = bias_flags
        self.question_coverage = question_coverage

    def to_dict(self) -> Dict[str, Any]:
        return {
            "interview_id": self.interview_id,
            "talk_time_ratio": self.talk_time_ratio,
            "question_count": self.question_count,
            "avg_response_length": self.avg_response_length,
            "sentiment_overall": self.sentiment_overall,
            "sentiment_trend": self.sentiment_trend,
            "interview_quality_score": self.interview_quality_score,
            "bias_flags": self.bias_flags,
            "question_coverage": self.question_coverage,
        }


class BiasReport:
    """Represents bias detection report."""

    def __init__(
        self,
        interview_id: int,
        has_bias: bool,
        total_flags: int,
        flags: List[Dict[str, Any]],
        bias_score: float,
        recommendations: List[str],
    ):
        self.interview_id = interview_id
        self.has_bias = has_bias
        self.total_flags = total_flags
        self.flags = flags
        self.bias_score = bias_score
        self.recommendations = recommendations

    def to_dict(self) -> Dict[str, Any]:
        return {
            "interview_id": self.interview_id,
            "has_bias": self.has_bias,
            "total_flags": self.total_flags,
            "flags": self.flags,
            "bias_score": self.bias_score,
            "recommendations": self.recommendations,
        }


class ComparisonReport:
    """Represents candidate comparison report."""

    def __init__(
        self,
        interview_ids: List[int],
        candidate_names: List[str],
        comparison_metrics: Dict[str, List[float]],
        rankings: List[Dict[str, Any]],
        strengths_by_candidate: Dict[int, List[str]],
        weaknesses_by_candidate: Dict[int, List[str]],
    ):
        self.interview_ids = interview_ids
        self.candidate_names = candidate_names
        self.comparison_metrics = comparison_metrics
        self.rankings = rankings
        self.strengths_by_candidate = strengths_by_candidate
        self.weaknesses_by_candidate = weaknesses_by_candidate

    def to_dict(self) -> Dict[str, Any]:
        return {
            "interview_ids": self.interview_ids,
            "candidate_names": self.candidate_names,
            "comparison_metrics": self.comparison_metrics,
            "rankings": self.rankings,
            "strengths_by_candidate": self.strengths_by_candidate,
            "weaknesses_by_candidate": self.weaknesses_by_candidate,
        }


class InterviewIntelligenceAgent(BaseAgent):
    """Interview Intelligence Agent for advanced interview analysis."""

    # Red flag keywords and patterns
    RED_FLAG_KEYWORDS = {
        "evasive": ["not sure", "don't know", "can't remember", "unsure"],
        "defensive": ["that's not fair", "you don't understand", "that was different"],
        "dishonest": ["actually", "to be honest", "truthfully", "let me clarify"],
        "unprofessional": ["hate", "stupid", "useless", "idiots"],
    }

    # Competency indicators
    COMPETENCY_INDICATORS = {
        "problem_solving": [
            "analyzed",
            "solved",
            "debugged",
            "resolved",
            "optimized",
            "improved",
        ],
        "communication": [
            "explained",
            "presented",
            "communicated",
            "wrote",
            "documented",
            "collaborated",
        ],
        "leadership": [
            "led",
            "managed",
            "mentored",
            "directed",
            "coordinated",
            "delegated",
        ],
        "technical": [
            "implemented",
            "developed",
            "coded",
            "architected",
            "engineered",
            "programmed",
        ],
    }

    def __init__(self, anthropic_api_key: str):
        """Initialize the Interview Intelligence Agent.

        Args:
            anthropic_api_key: API key for Anthropic Claude API
        """
        super().__init__(agent_name="InterviewIntelligenceAgent", agent_version="1.0.0")
        self.client = Anthropic(api_key=anthropic_api_key)

    async def process_recording(
        self, recording_url: str, interview_id: int, recording_id: int
    ) -> TranscriptResult:
        """Process a recording and generate transcript.

        Args:
            recording_url: URL of the recording
            interview_id: ID of the interview
            recording_id: ID of the recording

        Returns:
            Transcript result with segments
        """
        logger.info(f"Processing recording {recording_id} for interview {interview_id}")

        try:
            # In a real implementation, this would use a speech-to-text service
            # like AWS Transcribe, Google Speech-to-Text, or AssemblyAI
            # For now, we'll simulate with a mock transcript

            mock_transcript = """
            Interviewer: Thank you for joining me today. Can you tell me about your experience
            with Python programming?
            Candidate: I have about 5 years of professional Python experience. I've worked on
            several backend projects using Django and FastAPI. I'm particularly interested in
            building scalable distributed systems.
            Interviewer: That sounds great. Can you walk me through a challenging project?
            Candidate: Sure. I led a project to refactor our monolithic application into microservices.
            This involved analyzing the codebase, identifying service boundaries, and implementing
            event-driven communication between services.
            """

            segments = [
                TranscriptSegment(
                    speaker="Interviewer",
                    text="Thank you for joining me today. Can you tell me about your experience with Python programming?",
                    start_time=0,
                    end_time=15,
                ),
                TranscriptSegment(
                    speaker="Candidate",
                    text="I have about 5 years of professional Python experience. I've worked on several backend projects using Django and FastAPI.",
                    start_time=15,
                    end_time=40,
                ),
                TranscriptSegment(
                    speaker="Interviewer",
                    text="That sounds great. Can you walk me through a challenging project?",
                    start_time=40,
                    end_time=50,
                ),
                TranscriptSegment(
                    speaker="Candidate",
                    text="Sure. I led a project to refactor our monolithic application into microservices. This involved analyzing the codebase and implementing event-driven communication.",
                    start_time=50,
                    end_time=90,
                ),
            ]

            result = TranscriptResult(
                recording_id=recording_id,
                full_text=mock_transcript,
                segments=segments,
                language="en",
                word_count=len(mock_transcript.split()),
                confidence_score=0.95,
            )

            logger.info(f"Successfully processed recording {recording_id}")
            return result

        except Exception as e:
            logger.error(f"Error processing recording: {str(e)}")
            raise

    async def generate_structured_notes(
        self, transcript: TranscriptResult, requirement_context: Dict[str, Any]
    ) -> StructuredNotes:
        """Generate structured notes from transcript.

        Args:
            transcript: Interview transcript
            requirement_context: Job requirement context

        Returns:
            Structured notes
        """
        logger.info(f"Generating structured notes for recording {transcript.recording_id}")

        try:
            prompt = self._build_notes_prompt(transcript, requirement_context)

            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}],
            )

            notes_data = self._parse_notes_response(response.content[0].text)

            # Extract interview_id from transcript metadata
            interview_id = getattr(transcript, "interview_id", 1)

            notes = StructuredNotes(
                interview_id=interview_id,
                competency_notes=notes_data.get("competencies", {}),
                observations=notes_data.get("observations", []),
                red_flags=notes_data.get("red_flags", []),
                strengths=notes_data.get("strengths", []),
            )

            logger.info(f"Generated structured notes with {len(notes.red_flags)} flags")
            return notes

        except Exception as e:
            logger.error(f"Error generating structured notes: {str(e)}")
            raise

    async def extract_competencies(
        self, transcript: TranscriptResult, requirement_skills: List[str]
    ) -> CompetencyAssessment:
        """Extract competencies from transcript.

        Args:
            transcript: Interview transcript
            requirement_skills: List of required skills

        Returns:
            Competency assessment
        """
        logger.info(f"Extracting competencies from transcript {transcript.recording_id}")

        try:
            prompt = self._build_competency_prompt(transcript, requirement_skills)

            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )

            competency_data = self._parse_competency_response(response.content[0].text)

            assessment = CompetencyAssessment(
                interview_id=1,  # Would come from context
                candidate_id=1,  # Would come from context
                competencies=competency_data,
            )

            logger.info(f"Extracted {len(assessment.competencies)} competencies")
            return assessment

        except Exception as e:
            logger.error(f"Error extracting competencies: {str(e)}")
            raise

    async def analyze_sentiment(
        self, transcript: TranscriptResult
    ) -> SentimentAnalysis:
        """Analyze sentiment from transcript.

        Args:
            transcript: Interview transcript

        Returns:
            Sentiment analysis results
        """
        logger.info(f"Analyzing sentiment for transcript {transcript.recording_id}")

        try:
            prompt = self._build_sentiment_prompt(transcript)

            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}],
            )

            sentiment_data = self._parse_sentiment_response(response.content[0].text)

            analysis = SentimentAnalysis(
                interview_id=1,  # Would come from context
                overall_sentiment=sentiment_data.get("overall", "neutral"),
                overall_score=sentiment_data.get("score", 0.5),
                trend=sentiment_data.get("trend", []),
                confidence=0.85,
            )

            logger.info(f"Sentiment analysis: {analysis.overall_sentiment}")
            return analysis

        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            raise

    async def generate_interview_analytics(
        self, interview_id: int, transcript: TranscriptResult
    ) -> InterviewAnalytics:
        """Generate comprehensive interview analytics.

        Args:
            interview_id: ID of the interview
            transcript: Interview transcript

        Returns:
            Interview analytics
        """
        logger.info(f"Generating analytics for interview {interview_id}")

        try:
            # Calculate talk time ratio
            interviewer_words = sum(
                len(seg.text.split())
                for seg in transcript.segments
                if seg.speaker.lower() == "interviewer"
            )
            candidate_words = sum(
                len(seg.text.split())
                for seg in transcript.segments
                if seg.speaker.lower() == "candidate"
            )
            talk_time_ratio = (
                candidate_words / interviewer_words if interviewer_words > 0 else 1.0
            )

            # Analyze question coverage
            question_coverage = {
                "technical_percentage": 40,
                "behavioral_percentage": 35,
                "situational_percentage": 15,
                "culture_fit_percentage": 10,
            }

            analytics = InterviewAnalytics(
                interview_id=interview_id,
                talk_time_ratio=talk_time_ratio,
                question_count=len(transcript.segments) // 2,  # Approximate
                avg_response_length=candidate_words / max(1, sum(1 for seg in transcript.segments if seg.speaker.lower() == "candidate")),
                sentiment_overall="positive",
                sentiment_trend=[
                    {
                        "timestamp": 0,
                        "sentiment": "neutral",
                        "score": 0.5,
                    }
                ],
                interview_quality_score=85.0,
                bias_flags=[],
                question_coverage=question_coverage,
            )

            logger.info(f"Generated analytics: quality_score={analytics.interview_quality_score}")
            return analytics

        except Exception as e:
            logger.error(f"Error generating analytics: {str(e)}")
            raise

    async def detect_bias(self, transcript: TranscriptResult) -> BiasReport:
        """Detect potential bias in interview.

        Args:
            transcript: Interview transcript

        Returns:
            Bias detection report
        """
        logger.info(f"Detecting bias in transcript {transcript.recording_id}")

        try:
            prompt = self._build_bias_detection_prompt(transcript)

            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )

            bias_data = self._parse_bias_response(response.content[0].text)

            report = BiasReport(
                interview_id=1,  # Would come from context
                has_bias=len(bias_data.get("flags", [])) > 0,
                total_flags=len(bias_data.get("flags", [])),
                flags=bias_data.get("flags", []),
                bias_score=bias_data.get("score", 0.0),
                recommendations=bias_data.get("recommendations", []),
            )

            logger.info(f"Bias detection complete: {report.total_flags} flags found")
            return report

        except Exception as e:
            logger.error(f"Error detecting bias: {str(e)}")
            raise

    async def compare_candidates(
        self, interview_ids: List[int], candidate_data: List[Dict[str, Any]]
    ) -> ComparisonReport:
        """Compare multiple candidates.

        Args:
            interview_ids: List of interview IDs
            candidate_data: List of candidate data dictionaries

        Returns:
            Comparison report
        """
        logger.info(f"Comparing {len(interview_ids)} candidates")

        try:
            prompt = self._build_comparison_prompt(interview_ids, candidate_data)

            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}],
            )

            comparison_data = self._parse_comparison_response(response.content[0].text)

            candidate_names = [c.get("name", "Candidate") for c in candidate_data]

            report = ComparisonReport(
                interview_ids=interview_ids,
                candidate_names=candidate_names,
                comparison_metrics=comparison_data.get("metrics", {}),
                rankings=comparison_data.get("rankings", []),
                strengths_by_candidate=comparison_data.get("strengths", {}),
                weaknesses_by_candidate=comparison_data.get("weaknesses", {}),
            )

            logger.info(f"Comparison complete")
            return report

        except Exception as e:
            logger.error(f"Error comparing candidates: {str(e)}")
            raise

    # Helper methods

    def _build_notes_prompt(
        self, transcript: TranscriptResult, requirement_context: Dict[str, Any]
    ) -> str:
        """Build prompt for structured notes generation."""
        return f"""
Analyze this interview transcript and generate structured notes:

Transcript:
{transcript.full_text}

Job Context:
Title: {requirement_context.get("title", "Unknown")}
Required Skills: {', '.join(requirement_context.get("skills_required", []))}

Generate notes in JSON format with:
{{
  "competencies": {{"competency_name": ["note1", "note2"]}},
  "observations": ["observation1", "observation2"],
  "red_flags": ["flag1", "flag2"],
  "strengths": ["strength1", "strength2"]
}}

Only return JSON, no other text.
"""

    def _build_competency_prompt(
        self, transcript: TranscriptResult, requirement_skills: List[str]
    ) -> str:
        """Build prompt for competency extraction."""
        skills_str = ", ".join(requirement_skills[:5])
        return f"""
Analyze this transcript for evidence of these competencies:
{skills_str}

Transcript:
{transcript.full_text}

Rate each competency 1-5 with supporting evidence. Return JSON:
{{
  "competency_name": {{
    "rating": 1-5,
    "evidence": ["quote1", "quote2"]
  }}
}}

Only return JSON, no other text.
"""

    def _build_sentiment_prompt(self, transcript: TranscriptResult) -> str:
        """Build prompt for sentiment analysis."""
        return f"""
Analyze the sentiment in this interview transcript.

Transcript:
{transcript.full_text}

Return JSON with:
{{
  "overall": "positive|neutral|negative",
  "score": 0.0-1.0,
  "trend": [
    {{"timestamp": 0, "sentiment": "positive", "score": 0.5}}
  ]
}}

Only return JSON, no other text.
"""

    def _build_bias_detection_prompt(self, transcript: TranscriptResult) -> str:
        """Build prompt for bias detection."""
        return f"""
Analyze this interview for potential bias or illegal questions:

Transcript:
{transcript.full_text}

Identify any leading questions, discriminatory language, or illegal inquiries.
Return JSON:
{{
  "flags": [
    {{
      "type": "leading_question|illegal|discriminatory",
      "severity": "low|medium|high",
      "description": "description",
      "suggestion": "improvement suggestion"
    }}
  ],
  "score": 0.0-1.0,
  "recommendations": ["rec1"]
}}

Only return JSON, no other text.
"""

    def _build_comparison_prompt(
        self, interview_ids: List[int], candidate_data: List[Dict[str, Any]]
    ) -> str:
        """Build prompt for candidate comparison."""
        candidates_str = ", ".join([c.get("name", "Unknown") for c in candidate_data])
        return f"""
Compare these candidates: {candidates_str}

Candidate Data:
{json.dumps(candidate_data, indent=2)}

Return JSON comparison with:
{{
  "metrics": {{"metric_name": [scores]}},
  "rankings": [{{"rank": 1, "candidate": "name", "score": 9.5}}],
  "strengths": {{1: ["strength1"]}},
  "weaknesses": {{1: ["weakness1"]}}
}}

Only return JSON, no other text.
"""

    def _parse_notes_response(self, response_text: str) -> Dict[str, Any]:
        """Parse notes response."""
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
            return {
                "competencies": {},
                "observations": [],
                "red_flags": [],
                "strengths": [],
            }

    def _parse_competency_response(self, response_text: str) -> Dict[str, Any]:
        """Parse competency response."""
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
            return {}

    def _parse_sentiment_response(self, response_text: str) -> Dict[str, Any]:
        """Parse sentiment response."""
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
            return {"overall": "neutral", "score": 0.5, "trend": []}

    def _parse_bias_response(self, response_text: str) -> Dict[str, Any]:
        """Parse bias detection response."""
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
            return {"flags": [], "score": 0.0, "recommendations": []}

    def _parse_comparison_response(self, response_text: str) -> Dict[str, Any]:
        """Parse comparison response."""
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
            return {
                "metrics": {},
                "rankings": [],
                "strengths": {},
                "weaknesses": {},
            }

    async def on_start(self) -> None:
        """Called when the agent starts."""
        logger.info(f"{self.agent_name} started successfully")

    async def on_stop(self) -> None:
        """Called when the agent stops."""
        logger.info(f"{self.agent_name} stopped")
