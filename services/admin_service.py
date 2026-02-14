import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from models.admin import SystemConfig, ReportDefinition, ReportExecution
from agents.admin_agent import AdminAgent

logger = logging.getLogger(__name__)


class AdminService:
    """Service layer for admin operations."""

    def __init__(self):
        """Initialize admin service."""
        self.agent = AdminAgent()

    async def initialize(self) -> None:
        """Initialize the service."""
        await self.agent.initialize()

    async def shutdown(self) -> None:
        """Shutdown the service."""
        await self.agent.shutdown()

    # ── User Management ──

    async def list_users(
        self, db: Session, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """List all users with optional filters."""
        return await self.agent.list_users(db, filters)

    async def create_user(self, db: Session, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user."""
        return await self.agent.create_user(db, user_data)

    async def deactivate_user(self, db: Session, user_id: int) -> Dict[str, Any]:
        """Deactivate a user."""
        return await self.agent.deactivate_user(db, user_id)

    async def bulk_import_users(
        self, db: Session, users_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Bulk import users."""
        return await self.agent.bulk_import_users(db, users_data)

    # ── System Configuration ──

    async def get_system_config(self, db: Session) -> Dict[str, Any]:
        """Get all system configuration."""
        return await self.agent.get_system_config(db)

    async def get_config_value(self, db: Session, config_key: str) -> Optional[Any]:
        """Get a specific config value."""
        try:
            config = db.execute(
                select(SystemConfig).where(SystemConfig.config_key == config_key)
            ).scalar()
            return config.config_value if config else None
        except Exception as e:
            logger.error(f"Error getting config {config_key}: {str(e)}")
            return None

    async def update_system_config(
        self, db: Session, config_key: str, config_value: Any, user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Update system configuration."""
        try:
            config = db.execute(
                select(SystemConfig).where(SystemConfig.config_key == config_key)
            ).scalar()

            if not config:
                # Create new config
                config = SystemConfig(
                    config_key=config_key,
                    config_value=config_value,
                    config_type=self._infer_config_type(config_value),
                    category="general",
                )
                db.add(config)
            else:
                config.config_value = config_value
                config.updated_by = user_id
                config.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(config)

            return {
                "config_key": config.config_key,
                "config_value": config.config_value,
                "updated_at": config.updated_at.isoformat() if config.updated_at else None,
            }
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating config: {str(e)}")
            raise

    async def get_system_health(self, db: Session) -> Dict[str, Any]:
        """Get system health status."""
        return await self.agent.get_system_health(db)

    # ── Report Definitions ──

    async def create_report_definition(
        self, db: Session, report_data: Dict[str, Any], user_id: int
    ) -> Dict[str, Any]:
        """Create a report definition."""
        return await self.agent.create_report_definition(db, report_data, user_id)

    async def get_report_definition(
        self, db: Session, report_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get a report definition."""
        try:
            report = db.execute(
                select(ReportDefinition).where(ReportDefinition.id == report_id)
            ).scalar()

            if not report:
                return None

            return {
                "id": report.id,
                "name": report.name,
                "description": report.description,
                "report_type": report.report_type,
                "data_source": report.data_source,
                "columns": report.columns,
                "filters": report.filters,
                "grouping": report.grouping,
                "sorting": report.sorting,
                "aggregations": report.aggregations,
                "chart_config": report.chart_config,
                "is_public": report.is_public,
                "schedule": report.schedule,
                "created_by": report.created_by,
                "created_at": report.created_at.isoformat(),
                "updated_at": report.updated_at.isoformat(),
            }
        except Exception as e:
            logger.error(f"Error getting report definition: {str(e)}")
            return None

    async def list_report_definitions(self, db: Session) -> List[Dict[str, Any]]:
        """List all report definitions."""
        try:
            reports = db.execute(select(ReportDefinition)).scalars().all()

            return [
                {
                    "id": r.id,
                    "name": r.name,
                    "report_type": r.report_type,
                    "data_source": r.data_source,
                    "is_public": r.is_public,
                    "created_by": r.created_by,
                    "created_at": r.created_at.isoformat(),
                }
                for r in reports
            ]
        except Exception as e:
            logger.error(f"Error listing report definitions: {str(e)}")
            return []

    async def update_report_definition(
        self, db: Session, report_id: int, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a report definition."""
        try:
            report = db.execute(
                select(ReportDefinition).where(ReportDefinition.id == report_id)
            ).scalar()

            if not report:
                raise ValueError(f"Report {report_id} not found")

            for key, value in updates.items():
                if hasattr(report, key):
                    setattr(report, key, value)

            db.commit()
            db.refresh(report)

            logger.info(f"Updated report definition: {report.name}")

            return {
                "id": report.id,
                "name": report.name,
                "updated_at": report.updated_at.isoformat(),
            }
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating report definition: {str(e)}")
            raise

    # ── Report Execution ──

    async def generate_report(
        self,
        db: Session,
        report_id: int,
        params: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Execute a report."""
        return await self.agent.generate_report(db, report_id, params, user_id)

    async def get_report_execution(
        self, db: Session, execution_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get a report execution result."""
        try:
            execution = db.execute(
                select(ReportExecution).where(ReportExecution.id == execution_id)
            ).scalar()

            if not execution:
                return None

            return {
                "id": execution.id,
                "report_id": execution.report_id,
                "parameters": execution.parameters,
                "status": execution.status,
                "result_data": execution.result_data,
                "row_count": execution.row_count,
                "execution_time_ms": execution.execution_time_ms,
                "export_format": execution.export_format,
                "export_path": execution.export_path,
                "executed_by": execution.executed_by,
                "executed_at": execution.executed_at.isoformat(),
                "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
                "error_message": execution.error_message,
            }
        except Exception as e:
            logger.error(f"Error getting report execution: {str(e)}")
            return None

    async def list_report_executions(
        self, db: Session, report_id: int, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """List execution history for a report."""
        try:
            executions = db.execute(
                select(ReportExecution)
                .where(ReportExecution.report_id == report_id)
                .order_by(ReportExecution.executed_at.desc())
                .limit(limit)
            ).scalars().all()

            return [
                {
                    "id": e.id,
                    "status": e.status,
                    "row_count": e.row_count,
                    "execution_time_ms": e.execution_time_ms,
                    "executed_by": e.executed_by,
                    "executed_at": e.executed_at.isoformat(),
                    "completed_at": e.completed_at.isoformat() if e.completed_at else None,
                }
                for e in executions
            ]
        except Exception as e:
            logger.error(f"Error listing executions: {str(e)}")
            return []

    async def schedule_report(
        self, db: Session, report_id: int, schedule: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Schedule a report."""
        return await self.agent.schedule_report(db, report_id, schedule)

    # ── Standard Reports ──

    async def get_standard_reports(self, db: Session) -> List[Dict[str, Any]]:
        """Get list of standard reports."""
        return await self.agent.get_standard_reports(db)

    async def run_standard_report(
        self, db: Session, report_name: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run a standard report."""
        try:
            if report_name == "pipeline_summary":
                return await self.agent.report_pipeline_summary(
                    db, params["start_date"], params["end_date"]
                )
            elif report_name == "recruiter_productivity":
                return await self.agent.report_recruiter_productivity(
                    db, params["start_date"], params["end_date"]
                )
            elif report_name == "client_activity":
                return await self.agent.report_client_activity(
                    db, params["customer_id"], params["start_date"], params["end_date"]
                )
            elif report_name == "supplier_performance":
                return await self.agent.report_supplier_performance(
                    db, params["start_date"], params["end_date"]
                )
            elif report_name == "financial_summary":
                return await self.agent.report_financial_summary(
                    db, params["start_date"], params["end_date"]
                )
            elif report_name == "compliance_audit":
                return await self.agent.report_compliance_audit(
                    db, params["start_date"], params["end_date"]
                )
            elif report_name == "diversity_metrics":
                return await self.agent.report_diversity_metrics(
                    db, params["start_date"], params["end_date"]
                )
            elif report_name == "time_to_fill":
                return await self.agent.report_time_to_fill(
                    db, params["start_date"], params["end_date"]
                )
            else:
                raise ValueError(f"Unknown standard report: {report_name}")
        except Exception as e:
            logger.error(f"Error running standard report: {str(e)}")
            raise

    # ── Private Helpers ──

    def _infer_config_type(self, value: Any) -> str:
        """Infer configuration type from value."""
        if isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "number"
        elif isinstance(value, dict):
            return "json"
        else:
            return "string"
