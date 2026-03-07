"""
MSP Shortlisting Agent — Ranks supplier submissions for a requirement.

Uses match score, supplier tier, submission speed, and historical quality
to generate top-N recommendations for the client.
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# Supplier tier multipliers
TIER_MULTIPLIERS = {
    "platinum": 1.15,
    "gold": 1.10,
    "silver": 1.05,
    "bronze": 1.00,
    "standard": 1.00,
    "new": 0.95,
}


@dataclass
class RankedSubmission:
    """A ranked submission with composite score."""
    submission_id: int
    candidate_id: int
    supplier_org_id: int
    supplier_name: str
    match_score: float
    tier_bonus: float
    speed_bonus: float
    quality_bonus: float
    composite_score: float
    rank: int
    recommendation: str  # TOP_PICK, RECOMMENDED, ACCEPTABLE, BELOW_THRESHOLD


class MSPShortlistAgent:
    """
    Ranks all supplier submissions for a requirement to generate
    shortlist recommendations for the client.
    """

    def __init__(self, top_n: int = 5, threshold: float = 40.0):
        self.top_n = top_n
        self.threshold = threshold

    def rank_submissions(
        self,
        submissions: List[Dict[str, Any]],
    ) -> List[RankedSubmission]:
        """
        Rank submissions by composite score.
        
        Each submission dict should contain:
          - submission_id: int
          - candidate_id: int
          - supplier_org_id: int
          - supplier_name: str
          - match_score: float (0-100, from RequirementMatchingAgent)
          - supplier_tier: str (platinum/gold/silver/bronze/standard/new)
          - hours_since_distribution: float
          - supplier_avg_quality: float (0-100, historical)
        """
        scored = []

        for sub in submissions:
            match_score = sub.get("match_score", 50)
            tier = sub.get("supplier_tier", "standard").lower()
            hours = sub.get("hours_since_distribution", 24)
            avg_quality = sub.get("supplier_avg_quality", 50)

            # Tier bonus (0-15 points)
            tier_mult = TIER_MULTIPLIERS.get(tier, 1.0)
            tier_bonus = (tier_mult - 1.0) * 100

            # Speed bonus (0-10 points) — faster submission = higher bonus
            if hours <= 12:
                speed_bonus = 10
            elif hours <= 24:
                speed_bonus = 7
            elif hours <= 48:
                speed_bonus = 4
            else:
                speed_bonus = 0

            # Quality bonus based on supplier's historical performance
            quality_bonus = (avg_quality / 100) * 10  # 0-10 points

            # Composite score
            composite = match_score * 0.70 + tier_bonus + speed_bonus + quality_bonus

            scored.append(RankedSubmission(
                submission_id=sub["submission_id"],
                candidate_id=sub["candidate_id"],
                supplier_org_id=sub["supplier_org_id"],
                supplier_name=sub.get("supplier_name", "Unknown"),
                match_score=round(match_score, 1),
                tier_bonus=round(tier_bonus, 1),
                speed_bonus=round(speed_bonus, 1),
                quality_bonus=round(quality_bonus, 1),
                composite_score=round(composite, 1),
                rank=0,
                recommendation="",
            ))

        # Sort by composite score descending
        scored.sort(key=lambda x: x.composite_score, reverse=True)

        # Assign ranks and recommendations
        for i, item in enumerate(scored):
            item.rank = i + 1
            if i == 0 and item.composite_score >= 60:
                item.recommendation = "TOP_PICK"
            elif item.composite_score >= 55:
                item.recommendation = "RECOMMENDED"
            elif item.composite_score >= self.threshold:
                item.recommendation = "ACCEPTABLE"
            else:
                item.recommendation = "BELOW_THRESHOLD"

        logger.info(
            f"Ranked {len(scored)} submissions, top score: "
            f"{scored[0].composite_score if scored else 0}"
        )

        return scored[:self.top_n] if self.top_n else scored

    def get_shortlist_summary(self, ranked: List[RankedSubmission]) -> Dict[str, Any]:
        """Generate a summary of the shortlist for the client."""
        top_picks = [r for r in ranked if r.recommendation == "TOP_PICK"]
        recommended = [r for r in ranked if r.recommendation == "RECOMMENDED"]

        return {
            "total_evaluated": len(ranked),
            "top_picks": len(top_picks),
            "recommended": len(recommended),
            "avg_score": round(sum(r.composite_score for r in ranked) / len(ranked), 1) if ranked else 0,
            "top_candidate": {
                "submission_id": ranked[0].submission_id,
                "composite_score": ranked[0].composite_score,
                "supplier": ranked[0].supplier_name,
            } if ranked else None,
        }
