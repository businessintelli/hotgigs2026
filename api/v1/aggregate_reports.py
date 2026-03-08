"""Aggregate reports API endpoints for comprehensive HR analytics.

This module provides 12 sophisticated aggregate report endpoints with realistic
mock data for demonstrating enterprise-grade HR analytics and performance tracking.

Role-Based Access:
  - MSP_ADMIN: Full access to all reports across all clients, suppliers, and recruiters.
  - COMPANY_ADMIN: Access to own company's data only (own jobs, own recruiters, suppliers serving them).
  - COMPANY_RECRUITER: Access to own performance, own assigned jobs/candidates. Limited aggregate views.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from enum import Enum

from schemas.aggregate_reports import (
    ClientPerformanceReport,
    ClientJobBreakdown,
    JobPerformanceReport,
    JobApplicantBreakdown,
    SupplierPerformanceReport,
    SupplierJobBreakdown,
    RecruiterPerformanceReport,
    RecruiterActivity,
    CompanyExecutiveReport,
    CrossDimensionalMatrix,
    PipelineVelocityReport,
    ConversionFunnelReport,
    ClientMetricItem,
    JobForClient,
    CandidateSummary,
    JobMetricItem,
    PhaseBreakdown,
    ApplicantDetail,
    MatchDimension,
    PhaseHistory,
    SupplierMetricItem,
    SupplierJobSubmission,
    RecruiterMetricItem,
    MonthlyTrend,
    DailyActivityData,
    SourceingChannelBreakdown,
    TopPerformer,
    DepartmentBreakdown,
    FunnelStage,
    ClientFunnelBreakdown,
    SupplierFunnelBreakdown,
    MonthFunnelTrend,
    PhaseVelocity,
    VelocityBreakdown,
    WeeklyVelocityTrend,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/aggregate-reports", tags=["Aggregate Reports"])


# ═══════════════════════════════════════════════════════════════════════════
# Role-Based Access Control
# ═══════════════════════════════════════════════════════════════════════════

class ReportRole(str, Enum):
    MSP_ADMIN = "msp_admin"
    COMPANY_ADMIN = "company_admin"
    COMPANY_RECRUITER = "company_recruiter"


# Report visibility matrix: which reports each role can access
ROLE_REPORT_ACCESS = {
    ReportRole.MSP_ADMIN: {
        "by_client": {"access": "full", "description": "All clients across the program"},
        "by_client_jobs": {"access": "full", "description": "Any client's job breakdown"},
        "by_job": {"access": "full", "description": "All jobs across all clients"},
        "by_job_applicants": {"access": "full", "description": "Any job's applicant details"},
        "by_supplier": {"access": "full", "description": "All suppliers across the program"},
        "by_supplier_jobs": {"access": "full", "description": "Any supplier's job submissions"},
        "by_recruiter": {"access": "full", "description": "All recruiters across all companies"},
        "by_recruiter_activity": {"access": "full", "description": "Any recruiter's detailed activity"},
        "by_company": {"access": "full", "description": "Full executive summary across all orgs"},
        "cross_dimensional": {"access": "full", "description": "All cross-dimensional matrices"},
        "pipeline_velocity": {"access": "full", "description": "Pipeline velocity across all jobs"},
        "conversion_funnel": {"access": "full", "description": "Full conversion funnel across all data"},
    },
    ReportRole.COMPANY_ADMIN: {
        "by_client": {"access": "none", "description": "Not applicable (you are a single company)"},
        "by_client_jobs": {"access": "own_company", "description": "Your company's jobs only"},
        "by_job": {"access": "own_company", "description": "Your company's jobs only"},
        "by_job_applicants": {"access": "own_company", "description": "Applicants to your company's jobs"},
        "by_supplier": {"access": "own_company", "description": "Suppliers serving your company"},
        "by_supplier_jobs": {"access": "own_company", "description": "Supplier performance on your jobs"},
        "by_recruiter": {"access": "own_company", "description": "Your company's recruiters only"},
        "by_recruiter_activity": {"access": "own_company", "description": "Your company's recruiter activity"},
        "by_company": {"access": "own_company", "description": "Your company's executive summary"},
        "cross_dimensional": {"access": "own_company", "description": "Cross-dimensional for your company only"},
        "pipeline_velocity": {"access": "own_company", "description": "Pipeline velocity for your jobs"},
        "conversion_funnel": {"access": "own_company", "description": "Conversion funnel for your jobs"},
    },
    ReportRole.COMPANY_RECRUITER: {
        "by_client": {"access": "none", "description": "Not available for recruiters"},
        "by_client_jobs": {"access": "none", "description": "Not available for recruiters"},
        "by_job": {"access": "assigned_only", "description": "Only your assigned jobs"},
        "by_job_applicants": {"access": "assigned_only", "description": "Applicants to your assigned jobs"},
        "by_supplier": {"access": "none", "description": "Not available for recruiters"},
        "by_supplier_jobs": {"access": "none", "description": "Not available for recruiters"},
        "by_recruiter": {"access": "self_only", "description": "Your own performance only"},
        "by_recruiter_activity": {"access": "self_only", "description": "Your own activity only"},
        "by_company": {"access": "none", "description": "Not available for recruiters"},
        "cross_dimensional": {"access": "none", "description": "Not available for recruiters"},
        "pipeline_velocity": {"access": "assigned_only", "description": "Velocity for your assigned jobs"},
        "conversion_funnel": {"access": "assigned_only", "description": "Funnel for your assigned jobs"},
    },
}


@router.get("/role-access-matrix", status_code=status.HTTP_200_OK)
async def get_role_access_matrix(
    role: Optional[str] = Query(None, description="Filter by role: msp_admin, company_admin, company_recruiter"),
):
    """Returns the report access matrix showing which reports each role can access.

    Used by the frontend to show/hide report tabs and display appropriate messaging.
    """
    if role:
        try:
            r = ReportRole(role)
            return {
                "role": r.value,
                "reports": ROLE_REPORT_ACCESS[r],
                "total_accessible": sum(1 for v in ROLE_REPORT_ACCESS[r].values() if v["access"] != "none"),
                "total_reports": len(ROLE_REPORT_ACCESS[r]),
            }
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid role: {role}. Valid: msp_admin, company_admin, company_recruiter")

    return {
        "roles": {
            r.value: {
                "reports": ROLE_REPORT_ACCESS[r],
                "total_accessible": sum(1 for v in ROLE_REPORT_ACCESS[r].values() if v["access"] != "none"),
                "total_reports": len(ROLE_REPORT_ACCESS[r]),
            }
            for r in ReportRole
        }
    }


# ═══════════════════════════════════════════════════════════════════════════
# Helper functions for mock data generation
# ═══════════════════════════════════════════════════════════════════════════

def _get_date_range(start_date: Optional[str], end_date: Optional[str]) -> tuple:
    """Parse date range query parameters."""
    if start_date:
        try:
            start = datetime.fromisoformat(start_date)
        except (ValueError, TypeError):
            start = datetime.now() - timedelta(days=90)
    else:
        start = datetime.now() - timedelta(days=90)

    if end_date:
        try:
            end = datetime.fromisoformat(end_date)
        except (ValueError, TypeError):
            end = datetime.now()
    else:
        end = datetime.now()

    return start, end


def _generate_monthly_trends(num_months: int = 6) -> List[MonthlyTrend]:
    """Generate realistic monthly trend data."""
    trends = []
    base_submissions = 45
    base_placements = 12

    for i in range(num_months - 1, -1, -1):
        month_date = datetime.now() - timedelta(days=30 * i)
        submissions = int(base_submissions * (0.85 + (i % 3) * 0.15))
        placements = int(base_placements * (0.90 + (i % 2) * 0.10))

        trends.append(
            MonthlyTrend(
                month=month_date.strftime("%Y-%m"),
                submissions=submissions,
                placements=placements,
                conversion_rate=round((placements / submissions * 100) if submissions > 0 else 0, 2),
            )
        )

    return trends


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINT 1: GET /by-client - Client Performance Report
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/by-client", response_model=ClientPerformanceReport, status_code=status.HTTP_200_OK)
async def get_client_performance_report(
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD format"),
    organization_id: Optional[str] = Query(None, description="Filter by organization"),
    role: Optional[str] = Query(None, description="User role: msp_admin, company_admin, company_recruiter"),
) -> ClientPerformanceReport:
    """Client Performance Report.

    For each client: total jobs posted, active jobs, submissions received, interviews,
    offers, placements, avg time-to-fill, fill rate, avg match score, spend, satisfaction.

    Access: MSP_ADMIN=full | COMPANY_ADMIN=N/A | COMPANY_RECRUITER=N/A
    """
    if role and role in ("company_admin", "company_recruiter"):
        raise HTTPException(status_code=403, detail="Client performance report is only available to MSP administrators.")
    start, end = _get_date_range(start_date, end_date)

    # Mock client data
    clients_data = [
        {
            "client_id": 1,
            "client_name": "TechCorp Industries",
            "total_jobs_posted": 18,
            "active_jobs": 5,
            "total_submissions_received": 247,
            "interviews_conducted": 68,
            "offers_extended": 15,
            "placements_made": 12,
            "avg_time_to_fill_days": 22.5,
            "fill_rate_percent": 66.7,
            "avg_match_score": 78.3,
            "total_spend": 185000.00,
            "satisfaction_score": 4.6,
            "contract_value": 450000.00,
            "active_contracts": 8,
            "top_job_title": "Senior Software Engineer",
            "pipeline_count": 34,
        },
        {
            "client_id": 2,
            "client_name": "Global Finance Group",
            "total_jobs_posted": 12,
            "active_jobs": 3,
            "total_submissions_received": 189,
            "interviews_conducted": 52,
            "offers_extended": 10,
            "placements_made": 9,
            "avg_time_to_fill_days": 28.0,
            "fill_rate_percent": 75.0,
            "avg_match_score": 81.5,
            "total_spend": 156000.00,
            "satisfaction_score": 4.7,
            "contract_value": 380000.00,
            "active_contracts": 6,
            "top_job_title": "Financial Analyst",
            "pipeline_count": 28,
        },
        {
            "client_id": 3,
            "client_name": "HealthConnect Solutions",
            "total_jobs_posted": 15,
            "active_jobs": 7,
            "total_submissions_received": 312,
            "interviews_conducted": 89,
            "offers_extended": 18,
            "placements_made": 14,
            "avg_time_to_fill_days": 19.2,
            "fill_rate_percent": 93.3,
            "avg_match_score": 84.2,
            "total_spend": 224000.00,
            "satisfaction_score": 4.8,
            "contract_value": 520000.00,
            "active_contracts": 10,
            "top_job_title": "Clinical Data Manager",
            "pipeline_count": 41,
        },
        {
            "client_id": 4,
            "client_name": "Manufacturing Plus",
            "total_jobs_posted": 22,
            "active_jobs": 8,
            "total_submissions_received": 198,
            "interviews_conducted": 45,
            "offers_extended": 12,
            "placements_made": 10,
            "avg_time_to_fill_days": 32.5,
            "fill_rate_percent": 45.5,
            "avg_match_score": 72.8,
            "total_spend": 128000.00,
            "satisfaction_score": 4.2,
            "contract_value": 310000.00,
            "active_contracts": 5,
            "top_job_title": "Plant Manager",
            "pipeline_count": 19,
        },
        {
            "client_id": 5,
            "client_name": "Retail Innovations Ltd",
            "total_jobs_posted": 28,
            "active_jobs": 12,
            "total_submissions_received": 425,
            "interviews_conducted": 115,
            "offers_extended": 22,
            "placements_made": 18,
            "avg_time_to_fill_days": 21.0,
            "fill_rate_percent": 64.3,
            "avg_match_score": 76.9,
            "total_spend": 298000.00,
            "satisfaction_score": 4.4,
            "contract_value": 650000.00,
            "active_contracts": 12,
            "top_job_title": "Store Operations Manager",
            "pipeline_count": 56,
        },
        {
            "client_id": 6,
            "client_name": "Energy Systems Corp",
            "total_jobs_posted": 10,
            "active_jobs": 4,
            "total_submissions_received": 156,
            "interviews_conducted": 38,
            "offers_extended": 8,
            "placements_made": 7,
            "avg_time_to_fill_days": 26.3,
            "fill_rate_percent": 70.0,
            "avg_match_score": 79.1,
            "total_spend": 142000.00,
            "satisfaction_score": 4.5,
            "contract_value": 280000.00,
            "active_contracts": 4,
            "top_job_title": "Power Systems Engineer",
            "pipeline_count": 22,
        },
        {
            "client_id": 7,
            "client_name": "Software Development Hub",
            "total_jobs_posted": 25,
            "active_jobs": 9,
            "total_submissions_received": 567,
            "interviews_conducted": 142,
            "offers_extended": 26,
            "placements_made": 22,
            "avg_time_to_fill_days": 18.5,
            "fill_rate_percent": 88.0,
            "avg_match_score": 85.3,
            "total_spend": 342000.00,
            "satisfaction_score": 4.9,
            "contract_value": 780000.00,
            "active_contracts": 14,
            "top_job_title": "Full Stack Developer",
            "pipeline_count": 67,
        },
    ]

    # Calculate summary totals
    summary = {
        "total_clients": len(clients_data),
        "total_jobs_posted": sum(c["total_jobs_posted"] for c in clients_data),
        "total_active_jobs": sum(c["active_jobs"] for c in clients_data),
        "total_submissions": sum(c["total_submissions_received"] for c in clients_data),
        "total_interviews": sum(c["interviews_conducted"] for c in clients_data),
        "total_offers": sum(c["offers_extended"] for c in clients_data),
        "total_placements": sum(c["placements_made"] for c in clients_data),
        "avg_time_to_fill": round(
            sum(c["avg_time_to_fill_days"] for c in clients_data) / len(clients_data), 2
        ),
        "avg_fill_rate": round(
            sum(c["fill_rate_percent"] for c in clients_data) / len(clients_data), 2
        ),
        "avg_match_score": round(
            sum(c["avg_match_score"] for c in clients_data) / len(clients_data), 2
        ),
        "total_client_spend": sum(c["total_spend"] for c in clients_data),
        "avg_satisfaction": round(
            sum(c["satisfaction_score"] for c in clients_data) / len(clients_data), 2
        ),
    }

    return ClientPerformanceReport(
        clients=[ClientMetricItem(**c) for c in clients_data],
        summary=summary,
        report_period=f"{start.date()} to {end.date()}",
        generated_at=datetime.now(),
    )


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINT 2: GET /by-client/{client_id}/jobs - Client Job Breakdown
# ═══════════════════════════════════════════════════════════════════════════

@router.get(
    "/by-client/{client_id}/jobs",
    response_model=ClientJobBreakdown,
    status_code=status.HTTP_200_OK,
)
async def get_client_job_breakdown(
    client_id: int,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    role: Optional[str] = Query(None, description="User role: msp_admin, company_admin, company_recruiter"),
) -> ClientJobBreakdown:
    """Client Job Breakdown.

    For a specific client: list all their jobs with per-job stats and top candidates.
    """
    start, end = _get_date_range(start_date, end_date)

    client_names = {
        1: "TechCorp Industries",
        2: "Global Finance Group",
        3: "HealthConnect Solutions",
        4: "Manufacturing Plus",
        5: "Retail Innovations Ltd",
        6: "Energy Systems Corp",
        7: "Software Development Hub",
    }

    client_name = client_names.get(client_id, "Unknown Client")

    jobs_data = [
        {
            "job_id": 101,
            "job_title": "Senior Software Engineer",
            "location": "San Francisco, CA",
            "priority": "HIGH",
            "bill_rate": 185.00,
            "submissions_count": 34,
            "interviews_count": 12,
            "shortlisted_count": 8,
            "offers_count": 2,
            "placements_count": 2,
            "days_open": 18,
            "current_status": "FILLED",
            "avg_candidate_score": 82.1,
            "top_3_candidates": [
                {"candidate_id": 201, "candidate_name": "Alice Johnson", "match_score": 92.5, "current_phase": "PLACED", "source": "LinkedIn"},
                {"candidate_id": 202, "candidate_name": "Bob Chen", "match_score": 88.3, "current_phase": "PLACED", "source": "Referral"},
                {"candidate_id": 203, "candidate_name": "Carol Davis", "match_score": 79.7, "current_phase": "INTERVIEW", "source": "Company Site"},
            ],
        },
        {
            "job_id": 102,
            "job_title": "DevOps Engineer",
            "location": "Austin, TX",
            "priority": "MEDIUM",
            "bill_rate": 155.00,
            "submissions_count": 28,
            "interviews_count": 9,
            "shortlisted_count": 6,
            "offers_count": 1,
            "placements_count": 1,
            "days_open": 25,
            "current_status": "FILLED",
            "avg_candidate_score": 80.2,
            "top_3_candidates": [
                {"candidate_id": 204, "candidate_name": "David Smith", "match_score": 87.6, "current_phase": "PLACED", "source": "Indeed"},
                {"candidate_id": 205, "candidate_name": "Emma Wilson", "match_score": 81.4, "current_phase": "OFFER", "source": "LinkedIn"},
                {"candidate_id": 206, "candidate_name": "Frank Miller", "match_score": 75.8, "current_phase": "SUBMITTED", "source": "Supplier"},
            ],
        },
        {
            "job_id": 103,
            "job_title": "Product Manager",
            "location": "New York, NY",
            "priority": "HIGH",
            "bill_rate": 175.00,
            "submissions_count": 42,
            "interviews_count": 14,
            "shortlisted_count": 10,
            "offers_count": 3,
            "placements_count": 0,
            "days_open": 35,
            "current_status": "ACTIVE",
            "avg_candidate_score": 78.5,
            "top_3_candidates": [
                {"candidate_id": 207, "candidate_name": "Grace Lee", "match_score": 85.2, "current_phase": "OFFER", "source": "Recruiter"},
                {"candidate_id": 208, "candidate_name": "Henry Brown", "match_score": 82.1, "current_phase": "INTERVIEW", "source": "LinkedIn"},
                {"candidate_id": 209, "candidate_name": "Iris Garcia", "match_score": 76.9, "current_phase": "SUBMITTED", "source": "Supplier"},
            ],
        },
    ]

    return ClientJobBreakdown(
        client_id=client_id,
        client_name=client_name,
        total_jobs=len(jobs_data),
        active_jobs=sum(1 for j in jobs_data if j["current_status"] == "ACTIVE"),
        filled_jobs=sum(1 for j in jobs_data if j["current_status"] == "FILLED"),
        jobs=[JobForClient(**j) for j in jobs_data],
        report_period=f"{start.date()} to {end.date()}",
        generated_at=datetime.now(),
    )


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINT 3: GET /by-job - Job Performance Report
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/by-job", response_model=JobPerformanceReport, status_code=status.HTTP_200_OK)
async def get_job_performance_report(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    organization_id: Optional[str] = Query(None),
    role: Optional[str] = Query(None, description="User role: msp_admin, company_admin, company_recruiter"),
) -> JobPerformanceReport:
    """Job Performance Report.

    For each job: title, client, location, priority, bill rate, applicants,
    phase breakdown, conversion rate, time-in-phase, days open, fill status.
    """
    start, end = _get_date_range(start_date, end_date)

    jobs_data = [
        {
            "job_id": 101,
            "job_title": "Senior Software Engineer",
            "client_name": "TechCorp Industries",
            "location": "San Francisco, CA",
            "priority": "HIGH",
            "bill_rate": 185.00,
            "total_applicants": 87,
            "phase_breakdown": [
                {"phase": "Sourced", "count": 87, "days_in_phase_avg": 2.1},
                {"phase": "Screening", "count": 52, "count": 52, "days_in_phase_avg": 3.2},
                {"phase": "Submitted", "count": 34, "days_in_phase_avg": 4.5},
                {"phase": "Interview", "count": 12, "days_in_phase_avg": 6.2},
                {"phase": "Offer", "count": 2, "days_in_phase_avg": 3.1},
                {"phase": "Placed", "count": 2, "days_in_phase_avg": 0.0},
            ],
            "conversion_rate_percent": 2.3,
            "avg_time_in_phase_days": 3.7,
            "days_open": 18,
            "fill_status": "FILLED",
            "filled_count": 2,
        },
        {
            "job_id": 102,
            "job_title": "DevOps Engineer",
            "client_name": "TechCorp Industries",
            "location": "Austin, TX",
            "priority": "MEDIUM",
            "bill_rate": 155.00,
            "total_applicants": 64,
            "phase_breakdown": [
                {"phase": "Sourced", "count": 64, "days_in_phase_avg": 2.3},
                {"phase": "Screening", "count": 41, "days_in_phase_avg": 3.0},
                {"phase": "Submitted", "count": 28, "days_in_phase_avg": 4.2},
                {"phase": "Interview", "count": 9, "days_in_phase_avg": 5.8},
                {"phase": "Offer", "count": 1, "days_in_phase_avg": 2.9},
                {"phase": "Placed", "count": 1, "days_in_phase_avg": 0.0},
            ],
            "conversion_rate_percent": 1.6,
            "avg_time_in_phase_days": 3.6,
            "days_open": 25,
            "fill_status": "FILLED",
            "filled_count": 1,
        },
        {
            "job_id": 104,
            "job_title": "Financial Analyst",
            "client_name": "Global Finance Group",
            "location": "New York, NY",
            "priority": "HIGH",
            "bill_rate": 145.00,
            "total_applicants": 72,
            "phase_breakdown": [
                {"phase": "Sourced", "count": 72, "days_in_phase_avg": 2.0},
                {"phase": "Screening", "count": 45, "days_in_phase_avg": 3.1},
                {"phase": "Submitted", "count": 31, "days_in_phase_avg": 4.7},
                {"phase": "Interview", "count": 11, "days_in_phase_avg": 6.5},
                {"phase": "Offer", "count": 2, "days_in_phase_avg": 3.2},
                {"phase": "Placed", "count": 2, "days_in_phase_avg": 0.0},
            ],
            "conversion_rate_percent": 2.8,
            "avg_time_in_phase_days": 3.9,
            "days_open": 22,
            "fill_status": "FILLED",
            "filled_count": 2,
        },
        {
            "job_id": 105,
            "job_title": "Clinical Data Manager",
            "client_name": "HealthConnect Solutions",
            "location": "Boston, MA",
            "priority": "HIGH",
            "bill_rate": 125.00,
            "total_applicants": 89,
            "phase_breakdown": [
                {"phase": "Sourced", "count": 89, "days_in_phase_avg": 1.8},
                {"phase": "Screening", "count": 58, "days_in_phase_avg": 2.9},
                {"phase": "Submitted", "count": 42, "days_in_phase_avg": 4.1},
                {"phase": "Interview", "count": 15, "days_in_phase_avg": 5.6},
                {"phase": "Offer", "count": 4, "days_in_phase_avg": 2.8},
                {"phase": "Placed", "count": 4, "days_in_phase_avg": 0.0},
            ],
            "conversion_rate_percent": 4.5,
            "avg_time_in_phase_days": 3.4,
            "days_open": 16,
            "fill_status": "FILLED",
            "filled_count": 4,
        },
        {
            "job_id": 103,
            "job_title": "Product Manager",
            "client_name": "TechCorp Industries",
            "location": "New York, NY",
            "priority": "HIGH",
            "bill_rate": 175.00,
            "total_applicants": 95,
            "phase_breakdown": [
                {"phase": "Sourced", "count": 95, "days_in_phase_avg": 2.5},
                {"phase": "Screening", "count": 62, "days_in_phase_avg": 3.4},
                {"phase": "Submitted", "count": 42, "days_in_phase_avg": 5.1},
                {"phase": "Interview", "count": 14, "days_in_phase_avg": 7.2},
                {"phase": "Offer", "count": 3, "days_in_phase_avg": 4.5},
                {"phase": "Placed", "count": 0, "days_in_phase_avg": 0.0},
            ],
            "conversion_rate_percent": 0.0,
            "avg_time_in_phase_days": 4.5,
            "days_open": 35,
            "fill_status": "ACTIVE",
            "filled_count": 0,
        },
    ]

    return JobPerformanceReport(
        jobs=[JobMetricItem(**j) for j in jobs_data],
        total_jobs=len(jobs_data),
        avg_fill_rate=round(
            sum(j["filled_count"] for j in jobs_data) / len(jobs_data), 2
        ),
        avg_time_to_fill=round(
            sum(j["days_open"] for j in jobs_data) / len(jobs_data), 2
        ),
        report_period=f"{start.date()} to {end.date()}",
        generated_at=datetime.now(),
    )


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINT 4: GET /by-job/{job_id}/applicants - Job Applicant Breakdown
# ═══════════════════════════════════════════════════════════════════════════

@router.get(
    "/by-job/{job_id}/applicants",
    response_model=JobApplicantBreakdown,
    status_code=status.HTTP_200_OK,
)
async def get_job_applicant_breakdown(
    job_id: int,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
) -> JobApplicantBreakdown:
    """Job Applicant Breakdown.

    For a specific job: list all applicants with phase, match score dimensions,
    skills, source, time-in-phase, phase history, and assigned recruiter.
    """
    start, end = _get_date_range(start_date, end_date)

    job_titles = {
        101: "Senior Software Engineer",
        102: "DevOps Engineer",
        103: "Product Manager",
        104: "Financial Analyst",
        105: "Clinical Data Manager",
    }

    client_names = {
        101: "TechCorp Industries",
        102: "TechCorp Industries",
        103: "TechCorp Industries",
        104: "Global Finance Group",
        105: "HealthConnect Solutions",
    }

    job_title = job_titles.get(job_id, "Unknown Job")
    client_name = client_names.get(job_id, "Unknown Client")

    applicants_data = [
        {
            "applicant_id": 301,
            "candidate_name": "Alice Johnson",
            "current_phase": "PLACED",
            "overall_match_score": 92.5,
            "match_dimensions": [
                {"dimension": "Technical Skills", "score": 94.0},
                {"dimension": "Experience Level", "score": 91.5},
                {"dimension": "Location Fit", "score": 95.0},
                {"dimension": "Salary Expectations", "score": 88.0},
                {"dimension": "Culture Fit", "score": 92.0},
                {"dimension": "Availability", "score": 90.0},
                {"dimension": "Communication", "score": 93.0},
            ],
            "skills": ["Python", "Go", "Kubernetes", "Docker", "AWS", "CI/CD"],
            "source": "LinkedIn",
            "time_in_current_phase_days": 2,
            "phase_history": [
                {"phase": "Sourced", "entered_date": datetime.now() - timedelta(days=15), "exited_date": datetime.now() - timedelta(days=13), "days_in_phase": 2},
                {"phase": "Screening", "entered_date": datetime.now() - timedelta(days=13), "exited_date": datetime.now() - timedelta(days=9), "days_in_phase": 4},
                {"phase": "Submitted", "entered_date": datetime.now() - timedelta(days=9), "exited_date": datetime.now() - timedelta(days=5), "days_in_phase": 4},
                {"phase": "Interview", "entered_date": datetime.now() - timedelta(days=5), "exited_date": datetime.now() - timedelta(days=2), "days_in_phase": 3},
                {"phase": "Offer", "entered_date": datetime.now() - timedelta(days=2), "exited_date": datetime.now(), "days_in_phase": 2},
            ],
            "recruiter_assigned": "Sarah Martinez",
        },
        {
            "applicant_id": 302,
            "candidate_name": "Bob Chen",
            "current_phase": "PLACED",
            "overall_match_score": 88.3,
            "match_dimensions": [
                {"dimension": "Technical Skills", "score": 90.0},
                {"dimension": "Experience Level", "score": 86.0},
                {"dimension": "Location Fit", "score": 92.0},
                {"dimension": "Salary Expectations", "score": 82.0},
                {"dimension": "Culture Fit", "score": 89.0},
                {"dimension": "Availability", "score": 88.0},
                {"dimension": "Communication", "score": 85.0},
            ],
            "skills": ["Java", "Spring Boot", "Kubernetes", "AWS", "Terraform"],
            "source": "Referral",
            "time_in_current_phase_days": 3,
            "phase_history": [
                {"phase": "Sourced", "entered_date": datetime.now() - timedelta(days=17), "exited_date": datetime.now() - timedelta(days=15), "days_in_phase": 2},
                {"phase": "Screening", "entered_date": datetime.now() - timedelta(days=15), "exited_date": datetime.now() - timedelta(days=11), "days_in_phase": 4},
                {"phase": "Submitted", "entered_date": datetime.now() - timedelta(days=11), "exited_date": datetime.now() - timedelta(days=7), "days_in_phase": 4},
                {"phase": "Interview", "entered_date": datetime.now() - timedelta(days=7), "exited_date": datetime.now() - timedelta(days=3), "days_in_phase": 4},
                {"phase": "Offer", "entered_date": datetime.now() - timedelta(days=3), "exited_date": datetime.now(), "days_in_phase": 3},
            ],
            "recruiter_assigned": "Michael Johnson",
        },
        {
            "applicant_id": 303,
            "candidate_name": "Carol Davis",
            "current_phase": "INTERVIEW",
            "overall_match_score": 79.7,
            "match_dimensions": [
                {"dimension": "Technical Skills", "score": 82.0},
                {"dimension": "Experience Level", "score": 78.0},
                {"dimension": "Location Fit", "score": 88.0},
                {"dimension": "Salary Expectations", "score": 75.0},
                {"dimension": "Culture Fit", "score": 81.0},
                {"dimension": "Availability", "score": 76.0},
                {"dimension": "Communication", "score": 80.0},
            ],
            "skills": ["Python", "JavaScript", "AWS", "PostgreSQL"],
            "source": "Company Site",
            "time_in_current_phase_days": 5,
            "phase_history": [
                {"phase": "Sourced", "entered_date": datetime.now() - timedelta(days=20), "exited_date": datetime.now() - timedelta(days=18), "days_in_phase": 2},
                {"phase": "Screening", "entered_date": datetime.now() - timedelta(days=18), "exited_date": datetime.now() - timedelta(days=14), "days_in_phase": 4},
                {"phase": "Submitted", "entered_date": datetime.now() - timedelta(days=14), "exited_date": datetime.now() - timedelta(days=9), "days_in_phase": 5},
                {"phase": "Interview", "entered_date": datetime.now() - timedelta(days=9), "exited_date": None, "days_in_phase": 5},
            ],
            "recruiter_assigned": "Sarah Martinez",
        },
        {
            "applicant_id": 304,
            "candidate_name": "David Smith",
            "current_phase": "SUBMITTED",
            "overall_match_score": 75.2,
            "match_dimensions": [
                {"dimension": "Technical Skills", "score": 78.0},
                {"dimension": "Experience Level", "score": 72.0},
                {"dimension": "Location Fit", "score": 82.0},
                {"dimension": "Salary Expectations", "score": 70.0},
                {"dimension": "Culture Fit", "score": 76.0},
                {"dimension": "Availability", "score": 73.0},
                {"dimension": "Communication", "score": 75.0},
            ],
            "skills": ["Python", "Go", "Docker"],
            "source": "Indeed",
            "time_in_current_phase_days": 6,
            "phase_history": [
                {"phase": "Sourced", "entered_date": datetime.now() - timedelta(days=25), "exited_date": datetime.now() - timedelta(days=23), "days_in_phase": 2},
                {"phase": "Screening", "entered_date": datetime.now() - timedelta(days=23), "exited_date": datetime.now() - timedelta(days=19), "days_in_phase": 4},
                {"phase": "Submitted", "entered_date": datetime.now() - timedelta(days=19), "exited_date": None, "days_in_phase": 6},
            ],
            "recruiter_assigned": "Jessica Lee",
        },
    ]

    return JobApplicantBreakdown(
        job_id=job_id,
        job_title=job_title,
        client_name=client_name,
        total_applicants=len(applicants_data),
        applicants=[ApplicantDetail(**a) for a in applicants_data],
        report_period=f"{start.date()} to {end.date()}",
        generated_at=datetime.now(),
    )


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINT 5: GET /by-supplier - Supplier Performance Report
# ═══════════════════════════════════════════════════════════════════════════

@router.get(
    "/by-supplier",
    response_model=SupplierPerformanceReport,
    status_code=status.HTTP_200_OK,
)
async def get_supplier_performance_report(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    organization_id: Optional[str] = Query(None),
    role: Optional[str] = Query(None, description="User role: msp_admin, company_admin, company_recruiter"),
) -> SupplierPerformanceReport:
    """Supplier Performance Report.

    For each supplier: submissions, placements, fill rate, avg match score,
    avg time-to-submit, rejection rate, quality/compliance scores, revenue,
    active contracts, SLA adherence.
    """
    start, end = _get_date_range(start_date, end_date)

    suppliers_data = [
        {
            "supplier_id": 501,
            "supplier_name": "TechTalent Recruiters",
            "tier": "Gold",
            "total_candidates_submitted": 142,
            "placements_made": 28,
            "fill_rate_percent": 19.7,
            "avg_match_score_submissions": 82.4,
            "avg_time_to_submit_days": 3.2,
            "rejection_rate_percent": 12.5,
            "interview_to_offer_rate_percent": 65.0,
            "quality_score": 87.5,
            "compliance_score": 94.2,
            "total_revenue_generated": 245000.00,
            "active_contracts": 12,
            "sla_adherence_percent": 98.5,
        },
        {
            "supplier_id": 502,
            "supplier_name": "Global Talent Solutions",
            "tier": "Gold",
            "total_candidates_submitted": 128,
            "placements_made": 24,
            "fill_rate_percent": 18.8,
            "avg_match_score_submissions": 80.1,
            "avg_time_to_submit_days": 3.8,
            "rejection_rate_percent": 14.2,
            "interview_to_offer_rate_percent": 61.5,
            "quality_score": 84.2,
            "compliance_score": 91.8,
            "total_revenue_generated": 218000.00,
            "active_contracts": 10,
            "sla_adherence_percent": 96.8,
        },
        {
            "supplier_id": 503,
            "supplier_name": "Staffing Experts Inc",
            "tier": "Silver",
            "total_candidates_submitted": 95,
            "placements_made": 16,
            "fill_rate_percent": 16.8,
            "avg_match_score_submissions": 77.3,
            "avg_time_to_submit_days": 4.5,
            "rejection_rate_percent": 18.7,
            "interview_to_offer_rate_percent": 58.3,
            "quality_score": 79.8,
            "compliance_score": 87.4,
            "total_revenue_generated": 148000.00,
            "active_contracts": 7,
            "sla_adherence_percent": 93.2,
        },
        {
            "supplier_id": 504,
            "supplier_name": "Professional Placements Ltd",
            "tier": "Silver",
            "total_candidates_submitted": 87,
            "placements_made": 14,
            "fill_rate_percent": 16.1,
            "avg_match_score_submissions": 75.8,
            "avg_time_to_submit_days": 5.2,
            "rejection_rate_percent": 21.5,
            "interview_to_offer_rate_percent": 54.2,
            "quality_score": 76.5,
            "compliance_score": 84.1,
            "total_revenue_generated": 128000.00,
            "active_contracts": 6,
            "sla_adherence_percent": 89.6,
        },
        {
            "supplier_id": 505,
            "supplier_name": "QuickStaff Recruiting",
            "tier": "Bronze",
            "total_candidates_submitted": 64,
            "placements_made": 8,
            "fill_rate_percent": 12.5,
            "avg_match_score_submissions": 71.2,
            "avg_time_to_submit_days": 6.1,
            "rejection_rate_percent": 28.3,
            "interview_to_offer_rate_percent": 42.8,
            "quality_score": 68.4,
            "compliance_score": 78.5,
            "total_revenue_generated": 72000.00,
            "active_contracts": 3,
            "sla_adherence_percent": 82.1,
        },
        {
            "supplier_id": 506,
            "supplier_name": "Elite Search Partners",
            "tier": "Gold",
            "total_candidates_submitted": 156,
            "placements_made": 32,
            "fill_rate_percent": 20.5,
            "avg_match_score_submissions": 84.6,
            "avg_time_to_submit_days": 2.8,
            "rejection_rate_percent": 10.2,
            "interview_to_offer_rate_percent": 68.7,
            "quality_score": 89.2,
            "compliance_score": 96.5,
            "total_revenue_generated": 285000.00,
            "active_contracts": 14,
            "sla_adherence_percent": 99.2,
        },
    ]

    summary = {
        "total_suppliers": len(suppliers_data),
        "total_submissions": sum(s["total_candidates_submitted"] for s in suppliers_data),
        "total_placements": sum(s["placements_made"] for s in suppliers_data),
        "avg_fill_rate": round(
            sum(s["fill_rate_percent"] for s in suppliers_data) / len(suppliers_data), 2
        ),
        "avg_match_score": round(
            sum(s["avg_match_score_submissions"] for s in suppliers_data) / len(suppliers_data), 2
        ),
        "avg_time_to_submit": round(
            sum(s["avg_time_to_submit_days"] for s in suppliers_data) / len(suppliers_data), 2
        ),
        "avg_rejection_rate": round(
            sum(s["rejection_rate_percent"] for s in suppliers_data) / len(suppliers_data), 2
        ),
        "avg_quality_score": round(
            sum(s["quality_score"] for s in suppliers_data) / len(suppliers_data), 2
        ),
        "total_revenue": sum(s["total_revenue_generated"] for s in suppliers_data),
    }

    return SupplierPerformanceReport(
        suppliers=[SupplierMetricItem(**s) for s in suppliers_data],
        summary=summary,
        report_period=f"{start.date()} to {end.date()}",
        generated_at=datetime.now(),
    )


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINT 6: GET /by-supplier/{supplier_id}/jobs - Supplier Job Breakdown
# ═══════════════════════════════════════════════════════════════════════════

@router.get(
    "/by-supplier/{supplier_id}/jobs",
    response_model=SupplierJobBreakdown,
    status_code=status.HTTP_200_OK,
)
async def get_supplier_job_breakdown(
    supplier_id: int,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    role: Optional[str] = Query(None, description="User role: msp_admin, company_admin, company_recruiter"),
) -> SupplierJobBreakdown:
    """Supplier Job Breakdown.

    For a specific supplier: list jobs they've submitted candidates to,
    with per-job stats, best candidate, and rejection reasons.
    """
    start, end = _get_date_range(start_date, end_date)

    supplier_names = {
        501: "TechTalent Recruiters",
        502: "Global Talent Solutions",
        503: "Staffing Experts Inc",
        504: "Professional Placements Ltd",
        505: "QuickStaff Recruiting",
        506: "Elite Search Partners",
    }

    supplier_name = supplier_names.get(supplier_id, "Unknown Supplier")
    tier_map = {501: "Gold", 502: "Gold", 503: "Silver", 504: "Silver", 505: "Bronze", 506: "Gold"}

    jobs_data = [
        {
            "job_id": 101,
            "job_title": "Senior Software Engineer",
            "client_name": "TechCorp Industries",
            "candidates_submitted": 18,
            "shortlisted_count": 6,
            "placed_count": 1,
            "avg_score": 81.3,
            "best_candidate_name": "Alice Johnson",
            "rejection_reasons": {"Overqualified": 2, "Salary mismatch": 1, "Location": 1, "Other": 8},
        },
        {
            "job_id": 104,
            "job_title": "Financial Analyst",
            "client_name": "Global Finance Group",
            "candidates_submitted": 14,
            "shortlisted_count": 5,
            "placed_count": 1,
            "avg_score": 78.9,
            "best_candidate_name": "Emma Rodriguez",
            "rejection_reasons": {"Experience gap": 3, "Technical skills": 2, "Cultural fit": 1, "Other": 8},
        },
        {
            "job_id": 105,
            "job_title": "Clinical Data Manager",
            "client_name": "HealthConnect Solutions",
            "candidates_submitted": 22,
            "shortlisted_count": 8,
            "placed_count": 2,
            "avg_score": 83.5,
            "best_candidate_name": "Jennifer Smith",
            "rejection_reasons": {"Background check": 1, "Salary expectations": 2, "Other": 9},
        },
    ]

    return SupplierJobBreakdown(
        supplier_id=supplier_id,
        supplier_name=supplier_name,
        tier=tier_map.get(supplier_id, "Unknown"),
        total_jobs_submitted_to=len(jobs_data),
        total_placements=sum(j["placed_count"] for j in jobs_data),
        jobs=[SupplierJobSubmission(**j) for j in jobs_data],
        report_period=f"{start.date()} to {end.date()}",
        generated_at=datetime.now(),
    )


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINT 7: GET /by-recruiter - Recruiter Performance Report
# ═══════════════════════════════════════════════════════════════════════════

@router.get(
    "/by-recruiter",
    response_model=RecruiterPerformanceReport,
    status_code=status.HTTP_200_OK,
)
async def get_recruiter_performance_report(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    organization_id: Optional[str] = Query(None),
    role: Optional[str] = Query(None, description="User role: msp_admin, company_admin, company_recruiter"),
) -> RecruiterPerformanceReport:
    """Recruiter Performance Report.

    For each recruiter: submissions, placements, conversion rate, avg time-to-submit,
    avg match score, revenue, requisitions, pipeline by phase, top skills/clients,
    and 6-month trends.
    """
    start, end = _get_date_range(start_date, end_date)

    recruiters_data = [
        {
            "recruiter_id": 601,
            "recruiter_name": "Sarah Martinez",
            "email": "sarah.martinez@company.com",
            "total_submissions": 68,
            "placements_made": 16,
            "conversion_rate_percent": 23.5,
            "avg_time_to_submit_days": 3.2,
            "avg_match_score": 82.3,
            "revenue_generated": 195000.00,
            "active_requisitions": 8,
            "candidates_in_pipeline_by_phase": {
                "Sourced": 45,
                "Screening": 28,
                "Submitted": 18,
                "Interview": 8,
                "Offer": 2,
            },
            "top_skills_handled": ["Python", "AWS", "Kubernetes", "React"],
            "top_clients_served": ["TechCorp Industries", "Software Development Hub"],
            "month_over_month_trends": _generate_monthly_trends(),
        },
        {
            "recruiter_id": 602,
            "recruiter_name": "Michael Johnson",
            "email": "michael.johnson@company.com",
            "total_submissions": 54,
            "placements_made": 12,
            "conversion_rate_percent": 22.2,
            "avg_time_to_submit_days": 3.8,
            "avg_match_score": 79.8,
            "revenue_generated": 156000.00,
            "active_requisitions": 6,
            "candidates_in_pipeline_by_phase": {
                "Sourced": 38,
                "Screening": 24,
                "Submitted": 16,
                "Interview": 6,
                "Offer": 1,
            },
            "top_skills_handled": ["Java", "Spring Boot", "SQL", "Docker"],
            "top_clients_served": ["Global Finance Group", "HealthConnect Solutions"],
            "month_over_month_trends": _generate_monthly_trends(),
        },
        {
            "recruiter_id": 603,
            "recruiter_name": "Jessica Lee",
            "email": "jessica.lee@company.com",
            "total_submissions": 72,
            "placements_made": 18,
            "conversion_rate_percent": 25.0,
            "avg_time_to_submit_days": 2.9,
            "avg_match_score": 84.1,
            "revenue_generated": 218000.00,
            "active_requisitions": 9,
            "candidates_in_pipeline_by_phase": {
                "Sourced": 52,
                "Screening": 31,
                "Submitted": 21,
                "Interview": 9,
                "Offer": 3,
            },
            "top_skills_handled": ["Go", "Rust", "TypeScript", "GraphQL"],
            "top_clients_served": ["Software Development Hub", "TechCorp Industries"],
            "month_over_month_trends": _generate_monthly_trends(),
        },
        {
            "recruiter_id": 604,
            "recruiter_name": "David Chen",
            "email": "david.chen@company.com",
            "total_submissions": 45,
            "placements_made": 9,
            "conversion_rate_percent": 20.0,
            "avg_time_to_submit_days": 4.2,
            "avg_match_score": 77.5,
            "revenue_generated": 118000.00,
            "active_requisitions": 5,
            "candidates_in_pipeline_by_phase": {
                "Sourced": 32,
                "Screening": 20,
                "Submitted": 14,
                "Interview": 5,
                "Offer": 1,
            },
            "top_skills_handled": ["Project Management", "Finance", "HR", "Operations"],
            "top_clients_served": ["Global Finance Group", "Manufacturing Plus"],
            "month_over_month_trends": _generate_monthly_trends(),
        },
        {
            "recruiter_id": 605,
            "recruiter_name": "Amanda Garcia",
            "email": "amanda.garcia@company.com",
            "total_submissions": 89,
            "placements_made": 22,
            "conversion_rate_percent": 24.7,
            "avg_time_to_submit_days": 3.1,
            "avg_match_score": 83.6,
            "revenue_generated": 268000.00,
            "active_requisitions": 10,
            "candidates_in_pipeline_by_phase": {
                "Sourced": 61,
                "Screening": 37,
                "Submitted": 25,
                "Interview": 10,
                "Offer": 4,
            },
            "top_skills_handled": ["DevOps", "Cloud Architecture", "Terraform", "CI/CD"],
            "top_clients_served": ["HealthConnect Solutions", "Software Development Hub"],
            "month_over_month_trends": _generate_monthly_trends(),
        },
    ]

    return RecruiterPerformanceReport(
        recruiters=[RecruiterMetricItem(**r) for r in recruiters_data],
        total_recruiters=len(recruiters_data),
        avg_conversion_rate=round(
            sum(r["conversion_rate_percent"] for r in recruiters_data) / len(recruiters_data), 2
        ),
        avg_submissions_per_recruiter=round(
            sum(r["total_submissions"] for r in recruiters_data) / len(recruiters_data), 2
        ),
        top_recruiter_id=605,
        report_period=f"{start.date()} to {end.date()}",
        generated_at=datetime.now(),
    )


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINT 8: GET /by-recruiter/{recruiter_id}/activity - Recruiter Activity
# ═══════════════════════════════════════════════════════════════════════════

@router.get(
    "/by-recruiter/{recruiter_id}/activity",
    response_model=RecruiterActivity,
    status_code=status.HTTP_200_OK,
)
async def get_recruiter_activity(
    recruiter_id: int,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    role: Optional[str] = Query(None, description="User role: msp_admin, company_admin, company_recruiter"),
) -> RecruiterActivity:
    """Recruiter Activity Breakdown.

    Detailed activity: daily/weekly submission counts, placement velocity,
    sourcing by channel, interview scheduling rate, offer acceptance rate,
    and pipeline health.
    """
    start, end = _get_date_range(start_date, end_date)

    recruiter_names = {
        601: "Sarah Martinez",
        602: "Michael Johnson",
        603: "Jessica Lee",
        604: "David Chen",
        605: "Amanda Garcia",
    }

    recruiter_name = recruiter_names.get(recruiter_id, "Unknown Recruiter")

    # Generate last 30 days of activity
    daily_activity = []
    for i in range(29, -1, -1):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        daily_activity.append(
            DailyActivityData(
                date=date,
                submissions_count=(2 + (i % 3)),
                placements_count=(0 if i % 7 != 0 else 1),
                interviews_scheduled=(1 + (i % 2)),
            )
        )

    return RecruiterActivity(
        recruiter_id=recruiter_id,
        recruiter_name=recruiter_name,
        daily_activity=daily_activity,
        weekly_submission_avg=12.3,
        placement_velocity_placements_per_week=3.2,
        candidate_sourcing_by_channel=[
            SourceingChannelBreakdown(
                channel="LinkedIn",
                candidates_sourced=34,
                placements_from_channel=8,
                quality_score=84.2,
            ),
            SourceingChannelBreakdown(
                channel="Referral",
                candidates_sourced=18,
                placements_from_channel=6,
                quality_score=89.5,
            ),
            SourceingChannelBreakdown(
                channel="Company Website",
                candidates_sourced=12,
                placements_from_channel=2,
                quality_score=76.3,
            ),
            SourceingChannelBreakdown(
                channel="Indeed",
                candidates_sourced=8,
                placements_from_channel=1,
                quality_score=71.2,
            ),
        ],
        interview_scheduling_rate=65.5,
        offer_acceptance_rate_percent=82.4,
        pipeline_health={
            "Active": 68,
            "In Progress": 41,
            "Stale": 5,
            "Archived": 124,
        },
        stale_candidates_count=5,
        report_period=f"{start.date()} to {end.date()}",
        generated_at=datetime.now(),
    )


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINT 9: GET /by-company - Company-wide Executive Report
# ═══════════════════════════════════════════════════════════════════════════

@router.get(
    "/by-company",
    response_model=CompanyExecutiveReport,
    status_code=status.HTTP_200_OK,
)
async def get_company_executive_report(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    organization_id: Optional[str] = Query(None),
    role: Optional[str] = Query(None, description="User role: msp_admin, company_admin, company_recruiter"),
) -> CompanyExecutiveReport:
    """Company-wide Executive Report.

    Org-wide metrics: active jobs, candidates in pipeline, placements YTD,
    avg time-to-fill, cost-per-hire, top performers by category,
    and 6-month trends.
    """
    start, end = _get_date_range(start_date, end_date)

    return CompanyExecutiveReport(
        organization_name="HotGigs 2026 - MSP/VMS Platform",
        total_active_jobs=48,
        total_candidates_in_pipeline=387,
        total_placements_ytd=156,
        avg_time_to_fill_days=23.4,
        avg_cost_per_hire=1850.00,
        fill_rate_percent=74.2,
        offer_acceptance_rate_percent=81.5,
        top_performing_clients=[
            TopPerformer(id=7, name="Software Development Hub", metric_value=22),
            TopPerformer(id=3, name="HealthConnect Solutions", metric_value=18),
            TopPerformer(id=5, name="Retail Innovations Ltd", metric_value=18),
        ],
        top_performing_suppliers=[
            TopPerformer(id=506, name="Elite Search Partners", metric_value=32),
            TopPerformer(id=501, name="TechTalent Recruiters", metric_value=28),
            TopPerformer(id=502, name="Global Talent Solutions", metric_value=24),
        ],
        top_performing_recruiters=[
            TopPerformer(id=605, name="Amanda Garcia", metric_value=22),
            TopPerformer(id=603, name="Jessica Lee", metric_value=18),
            TopPerformer(id=601, name="Sarah Martinez", metric_value=16),
        ],
        month_over_month_trends=_generate_monthly_trends(),
        department_breakdown=[
            DepartmentBreakdown(
                department="Engineering",
                active_jobs=18,
                filled_jobs=15,
                placements_ytd=52,
                avg_time_to_fill_days=20.2,
            ),
            DepartmentBreakdown(
                department="Finance & Accounting",
                active_jobs=8,
                filled_jobs=6,
                placements_ytd=18,
                avg_time_to_fill_days=26.5,
            ),
            DepartmentBreakdown(
                department="Healthcare",
                active_jobs=12,
                filled_jobs=11,
                placements_ytd=45,
                avg_time_to_fill_days=19.8,
            ),
            DepartmentBreakdown(
                department="Operations & Management",
                active_jobs=10,
                filled_jobs=8,
                placements_ytd=28,
                avg_time_to_fill_days=28.3,
            ),
        ],
        total_revenue_ytd=2480000.00,
        cost_per_fill_avg=1850.00,
        report_period=f"{start.date()} to {end.date()}",
        generated_at=datetime.now(),
    )


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINT 10: GET /cross-dimensional - Cross-Dimensional Matrix
# ═══════════════════════════════════════════════════════════════════════════

@router.get(
    "/cross-dimensional",
    response_model=CrossDimensionalMatrix,
    status_code=status.HTTP_200_OK,
)
async def get_cross_dimensional_matrix(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    organization_id: Optional[str] = Query(None),
    role: Optional[str] = Query(None, description="User role: msp_admin, company_admin, company_recruiter"),
) -> CrossDimensionalMatrix:
    """Cross-Dimensional Matrix.

    Client × Supplier placements grid, Client × Recruiter performance grid,
    Supplier × Skill strength grid, Priority × TTF, Source × Conversion,
    Location × Fill Rate.
    """
    start, end = _get_date_range(start_date, end_date)

    return CrossDimensionalMatrix(
        client_supplier_placements={
            "TechCorp Industries": {
                "TechTalent Recruiters": 6,
                "Elite Search Partners": 5,
                "Global Talent Solutions": 4,
            },
            "Global Finance Group": {
                "TechTalent Recruiters": 4,
                "Global Talent Solutions": 3,
                "Staffing Experts Inc": 2,
            },
            "HealthConnect Solutions": {
                "Elite Search Partners": 7,
                "TechTalent Recruiters": 5,
                "Global Talent Solutions": 3,
            },
            "Software Development Hub": {
                "Elite Search Partners": 9,
                "TechTalent Recruiters": 8,
                "Global Talent Solutions": 5,
            },
        },
        client_recruiter_performance={
            "TechCorp Industries": {
                "Amanda Garcia": 8,
                "Jessica Lee": 6,
                "Sarah Martinez": 5,
            },
            "Global Finance Group": {
                "Michael Johnson": 5,
                "David Chen": 4,
            },
            "HealthConnect Solutions": {
                "Jessica Lee": 8,
                "Amanda Garcia": 7,
                "Sarah Martinez": 3,
            },
            "Software Development Hub": {
                "Amanda Garcia": 9,
                "Jessica Lee": 7,
                "Sarah Martinez": 6,
            },
        },
        supplier_skill_strength={
            "TechTalent Recruiters": {
                "Python": 24,
                "Go": 18,
                "Kubernetes": 22,
                "Docker": 20,
            },
            "Elite Search Partners": {
                "Java": 28,
                "Spring Boot": 25,
                "AWS": 30,
                "Terraform": 19,
            },
            "Global Talent Solutions": {
                "React": 16,
                "TypeScript": 14,
                "Node.js": 12,
                "PostgreSQL": 15,
            },
        },
        job_priority_ttf={
            "CRITICAL": 15.2,
            "HIGH": 22.5,
            "MEDIUM": 28.3,
            "LOW": 35.8,
        },
        source_conversion_rate={
            "LinkedIn": 24.5,
            "Referral": 32.1,
            "Company Website": 18.3,
            "Indeed": 16.2,
            "Supplier Network": 20.8,
        },
        location_fill_rate={
            "San Francisco, CA": 88.5,
            "New York, NY": 76.2,
            "Austin, TX": 82.3,
            "Boston, MA": 91.2,
            "Remote": 85.7,
        },
        report_period=f"{start.date()} to {end.date()}",
        generated_at=datetime.now(),
    )


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINT 11: GET /pipeline-velocity - Pipeline Velocity Report
# ═══════════════════════════════════════════════════════════════════════════

@router.get(
    "/pipeline-velocity",
    response_model=PipelineVelocityReport,
    status_code=status.HTTP_200_OK,
)
async def get_pipeline_velocity_report(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    organization_id: Optional[str] = Query(None),
    role: Optional[str] = Query(None, description="User role: msp_admin, company_admin, company_recruiter"),
) -> PipelineVelocityReport:
    """Pipeline Velocity Report.

    Avg days in each phase (sourced→screening→submitted→interview→offer→placed),
    by client, by priority, by job type. Bottleneck identification.
    Week-over-week velocity trends.
    """
    start, end = _get_date_range(start_date, end_date)

    # Overall phase velocities
    overall_phases = [
        PhaseVelocity(
            from_phase="Sourced",
            to_phase="Screening",
            avg_days=2.3,
            median_days=2.0,
            conversion_rate_percent=72.5,
        ),
        PhaseVelocity(
            from_phase="Screening",
            to_phase="Submitted",
            avg_days=4.1,
            median_days=3.5,
            conversion_rate_percent=68.3,
        ),
        PhaseVelocity(
            from_phase="Submitted",
            to_phase="Interview",
            avg_days=5.6,
            median_days=5.0,
            conversion_rate_percent=35.8,
        ),
        PhaseVelocity(
            from_phase="Interview",
            to_phase="Offer",
            avg_days=6.8,
            median_days=6.0,
            conversion_rate_percent=24.5,
        ),
        PhaseVelocity(
            from_phase="Offer",
            to_phase="Placed",
            avg_days=3.2,
            median_days=3.0,
            conversion_rate_percent=85.2,
        ),
    ]

    # Weekly trends
    weekly_trends = []
    for i in range(11, -1, -1):
        week_date = datetime.now() - timedelta(weeks=i)
        weekly_trends.append(
            WeeklyVelocityTrend(
                week=week_date.strftime("%Y-W%V"),
                avg_time_across_all_phases=22.0 + (i % 4) - 1.5,
            )
        )

    return PipelineVelocityReport(
        overall_phase_velocities=overall_phases,
        bottleneck_phase="Interview",
        bottleneck_avg_days=6.8,
        velocity_by_client=[
            VelocityBreakdown(
                dimension="client",
                dimension_value="TechCorp Industries",
                phase_velocities=overall_phases,
            ),
            VelocityBreakdown(
                dimension="client",
                dimension_value="HealthConnect Solutions",
                phase_velocities=[
                    PhaseVelocity(
                        from_phase="Sourced",
                        to_phase="Screening",
                        avg_days=2.0,
                        median_days=1.8,
                        conversion_rate_percent=75.2,
                    ),
                    PhaseVelocity(
                        from_phase="Screening",
                        to_phase="Submitted",
                        avg_days=3.8,
                        median_days=3.5,
                        conversion_rate_percent=70.1,
                    ),
                    PhaseVelocity(
                        from_phase="Submitted",
                        to_phase="Interview",
                        avg_days=5.2,
                        median_days=4.8,
                        conversion_rate_percent=38.2,
                    ),
                ],
            ),
        ],
        velocity_by_priority=[
            VelocityBreakdown(
                dimension="priority",
                dimension_value="CRITICAL",
                phase_velocities=overall_phases,
            ),
            VelocityBreakdown(
                dimension="priority",
                dimension_value="HIGH",
                phase_velocities=overall_phases,
            ),
        ],
        velocity_by_job_type=[
            VelocityBreakdown(
                dimension="job_type",
                dimension_value="Technical",
                phase_velocities=overall_phases,
            ),
            VelocityBreakdown(
                dimension="job_type",
                dimension_value="Non-Technical",
                phase_velocities=overall_phases,
            ),
        ],
        week_over_week_trends=weekly_trends,
        report_period=f"{start.date()} to {end.date()}",
        generated_at=datetime.now(),
    )


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINT 12: GET /conversion-funnel - Conversion Funnel Report
# ═══════════════════════════════════════════════════════════════════════════

@router.get(
    "/conversion-funnel",
    response_model=ConversionFunnelReport,
    status_code=status.HTTP_200_OK,
)
async def get_conversion_funnel_report(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    organization_id: Optional[str] = Query(None),
    role: Optional[str] = Query(None, description="User role: msp_admin, company_admin, company_recruiter"),
) -> ConversionFunnelReport:
    """Conversion Funnel Report.

    Full funnel from sourced → screening → submitted → interview → offer → placed
    with counts, drop-off %, avg days between transitions.
    By client, by supplier, and monthly trends.
    """
    start, end = _get_date_range(start_date, end_date)

    # Overall funnel
    overall_funnel = [
        FunnelStage(
            stage="Sourced",
            count=1247,
            conversion_from_start_percent=100.0,
            dropoff_from_previous_percent=0.0,
            avg_days_to_this_stage=0.0,
        ),
        FunnelStage(
            stage="Screening",
            count=847,
            conversion_from_start_percent=67.9,
            dropoff_from_previous_percent=32.1,
            avg_days_to_this_stage=2.3,
        ),
        FunnelStage(
            stage="Submitted",
            count=578,
            conversion_from_start_percent=46.3,
            dropoff_from_previous_percent=31.9,
            avg_days_to_this_stage=6.4,
        ),
        FunnelStage(
            stage="Interview",
            count=206,
            conversion_from_start_percent=16.5,
            dropoff_from_previous_percent=64.4,
            avg_days_to_this_stage=12.0,
        ),
        FunnelStage(
            stage="Offer",
            count=52,
            conversion_from_start_percent=4.2,
            dropoff_from_previous_percent=74.8,
            avg_days_to_this_stage=18.8,
        ),
        FunnelStage(
            stage="Placed",
            count=44,
            conversion_from_start_percent=3.5,
            dropoff_from_previous_percent=15.4,
            avg_days_to_this_stage=22.0,
        ),
    ]

    # Monthly trends
    monthly_trends = []
    for i in range(5, -1, -1):
        month_date = datetime.now() - timedelta(days=30 * i)
        monthly_trends.append(
            MonthFunnelTrend(
                month=month_date.strftime("%Y-%m"),
                sourced_count=200 + (i * 10),
                screening_count=int((200 + (i * 10)) * 0.68),
                submitted_count=int((200 + (i * 10)) * 0.46),
                interviewed_count=int((200 + (i * 10)) * 0.17),
                offered_count=int((200 + (i * 10)) * 0.04),
                placed_count=int((200 + (i * 10)) * 0.035),
            )
        )

    return ConversionFunnelReport(
        overall_funnel=overall_funnel,
        overall_conversion_rate=3.5,
        by_client=[
            ClientFunnelBreakdown(
                client_name="TechCorp Industries",
                stages=overall_funnel,
                overall_conversion_percent=4.2,
            ),
            ClientFunnelBreakdown(
                client_name="HealthConnect Solutions",
                stages=overall_funnel,
                overall_conversion_percent=5.1,
            ),
        ],
        by_supplier=[
            SupplierFunnelBreakdown(
                supplier_name="Elite Search Partners",
                stages=overall_funnel,
                overall_conversion_percent=4.8,
            ),
            SupplierFunnelBreakdown(
                supplier_name="TechTalent Recruiters",
                stages=overall_funnel,
                overall_conversion_percent=4.1,
            ),
        ],
        month_trends=monthly_trends,
        report_period=f"{start.date()} to {end.date()}",
        generated_at=datetime.now(),
    )


logger.info("Aggregate Reports API router initialized with 12 endpoints")
