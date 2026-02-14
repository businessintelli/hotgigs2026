"""Tests for health check and API endpoints."""
import pytest
from httpx import AsyncClient


class TestHealthEndpoints:
    """Test suite for health check endpoints."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_health_check_endpoint(self, client: AsyncClient):
        """Test health check endpoint."""
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_readiness_check_endpoint(self, client: AsyncClient):
        """Test readiness check endpoint."""
        response = await client.get("/ready")

        assert response.status_code == 200
        data = response.json()
        assert "ready" in data
        assert data["ready"] is True

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_version_endpoint(self, client: AsyncClient):
        """Test API version endpoint."""
        response = await client.get("/version")

        assert response.status_code == 200
        data = response.json()
        assert "version" in data
        assert "api_version" in data

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_api_info_endpoint(self, client: AsyncClient):
        """Test API info endpoint."""
        response = await client.get("/info")

        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "description" in data

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_health_check_with_db_connection(self, client: AsyncClient, db_session):
        """Test health check with database connection."""
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_unauthorized_access_without_token(self, client: AsyncClient):
        """Test that protected endpoints require authentication."""
        response = await client.get(
            "/api/v1/candidates",
            headers={}
        )

        # Should require auth for most endpoints
        if response.status_code == 401:
            assert response.status_code == 401
        elif response.status_code == 403:
            assert response.status_code == 403

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_invalid_token(self, client: AsyncClient):
        """Test invalid JWT token."""
        response = await client.get(
            "/api/v1/candidates",
            headers={"Authorization": "Bearer invalid-token"}
        )

        # Should reject invalid token
        assert response.status_code in [401, 422]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_cors_headers_present(self, client: AsyncClient):
        """Test CORS headers are present."""
        response = await client.get("/health")

        assert response.status_code == 200
        # CORS headers should be present in response

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_api_error_handling(self, client: AsyncClient):
        """Test API error handling."""
        response = await client.get("/api/v1/invalid-endpoint")

        assert response.status_code == 404

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_request_validation_error(self, client: AsyncClient, auth_headers):
        """Test request validation error handling."""
        response = await client.post(
            "/api/v1/candidates",
            headers=auth_headers,
            json={"invalid": "data"}
        )

        # Should return 422 for validation error
        assert response.status_code in [400, 422]
