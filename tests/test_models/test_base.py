"""Tests for Base Model."""
import pytest
from datetime import datetime

from models.base import BaseModel


class TestBaseModel:
    """Test suite for BaseModel."""

    @pytest.mark.unit
    def test_base_model_has_id(self):
        """Test that base model has id field."""
        # Create a minimal model for testing
        class TestModel(BaseModel):
            __tablename__ = "test_models"

        model = TestModel()
        assert hasattr(model, "id")

    @pytest.mark.unit
    def test_base_model_has_timestamps(self):
        """Test that base model has timestamp fields."""
        class TestModel(BaseModel):
            __tablename__ = "test_models"

        model = TestModel()
        assert hasattr(model, "created_at")
        assert hasattr(model, "updated_at")

    @pytest.mark.unit
    def test_base_model_created_at_timestamp(self, db_session):
        """Test created_at timestamp is set."""
        from models.candidate import Candidate

        candidate = Candidate(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
        )

        db_session.add(candidate)
        db_session.commit()

        assert candidate.created_at is not None
        assert isinstance(candidate.created_at, datetime)

    @pytest.mark.unit
    def test_base_model_updated_at_timestamp(self, db_session):
        """Test updated_at timestamp is updated."""
        from models.candidate import Candidate

        candidate = Candidate(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
        )

        db_session.add(candidate)
        db_session.commit()

        original_updated_at = candidate.updated_at

        # Update the candidate
        candidate.first_name = "Jane"
        db_session.commit()

        assert candidate.updated_at >= original_updated_at

    @pytest.mark.unit
    def test_base_model_is_active_flag(self, db_session):
        """Test is_active flag on base model."""
        from models.candidate import Candidate

        candidate = Candidate(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
        )

        db_session.add(candidate)
        db_session.commit()

        assert candidate.is_active is True

    @pytest.mark.unit
    def test_base_model_soft_delete(self, db_session):
        """Test soft delete functionality."""
        from models.candidate import Candidate

        candidate = Candidate(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
        )

        db_session.add(candidate)
        db_session.commit()

        candidate_id = candidate.id

        # Soft delete
        candidate.is_active = False
        db_session.commit()

        # Verify soft delete
        assert candidate.is_active is False

        # Original record should still exist in DB
        from sqlalchemy import select

        stmt = select(Candidate).where(Candidate.id == candidate_id)
        result = db_session.execute(stmt)
        found_candidate = result.scalar_one_or_none()

        assert found_candidate is not None
        assert found_candidate.is_active is False
