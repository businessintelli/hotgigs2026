"""Compliance verification agent — checks compliance status and calculates risk."""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class ComplianceVerification:
    is_compliant: bool
    risk_score: float
    risk_level: str
    gaps: List[Dict[str, Any]] = field(default_factory=list)
    expiring_soon: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)


class ComplianceVerificationAgent:
    WEIGHTS = {"completeness": 0.40, "timeliness": 0.25, "expiration_risk": 0.20, "provider_reliability": 0.15}

    def verify(
        self,
        compliance_records: List[Dict[str, Any]],
        days_to_expiry_threshold: int = 30,
    ) -> ComplianceVerification:
        if not compliance_records:
            return ComplianceVerification(
                is_compliant=True, risk_score=0, risk_level="LOW",
                recommendations=["No compliance requirements configured"])

        mandatory = [r for r in compliance_records if r.get("is_mandatory", True)]
        total_mandatory = len(mandatory)
        completed_mandatory = len([r for r in mandatory if r.get("status", "").upper() == "COMPLETED"])

        # 1. Completeness (40%)
        completeness = (completed_mandatory / total_mandatory * 100) if total_mandatory > 0 else 100

        # 2. Timeliness (25%)
        on_time = 0
        for r in compliance_records:
            if r.get("status", "").upper() == "COMPLETED" and r.get("required_by") and r.get("completed_at"):
                if str(r["completed_at"]) <= str(r["required_by"]):
                    on_time += 1
        timeliness = (on_time / max(completed_mandatory, 1)) * 100

        # 3. Expiration risk (20%)
        expiring = []
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        for r in compliance_records:
            if r.get("expires_at"):
                try:
                    exp = datetime.fromisoformat(str(r["expires_at"]).replace("Z", "+00:00")) if isinstance(r["expires_at"], str) else r["expires_at"]
                    days_left = (exp - now).days
                    if 0 < days_left <= days_to_expiry_threshold:
                        expiring.append({"id": r.get("id"), "days_left": days_left, "type": r.get("requirement_type")})
                except (ValueError, TypeError):
                    pass

        expiration_score = max(0, 100 - len(expiring) * 20)

        # 4. Provider reliability (15%)
        passed = len([r for r in compliance_records if r.get("passed") is True])
        failed = len([r for r in compliance_records if r.get("passed") is False])
        provider_score = (passed / max(passed + failed, 1)) * 100

        # Weighted risk (invert: higher = more risk)
        compliance_score = (
            completeness * self.WEIGHTS["completeness"] +
            timeliness * self.WEIGHTS["timeliness"] +
            expiration_score * self.WEIGHTS["expiration_risk"] +
            provider_score * self.WEIGHTS["provider_reliability"]
        )
        risk_score = max(0, 100 - compliance_score)

        risk_level = "HIGH" if risk_score >= 60 else "MEDIUM" if risk_score >= 30 else "LOW"

        gaps = [{"id": r.get("id"), "type": r.get("requirement_type"), "status": r.get("status")}
                for r in mandatory if r.get("status", "").upper() not in ("COMPLETED",)]

        recommendations = []
        if gaps:
            recommendations.append(f"Complete {len(gaps)} outstanding compliance items")
        if expiring:
            recommendations.append(f"Renew {len(expiring)} items expiring within {days_to_expiry_threshold} days")
        if risk_level == "HIGH":
            recommendations.append("Escalate to compliance team for immediate review")

        return ComplianceVerification(
            is_compliant=len(gaps) == 0 and len(expiring) == 0,
            risk_score=round(risk_score, 1), risk_level=risk_level,
            gaps=gaps, expiring_soon=expiring, recommendations=recommendations,
            details={"completeness": round(completeness, 1), "timeliness": round(timeliness, 1),
                     "expiration_score": round(expiration_score, 1), "provider_score": round(provider_score, 1)},
        )
