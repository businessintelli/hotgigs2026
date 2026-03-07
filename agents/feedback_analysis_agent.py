"""
Feedback Analysis Agent — Analyzes client rejection patterns and
generates actionable insights for suppliers and MSP recruiters.
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from collections import Counter

logger = logging.getLogger(__name__)


@dataclass
class FeedbackInsight:
    """An insight derived from client feedback analysis."""
    category: str  # SKILL_GAP, EXPERIENCE_MISMATCH, RATE_ISSUE, QUALITY_CONCERN, POSITIVE_PATTERN
    description: str
    frequency: int
    severity: str  # HIGH, MEDIUM, LOW
    actionable_advice: str


@dataclass
class FeedbackAnalysis:
    """Complete analysis of client feedback for a supplier or requirement."""
    total_feedbacks: int
    shortlisted_count: int
    rejected_count: int
    interview_count: int
    hold_count: int
    shortlist_rate: float
    insights: List[FeedbackInsight] = field(default_factory=list)
    top_rejection_reasons: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class FeedbackAnalysisAgent:
    """
    Analyzes patterns in client feedback to generate insights.
    Helps suppliers improve submission quality over time.
    """

    REJECTION_KEYWORDS = {
        "skill": ["skill", "technology", "programming", "framework", "tool", "language"],
        "experience": ["experience", "senior", "junior", "years", "level"],
        "rate": ["rate", "budget", "cost", "expensive", "salary", "compensation"],
        "culture": ["culture", "fit", "team", "communication", "soft skill"],
        "availability": ["available", "start date", "notice period", "immediate"],
        "location": ["location", "remote", "onsite", "relocation", "timezone"],
        "quality": ["resume", "quality", "presentation", "formatting", "detail"],
    }

    def analyze_feedbacks(
        self,
        feedbacks: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> FeedbackAnalysis:
        """
        Analyze a collection of client feedbacks.
        
        Args:
            feedbacks: list of dicts with keys: decision, feedback_notes, rating,
                      candidate_skills, requirement_skills, submission_date
            context: optional dict with keys: supplier_name, requirement_title
        """
        total = len(feedbacks)
        if total == 0:
            return FeedbackAnalysis(
                total_feedbacks=0, shortlisted_count=0, rejected_count=0,
                interview_count=0, hold_count=0, shortlist_rate=0,
            )

        decisions = Counter(f.get("decision", "unknown") for f in feedbacks)
        shortlisted = decisions.get("shortlist", 0) + decisions.get("interview", 0)
        rejected = decisions.get("reject", 0)

        analysis = FeedbackAnalysis(
            total_feedbacks=total,
            shortlisted_count=decisions.get("shortlist", 0),
            rejected_count=rejected,
            interview_count=decisions.get("interview", 0),
            hold_count=decisions.get("hold", 0),
            shortlist_rate=round((shortlisted / total) * 100, 1) if total > 0 else 0,
        )

        # Analyze rejection patterns
        rejection_feedbacks = [f for f in feedbacks if f.get("decision") == "reject"]
        if rejection_feedbacks:
            analysis.insights = self._extract_insights(rejection_feedbacks)
            analysis.top_rejection_reasons = self._categorize_rejections(rejection_feedbacks)

        # Generate recommendations
        analysis.recommendations = self._generate_recommendations(analysis)

        logger.info(
            f"Analyzed {total} feedbacks: {analysis.shortlist_rate}% shortlist rate, "
            f"{len(analysis.insights)} insights generated"
        )
        return analysis

    def _extract_insights(self, rejections: List[Dict]) -> List[FeedbackInsight]:
        """Extract insights from rejection feedback notes."""
        insights = []
        category_counts = Counter()

        for feedback in rejections:
            notes = (feedback.get("feedback_notes") or "").lower()
            for category, keywords in self.REJECTION_KEYWORDS.items():
                if any(kw in notes for kw in keywords):
                    category_counts[category] += 1

        for category, count in category_counts.most_common(5):
            severity = "HIGH" if count >= 3 else ("MEDIUM" if count >= 2 else "LOW")
            insight = FeedbackInsight(
                category=category.upper() + "_GAP",
                description=f"Client rejected {count} submissions citing {category} issues",
                frequency=count,
                severity=severity,
                actionable_advice=self._get_advice(category),
            )
            insights.append(insight)

        return insights

    def _categorize_rejections(self, rejections: List[Dict]) -> List[Dict[str, Any]]:
        """Categorize rejections by primary reason."""
        reasons = []
        for feedback in rejections:
            notes = feedback.get("feedback_notes") or ""
            primary_category = "other"
            for category, keywords in self.REJECTION_KEYWORDS.items():
                if any(kw in notes.lower() for kw in keywords):
                    primary_category = category
                    break
            reasons.append({
                "category": primary_category,
                "notes": notes[:200],
                "rating": feedback.get("rating"),
            })
        return reasons

    def _get_advice(self, category: str) -> str:
        """Get actionable advice for a rejection category."""
        advice_map = {
            "skill": "Ensure candidates have verified proficiency in required technologies. Consider submitting candidates with hands-on project experience.",
            "experience": "Align candidate experience levels more closely with requirements. Check min/max year ranges carefully.",
            "rate": "Review rate expectations against client budget. Consider proposing candidates within budget range.",
            "culture": "Include more details about candidate's communication skills and team experience in submissions.",
            "availability": "Prioritize candidates who can start within the required timeline. Verify notice periods before submission.",
            "location": "Confirm candidate willingness to work from required location. Clarify remote/hybrid expectations.",
            "quality": "Improve resume formatting and completeness. Ensure all submission notes are detailed and professional.",
        }
        return advice_map.get(category, "Review submission quality and alignment with requirements.")

    def _generate_recommendations(self, analysis: FeedbackAnalysis) -> List[str]:
        """Generate high-level recommendations based on analysis."""
        recs = []

        if analysis.shortlist_rate < 30:
            recs.append("Submission quality needs improvement — shortlist rate is below 30%")
        elif analysis.shortlist_rate > 70:
            recs.append("Excellent submission quality — maintain current approach")

        high_severity = [i for i in analysis.insights if i.severity == "HIGH"]
        if high_severity:
            recs.append(f"Address {len(high_severity)} high-severity issue(s) immediately")
            for hs in high_severity:
                recs.append(f"  - {hs.actionable_advice}")

        if analysis.rejected_count > analysis.shortlisted_count * 2:
            recs.append("Consider pre-screening candidates more thoroughly before submission")

        return recs
