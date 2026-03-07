"""MSP/VMS workflow request/response schemas."""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


# --- Requirement Distribution ---

class DistributeRequirementRequest(BaseModel):
    """Distribute a requirement to suppliers."""
    supplier_org_ids: List[int] = Field(..., min_length=1)
    expires_at: Optional[datetime] = None
    max_submissions: int = Field(default=3, ge=1, le=20)
    notes_to_supplier: Optional[str] = None


class DistributionResponse(BaseModel):
    """Requirement distribution response."""
    id: int
    organization_id: int
    requirement_id: int
    supplier_org_id: int
    supplier_org_name: Optional[str] = None
    status: str
    distributed_at: datetime
    expires_at: Optional[datetime] = None
    max_submissions: int
    submission_count: int = 0
    notes_to_supplier: Optional[str] = None

    class Config:
        from_attributes = True


class DistributionListResponse(BaseModel):
    """List of distributions for a requirement."""
    items: List[DistributionResponse]
    total: int


# --- Supplier Submissions ---

class SupplierSubmitCandidateRequest(BaseModel):
    """Supplier submits a candidate for a distributed requirement."""
    candidate_id: int
    requirement_distribution_id: int
    bill_rate: Optional[float] = Field(None, ge=0)
    pay_rate: Optional[float] = Field(None, ge=0)
    availability_date: Optional[date] = None
    supplier_notes: Optional[str] = None
    candidate_summary: Optional[str] = None


class SupplierSubmissionResponse(BaseModel):
    """Supplier submission response."""
    id: int
    organization_id: int
    requirement_distribution_id: int
    candidate_id: int
    candidate_name: Optional[str] = None
    supplier_org_name: Optional[str] = None
    status: str
    bill_rate: Optional[float] = None
    pay_rate: Optional[float] = None
    availability_date: Optional[date] = None
    supplier_notes: Optional[str] = None
    quality_score: Optional[float] = None
    match_score: Optional[float] = None
    duplicate_flag: Optional[str] = None
    submitted_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class SubmissionListResponse(BaseModel):
    """Paginated list of submissions."""
    items: List[SupplierSubmissionResponse]
    total: int
    offset: int
    limit: int


# --- MSP Review ---

class MSPReviewRequest(BaseModel):
    """MSP reviews a supplier submission."""
    decision: str = Field(..., pattern="^(approve|reject|request_changes)$")
    match_score: Optional[float] = Field(None, ge=0, le=100)
    quality_rating: Optional[int] = Field(None, ge=1, le=5)
    screening_notes: Optional[str] = None
    strengths: Optional[str] = None
    concerns: Optional[str] = None
    recommendation: Optional[str] = None


class MSPReviewResponse(BaseModel):
    """MSP review response."""
    id: int
    supplier_submission_id: int
    reviewer_id: int
    reviewer_name: Optional[str] = None
    decision: str
    match_score: Optional[float] = None
    quality_rating: Optional[int] = None
    screening_notes: Optional[str] = None
    strengths: Optional[str] = None
    concerns: Optional[str] = None
    recommendation: Optional[str] = None
    forwarded_to_client_at: Optional[datetime] = None
    reviewed_at: datetime

    class Config:
        from_attributes = True


# --- Client Feedback ---

class ClientFeedbackRequest(BaseModel):
    """Client provides feedback on MSP-submitted candidate."""
    decision: str = Field(..., pattern="^(shortlist|reject|interview|hold)$")
    feedback_notes: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    preferred_interview_date: Optional[datetime] = None
    interview_type: Optional[str] = None


class ClientFeedbackResponse(BaseModel):
    """Client feedback response."""
    id: int
    supplier_submission_id: int
    client_user_id: int
    decision: str
    feedback_notes: Optional[str] = None
    rating: Optional[int] = None
    feedback_at: datetime

    class Config:
        from_attributes = True


# --- Placement ---

class PlacementCreateRequest(BaseModel):
    """Create a placement record."""
    requirement_id: int
    candidate_id: int
    supplier_org_id: int
    client_org_id: int
    supplier_submission_id: Optional[int] = None
    start_date: date
    end_date: Optional[date] = None
    bill_rate: float = Field(..., ge=0)
    pay_rate: float = Field(..., ge=0)
    msp_margin: Optional[float] = None
    currency: str = Field(default="USD", max_length=10)
    timesheet_frequency: str = Field(default="weekly", pattern="^(weekly|biweekly|monthly)$")
    work_location: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    manager_name: Optional[str] = None
    manager_email: Optional[str] = None


class PlacementResponse(BaseModel):
    """Placement record response."""
    id: int
    organization_id: int
    requirement_id: int
    candidate_id: int
    candidate_name: Optional[str] = None
    supplier_org_id: int
    supplier_org_name: Optional[str] = None
    client_org_id: int
    client_org_name: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    bill_rate: float
    pay_rate: float
    msp_margin: Optional[float] = None
    status: str
    work_location: Optional[str] = None
    job_title: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PlacementListResponse(BaseModel):
    """Paginated list of placements."""
    items: List[PlacementResponse]
    total: int
    offset: int
    limit: int


# --- Dashboard Metrics ---

class MSPDashboardMetrics(BaseModel):
    """MSP dashboard aggregate metrics."""
    total_clients: int = 0
    total_suppliers: int = 0
    active_requirements: int = 0
    total_distributions: int = 0
    pending_submissions: int = 0
    submissions_this_month: int = 0
    active_placements: int = 0
    placements_this_month: int = 0
    avg_time_to_fill_days: Optional[float] = None
    avg_submission_quality: Optional[float] = None
    fill_rate_percent: Optional[float] = None


class SupplierScorecard(BaseModel):
    """Supplier performance scorecard."""
    supplier_org_id: int
    supplier_name: str
    tier: Optional[str] = None
    total_submissions: int = 0
    approved_submissions: int = 0
    rejected_submissions: int = 0
    total_placements: int = 0
    avg_quality_score: Optional[float] = None
    avg_response_time_hours: Optional[float] = None
    fill_rate_percent: Optional[float] = None


class ClientMetrics(BaseModel):
    """Client-specific metrics."""
    client_org_id: int
    client_name: str
    total_requirements: int = 0
    active_requirements: int = 0
    filled_requirements: int = 0
    total_submissions_received: int = 0
    active_placements: int = 0
    avg_time_to_fill_days: Optional[float] = None
