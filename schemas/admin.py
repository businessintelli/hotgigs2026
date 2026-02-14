from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class SystemConfigBase(BaseModel):
    """Base system config schema."""
    config_key: str
    config_value: Dict[str, Any]
    config_type: str
    category: str
    description: Optional[str] = None
    is_encrypted: bool = False


class SystemConfigCreate(SystemConfigBase):
    """Create system config schema."""
    pass


class SystemConfigUpdate(BaseModel):
    """Update system config schema."""
    config_value: Dict[str, Any]
    description: Optional[str] = None
    is_encrypted: Optional[bool] = None


class SystemConfigResponse(SystemConfigBase):
    """System config response schema."""
    id: int
    updated_by: Optional[int] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReportColumnDefinition(BaseModel):
    """Report column definition."""
    field: str
    label: str
    type: str
    format: Optional[str] = None
    sortable: bool = True
    visible: bool = True


class ReportFilter(BaseModel):
    """Report filter definition."""
    field: str
    operator: str  # eq/ne/gt/lt/contains/in
    default_value: Optional[Any] = None


class ReportSorting(BaseModel):
    """Report sorting definition."""
    field: str
    direction: str  # asc/desc


class ReportAggregation(BaseModel):
    """Report aggregation definition."""
    field: str
    function: str  # sum/avg/count/min/max


class ChartConfig(BaseModel):
    """Chart configuration."""
    type: str  # bar/line/pie/table
    x_axis: Optional[str] = None
    y_axis: Optional[str] = None
    title: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class ReportScheduleConfig(BaseModel):
    """Report schedule configuration."""
    frequency: str  # daily/weekly/monthly
    day_of_week: Optional[str] = None  # For weekly: mon/tue/wed/thu/fri/sat/sun
    day_of_month: Optional[int] = None  # For monthly: 1-31
    time: str  # HH:MM format
    recipients: List[str]  # Email addresses
    format: str = "json"  # json/csv/xlsx/pdf


class ReportDefinitionBase(BaseModel):
    """Base report definition schema."""
    name: str
    description: Optional[str] = None
    report_type: str
    data_source: str
    columns: List[ReportColumnDefinition]
    filters: Optional[List[ReportFilter]] = None
    grouping: Optional[List[str]] = None
    sorting: Optional[List[ReportSorting]] = None
    aggregations: Optional[List[ReportAggregation]] = None
    chart_config: Optional[ChartConfig] = None
    is_public: bool = True


class ReportDefinitionCreate(ReportDefinitionBase):
    """Create report definition schema."""
    schedule: Optional[ReportScheduleConfig] = None


class ReportDefinitionUpdate(BaseModel):
    """Update report definition schema."""
    name: Optional[str] = None
    description: Optional[str] = None
    columns: Optional[List[ReportColumnDefinition]] = None
    filters: Optional[List[ReportFilter]] = None
    grouping: Optional[List[str]] = None
    sorting: Optional[List[ReportSorting]] = None
    aggregations: Optional[List[ReportAggregation]] = None
    chart_config: Optional[ChartConfig] = None
    is_public: Optional[bool] = None
    schedule: Optional[ReportScheduleConfig] = None


class ReportDefinitionResponse(ReportDefinitionBase):
    """Report definition response schema."""
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReportExecutionBase(BaseModel):
    """Base report execution schema."""
    parameters: Optional[Dict[str, Any]] = None
    export_format: Optional[str] = None


class ReportExecutionCreate(ReportExecutionBase):
    """Create report execution schema."""
    pass


class ReportExecutionResponse(BaseModel):
    """Report execution response schema."""
    id: int
    report_id: int
    parameters: Optional[Dict[str, Any]] = None
    status: str
    result_data: Optional[Dict[str, Any]] = None
    row_count: int
    execution_time_ms: Optional[int] = None
    export_format: Optional[str] = None
    export_path: Optional[str] = None
    executed_by: Optional[int] = None
    executed_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    """Create user schema."""
    email: str
    first_name: str
    last_name: str
    role: str
    phone: Optional[str] = None


class UserUpdate(BaseModel):
    """Update user schema."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """User response schema."""
    id: int
    email: str
    first_name: str
    last_name: str
    role: str
    phone: Optional[str] = None
    is_active: bool
    last_login_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class BulkUserImport(BaseModel):
    """Bulk user import schema."""
    users: List[UserCreate]
    send_invitations: bool = True


class BulkUserImportResponse(BaseModel):
    """Bulk import response."""
    total: int
    successful: int
    failed: int
    errors: List[Dict[str, str]] = []


class HealthCheckStatus(BaseModel):
    """Health check status."""
    component: str
    status: str  # healthy/degraded/unhealthy
    details: Optional[Dict[str, Any]] = None


class SystemHealthResponse(BaseModel):
    """System health response."""
    overall_status: str
    timestamp: datetime
    components: List[HealthCheckStatus]


class StandardReportParams(BaseModel):
    """Standard report parameters."""
    start_date: str
    end_date: str
    customer_id: Optional[int] = None
    user_id: Optional[int] = None


class PipelineSummaryResponse(BaseModel):
    """Pipeline summary report."""
    total_requirements: int
    total_candidates: int
    stage_breakdown: Dict[str, int]
    velocity_metrics: Dict[str, float]
    conversion_rates: Dict[str, float]
    period: str


class RecruiterProductivityResponse(BaseModel):
    """Recruiter productivity report."""
    recruiter_id: int
    recruiter_name: str
    total_submissions: int
    total_placements: int
    average_match_score: float
    avg_days_to_submission: float
    avg_days_to_placement: float
    period: str


class ClientActivityResponse(BaseModel):
    """Client activity report."""
    customer_id: int
    customer_name: str
    total_requirements: int
    total_submissions: int
    total_placements: int
    avg_time_to_fill_days: float
    total_spend: float
    period: str


class SupplierPerformanceResponse(BaseModel):
    """Supplier performance report."""
    supplier_id: int
    supplier_name: str
    total_submissions: int
    placement_count: int
    fill_rate: float
    average_quality_score: float
    response_time_hours: float
    ranking: int
    period: str


class FinancialSummaryResponse(BaseModel):
    """Financial summary report."""
    total_placements: int
    total_revenue: float
    total_bill_amount: float
    total_cost: float
    gross_margin: float
    gross_margin_percent: float
    referral_bonuses_paid: float
    period: str


class ComplianceAuditResponse(BaseModel):
    """Compliance audit report."""
    total_contracts: int
    active_contracts: int
    pending_signature_count: int
    expired_documents: int
    completion_rate_percent: float
    expiring_soon_count: int
    period: str


class DiversityMetricsResponse(BaseModel):
    """Diversity metrics report."""
    total_candidates: int
    source_distribution: Dict[str, int]
    stage_progression_by_source: Dict[str, Dict[str, float]]
    diversity_score: float
    period: str


class TimeToFillResponse(BaseModel):
    """Time-to-fill metrics report."""
    average_time_to_fill_days: float
    by_priority: Dict[str, float]
    by_customer: Dict[str, float]
    by_role: Dict[str, float]
    by_stage: Dict[str, float]
    period: str
