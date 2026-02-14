"""Shared test fixtures and configuration for all tests."""
import pytest
import pytest_asyncio
import asyncio
import json
from datetime import datetime, timedelta
from typing import AsyncGenerator, Optional
from unittest.mock import Mock, AsyncMock, patch

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.pool import StaticPool

# Import application modules
from api.main import app
from api.dependencies import get_db, get_current_user
from database.base import Base
from config.settings import Settings
from models.user import User
from models.customer import Customer
from models.requirement import Requirement
from models.candidate import Candidate
from models.enums import UserRole, CandidateStatus, RequirementStatus, Priority
from utils.security import create_access_token


# ==================== Database Configuration ====================

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def db_engine():
    """Create test database engine with in-memory SQLite."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session = async_sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client with dependency overrides."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


# ==================== Sample Data Fixtures ====================


@pytest.fixture
def sample_user(db_session) -> User:
    """Create sample user."""
    user = User(
        email="testuser@example.com",
        username="testuser",
        hashed_password="hashed_password",
        first_name="Test",
        last_name="User",
        role=UserRole.RECRUITER,
        is_active=True,
    )
    db_session.add(user)
    return user


@pytest.fixture
def sample_admin_user(db_session) -> User:
    """Create sample admin user."""
    user = User(
        email="admin@example.com",
        username="admin",
        hashed_password="hashed_password",
        first_name="Admin",
        last_name="User",
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(user)
    return user


@pytest.fixture
def sample_customer(db_session) -> Customer:
    """Create sample customer."""
    customer = Customer(
        company_name="Tech Corp",
        industry="Technology",
        contact_email="contact@techcorp.com",
        contact_phone="555-0100",
        location_city="San Francisco",
        location_state="CA",
        location_country="USA",
        website="https://techcorp.com",
        status="active",
        tier="gold",
    )
    db_session.add(customer)
    return customer


@pytest.fixture
def sample_requirement(sample_customer, db_session) -> Requirement:
    """Create sample job requirement."""
    requirement = Requirement(
        customer_id=sample_customer.id,
        title="Senior Python Engineer",
        description="Looking for experienced Python engineer",
        skills_required=["Python", "FastAPI", "SQL"],
        skills_preferred=["Docker", "Kubernetes"],
        experience_min=5.0,
        experience_max=10.0,
        education_level="Bachelor",
        employment_type="Full-time",
        work_mode="Remote",
        location_city="San Francisco",
        location_state="CA",
        location_country="USA",
        rate_min=120000,
        rate_max=180000,
        rate_type="annual",
        duration_months=12,
        positions_count=2,
        priority=Priority.HIGH,
        status=RequirementStatus.ACTIVE,
        submission_deadline=datetime.utcnow() + timedelta(days=30),
        start_date=datetime.utcnow() + timedelta(days=15),
    )
    db_session.add(requirement)
    return requirement


@pytest.fixture
def sample_candidate(db_session) -> Candidate:
    """Create sample candidate."""
    candidate = Candidate(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="555-0101",
        linkedin_url="https://linkedin.com/in/johndoe",
        location_city="San Francisco",
        location_state="CA",
        location_country="USA",
        current_title="Senior Developer",
        current_company="TechCorp",
        total_experience_years=8.0,
        skills=[
            {"skill": "Python", "level": "Expert", "years": 7},
            {"skill": "FastAPI", "level": "Advanced", "years": 3},
            {"skill": "SQL", "level": "Advanced", "years": 6},
            {"skill": "Docker", "level": "Intermediate", "years": 2},
        ],
        education=[
            {
                "degree": "Bachelor",
                "field": "Computer Science",
                "institution": "UC Berkeley",
                "year": 2015,
            }
        ],
        certifications=["AWS Solutions Architect"],
        desired_rate=150000.0,
        desired_rate_type="annual",
        availability_date=datetime.utcnow() + timedelta(days=14),
        work_authorization="US Citizen",
        willing_to_relocate=False,
        status=CandidateStatus.SOURCED,
        source="LinkedIn",
    )
    db_session.add(candidate)
    return candidate


@pytest.fixture
def sample_candidate_with_skills(db_session) -> Candidate:
    """Create sample candidate with specific skills."""
    candidate = Candidate(
        first_name="Jane",
        last_name="Smith",
        email="jane.smith@example.com",
        phone="555-0102",
        linkedin_url="https://linkedin.com/in/janesmith",
        location_city="San Francisco",
        location_state="CA",
        location_country="USA",
        current_title="Lead Engineer",
        current_company="StartupXYZ",
        total_experience_years=10.0,
        skills=[
            {"skill": "Python", "level": "Expert", "years": 9},
            {"skill": "FastAPI", "level": "Expert", "years": 5},
            {"skill": "SQL", "level": "Expert", "years": 8},
            {"skill": "Docker", "level": "Expert", "years": 4},
            {"skill": "Kubernetes", "level": "Advanced", "years": 3},
        ],
        education=[
            {
                "degree": "Master",
                "field": "Computer Science",
                "institution": "Stanford",
                "year": 2016,
            }
        ],
        certifications=["AWS Solutions Architect", "Kubernetes CKA"],
        desired_rate=180000.0,
        desired_rate_type="annual",
        availability_date=datetime.utcnow() + timedelta(days=7),
        work_authorization="US Citizen",
        willing_to_relocate=True,
        status=CandidateStatus.SOURCED,
        source="Referral",
    )
    db_session.add(candidate)
    return candidate


@pytest.fixture
def sample_candidate_missing_skills(db_session) -> Candidate:
    """Create sample candidate with missing key skills."""
    candidate = Candidate(
        first_name="Bob",
        last_name="Junior",
        email="bob.junior@example.com",
        phone="555-0103",
        location_city="Los Angeles",
        location_state="CA",
        location_country="USA",
        current_title="Junior Developer",
        current_company="SmallCompany",
        total_experience_years=1.5,
        skills=[
            {"skill": "Python", "level": "Intermediate", "years": 1},
            {"skill": "JavaScript", "level": "Beginner", "years": 0.5},
        ],
        education=[
            {
                "degree": "Bachelor",
                "field": "Computer Science",
                "institution": "Local University",
                "year": 2023,
            }
        ],
        certifications=[],
        desired_rate=70000.0,
        desired_rate_type="annual",
        availability_date=datetime.utcnow() + timedelta(days=30),
        work_authorization="US Visa Sponsorship Required",
        willing_to_relocate=False,
        status=CandidateStatus.SOURCED,
        source="Job Board",
    )
    db_session.add(candidate)
    return candidate


# ==================== Authentication Fixtures ====================


@pytest.fixture
def auth_headers(sample_user) -> dict:
    """Generate valid JWT auth headers for testing."""
    token = create_access_token(
        data={"sub": str(sample_user.id), "email": sample_user.email},
        expires_delta=timedelta(hours=1),
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_headers(sample_admin_user) -> dict:
    """Generate valid JWT auth headers for admin user."""
    token = create_access_token(
        data={"sub": str(sample_admin_user.id), "email": sample_admin_user.email},
        expires_delta=timedelta(hours=1),
    )
    return {"Authorization": f"Bearer {token}"}


# ==================== Mock External Services ====================


@pytest.fixture
def mock_redis_client():
    """Mock Redis client."""
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=None)
    mock_client.setex = AsyncMock(return_value=True)
    mock_client.delete = AsyncMock(return_value=1)
    return mock_client


@pytest.fixture
def mock_s3_client():
    """Mock AWS S3 client."""
    mock_client = AsyncMock()
    mock_client.put_object = AsyncMock(return_value={"ETag": "fake-etag"})
    mock_client.get_object = AsyncMock(
        return_value={"Body": AsyncMock(read=AsyncMock(return_value=b"test content"))}
    )
    mock_client.delete_object = AsyncMock(return_value={})
    return mock_client


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client."""
    mock_client = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(
        return_value=Mock(
            choices=[Mock(message=Mock(content="Mock AI response"))]
        )
    )
    return mock_client


@pytest.fixture
def mock_email_service():
    """Mock email service."""
    mock_service = AsyncMock()
    mock_service.send_email = AsyncMock(return_value={"message_id": "fake-id"})
    mock_service.send_bulk_email = AsyncMock(
        return_value={"sent": 5, "failed": 0}
    )
    return mock_service


# ==================== Settings Override ====================


@pytest.fixture
def test_settings():
    """Get test settings."""
    settings = Settings(
        debug=True,
        log_level="DEBUG",
        database_url=TEST_DATABASE_URL,
        redis_url="redis://localhost:6379/1",
        jwt_secret="test-secret-key",
        jwt_algorithm="HS256",
        jwt_expiry_hours=1,
        enable_ai_parsing=False,
        enable_auto_matching=False,
        enable_email_notifications=False,
    )
    return settings


# ==================== Event Loop Configuration ====================


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ==================== Utility Fixtures ====================


@pytest.fixture
def mock_datetime():
    """Fixture to freeze datetime for testing."""
    now = datetime(2024, 1, 15, 10, 0, 0)
    with patch("datetime.datetime") as mock_dt:
        mock_dt.utcnow.return_value = now
        mock_dt.now.return_value = now
        yield mock_dt


@pytest.fixture
def sample_resume_text() -> str:
    """Sample resume text for testing."""
    return """
    JOHN DOE
    San Francisco, CA | john.doe@example.com | (555) 0101 | linkedin.com/in/johndoe

    PROFESSIONAL SUMMARY
    Experienced Senior Python Developer with 8+ years of software development experience.
    Expertise in building scalable APIs using FastAPI and managing databases with SQL.

    EXPERIENCE
    Senior Developer | TechCorp | Jan 2020 - Present
    - Led development of microservices architecture using Python and FastAPI
    - Managed team of 5 engineers
    - Reduced API response time by 40% through optimization

    Senior Developer | StartupABC | Jan 2018 - Dec 2019
    - Developed RESTful APIs using Python and Flask
    - Designed database schemas for high-traffic applications
    - Mentored junior developers

    EDUCATION
    Bachelor of Science in Computer Science | UC Berkeley | 2015

    SKILLS
    Languages: Python, JavaScript, SQL, Bash
    Frameworks: FastAPI, Flask, Django
    Databases: PostgreSQL, MySQL, MongoDB
    Cloud: AWS, Google Cloud Platform
    Tools: Docker, Git, Jenkins, Linux

    CERTIFICATIONS
    AWS Solutions Architect Associate | 2021
    """


@pytest.fixture
def sample_match_scores() -> dict:
    """Sample match score breakdown."""
    return {
        "overall_score": 0.85,
        "skill_score": 0.90,
        "experience_score": 0.85,
        "education_score": 0.80,
        "location_score": 0.70,
        "rate_score": 0.80,
        "availability_score": 0.95,
        "culture_score": 0.75,
    }


@pytest.fixture
def sample_interview_questions() -> list:
    """Sample interview questions."""
    return [
        {
            "id": 1,
            "category": "technical",
            "question": "Explain the difference between async and await in Python",
            "difficulty": "intermediate",
        },
        {
            "id": 2,
            "category": "behavioral",
            "question": "Tell us about a challenging project you led",
            "difficulty": "medium",
        },
        {
            "id": 3,
            "category": "technical",
            "question": "Design a system for handling 1M requests per second",
            "difficulty": "hard",
        },
    ]


@pytest.fixture
def sample_interview_response() -> dict:
    """Sample candidate interview response."""
    return {
        "candidate_id": 1,
        "requirement_id": 1,
        "question_id": 1,
        "response": "Async/await is used for asynchronous programming...",
        "duration_seconds": 120,
        "sentiment": "positive",
        "confidence_score": 0.85,
    }


# ==================== Async Context Manager Tests ====================


@pytest_asyncio.fixture
async def async_session_fixture(db_engine):
    """Async session fixture for async tests."""
    async_session = async_sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
        await session.rollback()
