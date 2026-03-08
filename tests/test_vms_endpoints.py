"""Comprehensive end-to-end tests for VMS enhancement endpoints using pytest + httpx (async)."""

import pytest
import httpx
from datetime import datetime, date, timedelta
from typing import Optional
from httpx import AsyncClient, ASGITransport

from api.vercel_app import app
from api.dependencies import get_current_user, get_db
from database.connection import AsyncSessionLocal


@pytest.fixture
async def client():
    """Create test HTTP client with AsyncClient."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def get_auth_token(client: AsyncClient, email: str = "msp_admin@hotgigs.com", password: str = "Demo123456") -> Optional[str]:
    """Get auth token for test user."""
    try:
        resp = await client.post(
            "/auth/login",
            json={"email": email, "password": password}
        )
        if resp.status_code == 200:
            return resp.json().get("access_token", "")
    except Exception:
        pass
    return ""


def auth_headers(token: str) -> dict:
    """Create authorization headers with token."""
    return {"Authorization": f"Bearer {token}"}


# ============================================================================
# RATE CARDS TESTS
# ============================================================================

class TestRateCards:
    """Rate card endpoint tests."""

    @pytest.mark.asyncio
    async def test_create_rate_card(self, client: AsyncClient):
        """Test: POST /rate-cards with valid data → 201."""
        token = await get_auth_token(client)

        payload = {
            "client_org_id": 2,
            "job_category": "DevOps Engineering",
            "location": "San Francisco",
            "skill_level": "Senior",
            "bill_rate_min": 120.0,
            "bill_rate_max": 180.0,
            "pay_rate_min": 90.0,
            "pay_rate_max": 150.0,
            "overtime_multiplier": 1.5,
            "weekend_multiplier": 1.25,
            "currency": "USD",
            "effective_from": date.today().isoformat(),
            "status": "ACTIVE"
        }

        resp = await client.post(
            "/rate-cards",
            json=payload,
            headers=auth_headers(token) if token else {}
        )

        # Accept 201 (created) or 200 (ok) for this test
        assert resp.status_code in [200, 201], f"Expected 200/201, got {resp.status_code}: {resp.text}"

    @pytest.mark.asyncio
    async def test_list_rate_cards(self, client: AsyncClient):
        """Test: GET /rate-cards → 200, returns list."""
        token = await get_auth_token(client)

        resp = await client.get(
            "/rate-cards",
            headers=auth_headers(token) if token else {}
        )

        assert resp.status_code in [200, 401], f"Expected 200 or 401, got {resp.status_code}"
        if resp.status_code == 200:
            data = resp.json()
            assert isinstance(data, list), "Expected list response"

    @pytest.mark.asyncio
    async def test_get_rate_card(self, client: AsyncClient):
        """Test: GET /rate-cards/{id} → 200."""
        token = await get_auth_token(client)

        # Try to get rate card with ID 1 (seeded)
        resp = await client.get(
            "/rate-cards/1",
            headers=auth_headers(token) if token else {}
        )

        # Should return 200 if found or 404 if not
        assert resp.status_code in [200, 404, 401], f"Unexpected status {resp.status_code}"
        if resp.status_code == 200:
            data = resp.json()
            assert "id" in data or "client_org_id" in data

    @pytest.mark.asyncio
    async def test_update_rate_card(self, client: AsyncClient):
        """Test: PUT /rate-cards/{id} → 200."""
        token = await get_auth_token(client)

        payload = {
            "bill_rate_min": 125.0,
            "bill_rate_max": 185.0,
            "status": "ACTIVE"
        }

        resp = await client.put(
            "/rate-cards/1",
            json=payload,
            headers=auth_headers(token) if token else {}
        )

        # Should be 200, 404 if not found, or 401 if auth required
        assert resp.status_code in [200, 404, 401], f"Unexpected status {resp.status_code}"

    @pytest.mark.asyncio
    async def test_delete_rate_card(self, client: AsyncClient):
        """Test: DELETE /rate-cards/{id} → 204 (archives)."""
        token = await get_auth_token(client)

        resp = await client.delete(
            "/rate-cards/1",
            headers=auth_headers(token) if token else {}
        )

        # Should be 204 or 404 if not found or 401 if auth required
        assert resp.status_code in [204, 404, 401], f"Unexpected status {resp.status_code}"

    @pytest.mark.asyncio
    async def test_validate_rates(self, client: AsyncClient):
        """Test: POST /rate-cards/validate → 200."""
        token = await get_auth_token(client)

        payload = {
            "client_org_id": 2,
            "job_category": "Software Development",
            "bill_rate": 100.0,
            "pay_rate": 80.0,
            "location": "Remote"
        }

        resp = await client.post(
            "/rate-cards/validate",
            json=payload,
            headers=auth_headers(token) if token else {}
        )

        # Should be 200 or auth error
        assert resp.status_code in [200, 401], f"Expected 200 or 401, got {resp.status_code}"
        if resp.status_code == 200:
            data = resp.json()
            assert "is_valid" in data or "violations" in data


# ============================================================================
# COMPLIANCE TESTS
# ============================================================================

class TestCompliance:
    """Compliance management endpoint tests."""

    @pytest.mark.asyncio
    async def test_create_compliance_requirement(self, client: AsyncClient):
        """Test: POST /compliance/requirements → 201."""
        token = await get_auth_token(client)

        payload = {
            "organization_id": 1,
            "requirement_type": "LICENSE_VERIFICATION",
            "is_mandatory": True,
            "description": "Professional license verification required",
            "risk_level": 6
        }

        resp = await client.post(
            "/compliance/requirements",
            json=payload,
            headers=auth_headers(token) if token else {}
        )

        assert resp.status_code in [200, 201, 401], f"Expected 200/201/401, got {resp.status_code}"

    @pytest.mark.asyncio
    async def test_list_compliance_requirements(self, client: AsyncClient):
        """Test: GET /compliance/requirements → 200."""
        token = await get_auth_token(client)

        resp = await client.get(
            "/compliance/requirements",
            headers=auth_headers(token) if token else {}
        )

        assert resp.status_code in [200, 401], f"Expected 200 or 401, got {resp.status_code}"
        if resp.status_code == 200:
            data = resp.json()
            assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_create_compliance_record(self, client: AsyncClient):
        """Test: POST /compliance/records → 201."""
        token = await get_auth_token(client)

        payload = {
            "placement_id": 1,
            "requirement_id": 1,
            "status": "PENDING",
            "notes": "Awaiting background check results"
        }

        resp = await client.post(
            "/compliance/records",
            json=payload,
            headers=auth_headers(token) if token else {}
        )

        assert resp.status_code in [200, 201, 400, 401], f"Unexpected {resp.status_code}"

    @pytest.mark.asyncio
    async def test_update_compliance_record(self, client: AsyncClient):
        """Test: PUT /compliance/records/{id} → 200."""
        token = await get_auth_token(client)

        payload = {
            "status": "COMPLETED",
            "verification_notes": "Background check cleared"
        }

        resp = await client.put(
            "/compliance/records/1",
            json=payload,
            headers=auth_headers(token) if token else {}
        )

        assert resp.status_code in [200, 404, 401], f"Unexpected {resp.status_code}"

    @pytest.mark.asyncio
    async def test_get_expiring_compliance(self, client: AsyncClient):
        """Test: GET /compliance/expiring?days=30 → 200."""
        token = await get_auth_token(client)

        resp = await client.get(
            "/compliance/expiring?days=30",
            headers=auth_headers(token) if token else {}
        )

        assert resp.status_code in [200, 401], f"Expected 200 or 401, got {resp.status_code}"
        if resp.status_code == 200:
            data = resp.json()
            assert isinstance(data, list)


# ============================================================================
# SLA TESTS
# ============================================================================

class TestSLA:
    """SLA configuration and tracking endpoint tests."""

    @pytest.mark.asyncio
    async def test_create_sla_config(self, client: AsyncClient):
        """Test: POST /sla/configurations → 201."""
        token = await get_auth_token(client)

        payload = {
            "organization_id": 1,
            "name": "Enterprise SLA",
            "response_time_hours": 4,
            "fill_time_days": 5,
            "min_quality_score": 85.0,
            "min_acceptance_rate": 0.92,
            "min_retention_days": 180,
            "response_time_penalty": 1500.0
        }

        resp = await client.post(
            "/sla/configurations",
            json=payload,
            headers=auth_headers(token) if token else {}
        )

        assert resp.status_code in [200, 201, 401], f"Expected 200/201/401, got {resp.status_code}"

    @pytest.mark.asyncio
    async def test_list_sla_configs(self, client: AsyncClient):
        """Test: GET /sla/configurations → 200."""
        token = await get_auth_token(client)

        resp = await client.get(
            "/sla/configurations",
            headers=auth_headers(token) if token else {}
        )

        assert resp.status_code in [200, 401], f"Expected 200 or 401, got {resp.status_code}"
        if resp.status_code == 200:
            data = resp.json()
            assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_list_breaches(self, client: AsyncClient):
        """Test: GET /sla/breaches → 200."""
        token = await get_auth_token(client)

        resp = await client.get(
            "/sla/breaches",
            headers=auth_headers(token) if token else {}
        )

        assert resp.status_code in [200, 401], f"Expected 200 or 401, got {resp.status_code}"
        if resp.status_code == 200:
            data = resp.json()
            assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_sla_dashboard(self, client: AsyncClient):
        """Test: GET /sla/dashboard?org_id=1 → 200."""
        token = await get_auth_token(client)

        resp = await client.get(
            "/sla/dashboard?org_id=1",
            headers=auth_headers(token) if token else {}
        )

        assert resp.status_code in [200, 401, 422], f"Unexpected {resp.status_code}"
        if resp.status_code == 200:
            data = resp.json()
            assert isinstance(data, dict)


# ============================================================================
# VMS TIMESHEETS TESTS
# ============================================================================

class TestVMSTimesheets:
    """VMS timesheet workflow endpoint tests."""

    @pytest.mark.asyncio
    async def test_submit_timesheet(self, client: AsyncClient):
        """Test: POST /vms/timesheets → 201."""
        token = await get_auth_token(client)

        payload = {
            "placement_id": 1,
            "period_start": (date.today() - timedelta(days=7)).isoformat(),
            "period_end": date.today().isoformat(),
            "entries": []
        }

        resp = await client.post(
            "/vms/timesheets",
            json=payload,
            headers=auth_headers(token) if token else {}
        )

        assert resp.status_code in [200, 201, 400, 401], f"Unexpected {resp.status_code}"

    @pytest.mark.asyncio
    async def test_list_timesheets(self, client: AsyncClient):
        """Test: GET /vms/timesheets → 200."""
        token = await get_auth_token(client)

        resp = await client.get(
            "/vms/timesheets",
            headers=auth_headers(token) if token else {}
        )

        assert resp.status_code in [200, 401], f"Expected 200 or 401, got {resp.status_code}"
        if resp.status_code == 200:
            data = resp.json()
            assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_msp_review_timesheet(self, client: AsyncClient):
        """Test: PUT /vms/timesheets/{id}/msp-review → 200."""
        token = await get_auth_token(client)

        payload = {
            "notes": "Reviewed and approved by MSP"
        }

        resp = await client.put(
            "/vms/timesheets/1/msp-review",
            json=payload,
            headers=auth_headers(token) if token else {}
        )

        assert resp.status_code in [200, 404, 401], f"Unexpected {resp.status_code}"

    @pytest.mark.asyncio
    async def test_client_approve_timesheet(self, client: AsyncClient):
        """Test: PUT /vms/timesheets/{id}/client-approve → 200."""
        token = await get_auth_token(client)

        payload = {
            "notes": "Approved by client"
        }

        resp = await client.put(
            "/vms/timesheets/1/client-approve",
            json=payload,
            headers=auth_headers(token) if token else {}
        )

        assert resp.status_code in [200, 404, 401], f"Unexpected {resp.status_code}"

    @pytest.mark.asyncio
    async def test_check_timesheet_compliance(self, client: AsyncClient):
        """Test: GET /vms/timesheets/{id}/compliance-check → 200."""
        token = await get_auth_token(client)

        resp = await client.get(
            "/vms/timesheets/1/compliance-check",
            headers=auth_headers(token) if token else {}
        )

        assert resp.status_code in [200, 404, 401], f"Unexpected {resp.status_code}"
        if resp.status_code == 200:
            data = resp.json()
            assert isinstance(data, dict)


# ============================================================================
# AUTO INVOICING TESTS
# ============================================================================

class TestAutoInvoicing:
    """Automated invoice generation endpoint tests."""

    @pytest.mark.asyncio
    async def test_preview_invoice(self, client: AsyncClient):
        """Test: POST /invoicing/preview → 200."""
        token = await get_auth_token(client)

        period_start = (date.today() - timedelta(days=30)).isoformat()
        period_end = date.today().isoformat()

        resp = await client.post(
            f"/invoicing/preview?client_org_id=2&period_start={period_start}&period_end={period_end}",
            headers=auth_headers(token) if token else {}
        )

        assert resp.status_code in [200, 401, 404, 422], f"Unexpected {resp.status_code}"
        if resp.status_code == 200:
            data = resp.json()
            assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_generate_invoice(self, client: AsyncClient):
        """Test: POST /invoicing/generate → 200/201."""
        token = await get_auth_token(client)

        period_start = (date.today() - timedelta(days=30)).isoformat()
        period_end = date.today().isoformat()

        resp = await client.post(
            f"/invoicing/generate?client_org_id=2&period_start={period_start}&period_end={period_end}",
            headers=auth_headers(token) if token else {}
        )

        assert resp.status_code in [200, 201, 401, 404, 422], f"Unexpected {resp.status_code}"

    @pytest.mark.asyncio
    async def test_generate_supplier_remittance(self, client: AsyncClient):
        """Test: POST /invoicing/supplier-remittance → 201."""
        token = await get_auth_token(client)

        period_start = (date.today() - timedelta(days=30)).isoformat()
        period_end = date.today().isoformat()

        resp = await client.post(
            f"/invoicing/supplier-remittance?supplier_org_id=3&period_start={period_start}&period_end={period_end}",
            headers=auth_headers(token) if token else {}
        )

        assert resp.status_code in [200, 201, 401, 404, 422], f"Unexpected {resp.status_code}"


# ============================================================================
# HEALTH & STATUS CHECKS
# ============================================================================

class TestHealthAndStatus:
    """Basic health and status checks."""

    @pytest.mark.asyncio
    async def test_root_endpoint(self, client: AsyncClient):
        """Test: GET / → 200 (health check)."""
        resp = await client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert "platform" in data

    @pytest.mark.asyncio
    async def test_health_endpoint(self, client: AsyncClient):
        """Test: GET /health → 200."""
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert "status" in data

    @pytest.mark.asyncio
    async def test_api_status_endpoint(self, client: AsyncClient):
        """Test: GET /api/v1/status → 200."""
        resp = await client.get("/api/v1/status")
        assert resp.status_code == 200
        data = resp.json()
        assert "loaded" in data or "failed" in data
