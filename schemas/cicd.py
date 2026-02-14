from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class EnvironmentCreate(BaseModel):
    """Create environment schema."""
    name: str
    display_name: str
    url: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class EnvironmentUpdate(BaseModel):
    """Update environment schema."""
    display_name: Optional[str] = None
    url: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    health_status: Optional[str] = None


class EnvironmentResponse(BaseModel):
    """Environment response schema."""
    id: int
    name: str
    display_name: str
    url: Optional[str] = None
    config: Dict[str, Any]
    current_version: Optional[str] = None
    last_deployed_at: Optional[datetime] = None
    status: str
    health_status: str
    last_health_check_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ComponentVersion(BaseModel):
    """Component version definition."""
    component: str
    old_version: str
    new_version: str


class ReleaseArtifact(BaseModel):
    """Release artifact definition."""
    name: str
    path: str
    checksum: str


class ReleaseCreate(BaseModel):
    """Create release schema."""
    version: str
    name: Optional[str] = None
    description: Optional[str] = None
    release_type: str  # major/minor/patch/hotfix
    components: Optional[List[ComponentVersion]] = None
    artifacts: Optional[List[ReleaseArtifact]] = None
    git_tag: Optional[str] = None
    git_commit: Optional[str] = None


class ReleaseUpdate(BaseModel):
    """Update release schema."""
    name: Optional[str] = None
    description: Optional[str] = None
    changelog: Optional[str] = None
    status: Optional[str] = None


class ReleaseResponse(BaseModel):
    """Release response schema."""
    id: int
    version: str
    name: Optional[str] = None
    description: Optional[str] = None
    changelog: Optional[str] = None
    ai_changelog: Optional[str] = None
    release_type: str
    components: Optional[List[ComponentVersion]] = None
    artifacts: Optional[List[ReleaseArtifact]] = None
    status: str
    released_at: Optional[datetime] = None
    released_by: Optional[int] = None
    git_tag: Optional[str] = None
    git_commit: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PipelineStep(BaseModel):
    """Pipeline step definition."""
    step: str
    status: str  # pending/running/completed/failed
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    output: Optional[str] = None


class DeploymentCreate(BaseModel):
    """Create deployment schema."""
    release_id: Optional[int] = None
    environment_id: int
    version: str
    notes: Optional[str] = None


class DeploymentResponse(BaseModel):
    """Deployment response schema."""
    id: int
    release_id: Optional[int] = None
    environment_id: int
    version: str
    status: str
    pipeline_steps: List[PipelineStep] = []
    pre_deploy_checks: Optional[Dict[str, Any]] = None
    post_deploy_checks: Optional[Dict[str, Any]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    deployed_by: int
    rollback_of: Optional[int] = None
    rollback_reason: Optional[str] = None
    error_message: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RollbackRequest(BaseModel):
    """Rollback request schema."""
    reason: str


class HealthCheckResult(BaseModel):
    """Health check result."""
    component: str
    status: str  # healthy/degraded/unhealthy
    response_time_ms: Optional[int] = None
    details: Optional[Dict[str, Any]] = None


class EnvironmentHealthResponse(BaseModel):
    """Environment health check response."""
    environment_id: int
    overall_status: str
    timestamp: datetime
    checks: List[HealthCheckResult]


class FeatureFlagCreate(BaseModel):
    """Create feature flag schema."""
    name: str
    description: Optional[str] = None
    rollout_percentage: int = 0
    target_environments: Optional[List[str]] = None
    target_roles: Optional[List[str]] = None
    config: Optional[Dict[str, Any]] = None


class FeatureFlagUpdate(BaseModel):
    """Update feature flag schema."""
    description: Optional[str] = None
    is_enabled: Optional[bool] = None
    rollout_percentage: Optional[int] = None
    target_environments: Optional[List[str]] = None
    target_roles: Optional[List[str]] = None
    config: Optional[Dict[str, Any]] = None


class FeatureFlagResponse(BaseModel):
    """Feature flag response schema."""
    id: int
    name: str
    description: Optional[str] = None
    is_enabled: bool
    rollout_percentage: int
    target_environments: Optional[List[str]] = None
    target_roles: Optional[List[str]] = None
    config: Dict[str, Any]
    created_by: int
    enabled_at: Optional[datetime] = None
    disabled_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PreDeployValidation(BaseModel):
    """Pre-deploy validation schema."""
    pending_migrations: List[str] = []
    config_complete: bool
    dependencies_available: bool
    validations_passed: bool
    warnings: List[str] = []


class DeploymentAnalytics(BaseModel):
    """Deployment analytics."""
    total_deployments: int
    successful_deployments: int
    failed_deployments: int
    rolled_back_deployments: int
    success_rate_percent: float
    average_deployment_time_minutes: float
    average_rollback_time_minutes: float
    mttr_hours: float  # Mean Time to Recovery
    period: str


class ChangelogRequest(BaseModel):
    """Changelog generation request."""
    from_version: str
    to_version: str


class VersionTrackingResponse(BaseModel):
    """Version tracking response."""
    component: str
    current_version: str
    previous_version: Optional[str] = None
    last_updated: datetime
    deployed_at: Optional[datetime] = None
