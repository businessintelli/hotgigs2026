"""Tests for security utilities."""
import pytest
from datetime import timedelta, datetime
from unittest.mock import patch

from utils.security import (
    create_access_token,
    verify_token,
    hash_password,
    verify_password,
)


class TestSecurity:
    """Test suite for security utilities."""

    @pytest.mark.unit
    def test_hash_password(self):
        """Test password hashing."""
        password = "test_password_123"
        hashed = hash_password(password)

        assert hashed != password
        assert len(hashed) > 0

    @pytest.mark.unit
    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "test_password_123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    @pytest.mark.unit
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False

    @pytest.mark.unit
    def test_create_access_token(self):
        """Test access token creation."""
        data = {"sub": "123", "email": "test@example.com"}
        token = create_access_token(data=data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    @pytest.mark.unit
    def test_create_access_token_with_expiry(self):
        """Test access token creation with custom expiry."""
        data = {"sub": "123"}
        expires_delta = timedelta(hours=2)
        token = create_access_token(data=data, expires_delta=expires_delta)

        assert token is not None

    @pytest.mark.unit
    def test_verify_token_valid(self):
        """Test token verification with valid token."""
        data = {"sub": "123", "email": "test@example.com"}
        token = create_access_token(data=data)

        payload = verify_token(token)

        assert payload is not None
        assert payload["sub"] == "123"
        assert payload["email"] == "test@example.com"

    @pytest.mark.unit
    def test_verify_token_invalid(self):
        """Test token verification with invalid token."""
        invalid_token = "invalid.token.here"

        payload = verify_token(invalid_token)

        assert payload is None

    @pytest.mark.unit
    def test_verify_token_expired(self):
        """Test token verification with expired token."""
        data = {"sub": "123"}
        # Create token with very short expiry
        with patch("datetime.datetime") as mock_datetime:
            mock_now = datetime(2024, 1, 1, 10, 0, 0)
            mock_datetime.utcnow.return_value = mock_now
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            token = create_access_token(
                data=data,
                expires_delta=timedelta(seconds=-1)  # Already expired
            )

        # Try to verify expired token
        payload = verify_token(token)

        # May return None or raise exception depending on implementation
        assert payload is None or isinstance(payload, type(None))

    @pytest.mark.unit
    def test_create_token_includes_exp(self):
        """Test that token includes expiry claim."""
        data = {"sub": "123"}
        token = create_access_token(data=data)

        payload = verify_token(token)

        assert payload is not None
        assert "exp" in payload

    @pytest.mark.unit
    def test_create_token_includes_iat(self):
        """Test that token includes issued-at claim."""
        data = {"sub": "123"}
        token = create_access_token(data=data)

        payload = verify_token(token)

        assert payload is not None
        assert "iat" in payload

    @pytest.mark.unit
    def test_password_hash_different_each_time(self):
        """Test that same password produces different hashes."""
        password = "test_password_123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True

    @pytest.mark.unit
    def test_token_with_custom_data(self):
        """Test token with custom data claims."""
        data = {
            "sub": "user_123",
            "email": "user@example.com",
            "role": "admin",
            "permissions": ["read", "write"],
        }
        token = create_access_token(data=data)
        payload = verify_token(token)

        assert payload["sub"] == "user_123"
        assert payload["email"] == "user@example.com"
        assert payload["role"] == "admin"
        assert payload["permissions"] == ["read", "write"]

    @pytest.mark.unit
    def test_hash_password_length(self):
        """Test that hashed passwords have reasonable length."""
        password = "short"
        hashed = hash_password(password)

        # Most hash algorithms produce hashes longer than original
        assert len(hashed) > len(password)
