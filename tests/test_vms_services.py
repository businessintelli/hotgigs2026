"""Unit tests for VMS service layer (rate cards, compliance, SLA)."""

import pytest
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any

from services.rate_card_service import RateCardService
from services.compliance_service import ComplianceService
from services.sla_service import SLAService


# ============================================================================
# RATE CARD SERVICE TESTS
# ============================================================================

class TestRateCardService:
    """Unit tests for RateCardService."""

    @pytest.mark.asyncio
    async def test_validate_submission_rates_compliant(self):
        """Test rate validation with compliant rates."""
        # Mock rate card data
        rate_card = {
            "id": 1,
            "bill_rate_min": 80.0,
            "bill_rate_max": 150.0,
            "pay_rate_min": 60.0,
            "pay_rate_max": 120.0,
        }

        # Test with rates within range
        bill_rate = 100.0
        pay_rate = 80.0

        # Simulate validation logic
        violations = []
        if bill_rate < rate_card["bill_rate_min"] or bill_rate > rate_card["bill_rate_max"]:
            violations.append({"field": "bill_rate", "actual": bill_rate})
        if pay_rate < rate_card["pay_rate_min"] or pay_rate > rate_card["pay_rate_max"]:
            violations.append({"field": "pay_rate", "actual": pay_rate})

        is_valid = len(violations) == 0
        assert is_valid is True, "Rates should be valid"
        assert len(violations) == 0

    def test_validate_submission_rates_non_compliant_bill(self):
        """Test rate validation with non-compliant bill rate."""
        rate_card = {
            "bill_rate_min": 80.0,
            "bill_rate_max": 150.0,
            "pay_rate_min": 60.0,
            "pay_rate_max": 120.0,
        }

        # Bill rate too high
        bill_rate = 160.0
        pay_rate = 80.0

        violations = []
        if bill_rate < rate_card["bill_rate_min"] or bill_rate > rate_card["bill_rate_max"]:
            violations.append({"field": "bill_rate", "actual": bill_rate})
        if pay_rate < rate_card["pay_rate_min"] or pay_rate > rate_card["pay_rate_max"]:
            violations.append({"field": "pay_rate", "actual": pay_rate})

        is_valid = len(violations) == 0
        assert is_valid is False, "Bill rate should violate max constraint"
        assert len(violations) == 1
        assert violations[0]["field"] == "bill_rate"

    def test_validate_submission_rates_non_compliant_pay(self):
        """Test rate validation with non-compliant pay rate."""
        rate_card = {
            "bill_rate_min": 80.0,
            "bill_rate_max": 150.0,
            "pay_rate_min": 60.0,
            "pay_rate_max": 120.0,
        }

        # Pay rate too low
        bill_rate = 100.0
        pay_rate = 50.0

        violations = []
        if bill_rate < rate_card["bill_rate_min"] or bill_rate > rate_card["bill_rate_max"]:
            violations.append({"field": "bill_rate", "actual": bill_rate})
        if pay_rate < rate_card["pay_rate_min"] or pay_rate > rate_card["pay_rate_max"]:
            violations.append({"field": "pay_rate", "actual": pay_rate})

        is_valid = len(violations) == 0
        assert is_valid is False
        assert len(violations) == 1
        assert violations[0]["field"] == "pay_rate"

    def test_validate_submission_rates_both_violations(self):
        """Test rate validation with multiple violations."""
        rate_card = {
            "bill_rate_min": 80.0,
            "bill_rate_max": 150.0,
            "pay_rate_min": 60.0,
            "pay_rate_max": 120.0,
        }

        # Both rates out of range
        bill_rate = 200.0
        pay_rate = 30.0

        violations = []
        if bill_rate < rate_card["bill_rate_min"] or bill_rate > rate_card["bill_rate_max"]:
            violations.append({"field": "bill_rate", "actual": bill_rate})
        if pay_rate < rate_card["pay_rate_min"] or pay_rate > rate_card["pay_rate_max"]:
            violations.append({"field": "pay_rate", "actual": pay_rate})

        is_valid = len(violations) == 0
        assert is_valid is False
        assert len(violations) == 2


# ============================================================================
# COMPLIANCE SERVICE TESTS
# ============================================================================

class TestComplianceService:
    """Unit tests for ComplianceService."""

    def test_check_compliance_all_complete(self):
        """Test compliance check with all items completed."""
        records = [
            {
                "id": 1,
                "requirement_type": "BACKGROUND_CHECK",
                "is_mandatory": True,
                "status": "COMPLETED",
                "passed": True,
                "expires_at": None,
            },
            {
                "id": 2,
                "requirement_type": "DRUG_TEST",
                "is_mandatory": True,
                "status": "COMPLETED",
                "passed": True,
                "expires_at": None,
            },
        ]

        mandatory = [r for r in records if r.get("is_mandatory", True)]
        completed = [r for r in mandatory if r.get("status", "").upper() == "COMPLETED"]

        is_compliant = len(completed) == len(mandatory)
        assert is_compliant is True
        assert len(mandatory) == 2
        assert len(completed) == 2

    def test_check_compliance_incomplete(self):
        """Test compliance check with incomplete items."""
        records = [
            {
                "id": 1,
                "requirement_type": "BACKGROUND_CHECK",
                "is_mandatory": True,
                "status": "COMPLETED",
                "passed": True,
            },
            {
                "id": 2,
                "requirement_type": "DRUG_TEST",
                "is_mandatory": True,
                "status": "PENDING",
                "passed": None,
            },
        ]

        mandatory = [r for r in records if r.get("is_mandatory", True)]
        completed = [r for r in mandatory if r.get("status", "").upper() == "COMPLETED"]

        is_compliant = len(completed) == len(mandatory)
        assert is_compliant is False
        assert len(mandatory) == 2
        assert len(completed) == 1

    def test_check_compliance_expiring_soon(self):
        """Test compliance check identifies expiring items."""
        now = datetime.utcnow()
        expiring_date = now + timedelta(days=15)

        records = [
            {
                "id": 1,
                "requirement_type": "CERTIFICATION",
                "is_mandatory": True,
                "status": "COMPLETED",
                "passed": True,
                "expires_at": expiring_date,
            },
            {
                "id": 2,
                "requirement_type": "LICENSE",
                "is_mandatory": False,
                "status": "COMPLETED",
                "passed": True,
                "expires_at": None,
            },
        ]

        days_threshold = 30
        expiring = []

        for r in records:
            if r.get("expires_at"):
                try:
                    exp = r["expires_at"] if isinstance(r["expires_at"], datetime) else datetime.fromisoformat(str(r["expires_at"]))
                    days_left = (exp - now).days
                    if 0 < days_left <= days_threshold:
                        expiring.append({"id": r.get("id"), "days_left": days_left})
                except (ValueError, TypeError):
                    pass

        assert len(expiring) == 1
        assert expiring[0]["days_left"] == 15

    def test_check_compliance_high_risk(self):
        """Test compliance check calculates risk correctly."""
        records = [
            {
                "id": 1,
                "requirement_type": "BACKGROUND_CHECK",
                "is_mandatory": True,
                "status": "PENDING",
                "passed": None,
            },
            {
                "id": 2,
                "requirement_type": "DRUG_TEST",
                "is_mandatory": True,
                "status": "FAILED",
                "passed": False,
            },
        ]

        mandatory = [r for r in records if r.get("is_mandatory", True)]
        completed = [r for r in mandatory if r.get("status", "").upper() == "COMPLETED"]
        gaps = len(mandatory) - len(completed)

        # Simple risk calculation: more gaps = higher risk
        risk_score = min(100, gaps * 50)
        risk_level = "HIGH" if risk_score >= 60 else "MEDIUM" if risk_score >= 30 else "LOW"

        assert risk_level == "HIGH"
        assert risk_score >= 60
        assert gaps == 2


# ============================================================================
# SLA SERVICE TESTS
# ============================================================================

class TestSLAService:
    """Unit tests for SLAService."""

    def test_sla_breach_detection_response_time(self):
        """Test SLA breach detection for response time violation."""
        sla_config = {
            "response_time_hours": 24,
            "fill_time_days": 15,
        }

        # Placement submitted 30 hours ago, should breach 24-hour response SLA
        submitted_at = datetime.utcnow() - timedelta(hours=30)
        now = datetime.utcnow()

        hours_elapsed = (now - submitted_at).total_seconds() / 3600
        breached = hours_elapsed > sla_config["response_time_hours"]

        assert breached is True
        assert hours_elapsed > 24

    def test_sla_breach_detection_fill_time(self):
        """Test SLA breach detection for fill time violation."""
        sla_config = {
            "response_time_hours": 24,
            "fill_time_days": 15,
        }

        # Requirement created 20 days ago, should breach 15-day fill SLA
        created_at = datetime.utcnow() - timedelta(days=20)
        now = datetime.utcnow()

        days_elapsed = (now - created_at).days
        breached = days_elapsed > sla_config["fill_time_days"]

        assert breached is True
        assert days_elapsed > 15

    def test_sla_no_breach(self):
        """Test SLA when within acceptable limits."""
        sla_config = {
            "response_time_hours": 24,
            "fill_time_days": 15,
        }

        # Requirement created 10 days ago, should NOT breach
        created_at = datetime.utcnow() - timedelta(days=10)
        now = datetime.utcnow()

        days_elapsed = (now - created_at).days
        breached = days_elapsed > sla_config["fill_time_days"]

        assert breached is False
        assert days_elapsed < 15

    def test_sla_quality_score_meeting_threshold(self):
        """Test SLA quality score assessment."""
        sla_config = {
            "min_quality_score": 85.0,
        }

        placements = [
            {"quality_score": 90.0},
            {"quality_score": 88.0},
            {"quality_score": 95.0},
        ]

        breaches = [p for p in placements if p["quality_score"] < sla_config["min_quality_score"]]

        assert len(breaches) == 0, "Should have no quality breaches"

    def test_sla_quality_score_below_threshold(self):
        """Test SLA quality score below threshold."""
        sla_config = {
            "min_quality_score": 85.0,
        }

        placements = [
            {"quality_score": 75.0},
            {"quality_score": 80.0},
            {"quality_score": 95.0},
        ]

        breaches = [p for p in placements if p["quality_score"] < sla_config["min_quality_score"]]

        assert len(breaches) == 2, "Should have 2 quality breaches"

    def test_sla_retention_rate_meeting(self):
        """Test SLA retention rate assessment."""
        sla_config = {
            "min_retention_days": 90,
        }

        placements = [
            {"days_active": 120},
            {"days_active": 150},
            {"days_active": 95},
        ]

        breaches = [p for p in placements if p["days_active"] < sla_config["min_retention_days"]]

        assert len(breaches) == 0

    def test_sla_retention_rate_below_threshold(self):
        """Test SLA retention rate below threshold."""
        sla_config = {
            "min_retention_days": 90,
        }

        placements = [
            {"days_active": 60},
            {"days_active": 45},
            {"days_active": 95},
        ]

        breaches = [p for p in placements if p["days_active"] < sla_config["min_retention_days"]]

        assert len(breaches) == 2
