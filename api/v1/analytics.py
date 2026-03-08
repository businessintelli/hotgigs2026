"""Advanced Analytics API endpoints.

Provides AI-powered analytics including candidate scorecards, applicant tracking,
skill analysis, match insights, recruiter performance, predictions, and comparisons.
"""

import logging
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.analytics import (
    CandidateScorecardResponse, StrongSkill, WeakSkill, RecommendedJob,
    ApplicantTrackingResponse, PipelineStageInfo, TopCandidateATS, ConversionRate,
    SkillAnalysisResponse, SkillStrength, SkillGap, DevelopmentRecommendation,
    MatchInsightsResponse, ScoreDistributionBucket, BestCandidate, DimensionAverage,
    RecruiterPerformanceResponse, MonthlyStat, TopMetric,
    PredictionsDashboardResponse, WorkforceForecast, SupplierPrediction, SkillShortageAlert,
    MatchComparisonResponse, CandidateComparisonRow, DimensionWinner,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["Advanced Analytics"])


# ── Helper Functions for Mock Data ──
def _get_mock_skills_for_candidate(candidate_id: int) -> tuple:
    """Generate mock skills for a candidate."""
    base_skills = {
        1: ["Python", "Django", "REST API", "Docker", "PostgreSQL"],
        2: ["JavaScript", "React", "Node.js", "TypeScript", "MongoDB"],
        3: ["Java", "Spring Boot", "Microservices", "AWS", "Kubernetes"],
        4: ["C#", ".NET", "Azure", "SQL Server"],
        5: ["Go", "Rust", "gRPC", "Protocol Buffers"],
    }
    skills = base_skills.get(candidate_id % 5 or 5, ["Python", "JavaScript", "SQL"])

    strong = [
        StrongSkill(skill=skills[0], proficiency=(80 + candidate_id % 20), market_demand="HIGH"),
        StrongSkill(skill=skills[1], proficiency=(70 + candidate_id % 20), market_demand="MEDIUM"),
    ]

    weak = [
        WeakSkill(skill="Kubernetes", importance_for_role="IMPORTANT"),
        WeakSkill(skill="Advanced ML", importance_for_role="NICE_TO_HAVE"),
    ]

    return strong, weak, skills


def _get_mock_recommended_jobs(candidate_id: int, limit: int = 5) -> List[RecommendedJob]:
    """Generate mock recommended jobs."""
    return [
        RecommendedJob(
            requirement_id=i,
            title=f"Senior {['Backend', 'Frontend', 'Full Stack', 'DevOps', 'Data Engineer'][i % 5]} Engineer",
            match_score=float(90 - i * 8),
            skill_match=float(88 - i * 6),
            experience_match=float(92 - i * 9),
        )
        for i in range(1, limit + 1)
    ]


def _get_match_strength(score: float) -> str:
    """Determine match strength from score."""
    if score >= 85:
        return "Strong Match"
    elif score >= 70:
        return "Good Match"
    elif score >= 55:
        return "Moderate Match"
    else:
        return "Weak Match"


@router.get(
    "/candidate/{candidate_id}/scorecard",
    response_model=CandidateScorecardResponse,
    status_code=status.HTTP_200_OK,
    summary="Get candidate scoring breakdown",
    description="Return full candidate scoring breakdown with skill analysis and recommended jobs.",
)
async def get_candidate_scorecard(
    candidate_id: int,
    session: AsyncSession = Depends(get_db),
) -> CandidateScorecardResponse:
    """
    Get full candidate scoring breakdown.

    Args:
        candidate_id: Candidate ID
        session: Database session

    Returns:
        Comprehensive candidate scorecard with all dimensions and analysis
    """
    try:
        # Mock data
        strong_skills, weak_skills, all_skills = _get_mock_skills_for_candidate(candidate_id)
        recommended = _get_mock_recommended_jobs(candidate_id)

        overall = float(75 + (candidate_id % 20))

        return CandidateScorecardResponse(
            candidate_id=candidate_id,
            candidate_name=f"Candidate {candidate_id}",
            candidate_email=f"candidate{candidate_id}@example.com",
            overall_score=overall,
            skill_score=float(78 + candidate_id % 15),
            experience_score=float(72 + candidate_id % 18),
            education_score=float(82 + candidate_id % 12),
            location_score=float(80 + candidate_id % 15),
            rate_score=float(75 + candidate_id % 20),
            availability_score=float(85 + candidate_id % 10),
            culture_score=float(70 + candidate_id % 25),
            strong_skills=strong_skills,
            weak_skills=weak_skills,
            missing_skills=["Kubernetes", "Advanced ML", "GraphQL"],
            standout_qualities=["Quick learner", "Excellent communication", "Problem solver"],
            recommended_jobs=recommended,
            match_strength=_get_match_strength(overall),
            generated_at=datetime.utcnow(),
        )

    except Exception as e:
        logger.error(f"Error getting candidate scorecard: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/requirement/{requirement_id}/applicant-tracking",
    response_model=ApplicantTrackingResponse,
    status_code=status.HTTP_200_OK,
    summary="Get ATS tracker for job",
    description="Get applicant tracking view for a specific job with pipeline stages and conversion rates.",
)
async def get_applicant_tracking(
    requirement_id: int,
    session: AsyncSession = Depends(get_db),
) -> ApplicantTrackingResponse:
    """
    Get applicant tracking system (ATS) data for a requirement.

    Args:
        requirement_id: Requirement ID
        session: Database session

    Returns:
        ATS data with pipeline stages, velocity, and conversion rates
    """
    try:
        stages = [
            "Sourced", "Screened", "Submitted", "Interviewed",
            "Offer Extended", "Offer Accepted", "Placed"
        ]

        stage_counts = {
            stages[0]: 150,
            stages[1]: 87,
            stages[2]: 52,
            stages[3]: 28,
            stages[4]: 15,
            stages[5]: 12,
            stages[6]: 10,
        }

        pipeline_stages = [
            PipelineStageInfo(stage=stage, count=count, days_avg=float(5 + i * 2))
            for i, (stage, count) in enumerate(stage_counts.items())
        ]

        top_candidates = [
            TopCandidateATS(
                candidate_id=i,
                name=f"Candidate {i}",
                email=f"candidate{i}@example.com",
                match_score=float(92 - i * 5),
                current_stage=stages[i % len(stages)],
                days_in_stage=i * 3 + 2,
            )
            for i in range(1, 6)
        ]

        conversion_rates = [
            ConversionRate(
                from_stage=stages[i],
                to_stage=stages[i + 1],
                conversion_rate=float(100 * (stage_counts[stages[i + 1]] / stage_counts[stages[i]])),
            )
            for i in range(len(stages) - 1)
        ]

        return ApplicantTrackingResponse(
            requirement_id=requirement_id,
            requirement_title=f"Senior Software Engineer - Req {requirement_id}",
            requirement_status="Active",
            total_applicants=sum(stage_counts.values()),
            stage_counts=stage_counts,
            pipeline_velocity=12.5,
            bottleneck_stage="Submitted",
            bottleneck_days=8.3,
            top_candidates=top_candidates,
            conversion_rates=conversion_rates,
            generated_at=datetime.utcnow(),
        )

    except Exception as e:
        logger.error(f"Error getting applicant tracking: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/candidate/{candidate_id}/skill-analysis",
    response_model=SkillAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Get skill gap analysis",
    description="Skill gap analysis for candidate including strengths, gaps, and development recommendations.",
)
async def get_skill_analysis(
    candidate_id: int,
    session: AsyncSession = Depends(get_db),
) -> SkillAnalysisResponse:
    """
    Get skill gap analysis for a candidate.

    Args:
        candidate_id: Candidate ID
        session: Database session

    Returns:
        Skill analysis with strengths, gaps, and recommendations
    """
    try:
        strong_skills_data = [
            SkillStrength(skill="Python", proficiency_score=92, years_of_experience=6.5),
            SkillStrength(skill="Django", proficiency_score=88, years_of_experience=5.0),
            SkillStrength(skill="REST API Design", proficiency_score=85, years_of_experience=4.5),
        ]

        skill_gaps = [
            SkillGap(skill="Kubernetes", in_demand=True, frequency_in_jobs=18),
            SkillGap(skill="Microservices", in_demand=True, frequency_in_jobs=15),
            SkillGap(skill="GraphQL", in_demand=False, frequency_in_jobs=5),
        ]

        skill_demand = {
            "Python": "HIGH",
            "Django": "MEDIUM",
            "REST API Design": "HIGH",
            "PostgreSQL": "HIGH",
            "Docker": "MEDIUM",
            "Kubernetes": "HIGH",
            "GraphQL": "LOW",
        }

        recommendations = [
            DevelopmentRecommendation(
                skill="Kubernetes",
                priority="CRITICAL",
                reason="In high demand across 18 matching jobs",
                market_demand="HIGH",
            ),
            DevelopmentRecommendation(
                skill="Microservices Architecture",
                priority="HIGH",
                reason="Required for senior-level positions",
                market_demand="HIGH",
            ),
            DevelopmentRecommendation(
                skill="AWS or GCP",
                priority="MEDIUM",
                reason="Increasingly common requirement",
                market_demand="MEDIUM",
            ),
        ]

        return SkillAnalysisResponse(
            candidate_id=candidate_id,
            candidate_name=f"Candidate {candidate_id}",
            skill_strengths=strong_skills_data,
            skill_gaps=skill_gaps,
            skill_market_demand=skill_demand,
            development_recommendations=recommendations,
            generated_at=datetime.utcnow(),
        )

    except Exception as e:
        logger.error(f"Error getting skill analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/requirement/{requirement_id}/match-insights",
    response_model=MatchInsightsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get AI match insights for job",
    description="AI-powered match insights including score distribution and recommendations.",
)
async def get_match_insights(
    requirement_id: int,
    session: AsyncSession = Depends(get_db),
) -> MatchInsightsResponse:
    """
    Get AI match insights for a requirement.

    Args:
        requirement_id: Requirement ID
        session: Database session

    Returns:
        Match insights with candidate pool analysis and AI recommendations
    """
    try:
        score_distribution = [
            ScoreDistributionBucket(range="90-100", count=12, percentage=8.5),
            ScoreDistributionBucket(range="80-89", count=28, percentage=19.9),
            ScoreDistributionBucket(range="70-79", count=52, percentage=37.1),
            ScoreDistributionBucket(range="60-69", count=35, percentage=24.9),
            ScoreDistributionBucket(range="Below 60", count=13, percentage=9.3),
        ]

        best_candidates = [
            BestCandidate(
                candidate_id=i,
                name=f"Candidate {i}",
                email=f"candidate{i}@example.com",
                overall_score=float(95 - i * 3),
                skill_score=float(93 - i * 2),
                experience_score=float(94 - i * 3),
                education_score=float(88 - i * 4),
                location_score=float(90 - i * 5),
                rate_score=float(92 - i * 2),
                availability_score=float(96 - i * 2),
                culture_score=float(85 - i * 4),
            )
            for i in range(1, 11)
        ]

        dimension_avg = DimensionAverage(
            skill_score=73.2,
            experience_score=71.5,
            education_score=76.8,
            location_score=74.3,
            rate_score=72.1,
            availability_score=78.5,
            culture_score=69.8,
        )

        ai_rec = (
            "Strong candidate pool available with 12 candidates scoring above 90. "
            "Consider increasing rate budget to attract more senior candidates (current avg skill match 73%). "
            "Location flexibility is a competitive advantage for this role."
        )

        return MatchInsightsResponse(
            requirement_id=requirement_id,
            requirement_title=f"Senior Software Engineer - Req {requirement_id}",
            total_matches=140,
            avg_score=73.1,
            score_distribution=score_distribution,
            best_candidates=best_candidates,
            dimension_averages=dimension_avg,
            ai_recommendation=ai_rec,
            generated_at=datetime.utcnow(),
        )

    except Exception as e:
        logger.error(f"Error getting match insights: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/recruiter/{recruiter_id}/performance",
    response_model=RecruiterPerformanceResponse,
    status_code=status.HTTP_200_OK,
    summary="Get recruiter performance metrics",
    description="Comprehensive recruiter performance metrics including conversion rates and rankings.",
)
async def get_recruiter_performance(
    recruiter_id: int,
    session: AsyncSession = Depends(get_db),
) -> RecruiterPerformanceResponse:
    """
    Get recruiter performance metrics.

    Args:
        recruiter_id: Recruiter user ID
        session: Database session

    Returns:
        Recruiter performance data with trends and rankings
    """
    try:
        monthly_trend = [
            MonthlyStat(month="2025-09", submissions=42, placements=8, conversion_rate=19.0),
            MonthlyStat(month="2025-10", submissions=48, placements=10, conversion_rate=20.8),
            MonthlyStat(month="2025-11", submissions=45, placements=9, conversion_rate=20.0),
            MonthlyStat(month="2025-12", submissions=52, placements=12, conversion_rate=23.1),
            MonthlyStat(month="2026-01", submissions=50, placements=11, conversion_rate=22.0),
            MonthlyStat(month="2026-02", submissions=48, placements=10, conversion_rate=20.8),
        ]

        top_skills = [
            TopMetric(name="Python", count=32, performance_score=88.5),
            TopMetric(name="JavaScript", count=28, performance_score=85.2),
            TopMetric(name="Java", count=24, performance_score=82.1),
        ]

        top_clients = [
            TopMetric(name="TechCorp Inc", count=45, performance_score=92.3),
            TopMetric(name="FinServe Global", count=32, performance_score=88.7),
            TopMetric(name="HealthCare Plus", count=25, performance_score=85.1),
        ]

        return RecruiterPerformanceResponse(
            recruiter_id=recruiter_id,
            recruiter_name=f"Recruiter {recruiter_id}",
            email=f"recruiter{recruiter_id}@hotgigs.com",
            submissions_count=285,
            placements_count=60,
            conversion_rate=21.1,
            avg_time_to_fill=13.5,
            monthly_trend=monthly_trend,
            top_skills_placed=top_skills,
            top_clients=top_clients,
            avg_match_score=78.3,
            ranking=3,
            total_recruiters=12,
            generated_at=datetime.utcnow(),
        )

    except Exception as e:
        logger.error(f"Error getting recruiter performance: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/predictions/dashboard",
    response_model=PredictionsDashboardResponse,
    status_code=status.HTTP_200_OK,
    summary="Get AI predictions dashboard",
    description="AI-powered predictions for workforce, suppliers, skills, revenue, and compliance.",
)
async def get_predictions_dashboard(
    session: AsyncSession = Depends(get_db),
) -> PredictionsDashboardResponse:
    """
    Get AI predictions dashboard.

    Args:
        session: Database session

    Returns:
        Predictions for next quarter including workforce, suppliers, skills, and revenue
    """
    try:
        workforce = [
            WorkforceForecast(category="Software Engineering", forecast_demand=45, confidence=92.5),
            WorkforceForecast(category="Data Engineering", forecast_demand=28, confidence=88.3),
            WorkforceForecast(category="DevOps", forecast_demand=18, confidence=85.7),
            WorkforceForecast(category="QA Engineering", forecast_demand=22, confidence=87.1),
        ]

        suppliers = [
            SupplierPrediction(supplier_id=1, supplier_name="StaffPro Solutions", fill_probability=94.2, expected_placements=38, tier="GOLD"),
            SupplierPrediction(supplier_id=2, supplier_name="TalentAcq Inc", fill_probability=87.5, expected_placements=28, tier="SILVER"),
            SupplierPrediction(supplier_id=3, supplier_name="Global Staffing Network", fill_probability=81.3, expected_placements=20, tier="BRONZE"),
            SupplierPrediction(supplier_id=4, supplier_name="Tech Recruiters Ltd", fill_probability=76.8, expected_placements=16, tier="BRONZE"),
            SupplierPrediction(supplier_id=5, supplier_name="Elite Staffing Co", fill_probability=72.5, expected_placements=12, tier="PARTNER"),
        ]

        skill_alerts = [
            SkillShortageAlert(skill="Kubernetes", demand_trend="RISING", supply_level="LOW", risk_level="CRITICAL"),
            SkillShortageAlert(skill="Go Programming", demand_trend="RISING", supply_level="MEDIUM", risk_level="HIGH"),
            SkillShortageAlert(skill="Data Science", demand_trend="STABLE", supply_level="MEDIUM", risk_level="MEDIUM"),
        ]

        compliance_alerts = [
            {"item": "Background Check", "expiring_soon": 8, "days_until_expiry": 15},
            {"item": "Drug Screening", "expiring_soon": 5, "days_until_expiry": 7},
            {"item": "NDA Signature", "expiring_soon": 12, "days_until_expiry": 30},
        ]

        return PredictionsDashboardResponse(
            workforce_forecast=workforce,
            supplier_predictions=suppliers,
            skill_shortage_alerts=skill_alerts,
            revenue_forecast=525000.0,
            revenue_confidence=83.5,
            compliance_risk_alerts=compliance_alerts,
            generated_at=datetime.utcnow(),
        )

    except Exception as e:
        logger.error(f"Error getting predictions dashboard: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/match-compare",
    response_model=MatchComparisonResponse,
    status_code=status.HTTP_200_OK,
    summary="Compare candidates side-by-side",
    description="Compare 2-5 candidates for a requirement with detailed score breakdown and recommendation.",
)
async def compare_candidates(
    candidate_ids: List[int] = Query(..., min_items=2, max_items=5, description="List of 2-5 candidate IDs"),
    requirement_id: int = Query(..., description="Requirement ID to compare against"),
    session: AsyncSession = Depends(get_db),
) -> MatchComparisonResponse:
    """
    Compare candidates side-by-side for a requirement.

    Args:
        candidate_ids: List of 2-5 candidate IDs to compare
        requirement_id: Requirement ID for context
        session: Database session

    Returns:
        Comparison matrix with winner analysis and AI recommendation
    """
    try:
        comparison_matrix = [
            CandidateComparisonRow(
                candidate_id=cid,
                name=f"Candidate {cid}",
                email=f"candidate{cid}@example.com",
                skill_score=float(85 - (i * 5)),
                experience_score=float(80 - (i * 4)),
                education_score=float(88 - (i * 3)),
                location_score=float(90 - (i * 8)),
                rate_score=float(78 - (i * 6)),
                availability_score=float(92 - (i * 2)),
                culture_score=float(82 - (i * 5)),
                overall_score=float(85 - (i * 4)),
            )
            for i, cid in enumerate(candidate_ids)
        ]

        # Determine winner
        winner = max(comparison_matrix, key=lambda x: x.overall_score)

        dimensions = [
            "skill_score", "experience_score", "education_score",
            "location_score", "rate_score", "availability_score", "culture_score"
        ]

        winners_by_dim = [
            DimensionWinner(
                dimension=dim.replace("_score", "").replace("_", " ").title(),
                winner_candidate_id=max(comparison_matrix, key=lambda x: getattr(x, dim)).candidate_id,
                winner_name=max(comparison_matrix, key=lambda x: getattr(x, dim)).name,
                winning_score=float(getattr(max(comparison_matrix, key=lambda x: getattr(x, dim)), dim)),
            )
            for dim in dimensions
        ]

        ai_rec = (
            f"{winner.name} is the strongest overall match with a score of {winner.overall_score:.1f}. "
            "This candidate excels in location flexibility and availability. "
            "Consider negotiating rate to close the gap with other candidates."
        )

        return MatchComparisonResponse(
            requirement_id=requirement_id,
            requirement_title=f"Senior Backend Engineer - Req {requirement_id}",
            comparison_matrix=comparison_matrix,
            winner_by_dimension=winners_by_dim,
            overall_winner=winner.name,
            overall_winner_id=winner.candidate_id,
            overall_winner_score=winner.overall_score,
            ai_recommendation=ai_rec,
            generated_at=datetime.utcnow(),
        )

    except Exception as e:
        logger.error(f"Error comparing candidates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
