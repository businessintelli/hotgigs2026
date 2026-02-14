from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, Float, Date, JSON, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import BaseModel


class SystemConfig(BaseModel):
    """System configuration settings."""

    __tablename__ = "system_configs"

    config_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    config_value: Mapped[dict] = mapped_column(JSON, nullable=False)
    config_type: Mapped[str] = mapped_column(String(50), nullable=False)  # string/number/boolean/json
    category: Mapped[str] = mapped_column(String(100), nullable=False)  # general/matching/notifications/security/integrations
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_encrypted: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<SystemConfig(key={self.config_key}, category={self.category})>"


class ReportDefinition(BaseModel):
    """Custom report definitions."""

    __tablename__ = "report_definitions"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    report_type: Mapped[str] = mapped_column(String(50), nullable=False)  # standard/custom
    data_source: Mapped[str] = mapped_column(String(100), nullable=False)  # requirements/candidates/submissions/placements/offers/suppliers/interviews/financial
    columns: Mapped[list] = mapped_column(JSON, nullable=False)  # [{field, label, type, format, sortable}]
    filters: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # [{field, operator, default_value}]
    grouping: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # [field1, field2]
    sorting: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # [{field, direction}]
    aggregations: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # [{field, function}]
    chart_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # {type, x_axis, y_axis}
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    schedule: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # {frequency, recipients, format}
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Relationships
    executions = relationship("ReportExecution", back_populates="report_definition", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<ReportDefinition(id={self.id}, name={self.name}, type={self.report_type})>"


class ReportExecution(BaseModel):
    """Report execution records."""

    __tablename__ = "report_executions"

    report_id: Mapped[int] = mapped_column(ForeignKey("report_definitions.id"), nullable=False, index=True)
    parameters: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Runtime params
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # pending/running/completed/failed
    result_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Report results
    row_count: Mapped[int] = mapped_column(Integer, default=0)
    execution_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    export_format: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # json/csv/xlsx/pdf
    export_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    executed_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    report_definition = relationship("ReportDefinition", back_populates="executions")

    def __repr__(self) -> str:
        return f"<ReportExecution(report_id={self.report_id}, status={self.status})>"
