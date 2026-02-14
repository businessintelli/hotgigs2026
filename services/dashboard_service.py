"""Dashboard and analytics service for comprehensive HR metrics."""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.requirement import Requirement
from models.candidate import Candidate
from models.submission import Submission
from models.offer import Offer
from models.interview import Interview
from models.match import MatchScore
from models.supplier import Supplier
from models.user import User
from models.resume import Resume
from models.enums import (
    RequirementStatus,
    CandidateStatus,
    SubmissionStatus,
    OfferStatus,
    InterviewStatus,
)

logger = logging.getLogger(__name__)


class DashboardService:
    """Service for dashboard and analytics operations."""

    def __init__(self, db: AsyncSession):
        """Initialize dashboard service.

        Args:
            db: Async database session
        """
        self.db = db

    async def get_overview_metrics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get executive summary metrics.

        Args:
            start_date: Filter start date
            end_date: Filter end date

        Returns:
            Dictionary with overview metrics
        """
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        # Total active requirements
        active_req = await self.db.execute(
            select(func.count(Requirement.id)).where(
                Requirement.status == RequirementStatus.ACTIVE
            )
        )
        total_active_requirements = active_req.scalar() or 0

        # Candidates in pipeline (not in final states)
        final_statuses = [
            CandidateStatus.PLACED,
            CandidateStatus.REJECTED,
            CandidateStatus.BACKOUT,
            CandidateStatus.TALENT_POOL,
        ]
        pipeline_cands = await self.db.execute(
            select(func.count(Candidate.id)).where(
                ~Candidate.status.in_(final_statuses)
            )
        )
        candidates_in_pipeline = pipeline_cands.scalar() or 0

        # Submissions this month
        month_subs = await self.db.execute(
            select(func.count(Submission.id)).where(
                and_(
                    Submission.created_at >= start_date,
                    Submission.created_at <= end_date,
                )
            )
        )
        submissions_this_month = month_subs.scalar() or 0

        # Placements this month
        month_placements = await self.db.execute(
            select(func.count(Offer.id)).where(
                and_(
                    Offer.status == OfferStatus.ACCEPTED,
                    Offer.created_at >= start_date,
                    Offer.created_at <= end_date,
                )
            )
        )
        placements_this_month = month_placements.scalar() or 0

        # Average time to fill
        avg_fill_time = await self._get_avg_time_to_fill(start_date, end_date)

        # Open vs filled ratio
        filled_req = await self.db.execute(
            select(func.count(Requirement.id)).where(
                Requirement.positions_filled > 0
            )
        )
        filled_count = filled_req.scalar() or 0
        open_vs_filled_ratio = (
            filled_count / total_active_requirements
            if total_active_requirements > 0
            else 0
        )

        # Total candidates
        total_cands = await self.db.execute(
            select(func.count(Candidate.id))
        )
        total_candidates = total_cands.scalar() or 0

        # Active suppliers
        active_sups = await self.db.execute(
            select(func.count(Supplier.id)).where(
                Supplier.is_active == True
            )
        )
        active_suppliers = active_sups.scalar() or 0

        return {
            "total_active_requirements": total_active_requirements,
            "candidates_in_pipeline": candidates_in_pipeline,
            "submissions_this_month": submissions_this_month,
            "placements_this_month": placements_this_month,
            "avg_time_to_fill_days": avg_fill_time,
            "open_vs_filled_ratio": round(open_vs_filled_ratio, 2),
            "total_candidates": total_candidates,
            "active_suppliers": active_suppliers,
        }

    async def get_pipeline_metrics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get pipeline metrics by stage.

        Args:
            start_date: Filter start date
            end_date: Filter end date

        Returns:
            Pipeline metrics with stage breakdown
        """
        pipeline_stages = [
            CandidateStatus.SOURCED,
            CandidateStatus.PARSED,
            CandidateStatus.MATCHED,
            CandidateStatus.SCREENING,
            CandidateStatus.SCORED,
            CandidateStatus.READY_FOR_SUBMISSION,
            CandidateStatus.SUBMITTED,
            CandidateStatus.CUSTOMER_REVIEW,
            CandidateStatus.INTERVIEW_SCHEDULED,
            CandidateStatus.INTERVIEW_COMPLETE,
            CandidateStatus.SELECTED,
            CandidateStatus.OFFER_EXTENDED,
            CandidateStatus.OFFER_ACCEPTED,
            CandidateStatus.PLACED,
        ]

        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=90)

        stages = []
        total_candidates = 0

        for stage in pipeline_stages:
            count = await self.db.execute(
                select(func.count(Candidate.id)).where(Candidate.status == stage)
            )
            stage_count = count.scalar() or 0
            total_candidates += stage_count

            stages.append(
                {
                    "stage": stage.value,
                    "count": stage_count,
                    "percentage": 0,  # Will calculate after
                    "velocity_avg_days": await self._get_stage_velocity(stage, start_date, end_date),
                }
            )

        # Calculate percentages
        if total_candidates > 0:
            for stage in stages:
                stage["percentage"] = round((stage["count"] / total_candidates) * 100, 2)

        # Find bottleneck
        bottleneck_stage = None
        bottleneck_avg_days = 0
        for stage in stages:
            if stage["velocity_avg_days"] and stage["velocity_avg_days"] > bottleneck_avg_days:
                bottleneck_avg_days = stage["velocity_avg_days"]
                bottleneck_stage = stage["stage"]

        return {
            "total_candidates": total_candidates,
            "stages": stages,
            "bottleneck_stage": bottleneck_stage,
            "bottleneck_avg_days": bottleneck_avg_days,
        }

    async def get_recruiter_performance(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get per-recruiter performance metrics.

        Args:
            start_date: Filter start date
            end_date: Filter end date

        Returns:
            Recruiter performance metrics
        """
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        # Get all recruiters
        recruiters_result = await self.db.execute(
            select(User).where(User.role.in_(["recruiter", "manager"]))
        )
        recruiters = recruiters_result.scalars().all()

        recruiter_metrics = []

        for recruiter in recruiters:
            # Total submissions in period
            subs = await self.db.execute(
                select(func.count(Submission.id))
                .join(Requirement)
                .where(
                    and_(
                        Requirement.assigned_recruiter_id == recruiter.id,
                        Submission.created_at >= start_date,
                        Submission.created_at <= end_date,
                    )
                )
            )
            total_submissions = subs.scalar() or 0

            # Total placements in period
            placements = await self.db.execute(
                select(func.count(Offer.id))
                .join(Submission)
                .join(Requirement)
                .where(
                    and_(
                        Requirement.assigned_recruiter_id == recruiter.id,
                        Offer.status == OfferStatus.ACCEPTED,
                        Offer.created_at >= start_date,
                        Offer.created_at <= end_date,
                    )
                )
            )
            total_placements = placements.scalar() or 0

            placement_rate = (
                (total_placements / total_submissions * 100)
                if total_submissions > 0
                else 0
            )

            # Average match score
            match_scores = await self.db.execute(
                select(func.avg(MatchScore.score))
                .join(Submission)
                .join(Requirement)
                .where(
                    and_(
                        Requirement.assigned_recruiter_id == recruiter.id,
                        Submission.created_at >= start_date,
                        Submission.created_at <= end_date,
                    )
                )
            )
            avg_match_score = match_scores.scalar() or 0

            # Average time to fill
            avg_ttf = await self._get_recruiter_avg_time_to_fill(recruiter.id, start_date, end_date)

            # Active requirements
            active_reqs = await self.db.execute(
                select(func.count(Requirement.id)).where(
                    and_(
                        Requirement.assigned_recruiter_id == recruiter.id,
                        Requirement.status == RequirementStatus.ACTIVE,
                    )
                )
            )
            active_requirements = active_reqs.scalar() or 0

            recruiter_metrics.append(
                {
                    "recruiter_id": recruiter.id,
                    "recruiter_name": recruiter.full_name,
                    "email": recruiter.email,
                    "total_submissions": total_submissions,
                    "total_placements": total_placements,
                    "placement_rate": round(placement_rate, 2),
                    "avg_match_score": round(float(avg_match_score), 2),
                    "avg_time_to_fill_days": round(avg_ttf, 2),
                    "active_requirements": active_requirements,
                    "submissions_this_month": total_submissions,  # Same as period
                }
            )

        # Calculate average placement rate
        avg_placement_rate = (
            sum(r["placement_rate"] for r in recruiter_metrics) / len(recruiter_metrics)
            if recruiter_metrics
            else 0
        )

        # Find top performer
        top_performer_id = (
            max(recruiter_metrics, key=lambda x: x["total_placements"])["recruiter_id"]
            if recruiter_metrics
            else None
        )

        return {
            "recruiters": sorted(recruiter_metrics, key=lambda x: x["total_placements"], reverse=True),
            "total_recruiters": len(recruiter_metrics),
            "top_performer_id": top_performer_id,
            "avg_placement_rate": round(avg_placement_rate, 2),
        }

    async def get_requirement_analytics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get requirement analytics.

        Args:
            start_date: Filter start date
            end_date: Filter end date

        Returns:
            Requirement analytics
        """
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=90)

        # Total requirements
        total_reqs = await self.db.execute(
            select(func.count(Requirement.id))
        )
        total_requirements = total_reqs.scalar() or 0

        # Active requirements
        active_reqs = await self.db.execute(
            select(func.count(Requirement.id)).where(
                Requirement.status == RequirementStatus.ACTIVE
            )
        )
        active_requirements = active_reqs.scalar() or 0

        # Filled requirements
        filled_reqs = await self.db.execute(
            select(func.count(Requirement.id)).where(
                Requirement.status == RequirementStatus.FILLED
            )
        )
        filled_requirements = filled_reqs.scalar() or 0

        fill_rate = (
            (filled_requirements / total_requirements * 100)
            if total_requirements > 0
            else 0
        )

        # Average time to fill
        avg_ttf = await self._get_avg_time_to_fill(start_date, end_date)

        # Average time to fill by priority
        priorities = ["critical", "high", "medium", "low"]
        avg_ttf_by_priority = {}
        for priority in priorities:
            ttf = await self._get_avg_time_to_fill_by_priority(priority, start_date, end_date)
            avg_ttf_by_priority[priority] = round(ttf, 2)

        # Top skills demanded
        top_skills = await self._get_top_skills_demanded(start_date, end_date)

        # Requirements by priority
        req_by_priority = {}
        for priority in priorities:
            count = await self.db.execute(
                select(func.count(Requirement.id)).where(
                    Requirement.priority == priority
                )
            )
            req_by_priority[priority] = count.scalar() or 0

        return {
            "total_requirements": total_requirements,
            "active_requirements": active_requirements,
            "filled_requirements": filled_requirements,
            "fill_rate": round(fill_rate, 2),
            "avg_time_to_fill_days": round(avg_ttf, 2),
            "avg_time_to_fill_by_priority": avg_ttf_by_priority,
            "top_skills_demanded": top_skills,
            "requirements_by_priority": req_by_priority,
        }

    async def get_submission_funnel(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get submission funnel metrics.

        Args:
            start_date: Filter start date
            end_date: Filter end date

        Returns:
            Submission funnel data
        """
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        funnel_stages = [
            ("total_pipeline", None),
            ("under_review", SubmissionStatus.PENDING_REVIEW),
            ("approved", SubmissionStatus.APPROVED),
            ("submitted", SubmissionStatus.SUBMITTED),
            ("customer_review", SubmissionStatus.UNDER_CUSTOMER_REVIEW),
            ("shortlisted", SubmissionStatus.SHORTLISTED),
        ]

        stages = []
        previous_count = None

        for label, status in funnel_stages:
            if status is None:
                # Total pipeline
                count = await self.db.execute(
                    select(func.count(Submission.id)).where(
                        and_(
                            Submission.created_at >= start_date,
                            Submission.created_at <= end_date,
                        )
                    )
                )
            else:
                count = await self.db.execute(
                    select(func.count(Submission.id)).where(
                        and_(
                            Submission.status == status,
                            Submission.created_at >= start_date,
                            Submission.created_at <= end_date,
                        )
                    )
                )

            stage_count = count.scalar() or 0

            conversion_rate = None
            if previous_count and previous_count > 0:
                conversion_rate = round((stage_count / previous_count * 100), 2)

            stages.append(
                {
                    "stage": label,
                    "count": stage_count,
                    "conversion_rate_from_previous": conversion_rate,
                }
            )

            previous_count = stage_count

        # Overall conversion rate
        overall_conversion = 0
        if stages:
            first_count = stages[0]["count"]
            last_count = stages[-1]["count"]
            if first_count > 0:
                overall_conversion = round((last_count / first_count * 100), 2)

        return {
            "total_pipeline": stages[0]["count"] if stages else 0,
            "stages": stages,
            "overall_conversion_rate": overall_conversion,
        }

    async def get_offer_metrics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get offer metrics.

        Args:
            start_date: Filter start date
            end_date: Filter end date

        Returns:
            Offer metrics
        """
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        # Total offers
        total_offers = await self.db.execute(
            select(func.count(Offer.id)).where(
                and_(
                    Offer.created_at >= start_date,
                    Offer.created_at <= end_date,
                )
            )
        )
        total_offers_count = total_offers.scalar() or 0

        # Accepted offers
        accepted = await self.db.execute(
            select(func.count(Offer.id)).where(
                and_(
                    Offer.status == OfferStatus.ACCEPTED,
                    Offer.created_at >= start_date,
                    Offer.created_at <= end_date,
                )
            )
        )
        accepted_count = accepted.scalar() or 0

        # Declined offers
        declined = await self.db.execute(
            select(func.count(Offer.id)).where(
                and_(
                    Offer.status == OfferStatus.DECLINED,
                    Offer.created_at >= start_date,
                    Offer.created_at <= end_date,
                )
            )
        )
        declined_count = declined.scalar() or 0

        # Negotiating offers
        negotiating = await self.db.execute(
            select(func.count(Offer.id)).where(
                and_(
                    Offer.status == OfferStatus.NEGOTIATING,
                    Offer.created_at >= start_date,
                    Offer.created_at <= end_date,
                )
            )
        )
        negotiating_count = negotiating.scalar() or 0

        acceptance_rate = (
            (accepted_count / total_offers_count * 100)
            if total_offers_count > 0
            else 0
        )

        # Average negotiation rounds
        avg_negotiations = 0.0
        # This would require tracking negotiation history in metadata

        # Backout rate (need to track accepted then placed status change)
        backout_rate = 0.0

        # Average time to accept
        avg_time_to_accept = await self._get_avg_time_to_accept_offer(start_date, end_date)

        return {
            "total_offers": total_offers_count,
            "accepted_offers": accepted_count,
            "declined_offers": declined_count,
            "negotiating_offers": negotiating_count,
            "acceptance_rate": round(acceptance_rate, 2),
            "avg_negotiation_rounds": avg_negotiations,
            "backout_rate": backout_rate,
            "avg_time_to_accept_days": round(avg_time_to_accept, 2),
            "avg_offer_value": None,
        }

    async def get_supplier_leaderboard(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get supplier leaderboard.

        Args:
            start_date: Filter start date
            end_date: Filter end date

        Returns:
            Ranked suppliers by performance
        """
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        suppliers_result = await self.db.execute(
            select(Supplier).where(Supplier.is_active == True)
        )
        suppliers = suppliers_result.scalars().all()

        leaderboard = []

        for supplier in suppliers:
            # Total placements
            placements = await self.db.execute(
                select(func.count(Offer.id))
                .join(Submission)
                .join(Candidate)
                .where(
                    and_(
                        Candidate.supplier_id == supplier.id,
                        Offer.status == OfferStatus.ACCEPTED,
                        Offer.created_at >= start_date,
                        Offer.created_at <= end_date,
                    )
                )
            )
            total_placements = placements.scalar() or 0

            # Total submissions
            submissions = await self.db.execute(
                select(func.count(Submission.id))
                .join(Candidate)
                .where(
                    and_(
                        Candidate.supplier_id == supplier.id,
                        Submission.created_at >= start_date,
                        Submission.created_at <= end_date,
                    )
                )
            )
            total_submissions = submissions.scalar() or 0

            submission_to_placement_rate = (
                (total_placements / total_submissions * 100)
                if total_submissions > 0
                else 0
            )

            # Average match quality
            avg_match = await self.db.execute(
                select(func.avg(MatchScore.score))
                .join(Submission)
                .join(Candidate)
                .where(
                    and_(
                        Candidate.supplier_id == supplier.id,
                        Submission.created_at >= start_date,
                        Submission.created_at <= end_date,
                    )
                )
            )
            avg_match_quality = float(avg_match.scalar() or 0)

            # This month placements
            this_month_placements = total_placements  # Since we're filtering by period

            leaderboard.append(
                {
                    "supplier_id": supplier.id,
                    "supplier_name": supplier.company_name,
                    "tier": supplier.tier or "new",
                    "total_placements": total_placements,
                    "total_submissions": total_submissions,
                    "submission_to_placement_rate": round(submission_to_placement_rate, 2),
                    "avg_match_quality": round(avg_match_quality, 2),
                    "this_month_placements": this_month_placements,
                    "rank": 0,  # Will set after sorting
                }
            )

        # Sort by placements
        leaderboard = sorted(leaderboard, key=lambda x: x["total_placements"], reverse=True)

        # Add ranks
        for idx, supplier in enumerate(leaderboard):
            supplier["rank"] = idx + 1

        return {
            "suppliers": leaderboard,
            "total_suppliers": len(leaderboard),
            "period": "monthly",
        }

    async def get_candidate_source_breakdown(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get candidate breakdown by source.

        Args:
            start_date: Filter start date
            end_date: Filter end date

        Returns:
            Candidates by source
        """
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=90)

        # Get all sources
        sources_result = await self.db.execute(
            select(Candidate.source).distinct().where(Candidate.source.isnot(None))
        )
        sources = sources_result.scalars().all()

        total_candidates = 0
        sources_breakdown = []

        for source in sources:
            # Total from source
            count = await self.db.execute(
                select(func.count(Candidate.id)).where(
                    and_(
                        Candidate.source == source,
                        Candidate.created_at >= start_date,
                        Candidate.created_at <= end_date,
                    )
                )
            )
            source_count = count.scalar() or 0
            total_candidates += source_count

            # Placements from source
            placements = await self.db.execute(
                select(func.count(Offer.id))
                .join(Submission)
                .join(Candidate)
                .where(
                    and_(
                        Candidate.source == source,
                        Offer.status == OfferStatus.ACCEPTED,
                        Offer.created_at >= start_date,
                        Offer.created_at <= end_date,
                    )
                )
            )
            placement_count = placements.scalar() or 0

            placement_rate = (
                (placement_count / source_count * 100) if source_count > 0 else 0
            )

            sources_breakdown.append(
                {
                    "source": source,
                    "count": source_count,
                    "percentage": 0,  # Will calculate after
                    "placements": placement_count,
                    "placement_rate": round(placement_rate, 2),
                }
            )

        # Calculate percentages
        if total_candidates > 0:
            for source in sources_breakdown:
                source["percentage"] = round((source["count"] / total_candidates) * 100, 2)

        return {
            "total_candidates": total_candidates,
            "sources": sorted(sources_breakdown, key=lambda x: x["count"], reverse=True),
        }

    async def get_time_series(
        self,
        metric: str,
        interval: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get historical time series data.

        Args:
            metric: Metric name (placements, submissions, etc.)
            interval: daily, weekly, or monthly
            start_date: Filter start date
            end_date: Filter end date

        Returns:
            Time series data
        """
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=90)

        data_points = []

        # Determine interval
        current_date = start_date
        while current_date <= end_date:
            if interval == "daily":
                next_date = current_date + timedelta(days=1)
            elif interval == "weekly":
                next_date = current_date + timedelta(weeks=1)
            else:  # monthly
                if current_date.month == 12:
                    next_date = current_date.replace(year=current_date.year + 1, month=1, day=1)
                else:
                    next_date = current_date.replace(month=current_date.month + 1, day=1)

            # Get metric value for this period
            value = 0
            if metric == "placements":
                result = await self.db.execute(
                    select(func.count(Offer.id)).where(
                        and_(
                            Offer.status == OfferStatus.ACCEPTED,
                            Offer.created_at >= current_date,
                            Offer.created_at < next_date,
                        )
                    )
                )
                value = result.scalar() or 0

            elif metric == "submissions":
                result = await self.db.execute(
                    select(func.count(Submission.id)).where(
                        and_(
                            Submission.created_at >= current_date,
                            Submission.created_at < next_date,
                        )
                    )
                )
                value = result.scalar() or 0

            data_points.append(
                {
                    "date": current_date.strftime("%Y-%m-%d"),
                    "value": value,
                }
            )

            current_date = next_date

        return {
            "metric": metric,
            "interval": interval,
            "data_points": data_points,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
        }

    async def get_kpi_summary(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get key performance indicators summary.

        Args:
            start_date: Filter start date
            end_date: Filter end date

        Returns:
            KPI summary
        """
        overview = await self.get_overview_metrics(start_date, end_date)
        req_analytics = await self.get_requirement_analytics(start_date, end_date)
        offer_metrics = await self.get_offer_metrics(start_date, end_date)
        recruiter_perf = await self.get_recruiter_performance(start_date, end_date)

        # Get 90 day history for trends
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        history_start = start_date - timedelta(days=60)
        history_overview = await self.get_overview_metrics(history_start, start_date)

        return {
            "fill_rate": {
                "current": req_analytics["fill_rate"],
                "target": 85.0,
                "trend": (req_analytics["fill_rate"] - history_overview.get("fill_rate", 0)),
            },
            "time_to_fill": {
                "current": req_analytics["avg_time_to_fill_days"],
                "target": 21.0,
                "trend": 0,  # Would need historical data
            },
            "submission_to_hire_ratio": {
                "current": (
                    (overview["submissions_this_month"] / overview["placements_this_month"])
                    if overview["placements_this_month"] > 0
                    else 0
                ),
                "target": 4.0,
                "trend": 0,
            },
            "cost_per_hire": {
                "current": 0,  # Would need cost data
                "target": 5000,
                "trend": 0,
            },
            "recruiter_productivity": {
                "current": round(
                    overview["placements_this_month"] / recruiter_perf["total_recruiters"]
                    if recruiter_perf["total_recruiters"] > 0
                    else 0,
                    2,
                ),
                "target": 2.0,
                "trend": 0,
            },
            "offer_acceptance_rate": {
                "current": offer_metrics["acceptance_rate"],
                "target": 90.0,
                "trend": 0,
            },
            "retention_rate_at_90days": {
                "current": 0,  # Would need tracking
                "target": 95.0,
                "trend": 0,
            },
        }

    # Helper methods

    async def _get_avg_time_to_fill(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> float:
        """Calculate average time to fill for requirements."""
        # Get filled requirements in period
        result = await self.db.execute(
            select(func.avg(func.julianday(Requirement.updated_at) - func.julianday(Requirement.created_at)))
            .where(
                and_(
                    Requirement.status == RequirementStatus.FILLED,
                    Requirement.updated_at >= start_date,
                    Requirement.updated_at <= end_date,
                )
            )
        )
        return float(result.scalar() or 0)

    async def _get_stage_velocity(
        self,
        stage: CandidateStatus,
        start_date: datetime,
        end_date: datetime,
    ) -> float:
        """Calculate average time spent in a stage."""
        # This would need candidate_status_history table
        return 0.0

    async def _get_recruiter_avg_time_to_fill(
        self,
        recruiter_id: int,
        start_date: datetime,
        end_date: datetime,
    ) -> float:
        """Calculate average time to fill for a specific recruiter."""
        result = await self.db.execute(
            select(func.avg(func.julianday(Requirement.updated_at) - func.julianday(Requirement.created_at)))
            .where(
                and_(
                    Requirement.assigned_recruiter_id == recruiter_id,
                    Requirement.status == RequirementStatus.FILLED,
                    Requirement.updated_at >= start_date,
                    Requirement.updated_at <= end_date,
                )
            )
        )
        return float(result.scalar() or 0)

    async def _get_avg_time_to_fill_by_priority(
        self,
        priority: str,
        start_date: datetime,
        end_date: datetime,
    ) -> float:
        """Calculate average time to fill by priority."""
        result = await self.db.execute(
            select(func.avg(func.julianday(Requirement.updated_at) - func.julianday(Requirement.created_at)))
            .where(
                and_(
                    Requirement.priority == priority,
                    Requirement.status == RequirementStatus.FILLED,
                    Requirement.updated_at >= start_date,
                    Requirement.updated_at <= end_date,
                )
            )
        )
        return float(result.scalar() or 0)

    async def _get_top_skills_demanded(
        self,
        start_date: datetime,
        end_date: datetime,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get top skills in demand."""
        # This would need to parse JSON skills and aggregate
        # For now, return empty
        return []

    async def _get_avg_time_to_accept_offer(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> float:
        """Calculate average time from offer to acceptance."""
        # Would need offer_response table or metadata
        return 0.0
