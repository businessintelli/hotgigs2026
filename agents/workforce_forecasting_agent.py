"""Workforce forecasting agent — predicts demand trends from historical data."""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from collections import defaultdict


@dataclass
class WorkforceForecast:
    forecast_period: str
    predicted_demand_by_category: Dict[str, int] = field(default_factory=dict)
    seasonal_trends: List[Dict[str, Any]] = field(default_factory=list)
    skill_shortage_alerts: List[Dict[str, Any]] = field(default_factory=list)
    capacity_utilization_percent: float = 0.0
    recommendations: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)


class WorkforceForecastingAgent:
    def forecast(
        self,
        historical_placements: List[Dict[str, Any]],
        current_active_placements: int = 0,
        historical_peak: int = 0,
    ) -> WorkforceForecast:
        if not historical_placements:
            return WorkforceForecast(
                forecast_period="next_quarter",
                recommendations=["Insufficient historical data for forecasting"])

        # Group by category and month
        by_category = defaultdict(int)
        by_month = defaultdict(int)
        by_skill = defaultdict(int)

        for p in historical_placements:
            cat = p.get("job_category", "unknown")
            by_category[cat] += 1

            start = str(p.get("start_date", ""))
            if len(start) >= 7:
                month = start[:7]
                by_month[month] += 1

            for skill in p.get("skills", []):
                by_skill[skill.lower()] += 1

        # Predict demand: simple moving average of last 3 months
        sorted_months = sorted(by_month.keys())
        recent = sorted_months[-3:] if len(sorted_months) >= 3 else sorted_months
        avg_monthly = sum(by_month[m] for m in recent) / max(len(recent), 1)

        predicted = {}
        total_placements = len(historical_placements)
        for cat, count in by_category.items():
            ratio = count / total_placements
            predicted[cat] = max(1, round(avg_monthly * ratio * 3))  # 3 months forecast

        # Seasonal trends
        seasonal = []
        for i in range(1, len(sorted_months)):
            prev = by_month[sorted_months[i-1]]
            curr = by_month[sorted_months[i]]
            change = ((curr - prev) / max(prev, 1)) * 100
            seasonal.append({"month": sorted_months[i], "placements": curr, "change_percent": round(change, 1)})

        # Skill shortage: skills with high demand but declining trend
        skill_alerts = []
        sorted_skills = sorted(by_skill.items(), key=lambda x: x[1], reverse=True)[:10]
        for skill, count in sorted_skills:
            if count >= 3:
                skill_alerts.append({"skill": skill, "demand_count": count, "trend": "high_demand"})

        # Capacity
        capacity = (current_active_placements / max(historical_peak, 1)) * 100 if historical_peak > 0 else 0

        recommendations = []
        if capacity > 85:
            recommendations.append("Capacity utilization above 85% — consider onboarding new suppliers")
        if avg_monthly > 0 and len(seasonal) >= 2 and seasonal[-1]["change_percent"] > 20:
            recommendations.append(f"Demand increasing — {seasonal[-1]['change_percent']:.0f}% growth last month")
        if skill_alerts:
            top_skills = [a["skill"] for a in skill_alerts[:3]]
            recommendations.append(f"High demand skills: {', '.join(top_skills)}")

        return WorkforceForecast(
            forecast_period="next_quarter",
            predicted_demand_by_category=predicted,
            seasonal_trends=seasonal[-6:],
            skill_shortage_alerts=skill_alerts,
            capacity_utilization_percent=round(capacity, 1),
            recommendations=recommendations,
            details={"avg_monthly_placements": round(avg_monthly, 1), "total_historical": total_placements},
        )
