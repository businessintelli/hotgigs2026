"""Smoke tests for platform health."""
import pytest
from httpx import AsyncClient


class TestSmokeTests:
    """Quick health check tests for platform components."""

    @pytest.mark.smoke
    @pytest.mark.asyncio
    async def test_database_connectivity(self, db_session):
        """Test database connectivity."""
        # Simple query to verify DB works
        from sqlalchemy import text

        result = await db_session.execute(text("SELECT 1"))
        assert result.scalar() == 1

    @pytest.mark.smoke
    @pytest.mark.asyncio
    async def test_api_health_check(self, client: AsyncClient):
        """Test API is responding to health checks."""
        response = await client.get("/health")
        assert response.status_code == 200

    @pytest.mark.smoke
    @pytest.mark.asyncio
    async def test_create_user(self, db_session, sample_user):
        """Test user creation."""
        from models.user import User

        user = User(
            email="smoketest@example.com",
            username="smoketest",
            hashed_password="hash",
            first_name="Smoke",
            last_name="Test",
        )

        db_session.add(user)
        db_session.commit()

        assert user.id is not None

    @pytest.mark.smoke
    @pytest.mark.asyncio
    async def test_create_candidate(self, db_session, sample_candidate):
        """Test candidate creation."""
        assert sample_candidate.id is not None

    @pytest.mark.smoke
    @pytest.mark.asyncio
    async def test_create_requirement(self, db_session, sample_requirement):
        """Test requirement creation."""
        assert sample_requirement.id is not None

    @pytest.mark.smoke
    @pytest.mark.asyncio
    async def test_app_startup(self, client: AsyncClient):
        """Test application startup."""
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    @pytest.mark.smoke
    @pytest.mark.asyncio
    async def test_database_tables_exist(self, db_session):
        """Test all database tables exist."""
        from sqlalchemy import inspect

        inspector = inspect(db_session.sync_session.get_bind())
        tables = inspector.get_table_names()

        # Check for essential tables
        assert "users" in tables or "user" in tables.lower()
        assert "candidates" in tables
        assert "requirements" in tables

    @pytest.mark.smoke
    @pytest.mark.asyncio
    async def test_basic_query(self, db_session, sample_candidate):
        """Test basic database query."""
        from models.candidate import Candidate
        from sqlalchemy import select

        stmt = select(Candidate).where(Candidate.id == sample_candidate.id)
        result = await db_session.execute(stmt)
        candidate = result.scalar_one_or_none()

        assert candidate is not None
        assert candidate.email == "john.doe@example.com"

    @pytest.mark.smoke
    def test_configuration_loaded(self, test_settings):
        """Test configuration is loaded correctly."""
        assert test_settings.debug is True
        assert test_settings.jwt_secret is not None

    @pytest.mark.smoke
    @pytest.mark.asyncio
    async def test_async_functionality(self):
        """Test async/await functionality."""
        import asyncio

        async def test_task():
            await asyncio.sleep(0.01)
            return "success"

        result = await test_task()
        assert result == "success"
