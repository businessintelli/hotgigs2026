# Test Suite Quick Start

## Installation

```bash
# Install test dependencies
pip install -r requirements-test.txt
```

## Quick Commands

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific marker
pytest -m smoke           # Smoke tests only
pytest -m integration     # Integration tests only
pytest -m unit           # Unit tests only

# Run specific file
pytest tests/test_models/test_candidate.py -v

# Run specific test
pytest tests/test_models/test_candidate.py::TestCandidate::test_create_candidate -v

# Run with output
pytest -v --tb=short

# Run and stop on first failure
pytest -x

# Run last failed
pytest --lf

# Run failed + changed
pytest --ff
```

## Test Structure

### Files to Know

- `conftest.py` - Shared fixtures (use these!)
- `pytest.ini` - Configuration
- `requirements-test.txt` - Dependencies

### Test Directories

```
tests/
├── test_models/      # Model tests
├── test_services/    # Service tests
├── test_agents/      # Agent tests
├── test_api/         # API tests
├── test_config/      # Config tests
├── test_utils/       # Utility tests
└── test_integration/ # Integration tests
```

## Available Fixtures

### Data Fixtures

```python
# In your test function parameters:
def test_something(self, sample_candidate, sample_requirement, db_session):
    # sample_candidate - Ready-to-use Candidate
    # sample_requirement - Ready-to-use Requirement
    # db_session - Database session
```

### Auth Fixtures

```python
async def test_api_endpoint(self, client, auth_headers):
    response = await client.get("/api/v1/candidates", headers=auth_headers)
```

### Mock Fixtures

```python
async def test_with_cache(self, matching_service, mock_redis_client):
    await matching_service.cache_match_results(mock_redis_client, ...)
```

## Writing Your First Test

```python
import pytest

class TestMyFeature:
    """Test suite for my feature."""

    @pytest.mark.unit
    def test_basic_case(self, db_session, sample_candidate):
        """Test basic functionality."""
        # Arrange
        candidate = sample_candidate

        # Act
        candidate.status = "matched"
        db_session.commit()

        # Assert
        assert candidate.status == "matched"
```

## Test Markers

```python
@pytest.mark.unit           # Unit test
@pytest.mark.integration    # Integration test
@pytest.mark.smoke          # Smoke test
@pytest.mark.asyncio        # Async test (if using async/await)
@pytest.mark.slow           # Slow test
```

## Async Tests

```python
@pytest.mark.asyncio
@pytest.mark.unit
async def test_async_operation(self, db_session):
    """Test async operation."""
    result = await some_async_function()
    assert result is not None
```

## Expected Output

```
tests/test_models/test_candidate.py::TestCandidate::test_create_candidate PASSED [5%]
tests/test_models/test_candidate.py::TestCandidate::test_candidate_skills_json PASSED [10%]
...

======================== 150 passed in 2.34s ========================
```

## Coverage Report

After running with `--cov`:

```bash
# View in terminal
pytest --cov=. --cov-report=term-missing

# Generate HTML report
pytest --cov=. --cov-report=html
# Open htmlcov/index.html in browser
```

## Common Issues & Solutions

### "No such table: candidates"
- Tables are created automatically in `conftest.py`
- Check SQLite and aiosqlite are installed

### "module not found"
- Run from project root
- Check PYTHONPATH: `export PYTHONPATH=/sessions/awesome-youthful-maxwell/hr_platform`

### "asyncio not installed"
- Install pytest-asyncio: `pip install pytest-asyncio`

### Tests hang
- Check for missing `await` keywords
- Verify `@pytest.mark.asyncio` is present
- Check `asyncio_mode = auto` in pytest.ini

## Running Test Agent

```bash
# Start the API server
python -m api.main

# In another terminal, run tests
curl -X POST http://localhost:8000/api/v1/tests/run-all \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Get results
curl http://localhost:8000/api/v1/tests/results/{run_id} \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Key Test Files

| File | Purpose | Key Tests |
|------|---------|-----------|
| `test_models/test_candidate.py` | Candidate model | 15+ tests |
| `test_models/test_requirement.py` | Requirement model | 12+ tests |
| `test_services/test_matching_service.py` | Matching logic | 20+ tests |
| `test_agents/test_base_agent.py` | Agent lifecycle | 15+ tests |
| `test_api/test_health.py` | API endpoints | 10+ tests |
| `test_config/test_settings.py` | Configuration | 12+ tests |
| `test_utils/test_security.py` | Security | 12+ tests |
| `test_integration/test_smoke.py` | Health checks | 10+ tests |

## Next Steps

1. Run `pytest` to execute all tests
2. Check coverage: `pytest --cov=. --cov-report=html`
3. Review TESTING.md for detailed documentation
4. Write tests for your changes
5. Ensure all tests pass before committing

## Tips

- Use descriptive test names
- Use fixtures to reduce setup code
- Mock external services
- Test both happy and error paths
- Keep tests focused and small
- Use markers for organization

## Help

For detailed documentation: See `TESTING.md`
For API testing: See `tests/test_api/test_health.py`
For fixtures: See `conftest.py`
For agent tests: See `tests/test_agents/`

Happy testing! 🧪
