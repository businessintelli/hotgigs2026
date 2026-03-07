"""
Auto-Distribution Agent — AI selects best suppliers for a requirement.

When a client creates a requirement, this agent recommends which
suppliers should receive it based on specialization, past performance,
capacity, and tier.
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SupplierRecommendation:
    """Recommendation for distributing a requirement to a supplier."""
    supplier_org_id: int
    supplier_name: str
    tier: str
    score: float  # 0-100
    reasons: List[str]
    priority: str  # HIGH, MEDIUM, LOW


class AutoDistributionAgent:
    """
    Recommends suppliers for a requirement based on multiple factors.
    
    Scoring:
      - Specialization match: 30%
      - Historical performance: 30%  
      - Capacity (current workload): 20%
      - Tier: 20%
    """

    TIER_SCORES = {
        "platinum": 100,
        "gold": 80,
        "silver": 60,
        "bronze": 40,
        "standard": 30,
        "new": 20,
    }

    def recommend_suppliers(
        self,
        requirement: Dict[str, Any],
        available_suppliers: List[Dict[str, Any]],
        max_recommendations: int = 5,
    ) -> List[SupplierRecommendation]:
        """
        Recommend suppliers for a requirement.
        
        Args:
            requirement: dict with keys: skills, industry, location, budget_max,
                         experience_level, urgency
            available_suppliers: list of dicts with keys: org_id, name, tier,
                                specializations, locations_served, avg_quality_score,
                                total_placements, active_distributions,
                                avg_response_time_hours, max_capacity
        """
        scored = []

        for supplier in available_suppliers:
            spec_score = self._score_specialization(requirement, supplier)
            perf_score = self._score_performance(supplier)
            capacity_score = self._score_capacity(supplier)
            tier_score = self._score_tier(supplier)

            composite = (
                spec_score * 0.30
                + perf_score * 0.30
                + capacity_score * 0.20
                + tier_score * 0.20
            )

            reasons = self._generate_reasons(
                supplier, spec_score, perf_score, capacity_score, tier_score
            )

            if composite >= 60:
                priority = "HIGH"
            elif composite >= 40:
                priority = "MEDIUM"
            else:
                priority = "LOW"

            scored.append(SupplierRecommendation(
                supplier_org_id=supplier.get("org_id", 0),
                supplier_name=supplier.get("name", "Unknown"),
                tier=supplier.get("tier", "standard"),
                score=round(composite, 1),
                reasons=reasons,
                priority=priority,
            ))

        # Sort by score descending
        scored.sort(key=lambda x: x.score, reverse=True)

        result = scored[:max_recommendations]
        logger.info(
            f"Recommended {len(result)} suppliers for requirement, "
            f"top score: {result[0].score if result else 0}"
        )
        return result

    def _score_specialization(self, requirement: Dict, supplier: Dict) -> float:
        """Score how well supplier specializes in the requirement's domain."""
        req_skills = set(s.lower() for s in requirement.get("skills", []))
        supplier_specs = set(s.lower() for s in supplier.get("specializations", []))

        if not req_skills:
            return 50

        if not supplier_specs:
            return 30

        overlap = len(req_skills.intersection(supplier_specs))
        coverage = overlap / len(req_skills) if req_skills else 0

        return min(100, coverage * 100)

    def _score_performance(self, supplier: Dict) -> float:
        """Score based on historical performance metrics."""
        avg_quality = supplier.get("avg_quality_score", 50)
        placements = supplier.get("total_placements", 0)
        response_time = supplier.get("avg_response_time_hours", 48)

        # Quality component (50%)
        quality_score = min(100, avg_quality)

        # Track record (30%)
        track_score = min(100, placements * 10)

        # Responsiveness (20%)
        if response_time <= 12:
            resp_score = 100
        elif response_time <= 24:
            resp_score = 80
        elif response_time <= 48:
            resp_score = 60
        else:
            resp_score = 30

        return quality_score * 0.5 + track_score * 0.3 + resp_score * 0.2

    def _score_capacity(self, supplier: Dict) -> float:
        """Score based on supplier's current workload."""
        active = supplier.get("active_distributions", 0)
        max_cap = supplier.get("max_capacity", 10)

        if max_cap <= 0:
            return 50

        utilization = active / max_cap
        if utilization < 0.5:
            return 100  # Plenty of capacity
        elif utilization < 0.75:
            return 70
        elif utilization < 0.9:
            return 40
        else:
            return 10  # Near capacity

    def _score_tier(self, supplier: Dict) -> float:
        """Score based on supplier tier."""
        tier = supplier.get("tier", "standard").lower()
        return self.TIER_SCORES.get(tier, 30)

    def _generate_reasons(
        self, supplier: Dict, spec: float, perf: float, cap: float, tier: float
    ) -> List[str]:
        """Generate human-readable reasons for the recommendation."""
        reasons = []

        if spec >= 70:
            reasons.append("Strong specialization match")
        elif spec >= 40:
            reasons.append("Moderate specialization overlap")

        if perf >= 70:
            reasons.append("Excellent track record")
        elif perf >= 50:
            reasons.append("Good performance history")

        if cap >= 80:
            reasons.append("High capacity available")
        elif cap <= 30:
            reasons.append("Limited capacity")

        tier_name = supplier.get("tier", "standard").capitalize()
        reasons.append(f"{tier_name} tier supplier")

        return reasons
