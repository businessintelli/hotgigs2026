# Interview Module Integration Guide

## Quick Integration Steps

### Step 1: Install Dependencies

Ensure Anthropic SDK is in requirements.txt (already present):
```bash
anthropic==0.7.10
```

### Step 2: Set Environment Variables

Add to `.env` file:
```bash
ANTHROPIC_API_KEY=sk-... # Your Anthropic API key
```

### Step 3: Update FastAPI Router (if using v1 router pattern)

Update `/sessions/awesome-youthful-maxwell/hr_platform/api/main.py` or create a router registration file:

```python
from api.v1.interviews import router as interviews_router

# In your main app initialization
app.include_router(interviews_router)
```

### Step 4: Database Migration

Create migration for new models:

```bash
# From hr_platform directory
alembic revision --autogenerate -m "Add interview intelligence models"
alembic upgrade head
```

The migration will create:
- `interview_recordings` table
- `interview_transcripts` table
- `interview_notes` table
- `competency_scores` table
- `interview_analytics` table
- `interview_questions` table
- `interview_responses` table

And add relationships to existing `interviews` table.

### Step 5: Initialize Agents in Application Startup

Update your app initialization to load agents:

```python
from agents.interview_agent import InterviewAgent
from agents.interview_intelligence_agent import InterviewIntelligenceAgent
from config import settings

# Global agent instances
interview_agent = None
intelligence_agent = None

@app.on_event("startup")
async def startup_event():
    global interview_agent, intelligence_agent

    # Initialize agents
    interview_agent = InterviewAgent(
        anthropic_api_key=settings.anthropic_api_key
    )
    await interview_agent.initialize()

    intelligence_agent = InterviewIntelligenceAgent(
        anthropic_api_key=settings.anthropic_api_key
    )
    await intelligence_agent.initialize()

@app.on_event("shutdown")
async def shutdown_event():
    global interview_agent, intelligence_agent

    # Shutdown agents
    if interview_agent:
        await interview_agent.shutdown()
    if intelligence_agent:
        await intelligence_agent.shutdown()
```

## Module Dependencies

### Python Packages
- `fastapi>=0.104.1` - Web framework
- `sqlalchemy>=2.0.23` - Database ORM
- `asyncpg>=0.29.0` - PostgreSQL async driver
- `pydantic>=2.5.0` - Data validation
- `anthropic>=0.7.10` - Claude API client

### External Services
- **Anthropic Claude API**: For question generation, response evaluation, and analysis
- **PostgreSQL**: For persistent storage
- **S3 (Optional)**: For recording storage

## Code Structure Overview

```
hr_platform/
├── models/
│   ├── interview.py                 # Interview and Feedback models
│   └── interview_intelligence.py     # Intelligence models (new)
├── agents/
│   ├── interview_agent.py            # Question generation & scoring (new)
│   └── interview_intelligence_agent.py # Recording analysis (new)
├── services/
│   └── interview_service.py          # Business logic (new)
├── schemas/
│   ├── interview.py                  # Interview schemas
│   └── interview_intelligence.py      # Intelligence schemas (new)
└── api/
    └── v1/
        └── interviews.py             # REST endpoints (new)
```

## API Usage Examples

### Example 1: Complete Interview Flow

```python
import httpx
from datetime import datetime, timedelta

async def full_interview_flow():
    async with httpx.AsyncClient() as client:
        # 1. Schedule interview
        schedule_resp = await client.post(
            "http://localhost:8000/api/v1/interviews/schedule",
            json={
                "candidate_id": 1,
                "requirement_id": 1,
                "interview_type": "ai_chat",
                "scheduled_at": (datetime.now() + timedelta(hours=1)).isoformat(),
                "duration_minutes": 45,
                "interviewer_name": "AI System"
            }
        )
        interview_id = schedule_resp.json()["id"]

        # 2. Start chat interview
        start_resp = await client.post(
            f"http://localhost:8000/api/v1/interviews/{interview_id}/start-chat"
        )
        first_question = start_resp.json()["first_question"]

        # 3. Submit response to first question
        response_resp = await client.post(
            f"http://localhost:8000/api/v1/interviews/{interview_id}/submit-response",
            params={
                "question_id": first_question["id"],
                "response_text": "I have 5 years of experience with Python..."
            }
        )
        evaluation = response_resp.json()

        # 4. Generate scorecard
        scorecard_resp = await client.post(
            f"http://localhost:8000/api/v1/interviews/{interview_id}/generate-scorecard"
        )
        scorecard = scorecard_resp.json()

        # 5. Get final summary
        summary_resp = await client.get(
            f"http://localhost:8000/api/v1/interviews/{interview_id}"
        )
        interview = summary_resp.json()

        return {
            "interview": interview,
            "evaluation": evaluation,
            "scorecard": scorecard
        }

# Run example
# result = asyncio.run(full_interview_flow())
```

### Example 2: Recording Processing

```python
async def process_interview_recording():
    async with httpx.AsyncClient() as client:
        # 1. Upload recording
        recording_resp = await client.post(
            "http://localhost:8000/api/v1/interviews/1/process-recording",
            json={
                "recording_url": "https://s3.amazonaws.com/bucket/recording.mp4",
                "recording_type": "video",
                "duration_seconds": 2700
            }
        )

        # 2. Get transcript
        transcript_resp = await client.get(
            "http://localhost:8000/api/v1/interviews/1/transcript"
        )
        transcript = transcript_resp.json()

        # 3. Get notes
        notes_resp = await client.get(
            "http://localhost:8000/api/v1/interviews/1/notes"
        )
        notes = notes_resp.json()

        # 4. Get analytics
        analytics_resp = await client.get(
            "http://localhost:8000/api/v1/interviews/1/analytics"
        )
        analytics = analytics_resp.json()

        return {
            "transcript": transcript,
            "notes": notes,
            "analytics": analytics
        }
```

### Example 3: Candidate Comparison

```python
async def compare_candidates():
    async with httpx.AsyncClient() as client:
        # Compare 3 candidates
        comparison_resp = await client.post(
            "http://localhost:8000/api/v1/interviews/compare",
            json={
                "interview_ids": [1, 2, 3]
            }
        )

        comparison = comparison_resp.json()

        print("Rankings:")
        for ranking in comparison["overall_rankings"]:
            print(f"  {ranking['rank']}. {ranking['candidate']} - Score: {ranking['score']}")

        print("\nTop Candidate Strengths:")
        for strength in comparison["strengths_by_candidate"]["1"]:
            print(f"  - {strength}")

        return comparison
```

## Service Layer Usage

### Direct Service Usage (Backend)

```python
from sqlalchemy.ext.asyncio import AsyncSession
from services.interview_service import InterviewService
from agents.interview_agent import InterviewAgent
from config import settings

# Initialize
db_session = AsyncSession(engine)
interview_agent = InterviewAgent(settings.anthropic_api_key)
service = InterviewService(db_session, interview_agent)

# Schedule
from schemas.interview import InterviewCreate
interview_data = InterviewCreate(
    candidate_id=1,
    requirement_id=1,
    interview_type="ai_chat"
)
interview = await service.schedule_interview(interview_data)

# Start chat
result = await service.start_chat_interview(
    interview_id=interview.id,
    requirement_id=1,
    candidate_id=1,
    candidate_profile=candidate_data,
    requirement_context=requirement_data
)
```

## Agent Usage Examples

### Interview Agent

```python
from agents.interview_agent import InterviewAgent
from config import settings

agent = InterviewAgent(settings.anthropic_api_key)
await agent.initialize()

# Generate questions
questions = await agent.generate_questions(
    requirement_id=1,
    candidate_id=1,
    candidate_profile={
        "id": 1,
        "first_name": "John",
        "current_title": "Software Engineer",
        "skills": [{"skill": "Python"}, {"skill": "Django"}]
    },
    requirement_context={
        "id": 1,
        "title": "Senior Python Developer",
        "skills_required": ["Python", "Django", "PostgreSQL"]
    }
)

# Evaluate response
evaluation = await agent.evaluate_response(
    question=questions[0],
    response="I have 5 years of professional Python experience...",
    requirement_context=requirement_context
)

print(f"Score: {evaluation.ai_score}/100")
print(f"Strengths: {evaluation.strengths}")
```

### Intelligence Agent

```python
from agents.interview_intelligence_agent import InterviewIntelligenceAgent
from config import settings

agent = InterviewIntelligenceAgent(settings.anthropic_api_key)
await agent.initialize()

# Process recording
transcript = await agent.process_recording(
    recording_url="https://s3.../recording.mp4",
    interview_id=1,
    recording_id=1
)

# Extract competencies
competencies = await agent.extract_competencies(
    transcript=transcript,
    requirement_skills=["Python", "Django", "Problem-solving"]
)

# Analyze sentiment
sentiment = await agent.analyze_sentiment(transcript)

# Generate analytics
analytics = await agent.generate_interview_analytics(
    interview_id=1,
    transcript=transcript
)

# Detect bias
bias_report = await agent.detect_bias(transcript)
```

## Database Schema

### New Tables Created

```sql
-- Recording
CREATE TABLE interview_recordings (
    id SERIAL PRIMARY KEY,
    interview_id INTEGER NOT NULL REFERENCES interviews(id),
    recording_url VARCHAR(500) NOT NULL,
    recording_type VARCHAR(50) NOT NULL,
    duration_seconds INTEGER,
    file_size INTEGER,
    storage_path VARCHAR(500),
    status VARCHAR(50) DEFAULT 'pending',
    processing_error TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Transcript
CREATE TABLE interview_transcripts (
    id SERIAL PRIMARY KEY,
    recording_id INTEGER NOT NULL REFERENCES interview_recordings(id),
    full_text TEXT NOT NULL,
    segments JSONB DEFAULT '[]',
    language VARCHAR(10) DEFAULT 'en',
    word_count INTEGER DEFAULT 0,
    confidence_score FLOAT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Notes
CREATE TABLE interview_notes (
    id SERIAL PRIMARY KEY,
    interview_id INTEGER NOT NULL REFERENCES interviews(id),
    note_type VARCHAR(50) NOT NULL,
    category VARCHAR(255),
    content TEXT NOT NULL,
    timestamp_start INTEGER,
    timestamp_end INTEGER,
    confidence FLOAT,
    source VARCHAR(50) DEFAULT 'ai',
    supporting_quotes JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Competency Scores
CREATE TABLE competency_scores (
    id SERIAL PRIMARY KEY,
    interview_id INTEGER NOT NULL REFERENCES interviews(id),
    candidate_id INTEGER NOT NULL REFERENCES candidates(id),
    competency_name VARCHAR(255) NOT NULL,
    rating INTEGER NOT NULL,
    evidence JSONB DEFAULT '[]',
    confidence FLOAT,
    assessed_by VARCHAR(50) DEFAULT 'ai',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Analytics
CREATE TABLE interview_analytics (
    id SERIAL PRIMARY KEY,
    interview_id INTEGER NOT NULL UNIQUE REFERENCES interviews(id),
    talk_time_ratio FLOAT,
    question_count INTEGER DEFAULT 0,
    avg_response_length FLOAT,
    sentiment_overall VARCHAR(50),
    sentiment_trend JSONB DEFAULT '{}',
    interview_quality_score FLOAT,
    bias_flags JSONB DEFAULT '[]',
    question_coverage JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Questions
CREATE TABLE interview_questions (
    id SERIAL PRIMARY KEY,
    interview_id INTEGER NOT NULL REFERENCES interviews(id),
    question_text TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    difficulty VARCHAR(20) DEFAULT 'medium',
    "order" INTEGER NOT NULL,
    generated_by VARCHAR(50) DEFAULT 'ai',
    context JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Responses
CREATE TABLE interview_responses (
    id SERIAL PRIMARY KEY,
    question_id INTEGER NOT NULL UNIQUE REFERENCES interview_questions(id),
    response_text TEXT,
    response_audio_url VARCHAR(500),
    response_video_url VARCHAR(500),
    duration_seconds INTEGER,
    answered_at TIMESTAMP,
    ai_score FLOAT,
    evaluator_score FLOAT,
    evaluation_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);
```

## Testing

### Unit Test Example

```python
import pytest
from agents.interview_agent import InterviewAgent
from unittest.mock import Mock, AsyncMock, patch

@pytest.mark.asyncio
async def test_generate_questions():
    # Mock Anthropic client
    with patch('agents.interview_agent.Anthropic') as mock_client:
        mock_client.return_value.messages.create = AsyncMock(
            return_value=Mock(
                content=[Mock(text='[{"text": "Question?", "category": "technical"}]')]
            )
        )

        agent = InterviewAgent("test-key")
        questions = await agent.generate_questions(
            requirement_id=1,
            candidate_id=1,
            candidate_profile={},
            requirement_context={},
            question_count=1
        )

        assert len(questions) == 1
        assert questions[0].question_text == "Question?"

@pytest.mark.asyncio
async def test_evaluate_response():
    with patch('agents.interview_agent.Anthropic') as mock_client:
        mock_client.return_value.messages.create = AsyncMock(
            return_value=Mock(
                content=[Mock(text='{"score": 85, "notes": "Good", "strengths": ["Clear"], "improvements": ["More detail"]}')]
            )
        )

        agent = InterviewAgent("test-key")
        from agents.interview_agent import InterviewQuestion

        evaluation = await agent.evaluate_response(
            question=InterviewQuestion("Test?", "technical"),
            response="Test answer",
            requirement_context={}
        )

        assert evaluation.ai_score == 85
```

## Monitoring and Logging

The module uses Python's logging framework. Set log level in settings:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Get logger for interview agents
interview_logger = logging.getLogger("agents.interview_agent")
intelligence_logger = logging.getLogger("agents.interview_intelligence_agent")
```

## Performance Tips

1. **Batch Processing**: Process multiple recordings asynchronously
2. **Caching**: Cache Claude API responses for identical questions
3. **Indexing**: Add database indexes on frequently queried fields
4. **Pagination**: Use pagination for requirement summaries with many interviews
5. **Async Processing**: Use background tasks for recording processing

## Troubleshooting

### Issue: "ANTHROPIC_API_KEY not set"
**Solution**: Add `ANTHROPIC_API_KEY` to `.env` file

### Issue: "Interview not found"
**Solution**: Verify interview_id exists before calling endpoints

### Issue: Claude API rate limiting
**Solution**: Implement retry logic with exponential backoff

### Issue: Recording processing timeout
**Solution**: Process long recordings asynchronously using Celery or similar

## Next Steps

1. Run database migrations
2. Update API router registration
3. Initialize agents in app startup
4. Test endpoints with sample data
5. Deploy to staging environment
6. Monitor logs and metrics
7. Gather feedback from users

## Support & Documentation

- See `INTERVIEW_MODULE.md` for complete feature documentation
- See `INTERVIEW_IMPLEMENTATION_SUMMARY.md` for code structure details
- Check agent docstrings for method-level documentation
- Review test cases for usage examples
