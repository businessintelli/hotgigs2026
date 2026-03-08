"""Schemas for SLA endpoints."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class SLAConfigurationCreate(BaseModel):
    organization_id: int
    name: str
    response_time_hours: Optional[int] = None
    fill_time_days: Optional[int] = None
    min_quality_score: Optional[float] = None
    min_acceptance_rate: Optional[float] = None
    min_retention_days: Optional[int] = None
    response_time_penalty: float = 100.0
    fill_time_penalty: float = 0.0
    quality_penalty_per_point: float = 0.0
    penalty_calculation: str = "cumulative"
    notes: Optional[str] = None


class SLAConfigurationResponse(BaseModel):
    id: int
    organization_id: int
    name: str
    response_time_hours: Optional[int]
    fill_time_days: Optional[int]
    min_quality_score: Optional[float]
    min_acceptance_rate: Optional[float]
    min_retention_days: Optional[int]
    response_time_penalty: float
    fill_time_penalty: float
    quality_penalty_per_point: float
    penalty_calculation: str
    is_active: bool
    notes: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True


class SLABreachResponse(BaseModel):
    id: int
    sla_config_id: int
    requirement_id: Optional[int]
    supplier_org_id: Optional[int]
    metric_type: str
    severity: str
    threshold_value: float
    actual_value: float
    variance: float
    penalty_amount: Optional[float]
    detected_at: datetime
    resolved_at: Optional[datetime]
    resolution_notes: Optional[str]
    class Config:
        from_attributes = True


class SLABreachResolve(BaseModel):
    resolution_notes: str


class SLADashboardResponse(BaseModel):
    total_configs: int
    active_breaches: int
    resolved_breaches: int
    critical_breaches: int
    total_penalties: float
    breaches_by_metric: dict = {}
    breaches_by_severity: dict = {}
