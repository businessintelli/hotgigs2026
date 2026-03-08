"""Reporting & Analytics API endpoints.

Provides platform-wide metrics, recruitment funnel analysis, supplier performance,
financial summary, compliance health, SLA performance, and detailed analytics reports.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from api.dependencies import get_db, get_current_user
from models.user import User
from schemas.reports import (
    RecruiterLeaderboardResponse,
    RecruiterLeaderboardItem,
    SourceAttributionResponse,
    SourceAttributionItem,
    CostAnalyticsResponse,
    CostByClient,
    CostByDepartment,
    CostTrendMonth,
    SkillMargin,
    DiversityAnalyticsResponse,
    DiversityByStage,
    HiringRateByCategory,
    InterviewToOfferRatio,
    SourceDiversityBreakdown,
    TimeAnalyticsResponse,
    TimeToFillByPriority,
    TimeToFillBySkill,
    TimeToFillByClient,
    TimeToFillTrendMonth,
    BottleneckAnalysis,
    PipelineAgingResponse,
    AgingByStage,
    StaleRequirement,
    AtRiskCandidate,
    MSPExecutiveSummaryResponse,
    RevenueByClient,
    FillRateBySupplier,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["Reports & Analytics"])


# ── Helper Types ──
class KPIMetric:
    """Simple KPI metric container."""
    def __init__(self, value: Any, label: str, unit: str = ""):
        self.value = value
        self.label = label
        self.unit = unit


def get_last_6_months() -> List[Dict[str, Any]]:
    """Generate last 6 months of data for trending."""
    months = []
    now = datetime.utcnow()
    for i in range(6):
        month_date = now - timedelta(days=30 * i)
        months.insert(0, {
            "month": month_date.strftime("%Y-%m"),
            "value": 0
        })
    return months


def _fallback_overview_metrics() -> Dict[str, Any]:
    """Fallback mock data for overview metrics."""
    return {
        "total_candidates": 1247,
        "active_requirements": 89,
        "placements_mtd": 34,
        "revenue_mtd": 425000.00,
        "candidates_trend": get_last_6_months(),
        "placements_trend": [
            {"month": "2025-09", "value": 28},
            {"month": "2025-10", "value": 31},
            {"month": "2025-11", "value": 29},
            {"month": "2025-12", "value": 36},
            {"month": "2026-01", "value": 32},
            {"month": "2026-02", "value": 34},
        ],
    }


def _fallback_recruitment_funnel() -> Dict[str, Any]:
    """Fallback mock data for recruitment funnel."""
    return {
        "stages": [
            {"stage": "Sourced", "count": 450, "conversion_percent": 100.0},
            {"stage": "Screened", "count": 320, "conversion_percent": 71.1},
            {"stage": "Submitted", "count": 195, "conversion_percent": 60.9},
            {"stage": "Interviewed", "count": 98, "conversion_percent": 50.3},
            {"stage": "Offered", "count": 52, "conversion_percent": 53.1},
            {"stage": "Placed", "count": 34, "conversion_percent": 65.4},
        ],
        "total_sourced": 450,
        "total_placed": 34,
        "overall_conversion_percent": 7.6,
    }


def _fallback_supplier_scorecard() -> Dict[str, Any]:
    """Fallback mock data for supplier scorecard."""
    return {
        "suppliers": [
            {
                "rank": 1,
                "name": "StaffPro Solutions",
                "fill_rate": 92.5,
                "avg_time_to_fill_days": 8.2,
                "quality_score": 94,
                "compliance_score": 98,
                "active_placements": 23,
                "composite_score": 94.2,
            },
            {
                "rank": 2,
                "name": "TalentAcq Inc",
                "fill_rate": 87.3,
                "avg_time_to_fill_days": 10.5,
                "quality_score": 88,
                "compliance_score": 95,
                "active_placements": 18,
                "composite_score": 89.7,
            },
            {
                "rank": 3,
                "name": "Global Staffing Network",
                "fill_rate": 81.2,
                "avg_time_to_fill_days": 12.1,
                "quality_score": 82,
                "compliance_score": 90,
                "active_placements": 15,
                "composite_score": 83.6,
            },
        ]
    }


def _fallback_financial_summary() -> Dict[str, Any]:
    """Fallback mock data for financial summary."""
    return {
        "total_billed": 1850000.00,
        "total_paid": 1620000.00,
        "gross_margin": 230000.00,
        "margin_percent": 12.4,
        "by_client": [
            {
                "client_name": "TechCorp Inc",
                "billed": 850000.00,
                "paid": 750000.00,
                "margin": 100000.00,
                "placements": 45,
            },
            {
                "client_name": "FinServe Global",
                "billed": 620000.00,
                "paid": 550000.00,
                "margin": 70000.00,
                "placements": 32,
            },
            {
                "client_name": "HealthCare Plus",
                "billed": 380000.00,
                "paid": 320000.00,
                "margin": 60000.00,
                "placements": 24,
            },
        ],
        "monthly_trend": [
            {"month": "2025-09", "billed": 285000, "paid": 245000, "margin": 40000},
            {"month": "2025-10", "billed": 310000, "paid": 268000, "margin": 42000},
            {"month": "2025-11", "billed": 295000, "paid": 260000, "margin": 35000},
            {"month": "2025-12", "billed": 355000, "paid": 310000, "margin": 45000},
            {"month": "2026-01", "billed": 325000, "paid": 285000, "margin": 40000},
            {"month": "2026-02", "billed": 280000, "paid": 252000, "margin": 28000},
        ],
    }


def _fallback_compliance_summary() -> Dict[str, Any]:
    """Fallback mock data for compliance summary."""
    return {
        "overall_compliance_percent": 94.2,
        "by_type": [
            {"type": "Background Check", "count": 87, "passed": 82, "percent": 94.3},
            {"type": "Drug Screening", "count": 87, "passed": 86, "percent": 98.9},
            {"type": "NDA Signed", "count": 89, "passed": 88, "percent": 98.9},
            {"type": "Certifications", "count": 45, "passed": 42, "percent": 93.3},
        ],
        "expiring_items_count": 12,
        "high_risk_gaps": 3,
        "overall_risk_level": "Low",
    }


def _fallback_sla_performance() -> Dict[str, Any]:
    """Fallback mock data for SLA performance."""
    return {
        "overall_sla_score": 92.1,
        "metrics": [
            {"metric": "Response Time", "target": 24, "actual": 18.5, "score": 94.2},
            {"metric": "Fill Time", "target": 15, "actual": 13.2, "score": 92.0},
            {"metric": "Quality Score", "target": 85, "actual": 88.5, "score": 95.3},
            {"metric": "Acceptance Rate", "target": 75, "actual": 82.1, "score": 91.0},
        ],
        "breach_count_mtd": 2,
        "trend_direction": "up",
    }


def _fallback_recruiter_leaderboard() -> List[RecruiterLeaderboardItem]:
    """Mock data for recruiter leaderboard."""
    recruiters = [
        {
            "rank": 1,
            "recruiter_name": "Sarah Chen",
            "submissions_count": 127,
            "placements_count": 34,
            "conversion_rate": 26.8,
            "avg_time_to_fill_days": 9.2,
            "avg_match_score": 87.5,
            "revenue_generated": 425000.00,
            "composite_score": 92.3,
        },
        {
            "rank": 2,
            "recruiter_name": "Michael Torres",
            "submissions_count": 115,
            "placements_count": 29,
            "conversion_rate": 25.2,
            "avg_time_to_fill_days": 10.8,
            "avg_match_score": 84.2,
            "revenue_generated": 362500.00,
            "composite_score": 88.7,
        },
        {
            "rank": 3,
            "recruiter_name": "Jessica Lee",
            "submissions_count": 98,
            "placements_count": 24,
            "conversion_rate": 24.5,
            "avg_time_to_fill_days": 11.5,
            "avg_match_score": 82.8,
            "revenue_generated": 300000.00,
            "composite_score": 85.2,
        },
        {
            "rank": 4,
            "recruiter_name": "David Patel",
            "submissions_count": 87,
            "placements_count": 20,
            "conversion_rate": 23.0,
            "avg_time_to_fill_days": 12.3,
            "avg_match_score": 81.5,
            "revenue_generated": 250000.00,
            "composite_score": 82.1,
        },
        {
            "rank": 5,
            "recruiter_name": "Emma Rodriguez",
            "submissions_count": 76,
            "placements_count": 17,
            "conversion_rate": 22.4,
            "avg_time_to_fill_days": 13.1,
            "avg_match_score": 79.3,
            "revenue_generated": 212500.00,
            "composite_score": 78.9,
        },
        {
            "rank": 6,
            "recruiter_name": "James Wilson",
            "submissions_count": 62,
            "placements_count": 13,
            "conversion_rate": 21.0,
            "avg_time_to_fill_days": 14.2,
            "avg_match_score": 77.8,
            "revenue_generated": 162500.00,
            "composite_score": 75.3,
        },
        {
            "rank": 7,
            "recruiter_name": "Lisa Kumar",
            "submissions_count": 51,
            "placements_count": 11,
            "conversion_rate": 21.6,
            "avg_time_to_fill_days": 13.8,
            "avg_match_score": 78.2,
            "revenue_generated": 137500.00,
            "composite_score": 74.2,
        },
        {
            "rank": 8,
            "recruiter_name": "Marcus Johnson",
            "submissions_count": 44,
            "placements_count": 8,
            "conversion_rate": 18.2,
            "avg_time_to_fill_days": 15.5,
            "avg_match_score": 75.1,
            "revenue_generated": 100000.00,
            "composite_score": 70.5,
        },
    ]
    return [RecruiterLeaderboardItem(**r) for r in recruiters]


def _fallback_source_attribution() -> List[SourceAttributionItem]:
    """Mock data for source attribution."""
    sources = [
        {
            "source_name": "LinkedIn",
            "candidates_sourced": 324,
            "candidates_placed": 87,
            "conversion_rate": 26.9,
            "avg_time_to_fill": 10.2,
            "avg_quality_score": 85.3,
            "cost_per_hire": 2450.00,
            "roi_score": 8.5,
        },
        {
            "source_name": "Indeed",
            "candidates_sourced": 218,
            "candidates_placed": 52,
            "conversion_rate": 23.9,
            "avg_time_to_fill": 12.5,
            "avg_quality_score": 82.1,
            "cost_per_hire": 1850.00,
            "roi_score": 7.2,
        },
        {
            "source_name": "Referral",
            "candidates_sourced": 156,
            "candidates_placed": 48,
            "conversion_rate": 30.8,
            "avg_time_to_fill": 8.7,
            "avg_quality_score": 88.7,
            "cost_per_hire": 500.00,
            "roi_score": 12.3,
        },
        {
            "source_name": "Job Board",
            "candidates_sourced": 142,
            "candidates_placed": 31,
            "conversion_rate": 21.8,
            "avg_time_to_fill": 13.2,
            "avg_quality_score": 79.5,
            "cost_per_hire": 3200.00,
            "roi_score": 5.8,
        },
        {
            "source_name": "Internal DB",
            "candidates_sourced": 128,
            "candidates_placed": 39,
            "conversion_rate": 30.5,
            "avg_time_to_fill": 7.5,
            "avg_quality_score": 87.2,
            "cost_per_hire": 200.00,
            "roi_score": 14.1,
        },
        {
            "source_name": "Career Page",
            "candidates_sourced": 95,
            "candidates_placed": 22,
            "conversion_rate": 23.2,
            "avg_time_to_fill": 11.8,
            "avg_quality_score": 81.4,
            "cost_per_hire": 150.00,
            "roi_score": 9.7,
        },
        {
            "source_name": "Agency",
            "candidates_sourced": 67,
            "candidates_placed": 18,
            "conversion_rate": 26.9,
            "avg_time_to_fill": 9.3,
            "avg_quality_score": 84.1,
            "cost_per_hire": 4500.00,
            "roi_score": 4.2,
        },
        {
            "source_name": "Event",
            "candidates_sourced": 32,
            "candidates_placed": 8,
            "conversion_rate": 25.0,
            "avg_time_to_fill": 10.6,
            "avg_quality_score": 83.5,
            "cost_per_hire": 6250.00,
            "roi_score": 2.9,
        },
    ]
    return [SourceAttributionItem(**s) for s in sources]


def _fallback_cost_analytics() -> Dict[str, Any]:
    """Mock data for cost analytics."""
    return {
        "overall_cost_per_hire": 2847.50,
        "avg_margin_percent": 38.5,
        "total_billing": 2850000.00,
        "total_cost": 1750000.00,
        "gross_profit": 1100000.00,
        "cost_by_client": [
            {
                "client_name": "TechCorp Inc",
                "total_cost": 520000.00,
                "total_billing": 950000.00,
                "placements": 45,
                "cost_per_placement": 11555.56,
            },
            {
                "client_name": "FinServe Global",
                "total_cost": 380000.00,
                "total_billing": 720000.00,
                "placements": 32,
                "cost_per_placement": 11875.00,
            },
            {
                "client_name": "HealthCare Plus",
                "total_cost": 280000.00,
                "total_billing": 520000.00,
                "placements": 24,
                "cost_per_placement": 11666.67,
            },
            {
                "client_name": "Enterprise Solutions",
                "total_cost": 310000.00,
                "total_billing": 450000.00,
                "placements": 18,
                "cost_per_placement": 17222.22,
            },
            {
                "client_name": "Retail Group Co",
                "total_cost": 260000.00,
                "total_billing": 210000.00,
                "placements": 16,
                "cost_per_placement": 16250.00,
            },
        ],
        "cost_by_department": [
            {
                "department": "Engineering",
                "total_cost": 620000.00,
                "total_billing": 1200000.00,
                "placements": 54,
                "cost_per_placement": 11481.48,
            },
            {
                "department": "Finance",
                "total_cost": 320000.00,
                "total_billing": 680000.00,
                "placements": 28,
                "cost_per_placement": 11428.57,
            },
            {
                "department": "Operations",
                "total_cost": 410000.00,
                "total_billing": 620000.00,
                "placements": 35,
                "cost_per_placement": 11714.29,
            },
            {
                "department": "Sales",
                "total_cost": 280000.00,
                "total_billing": 280000.00,
                "placements": 22,
                "cost_per_placement": 12727.27,
            },
            {
                "department": "HR & Admin",
                "total_cost": 120000.00,
                "total_billing": 70000.00,
                "placements": 10,
                "cost_per_placement": 12000.00,
            },
        ],
        "cost_trend": [
            {
                "month": "2025-09",
                "total_cost": 285000.00,
                "total_billing": 415000.00,
                "gross_profit": 130000.00,
                "margin_percent": 31.3,
            },
            {
                "month": "2025-10",
                "total_cost": 310000.00,
                "total_billing": 480000.00,
                "gross_profit": 170000.00,
                "margin_percent": 35.4,
            },
            {
                "month": "2025-11",
                "total_cost": 295000.00,
                "total_billing": 440000.00,
                "gross_profit": 145000.00,
                "margin_percent": 33.0,
            },
            {
                "month": "2025-12",
                "total_cost": 320000.00,
                "total_billing": 510000.00,
                "gross_profit": 190000.00,
                "margin_percent": 37.3,
            },
            {
                "month": "2026-01",
                "total_cost": 340000.00,
                "total_billing": 525000.00,
                "gross_profit": 185000.00,
                "margin_percent": 35.2,
            },
            {
                "month": "2026-02",
                "total_cost": 300000.00,
                "total_billing": 480000.00,
                "gross_profit": 180000.00,
                "margin_percent": 37.5,
            },
        ],
        "margin_by_skill": [
            {
                "skill_category": "Cloud Architecture",
                "avg_margin_percent": 42.5,
                "placements": 28,
                "total_billing": 580000.00,
            },
            {
                "skill_category": "Data Science",
                "avg_margin_percent": 40.2,
                "placements": 22,
                "total_billing": 520000.00,
            },
            {
                "skill_category": "Full-Stack Development",
                "avg_margin_percent": 38.1,
                "placements": 45,
                "total_billing": 620000.00,
            },
            {
                "skill_category": "DevOps Engineering",
                "avg_margin_percent": 39.8,
                "placements": 18,
                "total_billing": 380000.00,
            },
            {
                "skill_category": "Financial Analysis",
                "avg_margin_percent": 35.2,
                "placements": 32,
                "total_billing": 450000.00,
            },
        ],
    }


def _fallback_diversity_analytics() -> Dict[str, Any]:
    """Mock data for diversity analytics (anonymized)."""
    return {
        "note": "All data anonymized and aggregated. No individual identification.",
        "pipeline_diversity": [
            {
                "stage": "Sourced",
                "total_count": 450,
                "diverse_count": 198,
                "diverse_percent": 44.0,
            },
            {
                "stage": "Screened",
                "total_count": 320,
                "diverse_count": 147,
                "diverse_percent": 45.9,
            },
            {
                "stage": "Submitted",
                "total_count": 195,
                "diverse_count": 91,
                "diverse_percent": 46.7,
            },
            {
                "stage": "Interviewed",
                "total_count": 98,
                "diverse_count": 48,
                "diverse_percent": 49.0,
            },
            {
                "stage": "Offered",
                "total_count": 52,
                "diverse_count": 26,
                "diverse_percent": 50.0,
            },
            {
                "stage": "Placed",
                "total_count": 34,
                "diverse_count": 17,
                "diverse_percent": 50.0,
            },
        ],
        "hiring_rate_by_category": [
            {
                "category": "Women",
                "pipeline_representation": 42.5,
                "hired_representation": 48.2,
                "hiring_rate": 5.7,
            },
            {
                "category": "Underrepresented Minorities",
                "pipeline_representation": 28.3,
                "hired_representation": 32.1,
                "hiring_rate": 3.8,
            },
            {
                "category": "Veterans",
                "pipeline_representation": 8.2,
                "hired_representation": 9.5,
                "hiring_rate": 1.3,
            },
            {
                "category": "Persons with Disabilities",
                "pipeline_representation": 6.1,
                "hired_representation": 7.2,
                "hiring_rate": 1.1,
            },
        ],
        "interview_to_offer_ratio": [
            {
                "category": "Women",
                "interviews": 78,
                "offers": 42,
                "conversion_rate": 53.8,
            },
            {
                "category": "Underrepresented Minorities",
                "interviews": 52,
                "offers": 26,
                "conversion_rate": 50.0,
            },
            {
                "category": "Veterans",
                "interviews": 12,
                "offers": 6,
                "conversion_rate": 50.0,
            },
            {
                "category": "Persons with Disabilities",
                "interviews": 8,
                "offers": 4,
                "conversion_rate": 50.0,
            },
        ],
        "source_diversity": [
            {
                "source": "LinkedIn",
                "total_candidates": 324,
                "diverse_candidates": 162,
                "diverse_percent": 50.0,
            },
            {
                "source": "Referral",
                "total_candidates": 156,
                "diverse_candidates": 56,
                "diverse_percent": 35.9,
            },
            {
                "source": "Indeed",
                "total_candidates": 218,
                "diverse_candidates": 110,
                "diverse_percent": 50.5,
            },
            {
                "source": "Internal DB",
                "total_candidates": 128,
                "diverse_candidates": 64,
                "diverse_percent": 50.0,
            },
            {
                "source": "Job Board",
                "total_candidates": 142,
                "diverse_candidates": 56,
                "diverse_percent": 39.4,
            },
        ],
    }


def _fallback_time_analytics() -> Dict[str, Any]:
    """Mock data for time-to-fill analytics."""
    return {
        "overall_avg_ttf_days": 18.5,
        "ttf_by_priority": [
            {
                "priority": "Urgent",
                "avg_days": 12.3,
                "min_days": 2,
                "max_days": 18,
                "count": 42,
            },
            {
                "priority": "High",
                "avg_days": 15.8,
                "min_days": 5,
                "max_days": 28,
                "count": 87,
            },
            {
                "priority": "Normal",
                "avg_days": 20.2,
                "min_days": 8,
                "max_days": 35,
                "count": 156,
            },
            {
                "priority": "Low",
                "avg_days": 28.5,
                "min_days": 15,
                "max_days": 45,
                "count": 65,
            },
        ],
        "ttf_by_skill_category": [
            {
                "skill_category": "Cloud Architecture",
                "avg_days": 14.2,
                "count": 28,
            },
            {
                "skill_category": "Data Science",
                "avg_days": 16.8,
                "count": 22,
            },
            {
                "skill_category": "Full-Stack Development",
                "avg_days": 18.5,
                "count": 45,
            },
            {
                "skill_category": "DevOps Engineering",
                "avg_days": 15.3,
                "count": 18,
            },
            {
                "skill_category": "Financial Analysis",
                "avg_days": 22.1,
                "count": 32,
            },
            {
                "skill_category": "Nursing",
                "avg_days": 24.7,
                "count": 27,
            },
        ],
        "ttf_by_client": [
            {
                "client_name": "TechCorp Inc",
                "avg_days": 13.2,
                "count": 45,
            },
            {
                "client_name": "FinServe Global",
                "avg_days": 16.8,
                "count": 32,
            },
            {
                "client_name": "HealthCare Plus",
                "avg_days": 25.3,
                "count": 24,
            },
            {
                "client_name": "Enterprise Solutions",
                "avg_days": 18.5,
                "count": 18,
            },
            {
                "client_name": "Retail Group Co",
                "avg_days": 20.1,
                "count": 16,
            },
        ],
        "ttf_trend_monthly": [
            {
                "month": "2025-09",
                "avg_days": 22.5,
                "count": 28,
            },
            {
                "month": "2025-10",
                "avg_days": 20.2,
                "count": 31,
            },
            {
                "month": "2025-11",
                "avg_days": 19.8,
                "count": 29,
            },
            {
                "month": "2025-12",
                "avg_days": 18.1,
                "count": 36,
            },
            {
                "month": "2026-01",
                "avg_days": 17.5,
                "count": 32,
            },
            {
                "month": "2026-02",
                "avg_days": 16.8,
                "count": 34,
            },
        ],
        "bottleneck_analysis": [
            {
                "stage": "Sourced",
                "avg_days_in_stage": 1.2,
                "total_candidates": 450,
                "candidates_stuck_7plus_days": 8,
            },
            {
                "stage": "Screened",
                "avg_days_in_stage": 2.5,
                "total_candidates": 320,
                "candidates_stuck_7plus_days": 12,
            },
            {
                "stage": "Submitted",
                "avg_days_in_stage": 4.2,
                "total_candidates": 195,
                "candidates_stuck_7plus_days": 28,
            },
            {
                "stage": "Interviewed",
                "avg_days_in_stage": 5.8,
                "total_candidates": 98,
                "candidates_stuck_7plus_days": 32,
            },
            {
                "stage": "Offered",
                "avg_days_in_stage": 3.2,
                "total_candidates": 52,
                "candidates_stuck_7plus_days": 8,
            },
            {
                "stage": "Placed",
                "avg_days_in_stage": 1.6,
                "total_candidates": 34,
                "candidates_stuck_7plus_days": 2,
            },
        ],
    }


def _fallback_pipeline_aging() -> Dict[str, Any]:
    """Mock data for pipeline aging report."""
    return {
        "aging_by_stage": [
            {
                "stage": "Sourced",
                "total_candidates": 450,
                "aging_7_plus_days": 24,
                "aging_14_plus_days": 8,
                "aging_30_plus_days": 2,
            },
            {
                "stage": "Screened",
                "total_candidates": 320,
                "aging_7_plus_days": 45,
                "aging_14_plus_days": 18,
                "aging_30_plus_days": 5,
            },
            {
                "stage": "Submitted",
                "total_candidates": 195,
                "aging_7_plus_days": 78,
                "aging_14_plus_days": 42,
                "aging_30_plus_days": 12,
            },
            {
                "stage": "Interviewed",
                "total_candidates": 98,
                "aging_7_plus_days": 62,
                "aging_14_plus_days": 38,
                "aging_30_plus_days": 15,
            },
            {
                "stage": "Offered",
                "total_candidates": 52,
                "aging_7_plus_days": 18,
                "aging_14_plus_days": 8,
                "aging_30_plus_days": 2,
            },
        ],
        "stale_requirements": [
            {
                "requirement_id": "REQ-2025-001",
                "requisition_title": "Senior Backend Engineer",
                "open_days": 62,
                "submissions_count": 2,
                "client_name": "TechCorp Inc",
            },
            {
                "requirement_id": "REQ-2025-018",
                "requisition_title": "Data Analyst",
                "open_days": 45,
                "submissions_count": 1,
                "client_name": "FinServe Global",
            },
            {
                "requirement_id": "REQ-2025-032",
                "requisition_title": "Network Administrator",
                "open_days": 38,
                "submissions_count": 2,
                "client_name": "Enterprise Solutions",
            },
        ],
        "at_risk_candidates": [
            {
                "candidate_id": "CAN-5428",
                "candidate_name": "Alex M.",
                "current_stage": "Submitted",
                "days_inactive": 22,
                "requirement": "Senior Backend Engineer",
            },
            {
                "candidate_id": "CAN-5521",
                "candidate_name": "Taylor K.",
                "current_stage": "Interviewed",
                "days_inactive": 18,
                "requirement": "DevOps Engineer",
            },
            {
                "candidate_id": "CAN-5634",
                "candidate_name": "Morgan L.",
                "current_stage": "Submitted",
                "days_inactive": 25,
                "requirement": "Data Scientist",
            },
            {
                "candidate_id": "CAN-5701",
                "candidate_name": "Jordan P.",
                "current_stage": "Screening",
                "days_inactive": 19,
                "requirement": "Solutions Architect",
            },
        ],
    }


def _fallback_msp_executive_summary() -> Dict[str, Any]:
    """Mock data for MSP executive summary."""
    return {
        "total_active_clients": 24,
        "total_active_suppliers": 47,
        "total_active_placements": 156,
        "revenue_by_client": [
            {
                "rank": 1,
                "client_name": "TechCorp Inc",
                "revenue": 950000.00,
                "placements": 45,
                "margin_percent": 38.2,
            },
            {
                "rank": 2,
                "client_name": "FinServe Global",
                "revenue": 720000.00,
                "placements": 32,
                "margin_percent": 36.1,
            },
            {
                "rank": 3,
                "client_name": "HealthCare Plus",
                "revenue": 520000.00,
                "placements": 24,
                "margin_percent": 46.2,
            },
            {
                "rank": 4,
                "client_name": "Enterprise Solutions",
                "revenue": 450000.00,
                "placements": 18,
                "margin_percent": 31.1,
            },
            {
                "rank": 5,
                "client_name": "Retail Group Co",
                "revenue": 210000.00,
                "placements": 16,
                "margin_percent": 23.8,
            },
        ],
        "fill_rate_by_supplier": [
            {
                "rank": 1,
                "supplier_name": "StaffPro Solutions",
                "fill_rate": 92.5,
                "placements": 23,
                "avg_quality_score": 94.0,
            },
            {
                "rank": 2,
                "supplier_name": "TalentAcq Inc",
                "fill_rate": 87.3,
                "placements": 18,
                "avg_quality_score": 88.0,
            },
            {
                "rank": 3,
                "supplier_name": "Global Staffing Network",
                "fill_rate": 81.2,
                "placements": 15,
                "avg_quality_score": 82.0,
            },
            {
                "rank": 4,
                "supplier_name": "TopTalent Recruiters",
                "fill_rate": 78.5,
                "placements": 12,
                "avg_quality_score": 80.5,
            },
            {
                "rank": 5,
                "supplier_name": "ProSearch Partners",
                "fill_rate": 75.3,
                "placements": 10,
                "avg_quality_score": 78.2,
            },
        ],
        "sla_compliance_rate": 94.2,
        "compliance_overall_score": 92.8,
        "month_over_month_growth": 8.5,
        "projected_quarterly_revenue": 2850000.00,
    }


@router.get("/overview")
async def get_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get platform-wide overview metrics.

    Returns:
        - Total candidates, active requirements, placements, revenue
        - Month-over-month trends (last 6 months)
    """
    try:
        # Try to query real data from DB
        # For now, fallback to mock data as tables may be empty
        data = _fallback_overview_metrics()

        return {
            "status": "success",
            "data": {
                "total_candidates": data["total_candidates"],
                "active_requirements": data["active_requirements"],
                "placements_mtd": data["placements_mtd"],
                "revenue_mtd": data["revenue_mtd"],
                "candidates_trend": data["candidates_trend"],
                "placements_trend": data["placements_trend"],
                "generated_at": datetime.utcnow().isoformat(),
            }
        }
    except Exception as e:
        logger.error(f"Error getting overview metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch overview metrics",
        )


@router.get("/recruitment-funnel")
async def get_recruitment_funnel(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get recruitment pipeline conversion rates.

    Returns:
        - Stages: Sourced → Screened → Submitted → Interviewed → Offered → Placed
        - Count and conversion % at each stage
    """
    try:
        data = _fallback_recruitment_funnel()

        return {
            "status": "success",
            "data": {
                "stages": data["stages"],
                "total_sourced": data["total_sourced"],
                "total_placed": data["total_placed"],
                "overall_conversion_percent": data["overall_conversion_percent"],
                "generated_at": datetime.utcnow().isoformat(),
            }
        }
    except Exception as e:
        logger.error(f"Error getting recruitment funnel: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch recruitment funnel",
        )


@router.get("/supplier-scorecard")
async def get_supplier_scorecard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get supplier performance metrics.

    Returns:
        - Per-supplier: fill_rate, avg_time_to_fill, quality_score, compliance_score, active_placements
        - Ranking by composite score
    """
    try:
        data = _fallback_supplier_scorecard()

        return {
            "status": "success",
            "data": {
                "suppliers": data["suppliers"],
                "generated_at": datetime.utcnow().isoformat(),
            }
        }
    except Exception as e:
        logger.error(f"Error getting supplier scorecard: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch supplier scorecard",
        )


@router.get("/financial-summary")
async def get_financial_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get revenue and cost analysis.

    Returns:
        - Total billed, total paid, gross margin, margin %
        - By client breakdown
        - By month trend (last 6 months)
    """
    try:
        data = _fallback_financial_summary()

        return {
            "status": "success",
            "data": {
                "total_billed": data["total_billed"],
                "total_paid": data["total_paid"],
                "gross_margin": data["gross_margin"],
                "margin_percent": data["margin_percent"],
                "by_client": data["by_client"],
                "monthly_trend": data["monthly_trend"],
                "generated_at": datetime.utcnow().isoformat(),
            }
        }
    except Exception as e:
        logger.error(f"Error getting financial summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch financial summary",
        )


@router.get("/compliance-summary")
async def get_compliance_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get compliance health check.

    Returns:
        - Overall compliance rate %
        - By requirement type breakdown
        - Expiring items count
        - High-risk gaps
    """
    try:
        data = _fallback_compliance_summary()

        return {
            "status": "success",
            "data": {
                "overall_compliance_percent": data["overall_compliance_percent"],
                "by_type": data["by_type"],
                "expiring_items_count": data["expiring_items_count"],
                "high_risk_gaps": data["high_risk_gaps"],
                "overall_risk_level": data["overall_risk_level"],
                "generated_at": datetime.utcnow().isoformat(),
            }
        }
    except Exception as e:
        logger.error(f"Error getting compliance summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch compliance summary",
        )


@router.get("/sla-performance")
async def get_sla_performance(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get SLA adherence metrics.

    Returns:
        - Overall SLA score
        - By metric type (response_time, fill_time, quality, etc.)
        - Breach count and trend
    """
    try:
        data = _fallback_sla_performance()

        return {
            "status": "success",
            "data": {
                "overall_sla_score": data["overall_sla_score"],
                "metrics": data["metrics"],
                "breach_count_mtd": data["breach_count_mtd"],
                "trend_direction": data["trend_direction"],
                "generated_at": datetime.utcnow().isoformat(),
            }
        }
    except Exception as e:
        logger.error(f"Error getting SLA performance: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch SLA performance",
        )


@router.get("/recruiter-leaderboard", response_model=RecruiterLeaderboardResponse)
async def get_recruiter_leaderboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get recruiter performance ranking.

    Returns:
        - Ranked list of recruiters by composite score
        - Each: recruiter_name, submissions, placements, conversion_rate, time_to_fill, match_score, revenue, rank
        - Composite score = placements (40%) + conversion (30%) + speed (20%) + quality (10%)
    """
    try:
        recruiters = _fallback_recruiter_leaderboard()

        return RecruiterLeaderboardResponse(
            recruiters=recruiters,
            total_recruiters=len(recruiters),
            generated_at=datetime.utcnow(),
        )
    except Exception as e:
        logger.error(f"Error getting recruiter leaderboard: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch recruiter leaderboard",
        )


@router.get("/source-attribution", response_model=SourceAttributionResponse)
async def get_source_attribution(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get recruitment source effectiveness.

    Returns:
        - List of sources (LinkedIn, Indeed, Referral, Job Board, Internal DB, Career Page, Agency, Event)
        - Each: candidates_sourced, candidates_placed, conversion_rate, time_to_fill, quality_score, cost_per_hire, roi_score
    """
    try:
        sources = _fallback_source_attribution()
        total_sourced = sum(s.candidates_sourced for s in sources)
        total_placed = sum(s.candidates_placed for s in sources)
        overall_conversion = (total_placed / total_sourced * 100) if total_sourced > 0 else 0

        return SourceAttributionResponse(
            sources=sources,
            total_candidates_sourced=total_sourced,
            total_candidates_placed=total_placed,
            overall_conversion_rate=overall_conversion,
            generated_at=datetime.utcnow(),
        )
    except Exception as e:
        logger.error(f"Error getting source attribution: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch source attribution",
        )


@router.get("/cost-analytics", response_model=CostAnalyticsResponse)
async def get_cost_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get cost per hire and financial analysis.

    Returns:
        - Overall cost per hire, avg margin %, total billing, total cost, gross profit
        - Cost breakdown by client and department
        - Cost trend (last 6 months) and margin analysis by skill
    """
    try:
        data = _fallback_cost_analytics()

        cost_by_client = [CostByClient(**item) for item in data["cost_by_client"]]
        cost_by_dept = [CostByDepartment(**item) for item in data["cost_by_department"]]
        cost_trend = [CostTrendMonth(**item) for item in data["cost_trend"]]
        margin_by_skill = [SkillMargin(**item) for item in data["margin_by_skill"]]

        return CostAnalyticsResponse(
            overall_cost_per_hire=data["overall_cost_per_hire"],
            avg_margin_percent=data["avg_margin_percent"],
            total_billing=data["total_billing"],
            total_cost=data["total_cost"],
            gross_profit=data["gross_profit"],
            cost_by_client=cost_by_client,
            cost_by_department=cost_by_dept,
            cost_trend=cost_trend,
            margin_by_skill=margin_by_skill,
            generated_at=datetime.utcnow(),
        )
    except Exception as e:
        logger.error(f"Error getting cost analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch cost analytics",
        )


@router.get("/diversity-analytics", response_model=DiversityAnalyticsResponse)
async def get_diversity_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get diversity metrics (anonymized and aggregated).

    Returns:
        - Pipeline diversity by stage
        - Hiring rate by category
        - Interview to offer conversion by category
        - Source diversity breakdown
        - Note: All data anonymized, no individual identification
    """
    try:
        data = _fallback_diversity_analytics()

        pipeline_diversity = [DiversityByStage(**item) for item in data["pipeline_diversity"]]
        hiring_rates = [HiringRateByCategory(**item) for item in data["hiring_rate_by_category"]]
        interview_to_offer = [InterviewToOfferRatio(**item) for item in data["interview_to_offer_ratio"]]
        source_diversity = [SourceDiversityBreakdown(**item) for item in data["source_diversity"]]

        return DiversityAnalyticsResponse(
            pipeline_diversity=pipeline_diversity,
            hiring_rate_by_category=hiring_rates,
            interview_to_offer_ratio=interview_to_offer,
            source_diversity=source_diversity,
            generated_at=datetime.utcnow(),
        )
    except Exception as e:
        logger.error(f"Error getting diversity analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch diversity analytics",
        )


@router.get("/time-analytics", response_model=TimeAnalyticsResponse)
async def get_time_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get time-to-fill deep dive analytics.

    Returns:
        - Overall average time to fill
        - Time by priority (urgent/high/normal/low)
        - Time by skill category and client
        - Monthly trend (last 6 months)
        - Bottleneck analysis (which stage takes longest)
    """
    try:
        data = _fallback_time_analytics()

        ttf_by_priority = [TimeToFillByPriority(**item) for item in data["ttf_by_priority"]]
        ttf_by_skill = [TimeToFillBySkill(**item) for item in data["ttf_by_skill_category"]]
        ttf_by_client = [TimeToFillByClient(**item) for item in data["ttf_by_client"]]
        ttf_trend = [TimeToFillTrendMonth(**item) for item in data["ttf_trend_monthly"]]
        bottlenecks = [BottleneckAnalysis(**item) for item in data["bottleneck_analysis"]]

        return TimeAnalyticsResponse(
            overall_avg_ttf_days=data["overall_avg_ttf_days"],
            ttf_by_priority=ttf_by_priority,
            ttf_by_skill_category=ttf_by_skill,
            ttf_by_client=ttf_by_client,
            ttf_trend_monthly=ttf_trend,
            bottleneck_analysis=bottlenecks,
            generated_at=datetime.utcnow(),
        )
    except Exception as e:
        logger.error(f"Error getting time analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch time analytics",
        )


@router.get("/pipeline-aging", response_model=PipelineAgingResponse)
async def get_pipeline_aging(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get stale requisitions and candidates analysis.

    Returns:
        - Aging by stage: candidates stuck >7, >14, >30 days per stage
        - Stale requirements: open >30 days with <3 submissions
        - At-risk candidates: no activity >14 days
    """
    try:
        data = _fallback_pipeline_aging()

        aging_by_stage = [AgingByStage(**item) for item in data["aging_by_stage"]]
        stale_reqs = [StaleRequirement(**item) for item in data["stale_requirements"]]
        at_risk = [AtRiskCandidate(**item) for item in data["at_risk_candidates"]]

        return PipelineAgingResponse(
            aging_by_stage=aging_by_stage,
            stale_requirements=stale_reqs,
            at_risk_candidates=at_risk,
            generated_at=datetime.utcnow(),
        )
    except Exception as e:
        logger.error(f"Error getting pipeline aging: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch pipeline aging",
        )


@router.get("/msp-executive", response_model=MSPExecutiveSummaryResponse)
async def get_msp_executive_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get MSP executive summary report.

    Returns:
        - Total active clients, suppliers, placements
        - Revenue by client (top 5) and fill rate by supplier (top 5)
        - SLA compliance rate and overall compliance score
        - Month-over-month growth and projected quarterly revenue
    """
    try:
        data = _fallback_msp_executive_summary()

        revenue_by_client = [RevenueByClient(**item) for item in data["revenue_by_client"]]
        fill_rate_by_supplier = [FillRateBySupplier(**item) for item in data["fill_rate_by_supplier"]]

        return MSPExecutiveSummaryResponse(
            total_active_clients=data["total_active_clients"],
            total_active_suppliers=data["total_active_suppliers"],
            total_active_placements=data["total_active_placements"],
            revenue_by_client=revenue_by_client,
            fill_rate_by_supplier=fill_rate_by_supplier,
            sla_compliance_rate=data["sla_compliance_rate"],
            compliance_overall_score=data["compliance_overall_score"],
            month_over_month_growth=data["month_over_month_growth"],
            projected_quarterly_revenue=data["projected_quarterly_revenue"],
            generated_at=datetime.utcnow(),
        )
    except Exception as e:
        logger.error(f"Error getting MSP executive summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch MSP executive summary",
        )
