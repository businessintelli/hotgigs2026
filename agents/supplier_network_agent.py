"""Supplier Network Management Agent for requirement distribution and tier management."""

import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from anthropic import AsyncAnthropic
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func, desc, and_
from agents.base_agent import BaseAgent
from agents.events import EventType
from models.supplier import Supplier, SupplierPerformance
from models.supplier_network import SupplierRequirement, SupplierRateCard, SupplierCommunication
from models.requirement import Requirement
from models.enums import SupplierTier

logger = logging.getLogger(__name__)


class SupplierNetworkAgent(BaseAgent):
    """Agent for managing supplier network, distributions, and performance tracking."""

    def __init__(self, anthropic_api_key: Optional[str] = None):
        """Initialize supplier network agent.

        Args:
            anthropic_api_key: Anthropic API key for LLM calls
        """
        super().__init__(agent_name="SupplierNetworkAgent", agent_version="1.0.0")
        self.anthropic_client = AsyncAnthropic(api_key=anthropic_api_key) if anthropic_api_key else None

    async def onboard_supplier(self, db: AsyncSession, supplier_data: dict) -> Supplier:
        """Onboard new supplier with validation and initialization.

        Args:
            db: Database session
            supplier_data: Supplier data for creation

        Returns:
            Created Supplier object
        """
        try:
            # Validate required fields
            if not supplier_data.get("company_name"):
                raise ValueError("company_name is required")

            # Create supplier with NEW tier
            supplier = Supplier(
                company_name=supplier_data["company_name"],
                contact_name=supplier_data.get("contact_name"),
                contact_email=supplier_data.get("contact_email"),
                contact_phone=supplier_data.get("contact_phone"),
                website=supplier_data.get("website"),
                specializations=supplier_data.get("specializations", []),
                locations_served=supplier_data.get("locations_served", []),
                tier=SupplierTier.NEW,
                commission_rate=supplier_data.get("commission_rate"),
                contract_start=supplier_data.get("contract_start"),
                contract_end=supplier_data.get("contract_end"),
                notes=supplier_data.get("notes"),
            )

            db.add(supplier)
            await db.flush()

            # Initialize performance tracking for this period
            period_start = datetime.utcnow().date()
            period_end = (datetime.utcnow() + timedelta(days=30)).date()

            perf = SupplierPerformance(
                supplier_id=supplier.id,
                period_start=period_start,
                period_end=period_end,
                submissions_count=0,
                placements_count=0,
            )
            db.add(perf)

            await db.commit()
            await db.refresh(supplier)

            logger.info(f"Onboarded new supplier: {supplier.id} - {supplier.company_name}")
            return supplier

        except Exception as e:
            await db.rollback()
            logger.error(f"Error onboarding supplier: {str(e)}")
            raise

    async def distribute_requirement(
        self,
        db: AsyncSession,
        requirement_id: int,
        supplier_ids: Optional[List[int]] = None,
        auto_select: bool = False,
    ) -> List[SupplierRequirement]:
        """Distribute requirement to suppliers or auto-select based on criteria.

        Args:
            db: Database session
            requirement_id: Requirement ID to distribute
            supplier_ids: List of supplier IDs to distribute to (if provided)
            auto_select: Whether to auto-select suppliers

        Returns:
            List of created SupplierRequirement records
        """
        try:
            # Fetch requirement
            req = await db.get(Requirement, requirement_id)
            if not req:
                raise ValueError(f"Requirement {requirement_id} not found")

            # Determine suppliers to distribute to
            if supplier_ids:
                selected_suppliers = supplier_ids
            elif auto_select:
                selected_suppliers = await self.auto_select_suppliers(db, requirement_id)
            else:
                selected_suppliers = []

            distributions = []
            now = datetime.utcnow()

            for supplier_id in selected_suppliers:
                # Check if already distributed
                existing = await db.execute(
                    select(SupplierRequirement).where(
                        and_(
                            SupplierRequirement.supplier_id == supplier_id,
                            SupplierRequirement.requirement_id == requirement_id,
                        )
                    )
                )
                if existing.scalar_one_or_none():
                    continue

                # Create distribution record
                dist = SupplierRequirement(
                    supplier_id=supplier_id,
                    requirement_id=requirement_id,
                    distributed_at=now,
                    response_status="pending",
                )
                db.add(dist)
                distributions.append(dist)

            await db.commit()
            logger.info(f"Distributed requirement {requirement_id} to {len(distributions)} suppliers")

            return distributions

        except Exception as e:
            await db.rollback()
            logger.error(f"Error distributing requirement: {str(e)}")
            raise

    async def auto_select_suppliers(
        self,
        db: AsyncSession,
        requirement_id: int,
        max_suppliers: int = 5,
    ) -> List[int]:
        """Smart supplier selection based on specialization match and performance.

        Args:
            db: Database session
            requirement_id: Requirement ID
            max_suppliers: Maximum suppliers to select

        Returns:
            List of selected supplier IDs ranked by score
        """
        try:
            # Fetch requirement with skills
            req = await db.get(Requirement, requirement_id)
            if not req:
                raise ValueError(f"Requirement {requirement_id} not found")

            req_skills = set(req.skills_required or [])
            req_location = req.location_city or ""

            # Get all active suppliers
            result = await db.execute(
                select(Supplier).where(Supplier.is_active == True).order_by(Supplier.tier)
            )
            suppliers = result.scalars().all()

            supplier_scores = []

            for supplier in suppliers:
                # Skill match score (35%)
                supplier_skills = set(supplier.specializations or [])
                if req_skills and supplier_skills:
                    skill_overlap = len(req_skills & supplier_skills) / len(req_skills)
                    skill_score = skill_overlap * 0.35
                else:
                    skill_score = 0

                # Tier score (30%)
                tier_weights = {
                    SupplierTier.PLATINUM: 0.30,
                    SupplierTier.GOLD: 0.25,
                    SupplierTier.SILVER: 0.20,
                    SupplierTier.BRONZE: 0.15,
                    SupplierTier.NEW: 0.10,
                }
                tier_score = tier_weights.get(supplier.tier, 0.10)

                # Location match score (20%)
                location_match = (
                    1.0 if req_location in (supplier.locations_served or []) else 0.5
                )
                location_score = location_match * 0.20

                # Get latest performance metrics
                perf_result = await db.execute(
                    select(SupplierPerformance)
                    .where(SupplierPerformance.supplier_id == supplier.id)
                    .order_by(desc(SupplierPerformance.period_end))
                    .limit(1)
                )
                perf = perf_result.scalar_one_or_none()

                # Performance score (15%)
                if perf and perf.overall_rating:
                    perf_score = min(perf.overall_rating / 5.0, 1.0) * 0.15
                else:
                    perf_score = 0.075  # Default middle score

                total_score = skill_score + tier_score + location_score + perf_score

                supplier_scores.append((supplier.id, total_score))

            # Sort by score and return top N
            supplier_scores.sort(key=lambda x: x[1], reverse=True)
            selected = [s[0] for s in supplier_scores[:max_suppliers]]

            logger.info(f"Auto-selected {len(selected)} suppliers for requirement {requirement_id}")
            return selected

        except Exception as e:
            logger.error(f"Error auto-selecting suppliers: {str(e)}")
            return []

    async def evaluate_performance(
        self,
        db: AsyncSession,
        supplier_id: int,
        period_start: datetime,
        period_end: datetime,
    ) -> SupplierPerformance:
        """Evaluate supplier performance for a period.

        Args:
            db: Database session
            supplier_id: Supplier ID
            period_start: Period start date
            period_end: Period end date

        Returns:
            SupplierPerformance record with calculated metrics
        """
        try:
            supplier = await db.get(Supplier, supplier_id)
            if not supplier:
                raise ValueError(f"Supplier {supplier_id} not found")

            # Get all submissions in period
            from models.match import MatchScore
            from models.submission import Submission

            submissions_result = await db.execute(
                select(Submission).where(
                    and_(
                        Submission.supplier_id == supplier_id,
                        Submission.created_at >= period_start,
                        Submission.created_at <= period_end,
                    )
                )
            )
            submissions = submissions_result.scalars().all()
            submissions_count = len(submissions)

            # Count placements (PLACED status)
            from models.enums import CandidateStatus

            placed_result = await db.execute(
                select(func.count()).where(
                    and_(
                        Submission.supplier_id == supplier_id,
                        Submission.created_at >= period_start,
                        Submission.created_at <= period_end,
                    )
                )
            )
            placements_count = placed_result.scalar() or 0

            # Calculate rejection rate
            rejection_count = 0
            match_scores = []

            for sub in submissions:
                if sub.status == "rejected":
                    rejection_count += 1
                if sub.match_score:
                    match_scores.append(sub.match_score)

            rejection_rate = (rejection_count / submissions_count) if submissions_count > 0 else 0
            avg_match_score = sum(match_scores) / len(match_scores) if match_scores else 0

            # Calculate average time to fill
            time_to_fills = []
            for sub in submissions:
                if sub.submitted_at and sub.created_at:
                    time_diff = (sub.submitted_at - sub.created_at).days
                    time_to_fills.append(time_diff)

            avg_time_to_fill = sum(time_to_fills) / len(time_to_fills) if time_to_fills else 0

            # Quality score based on placement rate and match score
            if submissions_count > 0:
                placement_rate = placements_count / submissions_count
                quality_score = (placement_rate * 0.6 + avg_match_score / 5.0 * 0.4) * 5
            else:
                quality_score = 0

            # Responsiveness score (based on response time)
            response_times = []
            for sub in submissions:
                if sub.responded_at and sub.created_at:
                    resp_time = (sub.responded_at - sub.created_at).total_seconds() / 3600
                    response_times.append(resp_time)

            responsiveness_score = 5.0 if not response_times else max(0, 5.0 - (sum(response_times) / len(response_times) / 24))

            # Overall rating (weighted formula)
            overall_rating = (
                quality_score * 0.5
                + responsiveness_score * 0.3
                + avg_match_score * 0.2
            )

            # Create or update performance record
            perf_result = await db.execute(
                select(SupplierPerformance).where(
                    and_(
                        SupplierPerformance.supplier_id == supplier_id,
                        SupplierPerformance.period_start == period_start.date(),
                        SupplierPerformance.period_end == period_end.date(),
                    )
                )
            )
            perf = perf_result.scalar_one_or_none()

            if not perf:
                perf = SupplierPerformance(
                    supplier_id=supplier_id,
                    period_start=period_start.date(),
                    period_end=period_end.date(),
                )

            perf.submissions_count = submissions_count
            perf.placements_count = placements_count
            perf.rejection_rate = rejection_rate
            perf.avg_match_score = avg_match_score
            perf.avg_time_to_fill = avg_time_to_fill
            perf.quality_score = quality_score
            perf.responsiveness_score = responsiveness_score
            perf.overall_rating = overall_rating

            db.add(perf)
            await db.commit()
            await db.refresh(perf)

            logger.info(f"Evaluated performance for supplier {supplier_id}: rating={overall_rating:.2f}")
            return perf

        except Exception as e:
            await db.rollback()
            logger.error(f"Error evaluating supplier performance: {str(e)}")
            raise

    async def update_tier(self, db: AsyncSession, supplier_id: int) -> Supplier:
        """Update supplier tier based on rolling 6-month performance.

        Args:
            db: Database session
            supplier_id: Supplier ID

        Returns:
            Updated Supplier object
        """
        try:
            supplier = await db.get(Supplier, supplier_id)
            if not supplier:
                raise ValueError(f"Supplier {supplier_id} not found")

            # Get last 6 months of performance data
            six_months_ago = (datetime.utcnow() - timedelta(days=180)).date()
            perf_result = await db.execute(
                select(SupplierPerformance).where(
                    and_(
                        SupplierPerformance.supplier_id == supplier_id,
                        SupplierPerformance.period_end >= six_months_ago,
                    )
                )
            )
            performances = perf_result.scalars().all()

            if not performances:
                # Not enough data, stay at current tier
                return supplier

            # Calculate average rating
            ratings = [p.overall_rating for p in performances if p.overall_rating]
            if not ratings:
                return supplier

            avg_rating = sum(ratings) / len(ratings)
            total_submissions = sum(p.submissions_count for p in performances)

            # Tier promotion/demotion logic
            new_tier = supplier.tier

            if total_submissions >= 5:
                if avg_rating >= 4.5:
                    new_tier = SupplierTier.PLATINUM
                elif avg_rating >= 3.5:
                    new_tier = SupplierTier.GOLD
                elif avg_rating >= 2.5:
                    new_tier = SupplierTier.SILVER
                elif avg_rating >= 1.5:
                    new_tier = SupplierTier.BRONZE
                else:
                    new_tier = SupplierTier.NEW

            if new_tier != supplier.tier:
                old_tier = supplier.tier
                supplier.tier = new_tier
                db.add(supplier)
                await db.commit()
                await db.refresh(supplier)
                logger.info(
                    f"Promoted supplier {supplier_id} from {old_tier} to {new_tier}"
                )

            return supplier

        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating supplier tier: {str(e)}")
            raise

    async def discover_suppliers(
        self,
        db: AsyncSession,
        industry: Optional[str] = None,
        skills: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Discover potential suppliers to fill gaps in network.

        Args:
            db: Database session
            industry: Industry filter
            skills: Skills to match

        Returns:
            List of supplier recommendations
        """
        try:
            # Get current supplier coverage
            suppliers_result = await db.execute(
                select(Supplier).where(Supplier.is_active == True)
            )
            current_suppliers = suppliers_result.scalars().all()

            covered_skills = set()
            covered_locations = set()

            for supplier in current_suppliers:
                covered_skills.update(supplier.specializations or [])
                covered_locations.update(supplier.locations_served or [])

            # If skills provided, identify gaps
            target_skills = set(skills or [])
            skill_gaps = target_skills - covered_skills

            # Use LLM to generate recommendations if we have gaps
            recommendations = []

            if skill_gaps and self.anthropic_client:
                prompt = f"""Based on the following skill gaps in our current supplier network:
- Missing Skills: {', '.join(skill_gaps)}
- Current Coverage: {', '.join(covered_skills)}

Suggest 5 types of suppliers we should recruit. For each, provide:
1. Supplier type/focus
2. Key specializations to look for
3. Geographic regions to target
4. Tier expectations

Format as JSON array."""

                message = await self.anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}],
                )

                try:
                    response_text = message.content[0].text
                    start_idx = response_text.find("[")
                    end_idx = response_text.rfind("]") + 1
                    if start_idx >= 0 and end_idx > start_idx:
                        recommendations = json.loads(response_text[start_idx:end_idx])
                except (json.JSONDecodeError, IndexError):
                    logger.warning("Failed to parse LLM supplier recommendations")

            logger.info(f"Discovered {len(recommendations)} supplier gaps")
            return recommendations

        except Exception as e:
            logger.error(f"Error discovering suppliers: {str(e)}")
            return []

    async def generate_supplier_scorecard(
        self, db: AsyncSession, supplier_id: int
    ) -> Dict[str, Any]:
        """Generate comprehensive supplier scorecard.

        Args:
            db: Database session
            supplier_id: Supplier ID

        Returns:
            Scorecard dictionary with all metrics and trends
        """
        try:
            supplier = await db.get(Supplier, supplier_id)
            if not supplier:
                raise ValueError(f"Supplier {supplier_id} not found")

            # Get performance history
            perf_result = await db.execute(
                select(SupplierPerformance)
                .where(SupplierPerformance.supplier_id == supplier_id)
                .order_by(desc(SupplierPerformance.period_end))
                .limit(12)  # Last 12 periods
            )
            performances = perf_result.scalars().all()

            # Calculate trends
            current_period = performances[0] if performances else None
            previous_periods = performances[1:] if len(performances) > 1 else []

            trend_data = {}
            if current_period and previous_periods:
                prev = previous_periods[0]
                trend_data = {
                    "submissions_trend": (
                        current_period.submissions_count - prev.submissions_count
                    ),
                    "placements_trend": (
                        current_period.placements_count - prev.placements_count
                    ),
                    "quality_trend": (
                        (current_period.quality_score or 0) - (prev.quality_score or 0)
                    ),
                    "responsiveness_trend": (
                        (current_period.responsiveness_score or 0)
                        - (prev.responsiveness_score or 0)
                    ),
                }

            # Get tier comparisons
            tier_result = await db.execute(
                select(func.avg(SupplierPerformance.overall_rating)).where(
                    SupplierPerformance.supplier_id.in_(
                        select(Supplier.id).where(Supplier.tier == supplier.tier)
                    )
                )
            )
            tier_avg_rating = tier_result.scalar() or 0

            scorecard = {
                "supplier_id": supplier.id,
                "company_name": supplier.company_name,
                "tier": supplier.tier,
                "contract_status": {
                    "start_date": supplier.contract_start,
                    "end_date": supplier.contract_end,
                    "commission_rate": supplier.commission_rate,
                },
                "current_metrics": {
                    "submissions_count": current_period.submissions_count if current_period else 0,
                    "placements_count": current_period.placements_count if current_period else 0,
                    "rejection_rate": current_period.rejection_rate if current_period else 0,
                    "avg_match_score": current_period.avg_match_score if current_period else 0,
                    "quality_score": current_period.quality_score if current_period else 0,
                    "responsiveness_score": current_period.responsiveness_score if current_period else 0,
                    "overall_rating": current_period.overall_rating if current_period else 0,
                },
                "trends": trend_data,
                "tier_comparison": {
                    "tier": supplier.tier,
                    "tier_avg_rating": tier_avg_rating,
                    "vs_tier_performance": (
                        (current_period.overall_rating or 0) - tier_avg_rating
                        if current_period
                        else 0
                    ),
                },
                "total_lifetime_submissions": supplier.total_submissions,
                "total_lifetime_placements": supplier.total_placements,
                "specializations": supplier.specializations,
                "locations_served": supplier.locations_served,
            }

            return scorecard

        except Exception as e:
            logger.error(f"Error generating supplier scorecard: {str(e)}")
            raise

    async def manage_rate_cards(
        self,
        db: AsyncSession,
        supplier_id: int,
        rate_card: dict,
    ) -> dict:
        """Store and update supplier rate cards.

        Args:
            db: Database session
            supplier_id: Supplier ID
            rate_card: Rate card data

        Returns:
            Created/updated rate card as dictionary
        """
        try:
            supplier = await db.get(Supplier, supplier_id)
            if not supplier:
                raise ValueError(f"Supplier {supplier_id} not found")

            # Check for existing rate card with same role/skill/location
            existing_result = await db.execute(
                select(SupplierRateCard).where(
                    and_(
                        SupplierRateCard.supplier_id == supplier_id,
                        SupplierRateCard.role_title == rate_card.get("role_title"),
                        SupplierRateCard.skill_category
                        == rate_card.get("skill_category"),
                    )
                )
            )
            existing = existing_result.scalar_one_or_none()

            if existing:
                # Update existing
                existing.min_rate = rate_card.get("min_rate", existing.min_rate)
                existing.max_rate = rate_card.get("max_rate", existing.max_rate)
                existing.rate_type = rate_card.get("rate_type", existing.rate_type)
                existing.location = rate_card.get("location", existing.location)
                existing.effective_date = rate_card.get("effective_date", existing.effective_date)
                existing.expiry_date = rate_card.get("expiry_date", existing.expiry_date)
                existing.notes = rate_card.get("notes", existing.notes)
                db.add(existing)
            else:
                # Create new
                new_card = SupplierRateCard(
                    supplier_id=supplier_id,
                    role_title=rate_card["role_title"],
                    skill_category=rate_card["skill_category"],
                    min_rate=rate_card["min_rate"],
                    max_rate=rate_card["max_rate"],
                    rate_type=rate_card.get("rate_type", "hourly"),
                    effective_date=rate_card.get("effective_date"),
                    location=rate_card.get("location"),
                    expiry_date=rate_card.get("expiry_date"),
                    notes=rate_card.get("notes"),
                )
                db.add(new_card)

            await db.commit()
            logger.info(f"Updated rate card for supplier {supplier_id}")

            return rate_card

        except Exception as e:
            await db.rollback()
            logger.error(f"Error managing rate card: {str(e)}")
            raise

    async def get_network_analytics(self, db: AsyncSession) -> Dict[str, Any]:
        """Get comprehensive network health analytics.

        Args:
            db: Database session

        Returns:
            Network analytics dictionary
        """
        try:
            # Total suppliers by tier
            suppliers_result = await db.execute(
                select(Supplier.tier, func.count(Supplier.id)).where(
                    Supplier.is_active == True
                ).group_by(Supplier.tier)
            )
            suppliers_by_tier = dict(suppliers_result.all())

            # Coverage analysis
            suppliers_result = await db.execute(
                select(Supplier).where(Supplier.is_active == True)
            )
            all_suppliers = suppliers_result.scalars().all()

            all_skills = set()
            all_locations = set()
            for supplier in all_suppliers:
                all_skills.update(supplier.specializations or [])
                all_locations.update(supplier.locations_served or [])

            # Performance by tier
            perf_result = await db.execute(
                select(
                    Supplier.tier,
                    func.avg(SupplierPerformance.overall_rating),
                    func.count(Supplier.id),
                )
                .join(SupplierPerformance)
                .where(Supplier.is_active == True)
                .group_by(Supplier.tier)
            )
            tier_performance = {row[0]: row[1] for row in perf_result.all()}

            # Top and bottom performers
            top_result = await db.execute(
                select(Supplier, SupplierPerformance.overall_rating)
                .join(SupplierPerformance)
                .where(Supplier.is_active == True)
                .order_by(desc(SupplierPerformance.overall_rating))
                .limit(5)
            )
            top_performers = [
                {"id": row[0].id, "name": row[0].company_name, "rating": row[1]}
                for row in top_result.all()
            ]

            bottom_result = await db.execute(
                select(Supplier, SupplierPerformance.overall_rating)
                .join(SupplierPerformance)
                .where(Supplier.is_active == True)
                .order_by(SupplierPerformance.overall_rating)
                .limit(5)
            )
            underperformers = [
                {"id": row[0].id, "name": row[0].company_name, "rating": row[1]}
                for row in bottom_result.all()
            ]

            analytics = {
                "total_suppliers": len(all_suppliers),
                "suppliers_by_tier": suppliers_by_tier,
                "coverage": {
                    "total_skills": len(all_skills),
                    "total_locations": len(all_locations),
                    "skills": list(all_skills)[:10],
                    "locations": list(all_locations)[:10],
                },
                "performance_by_tier": tier_performance,
                "top_performers": top_performers,
                "underperformers": underperformers,
                "network_health": "healthy"
                if len(all_suppliers) > 5 and len(all_skills) > 10
                else "needs_improvement",
            }

            return analytics

        except Exception as e:
            logger.error(f"Error getting network analytics: {str(e)}")
            return {}

    async def on_start(self) -> None:
        """Called when agent starts."""
        logger.info("Supplier Network Agent started")

    async def on_stop(self) -> None:
        """Called when agent stops."""
        logger.info("Supplier Network Agent stopped")
