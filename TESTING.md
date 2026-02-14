# HR Platform Test Suite

Comprehensive unit, integration, and system test suite for the HR Automation Platform.

## Overview

The test suite includes:

- **Unit Tests**: Individual component testing (models, services, agents, utilities)
- **Integration Tests**: End-to-end workflow testing (hiring pipeline, referrals, contracts)
- **Smoke Tests**: Quick health checks of platform components
- **API Tests**: HTTP endpoint validation
- **Performance Tests**: Basic performance benchmarks
- **Test Agent**: Automated test orchestration and reporting

## Setup

### Install Test Dependencies

```bash
pip install -r requirements-test.txt
```

### Configuration

Tests use an in-memory SQLite database. All database setup is handled automatically by fixtures in `conftest.py`.

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# Smoke tests only
pytest -m smoke

# Integration tests only
pytest -m integration

# Unit tests only
pytest -m unit
```

### Run Specific Test File

```bash
pytest tests/test_models/test_candidate.py
```

### Run with Coverage Report

```bash
pytest --cov=. --cov-report=html
```

This generates an HTML coverage report in `htmlcov/index.html`.

### Run with Verbose Output

```bash
pytest -v
```

### Run Single Test

```bash
pytest tests/test_models/test_candidate.py::TestCandidate::test_create_candidate -v
```

## Test Structure

```
tests/
├── __init__.py
├── conftest.py                    # Shared fixtures and configuration
├── test_models/                   # Model unit tests
│   ├── test_base.py
│   ├── test_candidate.py
│   └── test_requirement.py
├── test_services/                 # Service layer tests
│   ├── test_matching_service.py
│   └── (more service tests)
├── test_agents/                   # Agent tests
│   ├── test_base_agent.py
│   └── (more agent tests)
├── test_api/                      # API endpoint tests
│   ├── test_health.py
│   └── (more API tests)
├── test_config/                   # Configuration tests
│   └── test_settings.py
├── test_utils/                    # Utility tests
│   └── test_security.py
└── test_integration/              # Integration tests
    ├── test_smoke.py
    └── (more integration tests)
```

## Test Fixtures

The `conftest.py` file provides reusable fixtures:

### Database Fixtures

- `db_engine`: In-memory SQLite engine
- `db_session`: Test database session
- `async_session_fixture`: Async session for async tests

### Client Fixtures

- `client`: FastAPI AsyncClient for API testing

### Sample Data Fixtures

- `sample_user`: Test user with recruiter role
- `sample_admin_user`: Test user with admin role
- `sample_customer`: Test customer
- `sample_requirement`: Test job requirement
- `sample_candidate`: Test candidate
- `sample_candidate_with_skills`: Candidate with all skills
- `sample_candidate_missing_skills`: Candidate missing key skills

### Authentication Fixtures

- `auth_headers`: JWT headers for recruiter
- `admin_auth_headers`: JWT headers for admin

### Mock Fixtures

- `mock_redis_client`: Mocked Redis client
- `mock_s3_client`: Mocked AWS S3 client
- `mock_openai_client`: Mocked OpenAI API
- `mock_email_service`: Mocked email service

### Utility Fixtures

- `test_settings`: Test configuration
- `sample_resume_text`: Sample resume for parsing tests
- `sample_match_scores`: Sample match score breakdown
- `sample_interview_questions`: Sample interview questions

## Test Agent

The `TestAgent` (in `agents/test_agent.py`) orchestrates automated testing:

### Test Categories

1. **Smoke Tests** - Quick health checks
   - Database connectivity
   - API endpoints responding
   - Agent initialization
   - External service connectivity

2. **Integration Tests** - End-to-end workflows
   - Full hiring pipeline
   - Referral pipeline
   - Contract pipeline

3. **Agent Tests** - Individual agent validation
   - Agent initialization
   - Event processing
   - Core functionality

4. **API Tests** - HTTP endpoint validation
   - Status codes
   - Response schemas
   - Authentication
   - Authorization

5. **Data Integrity Tests** - Data consistency
   - Foreign key constraints
   - Enum validation
   - Required fields

6. **Performance Tests** - Performance benchmarks
   - Query execution time
   - Batch operations

### Running Test Agent

Via API endpoints:

```bash
# Run full test suite
curl -X POST http://localhost:8000/api/v1/tests/run-all \
  -H "Authorization: Bearer YOUR_TOKEN"

# Run smoke tests
curl -X POST http://localhost:8000/api/v1/tests/smoke \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get test results
curl http://localhost:8000/api/v1/tests/results/{run_id} \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get test history
curl http://localhost:8000/api/v1/tests/history \
  -H "Authorization: Bearer YOUR_TOKEN"

# Generate test report
curl -X POST http://localhost:8000/api/v1/tests/generate-report \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"run_id": "run_id_here"}'
```

## Model Tests

### Candidate Model Tests

Location: `tests/test_models/test_candidate.py`

Tests:
- Candidate creation
- Required fields validation
- Full name property
- Skills JSON storage
- Education JSON storage
- Status transitions
- Location tracking
- Availability date
- Rate preferences
- Source tracking
- Engagement score
- Metadata storage
- Unique email constraint

Example:
```python
def test_create_candidate(self, db_session):
    candidate = Candidate(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
    )
    db_session.add(candidate)
    db_session.commit()
    assert candidate.id is not None
```

### Requirement Model Tests

Location: `tests/test_models/test_requirement.py`

Tests:
- Requirement creation
- Skills required/preferred
- Experience levels
- Education requirements
- Certifications
- Location specification
- Work mode
- Rate range
- Duration
- Position count tracking
- Priority levels
- Status transitions
- Deadline tracking

## Service Tests

### Matching Service Tests

Location: `tests/test_services/test_matching_service.py`

Tests:
- Exact skill matching
- Partial skill matching
- Experience score computation
- Overall score computation
- Bidirectional matching
- Configurable weights
- Missing skills detection
- Empty candidate handling
- Score caching
- Batch operations

Example:
```python
async def test_compute_skill_match_exact(self, matching_service):
    result = await matching_service.match_requirement_to_candidates(
        db_session=mock_session,
        requirement_id=1,
    )
    assert result["matches"][0]["skill_score"] == 1.0
```

## Agent Tests

### Base Agent Tests

Location: `tests/test_agents/test_base_agent.py`

Tests:
- Agent initialization
- Startup/shutdown lifecycle
- Event handler registration
- Event processing
- Event emission
- Health checks
- Error handling
- Multiple event handlers

## API Tests

### Health Check Tests

Location: `tests/test_api/test_health.py`

Tests:
- Health check endpoint
- Readiness check
- Version endpoint
- API info endpoint
- CORS headers
- Error handling
- Validation errors

## Configuration Tests

### Settings Tests

Location: `tests/test_config/test_settings.py`

Tests:
- Settings initialization
- Default values
- Database configuration
- JWT configuration
- Matching weights
- Weight validation
- CORS origins parsing
- Feature flags
- AWS configuration
- Email configuration
- Redis configuration
- RabbitMQ configuration

## Utility Tests

### Security Tests

Location: `tests/test_utils/test_security.py`

Tests:
- Password hashing
- Password verification
- JWT token creation
- Token verification
- Token expiry
- Custom token claims
- Password hash uniqueness

## Writing New Tests

### Basic Unit Test

```python
import pytest

class TestMyComponent:
    """Test suite for MyComponent."""

    @pytest.mark.unit
    def test_basic_functionality(self, db_session):
        """Test basic functionality."""
        # Setup
        obj = MyModel(name="test")
        db_session.add(obj)
        db_session.commit()

        # Act
        result = obj.some_method()

        # Assert
        assert result == expected_value
```

### Async Test

```python
@pytest.mark.unit
@pytest.mark.asyncio
async def test_async_operation(self, db_session):
    """Test async operation."""
    result = await some_async_function(db_session)
    assert result is not None
```

### Test with Mocks

```python
@pytest.mark.unit
@pytest.mark.asyncio
async def test_with_mock(self, matching_service, mock_redis_client):
    """Test with mocked dependencies."""
    result = await matching_service.cache_match_results(
        redis_client=mock_redis_client,
        requirement_id=1,
        matches=[{"candidate_id": 1}],
    )
    assert result is True
```

### Test with Fixtures

```python
@pytest.mark.unit
def test_with_fixtures(self, sample_candidate, sample_requirement, db_session):
    """Test using multiple fixtures."""
    match = MatchScore(
        requirement_id=sample_requirement.id,
        candidate_id=sample_candidate.id,
        overall_score=0.85,
    )
    db_session.add(match)
    db_session.commit()

    assert match.id is not None
```

## Best Practices

1. **Use Fixtures**: Leverage provided fixtures rather than creating duplicate setup code
2. **Mark Tests**: Use `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.smoke`
3. **Async Tests**: Use `@pytest.mark.asyncio` for async tests
4. **Mocking**: Mock external services (OpenAI, S3, Email) not core functionality
5. **Isolation**: Each test should be independent and not rely on other tests
6. **Assertions**: Use clear, specific assertions
7. **Naming**: Use descriptive test names that explain what is being tested
8. **Documentation**: Add docstrings explaining the test purpose

## CI/CD Integration

For GitHub Actions, use:

```yaml
- name: Run tests
  run: pytest --cov=. --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    files: ./coverage.xml
```

## Troubleshooting

### Tests Fail Due to Database Issues

- Ensure SQLite is installed: `pip install aiosqlite`
- Clear any existing test database: `rm -f test.db`
- Run tests in isolation: `pytest --tb=short`

### Async Test Errors

- Ensure `pytest-asyncio` is installed
- Check `pytest.ini` has `asyncio_mode = auto`
- Use `@pytest.mark.asyncio` decorator

### Import Errors

- Ensure `PYTHONPATH` includes project root
- Check all `__init__.py` files exist
- Run from project root: `cd /sessions/awesome-youthful-maxwell/hr_platform && pytest`

### Fixture Not Found

- Check fixture is defined in `conftest.py`
- Verify fixture name matches parameter name exactly
- Ensure conftest.py is in same or parent directory

## Performance Targets

- Unit tests: < 5 seconds total
- Integration tests: < 30 seconds total
- Full suite: < 2 minutes total
- Individual test: < 1 second (except slow marked tests)

## Continuous Improvement

Monitor test metrics:
- Code coverage (target: > 80%)
- Test execution time
- Flaky test rate (target: 0%)
- Defect escape rate

Add tests for:
- New features
- Bug fixes
- Edge cases
- Integration points
- Error scenarios

## Contributing Tests

When contributing tests:

1. Follow existing patterns
2. Use provided fixtures
3. Add appropriate markers
4. Update test documentation
5. Ensure tests pass locally
6. Verify coverage hasn't decreased

## References

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [FastAPI Testing](https://fastapi.tiangolo.com/advanced/testing-dependencies/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
