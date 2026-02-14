"""Pydantic schemas for interview intelligence features."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from schemas.common import BaseResponse


class TranscriptSegment(BaseModel):
    """Single segment of interview transcript."""

    speaker: str = Field(..., description="Speaker name (Interviewer/Candidate)")
    text: str = Field(..., description="Segment text")
    start_time: int = Field(..., ge=0, description="Start time in seconds")
    end_time: int = Field(..., ge=0, description="End time in seconds")
    confidence: Optional[float] = Field(None, ge=0, le=1)


class RecordingCreate(BaseModel):
    """Create interview recording."""

    interview_id: int
    recording_url: str = Field(..., max_length=500)
    recording_type: str = Field(..., description="audio or video")
    duration_seconds: Optional[int] = Field(None, ge=0)
    file_size: Optional[int] = Field(None, ge=0)


class RecordingResponse(BaseResponse):
    """Interview recording response."""

    interview_id: int
    recording_url: str
    recording_type: str
    duration_seconds: Optional[int] = None
    file_size: Optional[int] = None
    storage_path: Optional[str] = None
    status: str
    processing_error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class TranscriptResponse(BaseResponse):
    """Interview transcript response."""

    recording_id: int
    full_text: str
    segments: Optional[List[TranscriptSegment]] = None
    language: str
    word_count: int
    confidence_score: Optional[float] = None

    class Config:
        from_attributes = True


class NoteCreate(BaseModel):
    """Create interview note."""

    interview_id: int
    note_type: str = Field(..., description="competency, observation, red_flag, strength")
    category: Optional[str] = Field(None, max_length=255)
    content: str = Field(...)
    timestamp_start: Optional[int] = Field(None, ge=0)
    timestamp_end: Optional[int] = Field(None, ge=0)
    confidence: Optional[float] = Field(None, ge=0, le=1)
    source: str = Field(default="ai")
    supporting_quotes: Optional[List[str]] = Field(default_factory=list)


class NoteResponse(BaseResponse):
    """Interview note response."""

    interview_id: int
    note_type: str
    category: Optional[str] = None
    content: str
    timestamp_start: Optional[int] = None
    timestamp_end: Optional[int] = None
    confidence: Optional[float] = None
    source: str
    supporting_quotes: Optional[List[str]] = None

    class Config:
        from_attributes = True


class CompetencyAssessment(BaseModel):
    """Competency assessment for a candidate."""

    competency_name: str
    rating: int = Field(..., ge=1, le=5)
    evidence: Optional[List[str]] = Field(default_factory=list)
    confidence: Optional[float] = Field(None, ge=0, le=1)
    assessed_by: str = Field(default="ai")


class SentimentDataPoint(BaseModel):
    """Single sentiment analysis data point."""

    timestamp: int = Field(..., ge=0, description="Seconds into interview")
    sentiment: str = Field(..., description="positive, neutral, negative")
    score: float = Field(..., ge=-1, le=1)
    description: Optional[str] = None


class SentimentResult(BaseModel):
    """Sentiment analysis results."""

    overall_sentiment: str
    overall_score: float
    trend: List[SentimentDataPoint]
    confidence_intervals: Optional[Dict[str, float]] = None


class QuestionCoverage(BaseModel):
    """Question coverage analysis."""

    technical_percentage: float = Field(..., ge=0, le=100)
    behavioral_percentage: float = Field(..., ge=0, le=100)
    situational_percentage: float = Field(..., ge=0, le=100)
    culture_fit_percentage: float = Field(..., ge=0, le=100)


class AnalyticsResponse(BaseModel):
    """Interview analytics response."""

    interview_id: int
    talk_time_ratio: Optional[float] = None
    question_count: int
    avg_response_length: Optional[float] = None
    sentiment_overall: Optional[str] = None
    sentiment_trend: Optional[Dict[str, Any]] = None
    interview_quality_score: Optional[float] = Field(None, ge=0, le=100)
    bias_flags: Optional[List[Dict[str, Any]]] = None
    question_coverage: Optional[QuestionCoverage] = None

    class Config:
        from_attributes = True


class BiasFlag(BaseModel):
    """Bias detection flag."""

    flag_type: str = Field(..., description="leading_question, illegal_question, pattern")
    severity: str = Field(..., description="low, medium, high")
    description: str
    timestamp: Optional[int] = Field(None, ge=0)
    suggestion: Optional[str] = None


class BiasReport(BaseModel):
    """Bias detection report."""

    interview_id: int
    has_bias: bool
    total_flags: int
    flags: List[BiasFlag]
    bias_score: float = Field(..., ge=0, le=1)
    recommendations: List[str]


class StructuredNote(BaseModel):
    """Structured interview note."""

    category: str
    content: str
    timestamp: Optional[int] = None
    source: str = "ai"


class ComparisonMetric(BaseModel):
    """Single comparison metric."""

    metric_name: str
    candidate_1_value: float
    candidate_2_value: float
    candidate_3_value: Optional[float] = None
    candidate_4_value: Optional[float] = None
    candidate_5_value: Optional[float] = None
    unit: Optional[str] = None


class CandidateComparisonSchema(BaseModel):
    """Comparison of multiple candidates."""

    candidate_ids: List[int]
    candidate_names: List[str]
    metrics: List[ComparisonMetric]
    overall_rankings: List[Dict[str, Any]]
    strengths_by_candidate: Dict[int, List[str]]
    weaknesses_by_candidate: Dict[int, List[str]]
    recommendations: str


class InterviewQuestionSchema(BaseModel):
    """Interview question schema."""

    question_text: str
    category: str = Field(..., description="technical, behavioral, situational, culture_fit")
    difficulty: str = Field(default="medium", description="easy, medium, hard")
    order: int = Field(..., ge=1)
    context: Optional[Dict[str, Any]] = None


class ResponseEvaluationSchema(BaseModel):
    """Response evaluation schema."""

    question_id: int
    response_text: Optional[str] = None
    ai_score: float = Field(..., ge=0, le=100)
    evaluation_notes: Optional[str] = None
    strengths: Optional[List[str]] = None
    areas_for_improvement: Optional[List[str]] = None


class ScorecardCompetency(BaseModel):
    """Competency rating in scorecard."""

    name: str
    rating: int = Field(..., ge=1, le=5)
    evidence: Optional[List[str]] = None
    comments: Optional[str] = None


class ScorecardSchema(BaseModel):
    """Interview scorecard schema."""

    interview_id: int
    candidate_id: int
    candidate_name: str
    requirement_id: int
    requirement_title: str
    interview_date: datetime
    interviewer_name: Optional[str] = None
    competencies: List[ScorecardCompetency]
    overall_rating: int = Field(..., ge=1, le=5)
    recommendation: str = Field(..., description="hire, consider, no_hire")
    strengths: List[str]
    weaknesses: List[str]
    next_steps: Optional[List[str]] = None
    comments: Optional[str] = None
    generated_by_ai: bool


class FeedbackSummary(BaseModel):
    """Feedback summary for interview."""

    interview_id: int
    candidates_interviewed: int
    avg_rating: float
    competency_highlights: Dict[str, List[str]]
    common_strengths: List[str]
    areas_needing_improvement: List[str]
    overall_recommendation: str


class InterviewResultSchema(BaseModel):
    """Complete interview result."""

    interview_id: int
    status: str
    questions_asked: int
    questions_answered: int
    avg_response_score: Optional[float] = None
    completion_percentage: float
    estimated_score: Optional[float] = None
    scorecard: Optional[ScorecardSchema] = None
