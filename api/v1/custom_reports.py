"""Custom Report Builder and Report Scheduler API endpoints."""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import random
import time

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from models.custom_reports import SavedReport, ReportSchedule
from models.enums import ReportType, DeliveryMethod, ExportFormat
from schemas.custom_reports import (
    SavedReportCreate, SavedReportUpdate, SavedReportResponse, SavedReportListResponse,
    ReportScheduleCreate, ReportScheduleUpdate, ReportScheduleResponse, ReportScheduleListResponse,
    ReportExecutionResult, ReportBuilderConfig, AvailableDimension, AvailableMetric, AvailableFilter,
    ReportTemplate, ReportTemplateListResponse, ScheduleRunHistory, ScheduleRunHistoryList,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/custom-reports", tags=["Custom Reports"])


# ─────────────────────────────────────────────────────────────────────────
# BUILDER CONFIG & TEMPLATES
# ─────────────────────────────────────────────────────────────────────────

@router.get("/builder-config", response_model=ReportBuilderConfig, summary="Get Report Builder Configuration")
async def get_builder_config(role: str = Query("admin")) -> ReportBuilderConfig:
    """
    Returns available dimensions, metrics, filters, and visualizations for the report builder UI.

    Args:
        role: User role (admin, msp_admin) for access control
    """
    # Validate role
    if role not in ["admin", "msp_admin"]:
        raise HTTPException(status_code=400, detail="Invalid role")

    available_dimensions = [
        AvailableDimension(key="client", label="Client", description="Client organization", category="Entity"),
        AvailableDimension(key="job", label="Job/Requirement", description="Job requirement", category="Entity"),
        AvailableDimension(key="supplier", label="Supplier", description="Supplier organization", category="Entity"),
        AvailableDimension(key="recruiter", label="Recruiter", description="Recruiter user", category="Entity"),
        AvailableDimension(key="department", label="Department", description="Client department", category="Entity"),
        AvailableDimension(key="location", label="Location", description="Work location", category="Entity"),
        AvailableDimension(key="skill", label="Skill", description="Required skill", category="Entity"),
        AvailableDimension(key="source", label="Source", description="Candidate source", category="Entity"),
        AvailableDimension(key="priority", label="Priority", description="Requirement priority", category="Status"),
        AvailableDimension(key="phase", label="Pipeline Phase", description="Candidate phase", category="Status"),
        AvailableDimension(key="month", label="Month", description="By calendar month", category="Time"),
        AvailableDimension(key="quarter", label="Quarter", description="By calendar quarter", category="Time"),
    ]

    available_metrics = [
        AvailableMetric(key="placements", label="Placements", description="Total placements completed", format_type="number"),
        AvailableMetric(key="submissions", label="Submissions", description="Total candidate submissions", format_type="number"),
        AvailableMetric(key="interviews", label="Interviews", description="Interviews scheduled/completed", format_type="number"),
        AvailableMetric(key="offers", label="Offers", description="Job offers made", format_type="number"),
        AvailableMetric(key="fill_rate", label="Fill Rate", description="Percentage of positions filled", format_type="percent"),
        AvailableMetric(key="avg_ttf", label="Avg Time to Fill", description="Average days to fill position", format_type="days"),
        AvailableMetric(key="avg_match_score", label="Avg Match Score", description="Average candidate match score", format_type="percent"),
        AvailableMetric(key="conversion_rate", label="Conversion Rate", description="Submission to placement conversion", format_type="percent"),
        AvailableMetric(key="revenue", label="Revenue", description="Total revenue generated", format_type="currency"),
        AvailableMetric(key="cost_per_hire", label="Cost per Hire", description="Average cost per hire", format_type="currency"),
        AvailableMetric(key="rejection_rate", label="Rejection Rate", description="Percentage rejected", format_type="percent"),
        AvailableMetric(key="sla_adherence", label="SLA Adherence", description="SLA compliance percentage", format_type="percent"),
        AvailableMetric(key="quality_score", label="Quality Score", description="Overall quality score", format_type="percent"),
        AvailableMetric(key="compliance_score", label="Compliance Score", description="Compliance score", format_type="percent"),
        AvailableMetric(key="pipeline_count", label="Pipeline Count", description="Active candidates in pipeline", format_type="number"),
        AvailableMetric(key="offer_acceptance_rate", label="Offer Acceptance Rate", description="Percentage of offers accepted", format_type="percent"),
    ]

    available_filters = [
        AvailableFilter(
            key="date_range",
            label="Date Range",
            type="date_range",
            options=[
                {"value": "last_7_days", "label": "Last 7 Days"},
                {"value": "last_30_days", "label": "Last 30 Days"},
                {"value": "last_90_days", "label": "Last 90 Days"},
                {"value": "last_365_days", "label": "Last Year"},
                {"value": "custom", "label": "Custom Range"},
            ]
        ),
        AvailableFilter(key="client_id", label="Client", type="select", options=None),
        AvailableFilter(key="supplier_id", label="Supplier", type="select", options=None),
        AvailableFilter(key="recruiter_id", label="Recruiter", type="select", options=None),
        AvailableFilter(key="priority", label="Priority", type="select", options=[
            {"value": "critical", "label": "Critical"},
            {"value": "high", "label": "High"},
            {"value": "medium", "label": "Medium"},
            {"value": "low", "label": "Low"},
        ]),
        AvailableFilter(key="status", label="Status", type="select", options=[
            {"value": "active", "label": "Active"},
            {"value": "pending", "label": "Pending"},
            {"value": "completed", "label": "Completed"},
            {"value": "on_hold", "label": "On Hold"},
        ]),
        AvailableFilter(key="location", label="Location", type="select", options=None),
        AvailableFilter(key="skill", label="Skill", type="select", options=None),
    ]

    available_visualizations = [
        "table",
        "bar_chart",
        "line_chart",
        "pie_chart",
        "heatmap",
        "stacked_bar",
        "funnel",
    ]

    return ReportBuilderConfig(
        available_dimensions=available_dimensions,
        available_metrics=available_metrics,
        available_filters=available_filters,
        available_visualizations=available_visualizations,
    )


@router.get("/templates", response_model=ReportTemplateListResponse, summary="Get Report Templates")
async def get_report_templates() -> ReportTemplateListResponse:
    """
    Returns predefined report templates that admins can use as starting points.
    """
    templates = [
        ReportTemplate(
            key="by-client",
            name="Placements by Client",
            description="Placements and fill rates grouped by client",
            category="Performance",
            dimensions=["client", "month"],
            metrics=["placements", "fill_rate", "avg_ttf"],
            visualization_type="bar_chart",
        ),
        ReportTemplate(
            key="conversion-funnel",
            name="Conversion Funnel",
            description="Candidate flow through pipeline phases",
            category="Pipeline",
            dimensions=["phase"],
            metrics=["submissions", "interviews", "offers", "placements"],
            visualization_type="funnel",
        ),
        ReportTemplate(
            key="recruiter-performance",
            name="Recruiter Performance",
            description="Performance metrics by recruiter",
            category="Team",
            dimensions=["recruiter"],
            metrics=["placements", "submission_count", "conversion_rate"],
            visualization_type="table",
        ),
        ReportTemplate(
            key="revenue-analysis",
            name="Revenue Analysis",
            description="Revenue by client and time period",
            category="Financial",
            dimensions=["client", "quarter"],
            metrics=["revenue", "cost_per_hire"],
            visualization_type="line_chart",
        ),
        ReportTemplate(
            key="quality-metrics",
            name="Quality Metrics",
            description="Quality and compliance scores",
            category="Quality",
            dimensions=["supplier", "month"],
            metrics=["quality_score", "compliance_score", "sla_adherence"],
            visualization_type="heatmap",
        ),
        ReportTemplate(
            key="skill-demand",
            name="Skill Demand",
            description="Job openings and placements by skill",
            category="Skills",
            dimensions=["skill", "location"],
            metrics=["pipeline_count", "placements"],
            visualization_type="bar_chart",
        ),
    ]

    return ReportTemplateListResponse(total=len(templates), items=templates)


# ─────────────────────────────────────────────────────────────────────────
# SAVED REPORTS - CRUD
# ─────────────────────────────────────────────────────────────────────────

@router.post("/saved", response_model=SavedReportResponse, status_code=status.HTTP_201_CREATED, summary="Create Saved Report")
async def create_saved_report(
    report: SavedReportCreate,
    role: str = Query("admin"),
    user_id: int = Query(1),
    org_id: int = Query(1),
    db: AsyncSession = Depends(get_db),
) -> SavedReportResponse:
    """
    Create a new saved report by selecting dimensions, metrics, filters, and visualizations.

    Args:
        report: Report configuration
        role: User role (admin, msp_admin)
        user_id: Current user ID
        org_id: Current organization ID
    """
    if role not in ["admin", "msp_admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    # Create report
    db_report = SavedReport(
        user_id=user_id,
        organization_id=org_id,
        report_name=report.report_name,
        description=report.description,
        report_type=report.report_type,
        dimensions=report.dimensions,
        metrics=report.metrics,
        filters=report.filters,
        group_by=report.group_by,
        sort_by=report.sort_by,
        sort_order=report.sort_order,
        visualization_type=report.visualization_type,
        role_access=report.role_access,
    )

    db.add(db_report)
    await db.commit()
    await db.refresh(db_report)

    logger.info(f"Created report {db_report.id} by user {user_id}")
    return SavedReportResponse.model_validate(db_report)


@router.get("/saved", response_model=SavedReportListResponse, summary="List Saved Reports")
async def list_saved_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_favorite: Optional[bool] = None,
    is_shared: Optional[bool] = None,
    role: str = Query("admin"),
    user_id: int = Query(1),
    org_id: int = Query(1),
    db: AsyncSession = Depends(get_db),
) -> SavedReportListResponse:
    """
    List saved reports with optional filtering by favorite/shared status.
    """
    filters = [
        SavedReport.organization_id == org_id,
        SavedReport.is_active == True,
    ]

    if is_favorite is not None:
        filters.append(SavedReport.is_favorite == is_favorite)

    if is_shared is not None:
        filters.append(SavedReport.is_shared == is_shared)

    # Get total count
    count_stmt = select(SavedReport).where(and_(*filters))
    count_result = await db.execute(count_stmt)
    total = len(count_result.fetchall())

    # Get paginated results
    offset = (page - 1) * page_size
    stmt = (
        select(SavedReport)
        .where(and_(*filters))
        .order_by(desc(SavedReport.created_at))
        .limit(page_size)
        .offset(offset)
    )
    result = await db.execute(stmt)
    reports = result.scalars().all()

    items = [SavedReportResponse.model_validate(r) for r in reports]
    return SavedReportListResponse(total=total, page=page, page_size=page_size, items=items)


@router.get("/saved/{report_id}", response_model=SavedReportResponse, summary="Get Saved Report")
async def get_saved_report(
    report_id: int,
    role: str = Query("admin"),
    user_id: int = Query(1),
    org_id: int = Query(1),
    db: AsyncSession = Depends(get_db),
) -> SavedReportResponse:
    """
    Get a single saved report by ID.
    """
    stmt = select(SavedReport).where(
        and_(
            SavedReport.id == report_id,
            SavedReport.organization_id == org_id,
            SavedReport.is_active == True,
        )
    )
    result = await db.execute(stmt)
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return SavedReportResponse.model_validate(report)


@router.put("/saved/{report_id}", response_model=SavedReportResponse, summary="Update Saved Report")
async def update_saved_report(
    report_id: int,
    report_update: SavedReportUpdate,
    role: str = Query("admin"),
    user_id: int = Query(1),
    org_id: int = Query(1),
    db: AsyncSession = Depends(get_db),
) -> SavedReportResponse:
    """
    Update a saved report configuration.
    """
    if role not in ["admin", "msp_admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    stmt = select(SavedReport).where(
        and_(
            SavedReport.id == report_id,
            SavedReport.organization_id == org_id,
            SavedReport.is_active == True,
        )
    )
    result = await db.execute(stmt)
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # Update only provided fields
    update_data = report_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(report, key, value)

    await db.commit()
    await db.refresh(report)

    logger.info(f"Updated report {report_id}")
    return SavedReportResponse.model_validate(report)


@router.delete("/saved/{report_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Saved Report")
async def delete_saved_report(
    report_id: int,
    role: str = Query("admin"),
    user_id: int = Query(1),
    org_id: int = Query(1),
    db: AsyncSession = Depends(get_db),
):
    """
    Soft delete a saved report.
    """
    if role not in ["admin", "msp_admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    stmt = select(SavedReport).where(
        and_(
            SavedReport.id == report_id,
            SavedReport.organization_id == org_id,
            SavedReport.is_active == True,
        )
    )
    result = await db.execute(stmt)
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    report.is_active = False
    await db.commit()

    logger.info(f"Deleted report {report_id}")


@router.post("/saved/{report_id}/favorite", response_model=SavedReportResponse, summary="Toggle Favorite")
async def toggle_favorite(
    report_id: int,
    role: str = Query("admin"),
    user_id: int = Query(1),
    org_id: int = Query(1),
    db: AsyncSession = Depends(get_db),
) -> SavedReportResponse:
    """
    Toggle report as favorite.
    """
    stmt = select(SavedReport).where(
        and_(
            SavedReport.id == report_id,
            SavedReport.organization_id == org_id,
            SavedReport.is_active == True,
        )
    )
    result = await db.execute(stmt)
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    report.is_favorite = not report.is_favorite
    await db.commit()
    await db.refresh(report)

    logger.info(f"Toggled favorite for report {report_id}")
    return SavedReportResponse.model_validate(report)


@router.post("/saved/{report_id}/share", response_model=SavedReportResponse, summary="Toggle Share")
async def toggle_share(
    report_id: int,
    role: str = Query("admin"),
    user_id: int = Query(1),
    org_id: int = Query(1),
    db: AsyncSession = Depends(get_db),
) -> SavedReportResponse:
    """
    Toggle report as shared with organization.
    """
    if role not in ["admin", "msp_admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    stmt = select(SavedReport).where(
        and_(
            SavedReport.id == report_id,
            SavedReport.organization_id == org_id,
            SavedReport.is_active == True,
        )
    )
    result = await db.execute(stmt)
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    report.is_shared = not report.is_shared
    await db.commit()
    await db.refresh(report)

    logger.info(f"Toggled share for report {report_id}")
    return SavedReportResponse.model_validate(report)


@router.post("/saved/{report_id}/duplicate", response_model=SavedReportResponse, status_code=status.HTTP_201_CREATED, summary="Duplicate Report")
async def duplicate_report(
    report_id: int,
    new_name: str = Query(..., min_length=1),
    role: str = Query("admin"),
    user_id: int = Query(1),
    org_id: int = Query(1),
    db: AsyncSession = Depends(get_db),
) -> SavedReportResponse:
    """
    Duplicate a report with a new name.
    """
    stmt = select(SavedReport).where(
        and_(
            SavedReport.id == report_id,
            SavedReport.organization_id == org_id,
            SavedReport.is_active == True,
        )
    )
    result = await db.execute(stmt)
    original = result.scalar_one_or_none()

    if not original:
        raise HTTPException(status_code=404, detail="Report not found")

    # Create duplicate
    duplicate = SavedReport(
        user_id=user_id,
        organization_id=org_id,
        report_name=new_name,
        description=original.description,
        report_type=original.report_type,
        dimensions=original.dimensions,
        metrics=original.metrics,
        filters=original.filters,
        group_by=original.group_by,
        sort_by=original.sort_by,
        sort_order=original.sort_order,
        visualization_type=original.visualization_type,
        role_access=original.role_access,
    )

    db.add(duplicate)
    await db.commit()
    await db.refresh(duplicate)

    logger.info(f"Duplicated report {report_id} as {duplicate.id}")
    return SavedReportResponse.model_validate(duplicate)


# ─────────────────────────────────────────────────────────────────────────
# REPORT EXECUTION
# ─────────────────────────────────────────────────────────────────────────

def _generate_mock_report_data(
    dimensions: List[str],
    metrics: List[str],
) -> tuple[List[Dict[str, Any]], int]:
    """Generate realistic mock report data based on selected dimensions and metrics."""

    # Sample data for mock generation
    clients = ["TechCorp Inc", "Finance Solutions LLC", "Healthcare Systems", "RetailMax", "ManufactureCo"]
    recruiters = ["Alice Johnson", "Bob Smith", "Carol White", "David Chen", "Emma Wilson"]
    suppliers = ["StaffPro Solutions", "TalentMatch Inc", "RecruitmentHub", "VentureTalent"]
    departments = ["Engineering", "Finance", "Operations", "Sales", "HR"]
    locations = ["New York", "San Francisco", "Chicago", "Austin", "Remote"]
    skills = ["Python", "Java", "SQL", "React", "AWS", "Leadership", "Data Analysis"]
    sources = ["LinkedIn", "Indeed", "Referral", "Job Board", "Direct Apply"]
    phases = ["Sourced", "Screening", "Interview", "Offer", "Placed", "Rejected"]
    priorities = ["Critical", "High", "Medium", "Low"]

    rows = []

    # Generate combinations based on dimensions
    if "client" in dimensions:
        client_list = clients[:3]
    else:
        client_list = [None]

    if "recruiter" in dimensions:
        recruiter_list = recruiters[:3]
    else:
        recruiter_list = [None]

    if "supplier" in dimensions:
        supplier_list = suppliers[:2]
    else:
        supplier_list = [None]

    if "department" in dimensions:
        dept_list = departments[:3]
    else:
        dept_list = [None]

    if "location" in dimensions:
        location_list = locations[:3]
    else:
        location_list = [None]

    if "skill" in dimensions:
        skill_list = skills[:3]
    else:
        skill_list = [None]

    if "source" in dimensions:
        source_list = sources[:3]
    else:
        source_list = [None]

    if "phase" in dimensions:
        phase_list = phases[:4]
    else:
        phase_list = [None]

    if "priority" in dimensions:
        priority_list = priorities
    else:
        priority_list = [None]

    # Generate rows for each combination
    months = ["January", "February", "March"] if "month" in dimensions else [None]
    quarters = ["Q1", "Q2", "Q3"] if "quarter" in dimensions else [None]

    for client in client_list:
        for recruiter in recruiter_list:
            for supplier in supplier_list:
                for dept in dept_list:
                    for location in location_list:
                        for skill in skill_list:
                            for source in source_list:
                                for phase in phase_list:
                                    for priority in priority_list:
                                        for month in months:
                                            for quarter in quarters:
                                                row = {}

                                                # Add dimensions to row
                                                if "client" in dimensions:
                                                    row["client"] = client
                                                if "recruiter" in dimensions:
                                                    row["recruiter"] = recruiter
                                                if "supplier" in dimensions:
                                                    row["supplier"] = supplier
                                                if "department" in dimensions:
                                                    row["department"] = dept
                                                if "location" in dimensions:
                                                    row["location"] = location
                                                if "skill" in dimensions:
                                                    row["skill"] = skill
                                                if "source" in dimensions:
                                                    row["source"] = source
                                                if "phase" in dimensions:
                                                    row["phase"] = phase
                                                if "priority" in dimensions:
                                                    row["priority"] = priority
                                                if "month" in dimensions:
                                                    row["month"] = month
                                                if "quarter" in dimensions:
                                                    row["quarter"] = quarter

                                                # Add metrics to row
                                                for metric in metrics:
                                                    if metric == "placements":
                                                        row["placements"] = random.randint(5, 50)
                                                    elif metric == "submissions":
                                                        row["submissions"] = random.randint(10, 100)
                                                    elif metric == "interviews":
                                                        row["interviews"] = random.randint(5, 40)
                                                    elif metric == "offers":
                                                        row["offers"] = random.randint(2, 20)
                                                    elif metric == "fill_rate":
                                                        row["fill_rate"] = round(random.uniform(0.3, 0.95), 2)
                                                    elif metric == "avg_ttf":
                                                        row["avg_ttf"] = random.randint(5, 60)
                                                    elif metric == "avg_match_score":
                                                        row["avg_match_score"] = round(random.uniform(0.55, 0.98), 2)
                                                    elif metric == "conversion_rate":
                                                        row["conversion_rate"] = round(random.uniform(0.1, 0.5), 2)
                                                    elif metric == "revenue":
                                                        row["revenue"] = round(random.uniform(5000, 150000), 2)
                                                    elif metric == "cost_per_hire":
                                                        row["cost_per_hire"] = round(random.uniform(1000, 8000), 2)
                                                    elif metric == "rejection_rate":
                                                        row["rejection_rate"] = round(random.uniform(0.1, 0.6), 2)
                                                    elif metric == "sla_adherence":
                                                        row["sla_adherence"] = round(random.uniform(0.7, 1.0), 2)
                                                    elif metric == "quality_score":
                                                        row["quality_score"] = round(random.uniform(0.65, 0.99), 2)
                                                    elif metric == "compliance_score":
                                                        row["compliance_score"] = round(random.uniform(0.75, 0.99), 2)
                                                    elif metric == "pipeline_count":
                                                        row["pipeline_count"] = random.randint(10, 150)
                                                    elif metric == "offer_acceptance_rate":
                                                        row["offer_acceptance_rate"] = round(random.uniform(0.6, 0.95), 2)

                                                rows.append(row)

    # Limit to 100 rows for reasonable response size
    if len(rows) > 100:
        rows = rows[:100]

    return rows, len(rows)


@router.post("/execute", response_model=ReportExecutionResult, summary="Execute Report")
async def execute_report(
    dimensions: List[str] = Query(...),
    metrics: List[str] = Query(...),
    filters: Optional[Dict[str, Any]] = None,
    role: str = Query("admin"),
) -> ReportExecutionResult:
    """
    Execute a report definition (does not need to be saved).
    Generates realistic mock data based on selected dimensions and metrics.

    Args:
        dimensions: Selected dimensions
        metrics: Selected metrics
        filters: Optional filter criteria
        role: User role
    """
    if not dimensions or not metrics:
        raise HTTPException(status_code=400, detail="Must specify at least one dimension and one metric")

    start_time = time.time()

    # Generate mock data
    data_rows, row_count = _generate_mock_report_data(dimensions, metrics)

    execution_time_ms = int((time.time() - start_time) * 1000)

    return ReportExecutionResult(
        report_id=None,
        report_name="Ad-Hoc Report",
        data={"rows": data_rows},
        row_count=row_count,
        execution_time_ms=execution_time_ms,
        generated_at=datetime.utcnow(),
    )


@router.post("/saved/{report_id}/execute", response_model=ReportExecutionResult, summary="Execute Saved Report")
async def execute_saved_report(
    report_id: int,
    role: str = Query("admin"),
    user_id: int = Query(1),
    org_id: int = Query(1),
    db: AsyncSession = Depends(get_db),
) -> ReportExecutionResult:
    """
    Execute a saved report and update its execution metadata.
    """
    stmt = select(SavedReport).where(
        and_(
            SavedReport.id == report_id,
            SavedReport.organization_id == org_id,
            SavedReport.is_active == True,
        )
    )
    result = await db.execute(stmt)
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    start_time = time.time()

    # Generate mock data
    dimensions = report.dimensions if isinstance(report.dimensions, list) else []
    metrics = report.metrics if isinstance(report.metrics, list) else []
    data_rows, row_count = _generate_mock_report_data(dimensions, metrics)

    execution_time_ms = int((time.time() - start_time) * 1000)

    # Update execution metadata
    report.last_run_at = datetime.utcnow()
    report.run_count += 1
    await db.commit()

    logger.info(f"Executed report {report_id}")

    return ReportExecutionResult(
        report_id=report_id,
        report_name=report.report_name,
        data={"rows": data_rows},
        row_count=row_count,
        execution_time_ms=execution_time_ms,
        generated_at=datetime.utcnow(),
    )


@router.post("/saved/{report_id}/export/{format}", summary="Export Report")
async def export_report(
    report_id: int,
    format: str,
    role: str = Query("admin"),
    user_id: int = Query(1),
    org_id: int = Query(1),
    db: AsyncSession = Depends(get_db),
):
    """
    Export a report in the specified format (PDF, XLSX, CSV).
    Returns a job ID for the export task (mock implementation).

    Args:
        report_id: ID of report to export
        format: Export format (pdf, xlsx, csv)
    """
    if format not in ["pdf", "xlsx", "csv"]:
        raise HTTPException(status_code=400, detail="Invalid format. Must be pdf, xlsx, or csv")

    stmt = select(SavedReport).where(
        and_(
            SavedReport.id == report_id,
            SavedReport.organization_id == org_id,
            SavedReport.is_active == True,
        )
    )
    result = await db.execute(stmt)
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # Mock: Return job ID for export task
    job_id = f"export_{report_id}_{int(time.time())}"

    logger.info(f"Initiated export of report {report_id} as {format}")

    return {
        "job_id": job_id,
        "report_id": report_id,
        "report_name": report.report_name,
        "format": format,
        "status": "queued",
        "message": f"Export queued. Check status with /jobs/{job_id}",
    }


# ─────────────────────────────────────────────────────────────────────────
# REPORT SCHEDULES - CRUD
# ─────────────────────────────────────────────────────────────────────────

@router.post("/schedules", response_model=ReportScheduleResponse, status_code=status.HTTP_201_CREATED, summary="Create Schedule")
async def create_schedule(
    schedule: ReportScheduleCreate,
    role: str = Query("admin"),
    user_id: int = Query(1),
    org_id: int = Query(1),
    db: AsyncSession = Depends(get_db),
) -> ReportScheduleResponse:
    """
    Create a scheduled report job for automated delivery.
    """
    if role not in ["admin", "msp_admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    if schedule.saved_report_id:
        # Verify report exists
        stmt = select(SavedReport).where(SavedReport.id == schedule.saved_report_id)
        result = await db.execute(stmt)
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Saved report not found")

    # Calculate next run time based on cron (mock: next day)
    next_run_at = datetime.utcnow() + timedelta(days=1)

    db_schedule = ReportSchedule(
        user_id=user_id,
        organization_id=org_id,
        saved_report_id=schedule.saved_report_id,
        predefined_report_key=schedule.predefined_report_key,
        schedule_name=schedule.schedule_name,
        cron_expression=schedule.cron_expression,
        frequency_label=schedule.frequency_label,
        delivery_method=schedule.delivery_method,
        delivery_recipients=schedule.delivery_recipients,
        export_format=schedule.export_format,
        is_enabled=schedule.is_enabled,
        next_run_at=next_run_at,
    )

    db.add(db_schedule)
    await db.commit()
    await db.refresh(db_schedule)

    logger.info(f"Created schedule {db_schedule.id} by user {user_id}")
    return ReportScheduleResponse.model_validate(db_schedule)


@router.get("/schedules", response_model=ReportScheduleListResponse, summary="List Schedules")
async def list_schedules(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_enabled: Optional[bool] = None,
    role: str = Query("admin"),
    user_id: int = Query(1),
    org_id: int = Query(1),
    db: AsyncSession = Depends(get_db),
) -> ReportScheduleListResponse:
    """
    List all report schedules for the organization.
    """
    filters = [
        ReportSchedule.organization_id == org_id,
        ReportSchedule.is_active == True,
    ]

    if is_enabled is not None:
        filters.append(ReportSchedule.is_enabled == is_enabled)

    # Get total count
    count_stmt = select(ReportSchedule).where(and_(*filters))
    count_result = await db.execute(count_stmt)
    total = len(count_result.fetchall())

    # Get paginated results
    offset = (page - 1) * page_size
    stmt = (
        select(ReportSchedule)
        .where(and_(*filters))
        .order_by(desc(ReportSchedule.created_at))
        .limit(page_size)
        .offset(offset)
    )
    result = await db.execute(stmt)
    schedules = result.scalars().all()

    items = [ReportScheduleResponse.model_validate(s) for s in schedules]
    return ReportScheduleListResponse(total=total, page=page, page_size=page_size, items=items)


@router.get("/schedules/{schedule_id}", response_model=ReportScheduleResponse, summary="Get Schedule")
async def get_schedule(
    schedule_id: int,
    role: str = Query("admin"),
    user_id: int = Query(1),
    org_id: int = Query(1),
    db: AsyncSession = Depends(get_db),
) -> ReportScheduleResponse:
    """
    Get a single schedule by ID.
    """
    stmt = select(ReportSchedule).where(
        and_(
            ReportSchedule.id == schedule_id,
            ReportSchedule.organization_id == org_id,
            ReportSchedule.is_active == True,
        )
    )
    result = await db.execute(stmt)
    schedule = result.scalar_one_or_none()

    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    return ReportScheduleResponse.model_validate(schedule)


@router.put("/schedules/{schedule_id}", response_model=ReportScheduleResponse, summary="Update Schedule")
async def update_schedule(
    schedule_id: int,
    schedule_update: ReportScheduleUpdate,
    role: str = Query("admin"),
    user_id: int = Query(1),
    org_id: int = Query(1),
    db: AsyncSession = Depends(get_db),
) -> ReportScheduleResponse:
    """
    Update a schedule configuration.
    """
    if role not in ["admin", "msp_admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    stmt = select(ReportSchedule).where(
        and_(
            ReportSchedule.id == schedule_id,
            ReportSchedule.organization_id == org_id,
            ReportSchedule.is_active == True,
        )
    )
    result = await db.execute(stmt)
    schedule = result.scalar_one_or_none()

    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    update_data = schedule_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(schedule, key, value)

    await db.commit()
    await db.refresh(schedule)

    logger.info(f"Updated schedule {schedule_id}")
    return ReportScheduleResponse.model_validate(schedule)


@router.delete("/schedules/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Schedule")
async def delete_schedule(
    schedule_id: int,
    role: str = Query("admin"),
    user_id: int = Query(1),
    org_id: int = Query(1),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a schedule.
    """
    if role not in ["admin", "msp_admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    stmt = select(ReportSchedule).where(
        and_(
            ReportSchedule.id == schedule_id,
            ReportSchedule.organization_id == org_id,
            ReportSchedule.is_active == True,
        )
    )
    result = await db.execute(stmt)
    schedule = result.scalar_one_or_none()

    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    schedule.is_active = False
    await db.commit()

    logger.info(f"Deleted schedule {schedule_id}")


@router.post("/schedules/{schedule_id}/toggle", response_model=ReportScheduleResponse, summary="Toggle Schedule")
async def toggle_schedule(
    schedule_id: int,
    role: str = Query("admin"),
    user_id: int = Query(1),
    org_id: int = Query(1),
    db: AsyncSession = Depends(get_db),
) -> ReportScheduleResponse:
    """
    Enable or disable a schedule.
    """
    if role not in ["admin", "msp_admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    stmt = select(ReportSchedule).where(
        and_(
            ReportSchedule.id == schedule_id,
            ReportSchedule.organization_id == org_id,
            ReportSchedule.is_active == True,
        )
    )
    result = await db.execute(stmt)
    schedule = result.scalar_one_or_none()

    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    schedule.is_enabled = not schedule.is_enabled
    await db.commit()
    await db.refresh(schedule)

    logger.info(f"Toggled schedule {schedule_id}")
    return ReportScheduleResponse.model_validate(schedule)


@router.get("/schedules/{schedule_id}/history", response_model=ScheduleRunHistoryList, summary="Get Schedule History")
async def get_schedule_history(
    schedule_id: int,
    limit: int = Query(10, ge=1, le=50),
    role: str = Query("admin"),
    user_id: int = Query(1),
    org_id: int = Query(1),
    db: AsyncSession = Depends(get_db),
) -> ScheduleRunHistoryList:
    """
    Get run history for a schedule (mock: last N runs).
    """
    stmt = select(ReportSchedule).where(
        and_(
            ReportSchedule.id == schedule_id,
            ReportSchedule.organization_id == org_id,
            ReportSchedule.is_active == True,
        )
    )
    result = await db.execute(stmt)
    schedule = result.scalar_one_or_none()

    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    # Mock: Generate fake run history
    runs = []
    now = datetime.utcnow()
    for i in range(limit):
        run_time = now - timedelta(days=i)
        runs.append(
            ScheduleRunHistory(
                run_id=schedule.run_count - i,
                scheduled_time=run_time,
                actual_time=run_time + timedelta(seconds=random.randint(5, 60)),
                status=random.choice(["success", "success", "success", "failed"]),
                row_count=random.randint(50, 200) if random.random() > 0.1 else None,
                execution_time_ms=random.randint(500, 5000) if random.random() > 0.1 else None,
                error_message=None if random.random() > 0.1 else "Connection timeout",
            )
        )

    return ScheduleRunHistoryList(schedule_id=schedule_id, total_runs=schedule.run_count, runs=runs)


@router.post("/schedules/{schedule_id}/run-now", status_code=status.HTTP_202_ACCEPTED, summary="Run Schedule Now")
async def run_schedule_now(
    schedule_id: int,
    role: str = Query("admin"),
    user_id: int = Query(1),
    org_id: int = Query(1),
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger an immediate run of a schedule.
    Returns 202 Accepted and a job ID.
    """
    if role not in ["admin", "msp_admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    stmt = select(ReportSchedule).where(
        and_(
            ReportSchedule.id == schedule_id,
            ReportSchedule.organization_id == org_id,
            ReportSchedule.is_active == True,
        )
    )
    result = await db.execute(stmt)
    schedule = result.scalar_one_or_none()

    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    job_id = f"run_{schedule_id}_{int(time.time())}"

    logger.info(f"Triggered immediate run of schedule {schedule_id}")

    return {
        "job_id": job_id,
        "schedule_id": schedule_id,
        "schedule_name": schedule.schedule_name,
        "status": "queued",
        "message": f"Report execution queued. Check status with /jobs/{job_id}",
    }


logger.info("Custom Reports router initialized")
