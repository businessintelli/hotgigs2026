# Integration Guide for Matching Engine

This guide shows how to integrate the Matching Engine module into the HR platform application.

## Step 1: Register API Routes

Update `/sessions/awesome-youthful-maxwell/hr_platform/api/main.py`:

```python
from api.v1.matching import router as matching_router
from api.v1.resumes import router as resumes_router

# Add these lines in the FastAPI app setup section:
app.include_router(matching_router)
app.include_router(resumes_router)
```

## Step 2: Initialize Agents on Startup

Update the startup event in `api/main.py`:

```python
from agents.matching_agent import MatchingAgent
from agents.resume_parser_agent import ResumeParserAgent
from agents.resume_tailoring_agent import ResumeTailoringAgent

# Global agent instances
matching_agent: MatchingAgent = None
parser_agent: ResumeParserAgent = None
tailor_agent: ResumeTailoringAgent = None

@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    global matching_agent, parser_agent, tailor_agent

    # ... existing initialization code ...

    # Initialize agents
    matching_agent = MatchingAgent()
    parser_agent = ResumeParserAgent()
    tailor_agent = ResumeTailoringAgent()

    await matching_agent.initialize()
    await parser_agent.initialize()
    await tailor_agent.initialize()

    logger.info("Matching Engine agents initialized")
```

## Step 3: Create Database Alembic Migration

The matching engine uses the existing `MatchScore` model. Ensure migrations are up to date:

```bash
alembic upgrade head
```

## Step 4: Install Required Dependencies

Add to `requirements.txt`:

```
# Resume parsing
pdfplumber>=0.9.0
python-docx>=0.8.11
spacy>=3.5.0

# NLP models
https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.5.0/en_core_web_sm-3.5.0-py3-none-any.whl

# LLM/API
anthropic>=0.7.0

# Utilities
python-multipart>=0.0.6
aiofiles>=23.0.0
```

Install spaCy model:

```bash
python -m spacy download en_core_web_sm
```

## Step 5: Configure Environment Variables

Add to `.env`:

```env
# Matching Configuration
MATCHING_SKILL_WEIGHT=0.35
MATCHING_EXPERIENCE_WEIGHT=0.25
MATCHING_EDUCATION_WEIGHT=0.15
MATCHING_LOCATION_WEIGHT=0.10
MATCHING_RATE_WEIGHT=0.10
MATCHING_AVAILABILITY_WEIGHT=0.05

# API Keys
ANTHROPIC_API_KEY=your_api_key_here

# File Storage
RESUME_UPLOAD_DIR=/var/hr_platform/resumes
```

## Step 6: Event Bus Integration

Register event handlers for matching events in `agents/agent_registry.py`:

```python
from agents.events import EventType
from services.matching_service import MatchingService

async def setup_matching_handlers(event_bus, matching_service):
    """Register matching event handlers."""

    async def on_requirement_activated(event):
        """When requirement is activated, batch match candidates."""
        await matching_service.recalculate_requirement_matches(
            event.entity_id
        )

    async def on_resume_parsed(event):
        """When resume is parsed, match candidate to requirements."""
        await matching_service.match_candidate_to_requirements(
            event.payload.get("candidate_id")
        )

    event_bus.subscribe(
        EventType.REQUIREMENT_ACTIVATED,
        on_requirement_activated
    )

    event_bus.subscribe(
        EventType.RESUME_PARSED,
        on_resume_parsed
    )
```

## Step 7: Async Session Setup

Ensure database session is properly configured in `api/dependencies.py`:

```python
from database import get_session

async def get_session_dependency():
    """Get database session for dependency injection."""
    async with get_session() as session:
        yield session
```

## Step 8: Testing

Create tests in `tests/test_matching_engine.py`:

```python
import pytest
from fastapi.testclient import TestClient
from api.main import app
from database import SessionLocal

client = TestClient(app)

@pytest.mark.asyncio
async def test_match_requirement_to_candidates():
    """Test requirement matching endpoint."""
    response = client.post("/api/v1/matching/requirement/1/match")
    assert response.status_code == 200
    assert "matches" in response.json()

@pytest.mark.asyncio
async def test_upload_resume():
    """Test resume upload."""
    with open("test_resume.pdf", "rb") as f:
        response = client.post(
            "/api/v1/resumes/upload",
            files={"file": f},
            params={"candidate_id": 1}
        )
    assert response.status_code == 201
    assert "id" in response.json()

@pytest.mark.asyncio
async def test_parse_resume():
    """Test resume parsing."""
    response = client.post("/api/v1/resumes/456/parse")
    assert response.status_code == 200
    assert "parsing_confidence" in response.json()
```

## Step 9: Run Tests

```bash
pytest tests/test_matching_engine.py -v
```

## Step 10: API Documentation

The endpoints are automatically documented in:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Full Startup Example

Here's a complete startup initialization:

```python
# api/main.py
import logging
from fastapi import FastAPI
from database import init_db, close_db
from config import settings
from api.middleware import setup_middleware
from api.v1.matching import router as matching_router
from api.v1.resumes import router as resumes_router
from agents.matching_agent import MatchingAgent
from agents.resume_parser_agent import ResumeParserAgent
from agents.resume_tailoring_agent import ResumeTailoringAgent
from agents.event_bus import EventBus, RedisPubSubBroker, RabbitMQBroker

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Enterprise HR Automation Platform",
    version="1.0.0",
    debug=settings.debug,
)

# Global instances
event_bus: EventBus = None
matching_agent: MatchingAgent = None
parser_agent: ResumeParserAgent = None
tailor_agent: ResumeTailoringAgent = None

# Register routers
app.include_router(matching_router)
app.include_router(resumes_router)

# Setup middleware
setup_middleware(app)

@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    global event_bus, matching_agent, parser_agent, tailor_agent

    logger.info(f"Starting {settings.app_name}")

    # Initialize database
    await init_db()
    logger.info("Database initialized")

    # Initialize event bus
    redis_broker = RedisPubSubBroker(settings.redis_url)
    rabbitmq_broker = RabbitMQBroker(
        settings.rabbitmq_url,
        settings.rabbitmq_queue_prefix
    )

    event_bus = EventBus(
        redis_broker=redis_broker,
        rabbitmq_broker=rabbitmq_broker
    )
    await event_bus.initialize()
    logger.info("Event bus initialized")

    # Initialize matching agents
    matching_agent = MatchingAgent()
    parser_agent = ResumeParserAgent()
    tailor_agent = ResumeTailoringAgent()

    await matching_agent.initialize()
    await parser_agent.initialize()
    await tailor_agent.initialize()

    logger.info("Matching Engine agents initialized")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    global event_bus

    logger.info(f"Shutting down {settings.app_name}")

    if event_bus:
        await event_bus.close()

    await close_db()

    logger.info(f"{settings.app_name} shut down successfully")
```

## Usage Examples

### Example 1: Match Candidates in Request Handler

```python
from fastapi import APIRouter, Depends
from database import get_session, AsyncSession
from services.matching_service import MatchingService

router = APIRouter()

@router.post("/custom-match/{requirement_id}")
async def custom_match(
    requirement_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Custom matching endpoint."""
    service = MatchingService()

    result = await service.match_requirement_to_candidates(
        session,
        requirement_id,
        limit=30,
        min_score=0.6
    )

    return result
```

### Example 2: Background Task for Batch Matching

```python
from fastapi import BackgroundTasks
from database import SessionLocal
from services.matching_service import MatchingService

@router.post("/batch-match")
async def trigger_batch_match(background_tasks: BackgroundTasks):
    """Trigger batch matching as background task."""

    async def run_batch_match():
        async with SessionLocal() as session:
            service = MatchingService()
            await service.batch_match_all(session, min_score=0.5)

    background_tasks.add_task(run_batch_match)

    return {"status": "Batch matching started in background"}
```

### Example 3: Webhook for Resume Upload

```python
@router.post("/webhooks/resume-uploaded")
async def on_resume_uploaded(
    candidate_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Process newly uploaded resume."""
    service = ResumeService()

    # Get latest resume
    resumes = await service.get_candidate_resumes(session, candidate_id)
    if resumes:
        latest_resume = resumes[0]

        # Parse it
        await service.parse_resume(session, latest_resume["id"])

        # Match to requirements
        from services.matching_service import MatchingService
        match_service = MatchingService()

        result = await match_service.match_candidate_to_requirements(
            session,
            candidate_id,
            limit=10
        )

        return {
            "status": "Resume processed",
            "matches_found": result["matches_found"]
        }
```

## Deployment Checklist

- [ ] Install all dependencies from `requirements.txt`
- [ ] Download spaCy model: `python -m spacy download en_core_web_sm`
- [ ] Set environment variables (.env file)
- [ ] Run database migrations: `alembic upgrade head`
- [ ] Create resume upload directory: `mkdir -p /var/hr_platform/resumes`
- [ ] Test endpoints with Swagger UI: `http://localhost:8000/docs`
- [ ] Run test suite: `pytest tests/test_matching_engine.py`
- [ ] Configure Redis for caching
- [ ] Configure RabbitMQ for event bus
- [ ] Set up monitoring/logging

## Troubleshooting Deployment

**Issue**: `ModuleNotFoundError: No module named 'spacy'`
- Solution: Run `pip install spacy` and `python -m spacy download en_core_web_sm`

**Issue**: `No Anthropic API key configured`
- Solution: Set `ANTHROPIC_API_KEY` in `.env` file (optional if resume tailoring not needed)

**Issue**: Resume upload fails with `FileNotFoundError`
- Solution: Ensure `RESUME_UPLOAD_DIR` exists and is writable

**Issue**: Matching scores take too long
- Solution: Enable Redis caching by setting `REDIS_URL` in environment

**Issue**: Database migration errors
- Solution: Run `alembic stamp head` then `alembic upgrade head`

## Performance Tuning

1. **Batch Processing**: Use `/api/v1/matching/batch` for large-scale matching
2. **Redis Caching**: Enable Redis to cache frequently accessed matches
3. **Database Indexes**: Ensure indexes on `requirement_id`, `candidate_id`, `overall_score`
4. **Connection Pooling**: Set `DATABASE_POOL_SIZE=50` for high concurrency
5. **Async Optimization**: Use connection pooling with asyncpg

## Next Steps

1. Follow this integration guide step by step
2. Run the test suite
3. Deploy to staging environment
4. Run load tests
5. Monitor performance in production
6. Iterate on weight configuration based on hiring outcomes
