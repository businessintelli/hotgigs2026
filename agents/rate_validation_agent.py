"""Rate validation agent — validates proposed rates against rate cards and historical data."""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class RateValidation:
    is_compliant: bool
    overall_score: float
    bill_rate_assessment: str
    pay_rate_assessment: str
    margin_percent: float
    recommendation: str
    suggested_bill_rate: Optional[float] = None
    suggested_pay_rate: Optional[float] = None
    justification: str = ""
    details: Dict[str, Any] = field(default_factory=dict)


class RateValidationAgent:
    WEIGHTS = {"rate_card": 0.40, "historical": 0.30, "margin": 0.20, "market": 0.10}

    def validate(
        self,
        proposed_bill_rate: float,
        proposed_pay_rate: float,
        rate_card: Optional[Dict[str, Any]] = None,
        historical_rates: Optional[List[Dict[str, Any]]] = None,
        market_avg_bill: Optional[float] = None,
    ) -> RateValidation:
        scores = {}

        # 1. Rate card compliance (40%)
        if rate_card:
            bill_in = rate_card["bill_rate_min"] <= proposed_bill_rate <= rate_card["bill_rate_max"]
            pay_in = rate_card["pay_rate_min"] <= proposed_pay_rate <= rate_card["pay_rate_max"]
            if bill_in and pay_in:
                scores["rate_card"] = 100
            else:
                bill_dev = 0
                if not bill_in:
                    if proposed_bill_rate > rate_card["bill_rate_max"]:
                        bill_dev = (proposed_bill_rate - rate_card["bill_rate_max"]) / rate_card["bill_rate_max"]
                    else:
                        bill_dev = (rate_card["bill_rate_min"] - proposed_bill_rate) / rate_card["bill_rate_min"]
                scores["rate_card"] = 70 if bill_dev <= 0.10 else 30
        else:
            scores["rate_card"] = 80  # No rate card = neutral

        # 2. Historical comparison (30%)
        if historical_rates and len(historical_rates) >= 3:
            hist_bills = [r["bill_rate"] for r in historical_rates]
            avg = sum(hist_bills) / len(hist_bills)
            std = (sum((x - avg) ** 2 for x in hist_bills) / len(hist_bills)) ** 0.5
            if std > 0:
                z = abs(proposed_bill_rate - avg) / std
                scores["historical"] = max(0, 100 - z * 25)
            else:
                scores["historical"] = 100 if abs(proposed_bill_rate - avg) < 5 else 60
        else:
            scores["historical"] = 75

        # 3. Margin analysis (20%)
        margin = ((proposed_bill_rate - proposed_pay_rate) / proposed_bill_rate * 100) if proposed_bill_rate > 0 else 0
        if 15 <= margin <= 25:
            scores["margin"] = 100
        elif 10 <= margin < 15 or 25 < margin <= 35:
            scores["margin"] = 70
        else:
            scores["margin"] = 30

        # 4. Market alignment (10%)
        if market_avg_bill:
            deviation = abs(proposed_bill_rate - market_avg_bill) / market_avg_bill
            scores["market"] = max(0, 100 - deviation * 200)
        else:
            scores["market"] = 75

        overall = sum(scores[k] * self.WEIGHTS[k] for k in self.WEIGHTS)
        is_compliant = scores.get("rate_card", 80) >= 70

        bill_assess = "within_range" if scores.get("rate_card", 0) >= 70 else "out_of_range"
        pay_assess = "acceptable" if margin >= 10 else "too_high"

        rec = "APPROVE" if overall >= 70 else "REVIEW" if overall >= 50 else "REJECT"

        suggested_bill = None
        suggested_pay = None
        if rate_card and not is_compliant:
            suggested_bill = min(max(proposed_bill_rate, rate_card["bill_rate_min"]), rate_card["bill_rate_max"])
            target_margin = 0.20
            suggested_pay = suggested_bill * (1 - target_margin)

        return RateValidation(
            is_compliant=is_compliant, overall_score=round(overall, 1),
            bill_rate_assessment=bill_assess, pay_rate_assessment=pay_assess,
            margin_percent=round(margin, 2), recommendation=rec,
            suggested_bill_rate=suggested_bill, suggested_pay_rate=suggested_pay,
            justification=f"Score {overall:.0f}/100. Rate card: {scores.get('rate_card',0):.0f}, Historical: {scores.get('historical',0):.0f}, Margin: {scores.get('margin',0):.0f}, Market: {scores.get('market',0):.0f}",
            details=scores,
        )
