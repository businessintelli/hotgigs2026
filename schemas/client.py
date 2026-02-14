from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, date


class ClientContactBase(BaseModel):
    """Base client contact schema."""
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    title: Optional[str] = None
    department: Optional[str] = None
    role_type: str
    is_primary: bool = False
    is_decision_maker: bool = False
    linkedin_url: Optional[str] = None
    notes: Optional[str] = None


class ClientContactCreate(ClientContactBase):
    """Create client contact schema."""
    pass


class ClientContactUpdate(BaseModel):
    """Update client contact schema."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    title: Optional[str] = None
    department: Optional[str] = None
    role_type: Optional[str] = None
    is_primary: Optional[bool] = None
    is_decision_maker: Optional[bool] = None
    linkedin_url: Optional[str] = None
    notes: Optional[str] = None


class ClientContactResponse(ClientContactBase):
    """Client contact response schema."""
    id: int
    client_id: int
    last_contacted_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SLAConfig(BaseModel):
    """SLA configuration."""
    time_to_submit_hours: int
    min_match_score: float
    max_submission_rejection_rate: float
    response_time_hours: int


class ClientBase(BaseModel):
    """Base client schema."""
    company_name: str
    industry: Optional[str] = None
    company_size: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    description: Optional[str] = None
    account_manager_id: Optional[int] = None
    client_tier: str = "standard"
    engagement_status: str = "active"
    annual_revenue_target: Optional[float] = None
    payment_terms: str = "net_30"
    billing_rate_type: Optional[str] = None
    sla_config: Optional[SLAConfig] = None
    contract_start_date: Optional[date] = None
    contract_end_date: Optional[date] = None
    preferences: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class ClientCreate(ClientBase):
    """Create client schema."""
    pass


class ClientUpdate(BaseModel):
    """Update client schema."""
    company_name: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    description: Optional[str] = None
    account_manager_id: Optional[int] = None
    client_tier: Optional[str] = None
    engagement_status: Optional[str] = None
    annual_revenue_target: Optional[float] = None
    payment_terms: Optional[str] = None
    billing_rate_type: Optional[str] = None
    sla_config: Optional[SLAConfig] = None
    contract_start_date: Optional[date] = None
    contract_end_date: Optional[date] = None
    preferences: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class ClientResponse(ClientBase):
    """Client response schema."""
    id: int
    customer_id: Optional[int] = None
    health_score: Optional[float] = None
    actual_revenue_ytd: float
    onboarded_at: Optional[datetime] = None
    last_interaction_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClientInteractionBase(BaseModel):
    """Base client interaction schema."""
    interaction_type: str
    subject: str
    notes: Optional[str] = None
    outcome: Optional[str] = None
    follow_up_date: Optional[date] = None
    follow_up_notes: Optional[str] = None


class ClientInteractionCreate(ClientInteractionBase):
    """Create client interaction schema."""
    contact_id: Optional[int] = None


class ClientInteractionResponse(ClientInteractionBase):
    """Client interaction response schema."""
    id: int
    client_id: int
    contact_id: Optional[int] = None
    recorded_by: int
    interaction_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class ClientBillingBase(BaseModel):
    """Base client billing schema."""
    placement_id: Optional[int] = None
    invoice_number: Optional[str] = None
    billing_period_start: date
    billing_period_end: date
    hours_billed: Optional[float] = None
    bill_rate: float
    total_amount: float
    status: str = "pending"
    due_date: Optional[date] = None
    notes: Optional[str] = None


class ClientBillingCreate(ClientBillingBase):
    """Create client billing schema."""
    pass


class ClientBillingUpdate(BaseModel):
    """Update client billing schema."""
    status: Optional[str] = None
    notes: Optional[str] = None


class ClientBillingResponse(ClientBillingBase):
    """Client billing response schema."""
    id: int
    client_id: int
    paid_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ClientHealthScore(BaseModel):
    """Client health score."""
    score: float  # 0-100
    status: str  # healthy/at_risk/critical
    activity_recency: float
    fill_rate: float
    submission_acceptance_rate: float
    contract_status: str
    payment_status: str


class ClientBillingSummary(BaseModel):
    """Client billing summary."""
    total_invoiced: float
    total_paid: float
    total_outstanding: float
    overdue_amount: float
    next_billing_date: Optional[date] = None


class ClientActivityMetrics(BaseModel):
    """Client activity metrics."""
    active_requirements: int
    open_submissions: int
    placed_candidates: int
    total_interactions_90d: int
    last_interaction_date: Optional[datetime] = None
    days_since_last_interaction: int


class ClientQBRReport(BaseModel):
    """Quarterly Business Review report."""
    client_id: int
    quarter: str
    start_date: date
    end_date: date
    total_requirements: int
    total_submissions: int
    total_placements: int
    fill_rate: float
    avg_time_to_fill_days: float
    total_spent: float
    revenue_vs_target: float
    key_metrics: Dict[str, Any]
    recommendations: List[str]
    generated_at: datetime


class ChurnRiskClient(BaseModel):
    """Client at churn risk."""
    client_id: int
    company_name: str
    churn_score: float  # 0-100
    risk_factors: List[str]
    last_activity: Optional[datetime] = None
    recommended_actions: List[str]


class ClientAnalytics(BaseModel):
    """Overall client analytics."""
    total_clients: int
    active_clients: int
    inactive_clients: int
    churned_clients: int
    at_risk_clients: int
    total_annual_revenue: float
    avg_client_revenue: float
    top_clients_by_revenue: List[Dict[str, Any]]
    revenue_by_tier: Dict[str, float]
    period: str
