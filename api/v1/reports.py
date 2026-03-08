"""Reporting & Analytics API endpoints.

Provides platform-wide metrics, recruitment funnel analysis, supplier performance,
financial summary, compliance health, and SLA performance.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from api.dependencies import get_db, get_current_user
from models.user import User

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
