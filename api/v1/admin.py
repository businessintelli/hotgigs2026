import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from services.admin_service import AdminService
from schemas.admin import (
    SystemConfigCreate, SystemConfigResponse, SystemConfigUpdate,
    ReportDefinitionCreate, ReportDefinitionUpdate, ReportDefinitionResponse,
    ReportExecutionResponse, UserCreate, UserResponse, BulkUserImport,
    BulkUserImportResponse, SystemHealthResponse, StandardReportParams,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])
admin_service = AdminService()


@router.on_event("startup")
async def startup():
    """Initialize admin service on startup."""
    await admin_service.initialize()


@router.on_event("shutdown")
async def shutdown():
    """Shutdown admin service."""
    await admin_service.shutdown()


# ── User Management ──

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    db: Session = Depends(get_db),
    role: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
):
    """List all users with optional filters."""
    try:
        filters = {}
        if role:
            filters["role"] = role
        if search:
            filters["search"] = search

        users = await admin_service.list_users(db, filters)
        return users
    except Exception as e:
        logger.error(f"Error listing users: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    """Create a new user."""
    try:
        result = await admin_service.create_user(db, user_data.model_dump())
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/users/bulk-import", response_model=BulkUserImportResponse)
async def bulk_import_users(
    import_data: BulkUserImport,
    db: Session = Depends(get_db),
):
    """Bulk import users."""
    try:
        users_list = [u.model_dump() for u in import_data.users]
        result = await admin_service.bulk_import_users(db, users_list)
        return result
    except Exception as e:
        logger.error(f"Error bulk importing users: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/users/{user_id}/deactivate", response_model=Dict[str, Any])
async def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    """Deactivate a user."""
    try:
        result = await admin_service.deactivate_user(db, user_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error deactivating user: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ── System Configuration ──

@router.get("/config", response_model=Dict[str, Any])
async def get_system_config(db: Session = Depends(get_db)):
    """Get all system configuration settings."""
    try:
        config = await admin_service.get_system_config(db)
        return config
    except Exception as e:
        logger.error(f"Error getting config: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/config/{config_key}", response_model=Dict[str, Any])
async def update_system_config(
    config_key: str,
    update_data: SystemConfigUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = None,
):
    """Update a system configuration setting."""
    try:
        result = await admin_service.update_system_config(
            db, config_key, update_data.config_value, current_user_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating config: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=SystemHealthResponse)
async def get_system_health(db: Session = Depends(get_db)):
    """Check system health."""
    try:
        health = await admin_service.get_system_health(db)
        return health
    except Exception as e:
        logger.error(f"Error checking health: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Report Definitions ──

@router.post("/reports", response_model=Dict[str, Any])
async def create_report_definition(
    report_data: ReportDefinitionCreate,
    db: Session = Depends(get_db),
    current_user_id: int = 1,
):
    """Create a report definition."""
    try:
        result = await admin_service.create_report_definition(
            db, report_data.model_dump(), current_user_id
        )
        return result
    except Exception as e:
        logger.error(f"Error creating report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports", response_model=List[Dict[str, Any]])
async def list_reports(db: Session = Depends(get_db)):
    """List all report definitions."""
    try:
        reports = await admin_service.list_report_definitions(db)
        return reports
    except Exception as e:
        logger.error(f"Error listing reports: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/{report_id}", response_model=Dict[str, Any])
async def get_report_definition(
    report_id: int,
    db: Session = Depends(get_db),
):
    """Get a report definition."""
    try:
        report = await admin_service.get_report_definition(db, report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        return report
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/reports/{report_id}", response_model=Dict[str, Any])
async def update_report_definition(
    report_id: int,
    update_data: ReportDefinitionUpdate,
    db: Session = Depends(get_db),
):
    """Update a report definition."""
    try:
        result = await admin_service.update_report_definition(
            db, report_id, update_data.model_dump(exclude_unset=True)
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Report Execution ──

@router.post("/reports/{report_id}/execute", response_model=Dict[str, Any])
async def execute_report(
    report_id: int,
    params: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db),
    current_user_id: int = 1,
):
    """Execute a report with optional parameters."""
    try:
        result = await admin_service.generate_report(db, report_id, params, current_user_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error executing report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/{report_id}/executions", response_model=List[Dict[str, Any]])
async def get_report_executions(
    report_id: int,
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get execution history for a report."""
    try:
        executions = await admin_service.list_report_executions(db, report_id, limit)
        return executions
    except Exception as e:
        logger.error(f"Error getting executions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/{report_id}/executions/{exec_id}", response_model=Dict[str, Any])
async def get_report_execution(
    report_id: int,
    exec_id: int,
    db: Session = Depends(get_db),
):
    """Get a specific report execution."""
    try:
        execution = await admin_service.get_report_execution(db, exec_id)
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
        if execution["report_id"] != report_id:
            raise HTTPException(status_code=403, detail="Execution does not belong to report")
        return execution
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting execution: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reports/{report_id}/schedule", response_model=Dict[str, Any])
async def schedule_report(
    report_id: int,
    schedule: Dict[str, Any],
    db: Session = Depends(get_db),
):
    """Schedule a report for recurring execution."""
    try:
        result = await admin_service.schedule_report(db, report_id, schedule)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error scheduling report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reports/{report_id}/export/{format}", response_model=Dict[str, Any])
async def export_report(
    report_id: int,
    format: str,
    db: Session = Depends(get_db),
):
    """Export report in specified format."""
    if format not in ["csv", "xlsx", "pdf", "json"]:
        raise HTTPException(status_code=400, detail="Invalid export format")

    try:
        # This would trigger actual export generation
        return {
            "report_id": report_id,
            "format": format,
            "status": "queued",
            "message": "Export job queued"
        }
    except Exception as e:
        logger.error(f"Error exporting report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Standard Reports ──

@router.get("/reports/standard", response_model=List[Dict[str, Any]])
async def list_standard_reports(db: Session = Depends(get_db)):
    """List all pre-built standard reports."""
    try:
        reports = await admin_service.get_standard_reports(db)
        return reports
    except Exception as e:
        logger.error(f"Error listing standard reports: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reports/standard/{report_name}", response_model=Dict[str, Any])
async def run_standard_report(
    report_name: str,
    params: StandardReportParams,
    db: Session = Depends(get_db),
):
    """Run a standard report with parameters."""
    try:
        result = await admin_service.run_standard_report(
            db, report_name, params.model_dump()
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error running standard report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
