from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, Float, Date, JSON, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import BaseModel


class Environment(BaseModel):
    """Deployment environments (dev, staging, prod, dr)."""

    __tablename__ = "environments"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    current_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    last_deployed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active")  # active/maintenance/offline
    health_status: Mapped[str] = mapped_column(String(50), default="unknown")  # healthy/degraded/unhealthy/unknown
    last_health_check_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    deployments = relationship("Deployment", back_populates="environment", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Environment(name={self.name}, status={self.status})>"


class Release(BaseModel):
    """Versioned releases with artifacts and changelog."""

    __tablename__ = "releases"

    version: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    changelog: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_changelog: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    release_type: Mapped[str] = mapped_column(String(50), nullable=False)  # major/minor/patch/hotfix
    components: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # [{component, old_version, new_version}]
    artifacts: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # [{name, path, checksum}]
    status: Mapped[str] = mapped_column(String(50), default="draft")  # draft/released/deprecated
    released_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    released_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    git_tag: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    git_commit: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Relationships
    deployments = relationship("Deployment", back_populates="release", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Release(version={self.version}, type={self.release_type})>"


class Deployment(BaseModel):
    """Deployment records with pipeline tracking."""

    __tablename__ = "deployments"

    release_id: Mapped[Optional[int]] = mapped_column(ForeignKey("releases.id"), nullable=True, index=True)
    environment_id: Mapped[int] = mapped_column(ForeignKey("environments.id"), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # pending/building/testing/deploying/deployed/failed/rolled_back
    pipeline_steps: Mapped[list] = mapped_column(JSON, default=list)  # [{step, status, started_at, completed_at, output}]
    pre_deploy_checks: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    post_deploy_checks: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    deployed_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    rollback_of: Mapped[Optional[int]] = mapped_column(ForeignKey("deployments.id"), nullable=True)
    rollback_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    release = relationship("Release", back_populates="deployments")
    environment = relationship("Environment", back_populates="deployments")

    def __repr__(self) -> str:
        return f"<Deployment(version={self.version}, environment_id={self.environment_id}, status={self.status})>"


class FeatureFlag(BaseModel):
    """Feature flags for gradual rollouts."""

    __tablename__ = "feature_flags"

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    rollout_percentage: Mapped[int] = mapped_column(Integer, default=0)  # 0-100
    target_environments: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # ["staging", "prod"]
    target_roles: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # ["admin", "recruiter"]
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    enabled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    disabled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<FeatureFlag(name={self.name}, enabled={self.is_enabled}, rollout={self.rollout_percentage}%)>"
