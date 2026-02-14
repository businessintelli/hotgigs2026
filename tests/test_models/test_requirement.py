"""Tests for Requirement model."""
import pytest
from datetime import datetime, timedelta
from sqlalchemy import select

from models.requirement import Requirement
from models.customer import Customer
from models.enums import RequirementStatus, Priority


class TestRequirement:
    """Test suite for Requirement model."""

    @pytest.mark.unit
    def test_create_requirement(self, sample_customer, db_session):
        """Test creating a requirement."""
        requirement = Requirement(
            customer_id=sample_customer.id,
            title="Senior Python Engineer",
            description="Looking for experienced Python engineer",
            status=RequirementStatus.ACTIVE,
        )

        db_session.add(requirement)
        db_session.commit()

        assert requirement.id is not None
        assert requirement.title == "Senior Python Engineer"
        assert requirement.status == RequirementStatus.ACTIVE

    @pytest.mark.unit
    def test_requirement_required_fields(self, sample_customer, db_session):
        """Test requirement required fields."""
        requirement = Requirement(
            customer_id=sample_customer.id,
            title="Software Engineer",
        )

        db_session.add(requirement)
        db_session.commit()

        assert requirement.customer_id == sample_customer.id
        assert requirement.title == "Software Engineer"

    @pytest.mark.unit
    def test_requirement_skills_required(self, sample_customer, db_session):
        """Test required skills for a requirement."""
        skills_required = ["Python", "FastAPI", "SQL", "PostgreSQL"]

        requirement = Requirement(
            customer_id=sample_customer.id,
            title="Senior Python Engineer",
            skills_required=skills_required,
        )

        db_session.add(requirement)
        db_session.commit()

        assert requirement.skills_required == skills_required
        assert len(requirement.skills_required) == 4
        assert "Python" in requirement.skills_required

    @pytest.mark.unit
    def test_requirement_skills_preferred(self, sample_customer, db_session):
        """Test preferred skills for a requirement."""
        skills_preferred = ["Docker", "Kubernetes", "GraphQL"]

        requirement = Requirement(
            customer_id=sample_customer.id,
            title="Senior Python Engineer",
            skills_preferred=skills_preferred,
        )

        db_session.add(requirement)
        db_session.commit()

        assert requirement.skills_preferred == skills_preferred
        assert "Docker" in requirement.skills_preferred

    @pytest.mark.unit
    def test_requirement_experience_levels(self, sample_customer, db_session):
        """Test experience level requirements."""
        requirement = Requirement(
            customer_id=sample_customer.id,
            title="Senior Python Engineer",
            experience_min=5.0,
            experience_max=10.0,
        )

        db_session.add(requirement)
        db_session.commit()

        assert requirement.experience_min == 5.0
        assert requirement.experience_max == 10.0

    @pytest.mark.unit
    def test_requirement_education_level(self, sample_customer, db_session):
        """Test education level requirements."""
        requirement = Requirement(
            customer_id=sample_customer.id,
            title="Senior Python Engineer",
            education_level="Bachelor",
        )

        db_session.add(requirement)
        db_session.commit()

        assert requirement.education_level == "Bachelor"

    @pytest.mark.unit
    def test_requirement_certifications(self, sample_customer, db_session):
        """Test certification requirements."""
        certifications = ["AWS Solutions Architect", "Kubernetes CKA"]

        requirement = Requirement(
            customer_id=sample_customer.id,
            title="Senior Python Engineer",
            certifications=certifications,
        )

        db_session.add(requirement)
        db_session.commit()

        assert requirement.certifications == certifications

    @pytest.mark.unit
    def test_requirement_location(self, sample_customer, db_session):
        """Test requirement location."""
        requirement = Requirement(
            customer_id=sample_customer.id,
            title="Senior Python Engineer",
            location_city="San Francisco",
            location_state="CA",
            location_country="USA",
        )

        db_session.add(requirement)
        db_session.commit()

        assert requirement.location_city == "San Francisco"
        assert requirement.location_state == "CA"
        assert requirement.location_country == "USA"

    @pytest.mark.unit
    def test_requirement_work_mode(self, sample_customer, db_session):
        """Test requirement work mode."""
        requirement = Requirement(
            customer_id=sample_customer.id,
            title="Senior Python Engineer",
            work_mode="Remote",
            employment_type="Full-time",
        )

        db_session.add(requirement)
        db_session.commit()

        assert requirement.work_mode == "Remote"
        assert requirement.employment_type == "Full-time"

    @pytest.mark.unit
    def test_requirement_rate_range(self, sample_customer, db_session):
        """Test requirement rate range."""
        requirement = Requirement(
            customer_id=sample_customer.id,
            title="Senior Python Engineer",
            rate_min=120000,
            rate_max=180000,
            rate_type="annual",
        )

        db_session.add(requirement)
        db_session.commit()

        assert requirement.rate_min == 120000
        assert requirement.rate_max == 180000
        assert requirement.rate_type == "annual"

    @pytest.mark.unit
    def test_requirement_duration(self, sample_customer, db_session):
        """Test requirement duration."""
        requirement = Requirement(
            customer_id=sample_customer.id,
            title="Senior Python Engineer",
            duration_months=12,
        )

        db_session.add(requirement)
        db_session.commit()

        assert requirement.duration_months == 12

    @pytest.mark.unit
    def test_requirement_positions_count(self, sample_customer, db_session):
        """Test positions count tracking."""
        requirement = Requirement(
            customer_id=sample_customer.id,
            title="Senior Python Engineer",
            positions_count=3,
            positions_filled=1,
        )

        db_session.add(requirement)
        db_session.commit()

        assert requirement.positions_count == 3
        assert requirement.positions_filled == 1

    @pytest.mark.unit
    def test_requirement_priority(self, sample_customer, db_session):
        """Test requirement priority levels."""
        requirement = Requirement(
            customer_id=sample_customer.id,
            title="Senior Python Engineer",
            priority=Priority.CRITICAL,
        )

        db_session.add(requirement)
        db_session.commit()

        assert requirement.priority == Priority.CRITICAL

    @pytest.mark.unit
    def test_requirement_status_transitions(self, sample_customer, db_session):
        """Test requirement status transitions."""
        requirement = Requirement(
            customer_id=sample_customer.id,
            title="Senior Python Engineer",
            status=RequirementStatus.DRAFT,
        )

        db_session.add(requirement)
        db_session.commit()

        # Test status transitions
        requirement.status = RequirementStatus.ACTIVE
        db_session.commit()
        assert requirement.status == RequirementStatus.ACTIVE

        requirement.status = RequirementStatus.ON_HOLD
        db_session.commit()
        assert requirement.status == RequirementStatus.ON_HOLD

        requirement.status = RequirementStatus.FILLED
        db_session.commit()
        assert requirement.status == RequirementStatus.FILLED

    @pytest.mark.unit
    def test_requirement_deadlines(self, sample_customer, db_session):
        """Test requirement deadlines."""
        submission_deadline = datetime.utcnow() + timedelta(days=30)
        start_date = datetime.utcnow() + timedelta(days=15)

        requirement = Requirement(
            customer_id=sample_customer.id,
            title="Senior Python Engineer",
            submission_deadline=submission_deadline,
            start_date=start_date,
        )

        db_session.add(requirement)
        db_session.commit()

        assert requirement.submission_deadline == submission_deadline
        assert requirement.start_date == start_date

    @pytest.mark.unit
    def test_requirement_notes(self, sample_customer, db_session):
        """Test requirement notes field."""
        notes = "High priority. Client is very demanding but good long-term prospect."

        requirement = Requirement(
            customer_id=sample_customer.id,
            title="Senior Python Engineer",
            notes=notes,
        )

        db_session.add(requirement)
        db_session.commit()

        assert requirement.notes == notes

    @pytest.mark.unit
    def test_requirement_metadata(self, sample_customer, db_session):
        """Test requirement metadata."""
        metadata = {
            "department": "Engineering",
            "cost_center": "CC-001",
            "business_unit": "Platform",
        }

        requirement = Requirement(
            customer_id=sample_customer.id,
            title="Senior Python Engineer",
            metadata=metadata,
        )

        db_session.add(requirement)
        db_session.commit()

        assert requirement.metadata == metadata

    @pytest.mark.unit
    def test_requirement_recruiter_assignment(self, sample_customer, sample_user, db_session):
        """Test requirement recruiter assignment."""
        requirement = Requirement(
            customer_id=sample_customer.id,
            title="Senior Python Engineer",
            assigned_recruiter_id=sample_user.id,
        )

        db_session.add(requirement)
        db_session.commit()

        assert requirement.assigned_recruiter_id == sample_user.id

    @pytest.mark.unit
    def test_requirement_repr(self, sample_customer):
        """Test requirement string representation."""
        requirement = Requirement(
            id=1,
            customer_id=sample_customer.id,
            title="Senior Python Engineer",
            status=RequirementStatus.ACTIVE,
        )

        repr_str = repr(requirement)
        assert "Senior Python Engineer" in repr_str
        assert "ACTIVE" in repr_str

    @pytest.mark.unit
    def test_requirement_multiple_statuses(self, sample_customer, db_session):
        """Test all requirement statuses."""
        statuses = [
            RequirementStatus.DRAFT,
            RequirementStatus.ACTIVE,
            RequirementStatus.ON_HOLD,
            RequirementStatus.FILLED,
            RequirementStatus.CANCELLED,
            RequirementStatus.CLOSED,
        ]

        for status in statuses:
            requirement = Requirement(
                customer_id=sample_customer.id,
                title=f"Position - {status}",
                status=status,
            )
            db_session.add(requirement)

        db_session.commit()

        # Verify all statuses were created
        result = db_session.query(Requirement).count()
        assert result == len(statuses)

    @pytest.mark.unit
    def test_requirement_all_priority_levels(self, sample_customer, db_session):
        """Test all priority levels."""
        priorities = [
            Priority.CRITICAL,
            Priority.HIGH,
            Priority.MEDIUM,
            Priority.LOW,
        ]

        for priority in priorities:
            requirement = Requirement(
                customer_id=sample_customer.id,
                title=f"Position - {priority}",
                priority=priority,
            )
            db_session.add(requirement)

        db_session.commit()

        # Verify all priorities were created
        result = db_session.query(Requirement).count()
        assert result == len(priorities)
