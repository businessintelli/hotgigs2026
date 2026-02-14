"""Tests for Candidate model."""
import pytest
from datetime import datetime, timedelta
from sqlalchemy import select

from models.candidate import Candidate
from models.enums import CandidateStatus


class TestCandidate:
    """Test suite for Candidate model."""

    @pytest.mark.unit
    def test_create_candidate(self, db_session):
        """Test creating a candidate."""
        candidate = Candidate(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="555-0100",
            current_title="Developer",
            current_company="TechCorp",
            total_experience_years=5.0,
            status=CandidateStatus.SOURCED,
            source="LinkedIn",
        )

        db_session.add(candidate)
        db_session.commit()

        assert candidate.id is not None
        assert candidate.full_name == "John Doe"
        assert candidate.status == CandidateStatus.SOURCED

    @pytest.mark.unit
    def test_candidate_required_fields(self, db_session):
        """Test candidate required fields validation."""
        candidate = Candidate(
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
        )

        db_session.add(candidate)
        db_session.commit()

        assert candidate.first_name == "Jane"
        assert candidate.last_name == "Smith"
        assert candidate.email == "jane@example.com"

    @pytest.mark.unit
    def test_candidate_full_name_property(self):
        """Test full_name property."""
        candidate = Candidate(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
        )

        assert candidate.full_name == "John Doe"

    @pytest.mark.unit
    def test_candidate_skills_json(self, db_session):
        """Test candidate skills as JSON."""
        skills = [
            {"skill": "Python", "level": "Expert", "years": 5},
            {"skill": "FastAPI", "level": "Advanced", "years": 2},
        ]

        candidate = Candidate(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            skills=skills,
        )

        db_session.add(candidate)
        db_session.commit()

        assert candidate.skills == skills
        assert len(candidate.skills) == 2
        assert candidate.skills[0]["skill"] == "Python"

    @pytest.mark.unit
    def test_candidate_education_json(self, db_session):
        """Test candidate education as JSON."""
        education = [
            {
                "degree": "Bachelor",
                "field": "Computer Science",
                "institution": "UC Berkeley",
                "year": 2015,
            }
        ]

        candidate = Candidate(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            education=education,
        )

        db_session.add(candidate)
        db_session.commit()

        assert candidate.education == education
        assert candidate.education[0]["degree"] == "Bachelor"

    @pytest.mark.unit
    def test_candidate_status_transitions(self, db_session):
        """Test candidate status transitions."""
        candidate = Candidate(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            status=CandidateStatus.SOURCED,
        )

        db_session.add(candidate)
        db_session.commit()

        # Test status changes
        candidate.status = CandidateStatus.PARSED
        db_session.commit()
        assert candidate.status == CandidateStatus.PARSED

        candidate.status = CandidateStatus.MATCHED
        db_session.commit()
        assert candidate.status == CandidateStatus.MATCHED

        candidate.status = CandidateStatus.PLACED
        db_session.commit()
        assert candidate.status == CandidateStatus.PLACED

    @pytest.mark.unit
    def test_candidate_location_fields(self, db_session):
        """Test candidate location fields."""
        candidate = Candidate(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            location_city="San Francisco",
            location_state="CA",
            location_country="USA",
        )

        db_session.add(candidate)
        db_session.commit()

        assert candidate.location_city == "San Francisco"
        assert candidate.location_state == "CA"
        assert candidate.location_country == "USA"

    @pytest.mark.unit
    def test_candidate_availability(self, db_session):
        """Test candidate availability tracking."""
        tomorrow = datetime.utcnow() + timedelta(days=1)

        candidate = Candidate(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            availability_date=tomorrow,
            work_authorization="US Citizen",
            willing_to_relocate=True,
        )

        db_session.add(candidate)
        db_session.commit()

        assert candidate.availability_date == tomorrow
        assert candidate.work_authorization == "US Citizen"
        assert candidate.willing_to_relocate is True

    @pytest.mark.unit
    def test_candidate_rate_preferences(self, db_session):
        """Test candidate rate preferences."""
        candidate = Candidate(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            desired_rate=150000.0,
            desired_rate_type="annual",
        )

        db_session.add(candidate)
        db_session.commit()

        assert candidate.desired_rate == 150000.0
        assert candidate.desired_rate_type == "annual"

    @pytest.mark.unit
    def test_candidate_source_tracking(self, db_session):
        """Test candidate source tracking."""
        candidate = Candidate(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            source="LinkedIn",
            source_detail="Passive candidate from Python group",
        )

        db_session.add(candidate)
        db_session.commit()

        assert candidate.source == "LinkedIn"
        assert candidate.source_detail == "Passive candidate from Python group"

    @pytest.mark.unit
    def test_candidate_engagement_score(self, db_session):
        """Test candidate engagement score."""
        candidate = Candidate(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            engagement_score=0.85,
        )

        db_session.add(candidate)
        db_session.commit()

        assert candidate.engagement_score == 0.85

    @pytest.mark.unit
    def test_candidate_metadata(self, db_session):
        """Test candidate metadata storage."""
        metadata = {
            "referral_source": "employee_referral",
            "tags": ["python", "senior", "remote"],
            "notes": "Highly recommended by team member",
        }

        candidate = Candidate(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            metadata=metadata,
        )

        db_session.add(candidate)
        db_session.commit()

        assert candidate.metadata == metadata
        assert candidate.metadata["tags"] == ["python", "senior", "remote"]

    @pytest.mark.unit
    def test_candidate_unique_email(self, db_session):
        """Test unique email constraint."""
        candidate1 = Candidate(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
        )
        db_session.add(candidate1)
        db_session.commit()

        candidate2 = Candidate(
            first_name="Jane",
            last_name="Smith",
            email="john@example.com",
        )
        db_session.add(candidate2)

        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()

    @pytest.mark.unit
    def test_candidate_repr(self):
        """Test candidate string representation."""
        candidate = Candidate(
            id=1,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            status=CandidateStatus.SOURCED,
        )

        repr_str = repr(candidate)
        assert "John Doe" in repr_str
        assert "SOURCED" in repr_str

    @pytest.mark.unit
    def test_candidate_certifications(self, db_session):
        """Test candidate certifications."""
        certifications = ["AWS Solutions Architect", "Kubernetes CKA", "OSCP"]

        candidate = Candidate(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            certifications=certifications,
        )

        db_session.add(candidate)
        db_session.commit()

        assert candidate.certifications == certifications
        assert len(candidate.certifications) == 3

    @pytest.mark.unit
    def test_candidate_notes(self, db_session):
        """Test candidate notes field."""
        notes = "Great technical skills. Needs improvement in soft skills."

        candidate = Candidate(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            notes=notes,
        )

        db_session.add(candidate)
        db_session.commit()

        assert candidate.notes == notes

    @pytest.mark.unit
    def test_candidate_last_contacted_tracking(self, db_session):
        """Test candidate last contacted timestamp."""
        contact_date = datetime.utcnow().date()

        candidate = Candidate(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            last_contacted_at=contact_date,
        )

        db_session.add(candidate)
        db_session.commit()

        assert candidate.last_contacted_at == contact_date
