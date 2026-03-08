"""Shared test fixtures for VMS enhancement tests."""

import pytest
import pytest_asyncio
from datetime import datetime, date, timedelta
from typing import AsyncGenerator, Optional

from httpx import AsyncClient

# Import if available (will fail gracefully)
try:
    from api.vercel_app import app
    from database.connection import get_db, AsyncSessionLocal
except ImportError:
    pass


# ============================================================================
# HTTP CLIENT FIXTURES
# ============================================================================

@pytest_asyncio.fixture
async def async_client():
    """Create async HTTP client for testing endpoints."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


# ============================================================================
# AUTHENTICATION FIXTURES
# ============================================================================

async def get_test_token(client: AsyncClient, email: str = "msp_admin@hotgigs.com", password: str = "Demo123456") -> Optional[str]:
    """Get auth token for test user."""
    try:
        resp = await client.post(
            "/auth/login",
            json={"email": email, "password": password}
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("access_token", "")
    except Exception:
        pass
    return None


def make_auth_headers(token: str) -> dict:
    """Create auth headers with bearer token."""
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


# ============================================================================
# TEST DATA FIXTURES
# ============================================================================

@pytest.fixture
def rate_card_payload():
    """Sample rate card creation payload."""
    return {
        "client_org_id": 2,
        "job_category": "Cloud Architecture",
        "location": "San Francisco",
        "skill_level": "Senior",
        "bill_rate_min": 130.0,
        "bill_rate_max": 200.0,
        "pay_rate_min": 100.0,
        "pay_rate_max": 160.0,
        "overtime_multiplier": 1.5,
        "weekend_multiplier": 1.25,
        "currency": "USD",
        "effective_from": date.today().isoformat(),
        "status": "ACTIVE"
    }


@pytest.fixture
def compliance_requirement_payload():
    """Sample compliance requirement creation payload."""
    return {
        "organization_id": 1,
        "requirement_type": "SECURITY_CLEARANCE",
        "is_mandatory": True,
        "description": "Security clearance level required for placement",
        "risk_level": 9
    }


@pytest.fixture
def timesheet_payload():
    """Sample timesheet creation payload."""
    return {
        "placement_id": 1,
        "period_start": (date.today() - timedelta(days=7)).isoformat(),
        "period_end": date.today().isoformat(),
        "entries": [],
        "total_hours": 40.0,
        "notes": "Weekly timesheet submission"
    }


@pytest.fixture
def sla_config_payload():
    """Sample SLA configuration payload."""
    return {
        "organization_id": 1,
        "name": "Standard VMS SLA",
        "response_time_hours": 24,
        "fill_time_days": 15,
        "min_quality_score": 80.0,
        "min_acceptance_rate": 0.85,
        "min_retention_days": 90,
        "response_time_penalty": 750.0
    }


@pytest.fixture
def invoice_generation_params():
    """Sample invoice generation parameters."""
    period_start = (date.today() - timedelta(days=30)).isoformat()
    period_end = date.today().isoformat()
    return {
        "client_org_id": 2,
        "period_start": period_start,
        "period_end": period_end
    }


@pytest.fixture
def supplier_data():
    """Sample supplier performance data."""
    return {
        "supplier_org_id": 3,
        "fill_rate": 0.78,
        "recent_fill_rate": 0.82,
        "specializations": ["Python", "FastAPI", "Kubernetes", "AWS"],
        "active_placements": 4,
        "max_capacity": 12,
        "sla_breaches_6months": 1,
        "avg_response_hours": 18,
    }


@pytest.fixture
def compliance_records():
    """Sample compliance records for verification."""
    now = datetime.utcnow()
    return [
        {
            "id": 1,
            "requirement_type": "BACKGROUND_CHECK",
            "is_mandatory": True,
            "status": "COMPLETED",
            "passed": True,
            "completed_at": now.isoformat(),
            "expires_at": (now + timedelta(days=365)).isoformat(),
        },
        {
            "id": 2,
            "requirement_type": "CERTIFICATION",
            "is_mandatory": False,
            "status": "COMPLETED",
            "passed": True,
            "completed_at": now.isoformat(),
            "expires_at": (now + timedelta(days=180)).isoformat(),
        },
    ]


@pytest.fixture
def historical_placements():
    """Sample historical placement data for forecasting."""
    return [
        {
            "job_category": "Software Development",
            "start_date": "2025-12-01",
            "skills": ["Python", "Django", "PostgreSQL"],
        },
        {
            "job_category": "Software Development",
            "start_date": "2026-01-05",
            "skills": ["Python", "FastAPI", "Redis"],
        },
        {
            "job_category": "Data Engineering",
            "start_date": "2026-01-12",
            "skills": ["Python", "Spark", "SQL"],
        },
        {
            "job_category": "Software Development",
            "start_date": "2026-02-01",
            "skills": ["Go", "Kubernetes", "gRPC"],
        },
        {
            "job_category": "Data Engineering",
            "start_date": "2026-02-15",
            "skills": ["Scala", "Spark", "Kafka"],
        },
    ]


@pytest.fixture
def candidate_availability():
    """Sample candidate interview availability."""
    return [
        {
            "date": "2026-03-16",
            "start_hour": 9,
            "end_hour": 12,
        },
        {
            "date": "2026-03-17",
            "start_hour": 14,
            "end_hour": 17,
        },
        {
            "date": "2026-03-18",
            "start_hour": 10,
            "end_hour": 15,
        },
    ]


# ============================================================================
# MARKERS
# ============================================================================

def pytest_configure(config):
    """Register custom pytest markers."""
    config.addinivalue_line("markers", "vms: VMS enhancement endpoint tests")
    config.addinivalue_line("markers", "rate_card: Rate card related tests")
    config.addinivalue_line("markers", "compliance: Compliance related tests")
    config.addinivalue_line("markers", "sla: SLA related tests")
    config.addinivalue_line("markers", "timesheet: Timesheet related tests")
    config.addinivalue_line("markers", "invoice: Invoice related tests")
    config.addinivalue_line("markers", "agent: AI agent tests")
