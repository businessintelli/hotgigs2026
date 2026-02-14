"""Pydantic schemas for AI Copilot."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from schemas.common import BaseResponse, PaginationParams


class CopilotMessageCreate(BaseModel):
    """Create a copilot message."""

    content: str = Field(..., min_length=1, max_length=10000)
    function_calls: Optional[List[Dict[str, Any]]] = Field(default=None)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class CopilotMessageResponse(BaseResponse):
    """Copilot message response."""

    conversation_id: int
    role: str
    content: str
    function_calls: Optional[List[Dict[str, Any]]] = None
    function_results: Optional[List[Dict[str, Any]]] = None
    tokens_used: int = 0
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class CopilotConversationCreate(BaseModel):
    """Create a copilot conversation."""

    title: str = Field(..., min_length=1, max_length=255)
    context_requirement_id: Optional[int] = None
    context_candidate_id: Optional[int] = None
    context_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class CopilotConversationUpdate(BaseModel):
    """Update a copilot conversation."""

    title: Optional[str] = Field(default=None, max_length=255)
    context_metadata: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class CopilotConversationResponse(BaseResponse):
    """Copilot conversation response."""

    user_id: int
    title: str
    context_requirement_id: Optional[int] = None
    context_candidate_id: Optional[int] = None
    context_metadata: Optional[Dict[str, Any]] = None
    message_count: int = 0
    total_tokens_used: int = 0
    messages: Optional[List[CopilotMessageResponse]] = Field(default=None)

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    """Chat request to copilot."""

    message: str = Field(..., min_length=1, max_length=10000)
    conversation_id: Optional[int] = None
    context_requirement_id: Optional[int] = None
    context_candidate_id: Optional[int] = None


class ChatResponse(BaseModel):
    """Chat response from copilot."""

    conversation_id: int
    message_id: int
    response: str
    function_calls: Optional[List[Dict[str, Any]]] = None
    function_results: Optional[List[Dict[str, Any]]] = None
    tokens_used: int
    timestamp: datetime


class CopilotInsightCreate(BaseModel):
    """Create a copilot insight."""

    insight_type: str = Field(..., min_length=1, max_length=50)
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    summary: Optional[str] = None
    severity: str = Field(default="info")
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    recommendations: Optional[List[str]] = Field(default_factory=list)
    confidence_score: Optional[float] = Field(default=0.0, ge=0.0, le=1.0)


class CopilotInsightResponse(BaseResponse):
    """Copilot insight response."""

    conversation_id: Optional[int] = None
    insight_type: str
    title: str
    content: str
    summary: Optional[str] = None
    severity: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    recommendations: Optional[List[str]] = None
    confidence_score: Optional[float] = None
    is_read: bool = False
    read_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class RequirementAnalysisResponse(BaseModel):
    """Requirement analysis response."""

    requirement_id: int
    title: str
    market_difficulty: str
    skill_availability: Dict[str, str]
    suggested_sourcing_channels: List[str]
    estimated_days_to_fill: int
    similar_past_requirements: List[Dict[str, Any]]
    key_risks: List[str]
    market_salary_range: Dict[str, float]


class CandidateComparisonResponse(BaseModel):
    """Candidate comparison response."""

    requirement_id: int
    candidates: List[Dict[str, Any]]
    comparison_matrix: Dict[str, Dict[str, Any]]
    recommendation: Dict[str, Any]
    top_candidate_id: int


class PipelineHealthResponse(BaseModel):
    """Pipeline health metrics response."""

    requirement_id: Optional[int] = None
    total_candidates: int
    candidates_by_stage: Dict[str, int]
    bottleneck_stage: Optional[str] = None
    velocity_candidates_per_week: float
    predicted_fill_rate: float
    time_to_fill_estimate_days: int
    quality_metrics: Dict[str, float]


class CandidateSuggestionResponse(BaseModel):
    """Candidate suggestion response."""

    candidate_id: int
    name: str
    title: str
    match_score: float
    key_strengths: List[str]
    potential_concerns: List[str]
    reasoning: str


class MarketInsightsResponse(BaseModel):
    """Market insights response."""

    skills: List[str]
    location: Optional[str] = None
    salary_ranges: Dict[str, Dict[str, float]]
    supply_demand_ratio: Dict[str, str]
    trending_skills: List[Dict[str, Any]]
    market_insights: str


class OutreachEmailResponse(BaseModel):
    """Generated outreach email response."""

    candidate_id: int
    requirement_id: int
    subject: str
    body: str
    personalization_notes: List[str]


class CandidateSummaryResponse(BaseModel):
    """Candidate summary response."""

    candidate_id: int
    name: str
    profile: Dict[str, Any]
    skills: List[Dict[str, Any]]
    experience_timeline: List[Dict[str, Any]]
    interview_history: List[Dict[str, Any]]
    placement_history: List[Dict[str, Any]]
    risk_factors: List[str]
    strengths: List[str]


class GeneratedInsightResponse(BaseModel):
    """Generated insight response."""

    insight_id: int
    insight_type: str
    title: str
    content: str
    severity: str
    recommendations: List[str]
    timestamp: datetime
