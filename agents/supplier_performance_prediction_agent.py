"""Supplier performance prediction agent — predicts fill likelihood."""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class SupplierPrediction:
    supplier_org_id: int
    fill_probability: float
    confidence: str
    strengths: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    predicted_response_days: float = 0.0
    recommended_max_submissions: int = 3
    details: Dict[str, Any] = field(default_factory=dict)


class SupplierPerformancePredictionAgent:
    WEIGHTS = {
        "fill_rate": 0.30, "specialization": 0.25,
        "capacity": 0.20, "trend": 0.15, "sla": 0.10,
    }

    def predict(
        self,
        supplier_data: Dict[str, Any],
        requirement_skills: List[str],
    ) -> SupplierPrediction:
        scores = {}
        strengths = []
        risks = []

        # 1. Historical fill rate (30%)
        fill_rate = supplier_data.get("fill_rate", 0)
        scores["fill_rate"] = min(fill_rate * 100, 100)
        if fill_rate >= 0.7:
            strengths.append(f"Strong fill rate: {fill_rate*100:.0f}%")
        elif fill_rate < 0.3:
            risks.append(f"Low fill rate: {fill_rate*100:.0f}%")

        # 2. Specialization match (25%)
        specializations = [s.lower() for s in supplier_data.get("specializations", [])]
        req_skills = [s.lower() for s in requirement_skills]
        if req_skills:
            overlap = len(set(specializations) & set(req_skills)) / len(req_skills)
            scores["specialization"] = overlap * 100
            if overlap >= 0.5:
                strengths.append(f"Good specialization match: {overlap*100:.0f}%")
        else:
            scores["specialization"] = 50

        # 3. Current capacity (20%)
        active = supplier_data.get("active_placements", 0)
        capacity = supplier_data.get("max_capacity", 20)
        utilization = active / max(capacity, 1)
        if utilization < 0.5:
            scores["capacity"] = 100
            strengths.append("Ample capacity available")
        elif utilization < 0.75:
            scores["capacity"] = 70
        elif utilization < 0.9:
            scores["capacity"] = 40
            risks.append("Near capacity limit")
        else:
            scores["capacity"] = 10
            risks.append("At or over capacity")

        # 4. Recent trend (15%)
        recent_rate = supplier_data.get("recent_fill_rate", fill_rate)
        if recent_rate > fill_rate * 1.1:
            scores["trend"] = 90
            strengths.append("Improving performance trend")
        elif recent_rate >= fill_rate * 0.9:
            scores["trend"] = 70
        else:
            scores["trend"] = 40
            risks.append("Declining performance trend")

        # 5. SLA compliance (10%)
        breaches = supplier_data.get("sla_breaches_6months", 0)
        if breaches == 0:
            scores["sla"] = 100
            strengths.append("Clean SLA record")
        elif breaches <= 2:
            scores["sla"] = 70
        else:
            scores["sla"] = max(0, 100 - breaches * 15)
            risks.append(f"{breaches} SLA breaches in last 6 months")

        probability = sum(scores[k] * self.WEIGHTS[k] for k in self.WEIGHTS)
        confidence = "HIGH" if probability >= 70 else "MEDIUM" if probability >= 45 else "LOW"

        avg_response = supplier_data.get("avg_response_hours", 48)
        predicted_days = avg_response / 24

        max_subs = 5 if probability >= 70 else 3 if probability >= 45 else 2

        return SupplierPrediction(
            supplier_org_id=supplier_data.get("supplier_org_id", 0),
            fill_probability=round(probability, 1),
            confidence=confidence, strengths=strengths, risks=risks,
            predicted_response_days=round(predicted_days, 1),
            recommended_max_submissions=max_subs, details=scores,
        )
