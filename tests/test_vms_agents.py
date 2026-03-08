"""Unit tests for all 5 new VMS AI agents."""

import pytest
from typing import Dict, Any, List

from agents.rate_validation_agent import RateValidationAgent, RateValidation
from agents.compliance_verification_agent import ComplianceVerificationAgent, ComplianceVerification
from agents.workforce_forecasting_agent import WorkforceForecastingAgent
from agents.supplier_performance_prediction_agent import SupplierPerformancePredictionAgent
from agents.auto_interview_scheduling_agent import AutoInterviewSchedulingAgent


# ============================================================================
# RATE VALIDATION AGENT TESTS
# ============================================================================

class TestRateValidationAgent:
    """Unit tests for RateValidationAgent."""

    def test_agent_instantiation(self):
        """Test: Agent can be instantiated."""
        agent = RateValidationAgent()
        assert agent is not None
        assert hasattr(agent, "validate")

    def test_validate_rate_within_card_range(self):
        """Test: Rates within rate card range."""
        agent = RateValidationAgent()

        rate_card = {
            "bill_rate_min": 80.0,
            "bill_rate_max": 150.0,
            "pay_rate_min": 60.0,
            "pay_rate_max": 120.0,
        }

        result = agent.validate(
            proposed_bill_rate=100.0,
            proposed_pay_rate=80.0,
            rate_card=rate_card,
        )

        assert isinstance(result, RateValidation)
        assert result.is_compliant is True
        assert 0 <= result.overall_score <= 100
        assert result.recommendation in ["APPROVE", "REVIEW", "REJECT"]

    def test_validate_rate_outside_card_range(self):
        """Test: Rates outside rate card range."""
        agent = RateValidationAgent()

        rate_card = {
            "bill_rate_min": 80.0,
            "bill_rate_max": 150.0,
            "pay_rate_min": 60.0,
            "pay_rate_max": 120.0,
        }

        result = agent.validate(
            proposed_bill_rate=200.0,  # Too high
            proposed_pay_rate=80.0,
            rate_card=rate_card,
        )

        assert isinstance(result, RateValidation)
        assert result.is_compliant is False

    def test_validate_with_historical_rates(self):
        """Test: Validation with historical rate comparison."""
        agent = RateValidationAgent()

        historical_rates = [
            {"bill_rate": 95.0},
            {"bill_rate": 100.0},
            {"bill_rate": 105.0},
        ]

        result = agent.validate(
            proposed_bill_rate=98.0,
            proposed_pay_rate=80.0,
            historical_rates=historical_rates,
        )

        assert isinstance(result, RateValidation)
        assert 0 <= result.overall_score <= 100

    def test_validate_margin_analysis(self):
        """Test: Margin analysis within acceptable range."""
        agent = RateValidationAgent()

        # 20% margin is ideal
        result = agent.validate(
            proposed_bill_rate=100.0,
            proposed_pay_rate=80.0,  # 20% margin
        )

        assert isinstance(result, RateValidation)
        assert result.margin_percent == 20.0
        # Margin in ideal range should have high score
        assert result.overall_score >= 60

    def test_validate_margin_too_low(self):
        """Test: Margin analysis with insufficient margin."""
        agent = RateValidationAgent()

        # Only 8% margin (too low)
        result = agent.validate(
            proposed_bill_rate=100.0,
            proposed_pay_rate=92.0,
        )

        assert isinstance(result, RateValidation)
        assert result.margin_percent < 10

    def test_validate_no_rate_card(self):
        """Test: Validation without rate card (neutral case)."""
        agent = RateValidationAgent()

        result = agent.validate(
            proposed_bill_rate=100.0,
            proposed_pay_rate=80.0,
            rate_card=None,
        )

        assert isinstance(result, RateValidation)
        assert 0 <= result.overall_score <= 100

    def test_validate_return_dataclass_fields(self):
        """Test: Return dataclass has all expected fields."""
        agent = RateValidationAgent()

        result = agent.validate(
            proposed_bill_rate=100.0,
            proposed_pay_rate=80.0,
        )

        # Check all fields exist
        assert hasattr(result, "is_compliant")
        assert hasattr(result, "overall_score")
        assert hasattr(result, "bill_rate_assessment")
        assert hasattr(result, "pay_rate_assessment")
        assert hasattr(result, "margin_percent")
        assert hasattr(result, "recommendation")
        assert hasattr(result, "justification")
        assert hasattr(result, "details")


# ============================================================================
# COMPLIANCE VERIFICATION AGENT TESTS
# ============================================================================

class TestComplianceVerificationAgent:
    """Unit tests for ComplianceVerificationAgent."""

    def test_agent_instantiation(self):
        """Test: Agent can be instantiated."""
        agent = ComplianceVerificationAgent()
        assert agent is not None
        assert hasattr(agent, "verify")

    def test_verify_all_compliant(self):
        """Test: All compliance items completed."""
        agent = ComplianceVerificationAgent()

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
                "status": "COMPLETED",
                "passed": True,
            },
        ]

        result = agent.verify(records)

        assert isinstance(result, ComplianceVerification)
        assert result.is_compliant is True
        assert result.risk_level in ["LOW", "MEDIUM", "HIGH"]
        assert 0 <= result.risk_score <= 100
        assert isinstance(result.gaps, list)
        assert len(result.gaps) == 0

    def test_verify_gaps_exist(self):
        """Test: Identifies compliance gaps."""
        agent = ComplianceVerificationAgent()

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

        result = agent.verify(records)

        assert isinstance(result, ComplianceVerification)
        assert result.is_compliant is False
        assert len(result.gaps) > 0
        assert result.risk_level in ["LOW", "MEDIUM", "HIGH"]

    def test_verify_expiring_items(self):
        """Test: Identifies expiring compliance items."""
        agent = ComplianceVerificationAgent()

        from datetime import datetime, timedelta
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
        ]

        result = agent.verify(records, days_to_expiry_threshold=30)

        assert isinstance(result, ComplianceVerification)
        assert len(result.expiring_soon) > 0
        assert any("Renew" in rec for rec in result.recommendations)

    def test_verify_high_risk(self):
        """Test: Calculates high risk level."""
        agent = ComplianceVerificationAgent()

        records = [
            {
                "id": 1,
                "requirement_type": "BACKGROUND_CHECK",
                "is_mandatory": True,
                "status": "FAILED",
                "passed": False,
            },
            {
                "id": 2,
                "requirement_type": "DRUG_TEST",
                "is_mandatory": True,
                "status": "PENDING",
                "passed": None,
            },
        ]

        result = agent.verify(records)

        assert isinstance(result, ComplianceVerification)
        assert result.risk_level in ["MEDIUM", "HIGH"]
        assert result.risk_score > 30

    def test_verify_empty_records(self):
        """Test: Handles empty compliance records."""
        agent = ComplianceVerificationAgent()

        result = agent.verify([])

        assert isinstance(result, ComplianceVerification)
        assert result.is_compliant is True
        assert result.risk_level == "LOW"

    def test_verify_return_dataclass_fields(self):
        """Test: Return dataclass has all expected fields."""
        agent = ComplianceVerificationAgent()

        result = agent.verify([])

        assert hasattr(result, "is_compliant")
        assert hasattr(result, "risk_score")
        assert hasattr(result, "risk_level")
        assert hasattr(result, "gaps")
        assert hasattr(result, "expiring_soon")
        assert hasattr(result, "recommendations")
        assert hasattr(result, "details")


# ============================================================================
# WORKFORCE FORECASTING AGENT TESTS
# ============================================================================

class TestWorkforceForecastingAgent:
    """Unit tests for WorkforceForecastingAgent."""

    def test_agent_instantiation(self):
        """Test: Agent can be instantiated."""
        agent = WorkforceForecastingAgent()
        assert agent is not None
        assert hasattr(agent, "forecast")

    def test_forecast_with_empty_data(self):
        """Test: Forecast handles empty historical data."""
        agent = WorkforceForecastingAgent()

        result = agent.forecast(
            historical_placements=[],
            current_active_placements=0,
            historical_peak=0,
        )

        assert result is not None
        assert hasattr(result, "forecast_period")
        assert hasattr(result, "recommendations")

    def test_forecast_with_sample_data(self):
        """Test: Forecast with sample placement data."""
        agent = WorkforceForecastingAgent()

        historical_data = [
            {
                "job_category": "Software Development",
                "start_date": "2025-01-15",
                "skills": ["Python", "FastAPI", "Docker"],
            },
            {
                "job_category": "Software Development",
                "start_date": "2025-02-01",
                "skills": ["Python", "React", "AWS"],
            },
            {
                "job_category": "Data Engineering",
                "start_date": "2025-02-10",
                "skills": ["Python", "Spark", "Airflow"],
            },
        ]

        result = agent.forecast(
            historical_placements=historical_data,
            current_active_placements=2,
            historical_peak=10,
        )

        assert result is not None
        assert isinstance(result.predicted_demand_by_category, dict)
        assert isinstance(result.seasonal_trends, list)
        assert isinstance(result.skill_shortage_alerts, list)
        assert 0 <= result.capacity_utilization_percent <= 100
        assert isinstance(result.recommendations, list)

    def test_forecast_dataclass_fields(self):
        """Test: Forecast returns all expected dataclass fields."""
        agent = WorkforceForecastingAgent()

        result = agent.forecast([])

        assert hasattr(result, "forecast_period")
        assert hasattr(result, "predicted_demand_by_category")
        assert hasattr(result, "seasonal_trends")
        assert hasattr(result, "skill_shortage_alerts")
        assert hasattr(result, "capacity_utilization_percent")
        assert hasattr(result, "recommendations")
        assert hasattr(result, "details")


# ============================================================================
# SUPPLIER PERFORMANCE PREDICTION AGENT TESTS
# ============================================================================

class TestSupplierPerformancePredictionAgent:
    """Unit tests for SupplierPerformancePredictionAgent."""

    def test_agent_instantiation(self):
        """Test: Agent can be instantiated."""
        agent = SupplierPerformancePredictionAgent()
        assert agent is not None
        assert hasattr(agent, "predict")

    def test_predict_with_sample_supplier(self):
        """Test: Predict supplier fill probability."""
        agent = SupplierPerformancePredictionAgent()

        supplier_data = {
            "supplier_org_id": 3,
            "fill_rate": 0.75,
            "recent_fill_rate": 0.80,
            "specializations": ["Python", "FastAPI", "AWS"],
            "active_placements": 5,
            "max_capacity": 15,
            "sla_breaches_6months": 0,
            "avg_response_hours": 24,
        }

        requirement_skills = ["Python", "FastAPI"]

        result = agent.predict(supplier_data, requirement_skills)

        assert result is not None
        assert result.supplier_org_id == 3
        assert 0 <= result.fill_probability <= 100
        assert result.confidence in ["LOW", "MEDIUM", "HIGH"]
        assert isinstance(result.strengths, list)
        assert isinstance(result.risks, list)
        assert result.predicted_response_days > 0
        assert result.recommended_max_submissions > 0

    def test_predict_high_fill_probability(self):
        """Test: Predict high fill probability scenario."""
        agent = SupplierPerformancePredictionAgent()

        supplier_data = {
            "supplier_org_id": 3,
            "fill_rate": 0.95,
            "recent_fill_rate": 0.98,
            "specializations": ["Python", "FastAPI", "AWS", "Docker"],
            "active_placements": 3,
            "max_capacity": 20,
            "sla_breaches_6months": 0,
            "avg_response_hours": 12,
        }

        result = agent.predict(supplier_data, ["Python", "FastAPI", "AWS"])

        assert result.fill_probability >= 70
        assert result.confidence == "HIGH"
        assert len(result.strengths) > 0

    def test_predict_low_fill_probability(self):
        """Test: Predict low fill probability scenario."""
        agent = SupplierPerformancePredictionAgent()

        supplier_data = {
            "supplier_org_id": 4,
            "fill_rate": 0.25,
            "recent_fill_rate": 0.20,
            "specializations": ["Java", "Spring"],
            "active_placements": 18,
            "max_capacity": 20,
            "sla_breaches_6months": 4,
            "avg_response_hours": 72,
        }

        result = agent.predict(supplier_data, ["Python", "FastAPI"])

        assert result.fill_probability < 50
        assert result.confidence in ["LOW", "MEDIUM"]
        assert len(result.risks) > 0

    def test_predict_dataclass_fields(self):
        """Test: Prediction returns all expected fields."""
        agent = SupplierPerformancePredictionAgent()

        supplier_data = {"supplier_org_id": 3, "fill_rate": 0.70}

        result = agent.predict(supplier_data, [])

        assert hasattr(result, "supplier_org_id")
        assert hasattr(result, "fill_probability")
        assert hasattr(result, "confidence")
        assert hasattr(result, "strengths")
        assert hasattr(result, "risks")
        assert hasattr(result, "predicted_response_days")
        assert hasattr(result, "recommended_max_submissions")
        assert hasattr(result, "details")


# ============================================================================
# AUTO INTERVIEW SCHEDULING AGENT TESTS
# ============================================================================

class TestAutoInterviewSchedulingAgent:
    """Unit tests for AutoInterviewSchedulingAgent."""

    def test_agent_instantiation(self):
        """Test: Agent can be instantiated."""
        agent = AutoInterviewSchedulingAgent()
        assert agent is not None
        assert hasattr(agent, "recommend_slots")

    def test_recommend_slots_with_availability(self):
        """Test: Recommend interview slots with candidate availability."""
        agent = AutoInterviewSchedulingAgent()

        candidate_availability = [
            {"date": "2026-03-15", "start_hour": 9, "end_hour": 17},
            {"date": "2026-03-16", "start_hour": 10, "end_hour": 14},
        ]

        result = agent.recommend_slots(
            candidate_availability=candidate_availability,
            interviewer_timezone="America/New_York",
            candidate_timezone="America/New_York",
            urgency_level="normal",
        )

        assert result is not None
        assert isinstance(result.recommended_slots, list)
        assert 0 <= result.timezone_match_score <= 100
        assert 0 <= result.urgency_score <= 100
        assert result.top_recommendation is None or isinstance(result.top_recommendation, dict)

    def test_recommend_slots_with_multiple_dates(self):
        """Test: Recommend slots across multiple dates."""
        agent = AutoInterviewSchedulingAgent()

        candidate_availability = [
            {"date": "2026-03-15", "start_hour": 9, "end_hour": 12},
            {"date": "2026-03-16", "start_hour": 14, "end_hour": 17},
            {"date": "2026-03-17", "start_hour": 10, "end_hour": 15},
        ]

        result = agent.recommend_slots(
            candidate_availability=candidate_availability,
            urgency_level="high",
            num_slots=5,
        )

        assert result.recommended_slots is not None
        assert len(result.recommended_slots) <= 5
        if result.recommended_slots:
            assert "date" in result.recommended_slots[0]
            assert "start_time" in result.recommended_slots[0]

    def test_recommend_slots_timezone_difference(self):
        """Test: Timezone difference affects matching score."""
        agent = AutoInterviewSchedulingAgent()

        candidate_availability = [
            {"date": "2026-03-15", "start_hour": 9, "end_hour": 17},
        ]

        # Same timezone
        result_same = agent.recommend_slots(
            candidate_availability=candidate_availability,
            interviewer_timezone="America/New_York",
            candidate_timezone="America/New_York",
        )

        # Different timezone (8 hour difference)
        result_diff = agent.recommend_slots(
            candidate_availability=candidate_availability,
            interviewer_timezone="America/New_York",
            candidate_timezone="Asia/Tokyo",
        )

        # Same timezone should have higher score than different timezone
        assert result_same.timezone_match_score >= result_diff.timezone_match_score

    def test_recommend_slots_urgency_levels(self):
        """Test: Urgency level affects slot scoring."""
        agent = AutoInterviewSchedulingAgent()

        candidate_availability = [
            {"date": "2026-03-15", "start_hour": 9, "end_hour": 17},
        ]

        # Low urgency
        result_low = agent.recommend_slots(
            candidate_availability=candidate_availability,
            urgency_level="low",
        )

        # Critical urgency
        result_critical = agent.recommend_slots(
            candidate_availability=candidate_availability,
            urgency_level="critical",
        )

        # Critical urgency should have higher score than low
        assert result_critical.urgency_score > result_low.urgency_score

    def test_recommend_slots_with_existing_interviews(self):
        """Test: Avoids conflicts with existing interviews."""
        agent = AutoInterviewSchedulingAgent()

        candidate_availability = [
            {"date": "2026-03-15", "start_hour": 9, "end_hour": 17},
        ]

        existing_interviews = [
            {"date": "2026-03-15", "start_time": "10:00"},
        ]

        result = agent.recommend_slots(
            candidate_availability=candidate_availability,
            existing_interviews=existing_interviews,
        )

        # Check that no slot conflicts with existing interview
        for slot in result.recommended_slots:
            if slot["date"] == "2026-03-15":
                assert not (slot["start_time"] == "10:00")

    def test_recommend_slots_empty_availability(self):
        """Test: Handle empty candidate availability."""
        agent = AutoInterviewSchedulingAgent()

        result = agent.recommend_slots(candidate_availability=[])

        assert result.recommended_slots == []
        assert "error" in result.details

    def test_recommend_slots_dataclass_fields(self):
        """Test: Returns all expected dataclass fields."""
        agent = AutoInterviewSchedulingAgent()

        candidate_availability = [
            {"date": "2026-03-15", "start_hour": 10, "end_hour": 16},
        ]

        result = agent.recommend_slots(candidate_availability)

        assert hasattr(result, "recommended_slots")
        assert hasattr(result, "timezone_match_score")
        assert hasattr(result, "urgency_score")
        assert hasattr(result, "top_recommendation")
        assert hasattr(result, "details")


# ============================================================================
# AGENT INTEGRATION TESTS
# ============================================================================

class TestAgentIntegration:
    """Integration tests across multiple agents."""

    def test_rate_and_compliance_workflow(self):
        """Test: Rate validation + compliance verification workflow."""
        rate_agent = RateValidationAgent()
        compliance_agent = ComplianceVerificationAgent()

        # Step 1: Validate rates
        rate_result = rate_agent.validate(
            proposed_bill_rate=100.0,
            proposed_pay_rate=80.0,
        )
        assert rate_result.recommendation in ["APPROVE", "REVIEW", "REJECT"]

        # Step 2: Verify compliance
        compliance_result = compliance_agent.verify([])
        assert compliance_result.risk_level in ["LOW", "MEDIUM", "HIGH"]

        # Both should complete successfully
        assert isinstance(rate_result, RateValidation)
        assert isinstance(compliance_result, ComplianceVerification)

    def test_multiple_agent_outputs_comparable(self):
        """Test: Multiple agents produce comparable outputs."""
        rate_agent = RateValidationAgent()
        compliance_agent = ComplianceVerificationAgent()

        rate_result = rate_agent.validate(
            proposed_bill_rate=100.0,
            proposed_pay_rate=80.0,
        )

        compliance_result = compliance_agent.verify([])

        # Both return dataclasses with scores
        assert isinstance(rate_result.overall_score, (int, float))
        assert isinstance(compliance_result.risk_score, (int, float))

        # Scores should be 0-100
        assert 0 <= rate_result.overall_score <= 100
        assert 0 <= compliance_result.risk_score <= 100
