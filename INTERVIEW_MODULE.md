# Interview Module Documentation

## Overview

The Interview Module is a comprehensive AI-powered interview management system that combines intelligent screening, real-time analysis, and competency assessment. It leverages Anthropic's Claude API for intelligent question generation, response evaluation, and insight extraction from interview recordings.

## Architecture

### Core Components

1. **Interview Agent** (`agents/interview_agent.py`)
   - Generates role-specific interview questions
   - Evaluates candidate responses in real-time
   - Creates structured interview scorecards
   - Calculates interview scores and feedback

2. **Interview Intelligence Agent** (`agents/interview_intelligence_agent.py`)
   - Processes interview recordings (audio/video)
   - Generates transcripts with timestamped segments
   - Extracts competencies from transcripts
   - Analyzes sentiment and confidence levels
   - Detects bias in interview questions
   - Compares multiple candidates

3. **Interview Service** (`services/interview_service.py`)
   - Manages interview lifecycle (scheduling, completion)
   - Handles recording processing
   - Generates and stores scorecards
   - Aggregates interview data and metrics

4. **Interview API** (`api/v1/interviews.py`)
   - REST endpoints for interview management
   - Question generation and response submission
   - Recording processing and transcript retrieval
   - Analytics and comparison endpoints

### Data Models

#### Core Interview Models
- `Interview`: Main interview record with scheduling and status
- `InterviewFeedback`: Evaluation and feedback data

#### Interview Intelligence Models
- `InterviewRecording`: Recording metadata and storage information
- `InterviewTranscript`: Full transcript with timestamped segments
- `InterviewNote`: Structured notes from analysis (competencies, observations, red flags)
- `CompetencyScore`: Competency assessment with ratings and evidence
- `InterviewAnalytics`: Interview metrics (talk time, sentiment, quality score)
- `InterviewQuestion`: AI-generated questions for chat interviews
- `InterviewResponse`: Candidate responses with evaluation scores

## Features

### 1. AI Chat Interview

**Question Generation**
- Role-specific questions based on job requirements
- Mix of technical, behavioral, situational, and culture-fit questions
- Adaptive difficulty levels
- Context-aware questions using candidate resume data

**Example:**
```python
# Generate interview questions
questions = await interview_agent.generate_questions(
    requirement_id=1,
    candidate_id=1,
    candidate_profile=candidate_data,
    requirement_context=requirement_data,
    question_count=10
)
```

**Question Types:**
- **Technical**: Assess domain expertise and specific skill proficiency
- **Behavioral**: Understand past experiences and work approach
- **Situational**: Evaluate problem-solving and decision-making
- **Culture Fit**: Assess alignment with team and company values

**Response Evaluation**
- Real-time scoring (0-100 scale)
- Identification of strengths and areas for improvement
- Confidence scoring
- Evidence extraction

### 2. Scorecard Generation

**Automated Scorecard Features:**
- Competency-based evaluation (1-5 rating scale)
- Core competencies assessed:
  - Technical Proficiency
  - Problem Solving
  - Communication
  - Leadership/Teamwork
  - Adaptability
  - Customer Focus
  - Analytical Thinking
  - Time Management

**Scorecard Output:**
```python
{
  "interview_id": 1,
  "candidate_name": "John Doe",
  "requirement_title": "Senior Backend Engineer",
  "competencies": [
    {
      "name": "Technical Proficiency",
      "rating": 4,
      "evidence": ["Demonstrated strong Python skills", "Excellent architecture knowledge"],
      "comments": "Strong technical foundation with good design patterns"
    }
  ],
  "overall_rating": 4,
  "recommendation": "hire",
  "strengths": ["Communication", "Problem-solving", "Technical depth"],
  "weaknesses": ["Leadership experience", "Public speaking"],
  "next_steps": ["Extend offer", "Negotiate salary"]
}
```

### 3. Interview Intelligence

**Transcript Processing:**
- Audio/video to text conversion
- Speaker identification (Interviewer vs Candidate)
- Timestamped segments for easy reference
- Confidence scores for accuracy

**Competency Extraction:**
- Analyzes transcript for evidence of key competencies
- Rates each competency (1-5)
- Provides supporting quotes and evidence
- Tracks confidence in assessments

**Sentiment Analysis:**
- Overall sentiment classification (positive/neutral/negative)
- Sentiment trend throughout interview
- Confidence intervals
- Red flag detection (evasiveness, inconsistencies)

**Interview Analytics:**
- Talk time ratio (candidate:interviewer)
- Average response length
- Question coverage analysis
- Interview quality score (0-100)
- Bias detection and flags

**Bias Detection:**
- Identifies leading questions
- Detects illegal or discriminatory questions
- Analyzes question patterns for fairness
- Provides recommendations for improvement

### 4. Candidate Comparison

Compare multiple candidates across:
- Competency ratings
- Technical proficiency
- Communication effectiveness
- Cultural fit indicators
- Overall assessment scores

**Output:**
```python
{
  "candidate_ids": [1, 2, 3],
  "candidate_names": ["Alice Smith", "Bob Jones", "Carol White"],
  "overall_rankings": [
    {"rank": 1, "candidate": "Alice Smith", "score": 4.5},
    {"rank": 2, "candidate": "Bob Jones", "score": 4.2},
    {"rank": 3, "candidate": "Carol White", "score": 3.8}
  ],
  "strengths_by_candidate": {
    1: ["Technical depth", "Communication", "Problem-solving"],
    2: ["Technical breadth", "Team collaboration"],
    3: ["Customer focus", "Adaptability"]
  }
}
```

## API Endpoints

### Interview Management

**Schedule Interview**
```
POST /api/v1/interviews/schedule
Content-Type: application/json

{
  "candidate_id": 1,
  "requirement_id": 1,
  "interview_type": "ai_chat",
  "scheduled_at": "2024-03-01T10:00:00Z",
  "duration_minutes": 45,
  "interviewer_name": "John Recruiter"
}
```

**Get Interview**
```
GET /api/v1/interviews/{interview_id}
```

**Update Interview**
```
PUT /api/v1/interviews/{interview_id}
Content-Type: application/json

{
  "status": "completed",
  "recording_url": "https://..."
}
```

### Chat Interview

**Start Chat Interview**
```
POST /api/v1/interviews/{interview_id}/start-chat
```

Returns:
```json
{
  "interview_id": 1,
  "status": "in_progress",
  "questions_count": 10,
  "first_question": {
    "question_text": "Tell me about your experience with Python...",
    "category": "technical",
    "difficulty": "medium",
    "order": 1
  }
}
```

**Get Questions**
```
GET /api/v1/interviews/{interview_id}/questions
```

**Submit Response**
```
POST /api/v1/interviews/{interview_id}/submit-response?question_id=1&response_text=...

{
  "ai_score": 78,
  "evaluation_notes": "Good understanding of concepts...",
  "strengths": ["Clear explanation", "Good examples"],
  "improvements": ["More technical depth needed"]
}
```

### Scorecard & Feedback

**Generate Scorecard**
```
POST /api/v1/interviews/{interview_id}/generate-scorecard
```

**Get Scorecard**
```
GET /api/v1/interviews/{interview_id}/scorecard
```

**Submit Feedback**
```
POST /api/v1/interviews/{interview_id}/feedback
Content-Type: application/json

{
  "evaluator": "Jane Manager",
  "overall_rating": 4,
  "technical_rating": 4,
  "communication_rating": 3,
  "culture_fit_rating": 4,
  "problem_solving_rating": 4,
  "strengths": ["Strong technical skills", "Good communication"],
  "weaknesses": ["Limited leadership experience"],
  "recommendation": "hire"
}
```

**Get Feedback**
```
GET /api/v1/interviews/{interview_id}/feedback
```

### Recording & Analysis

**Process Recording**
```
POST /api/v1/interviews/{interview_id}/process-recording
Content-Type: application/json

{
  "recording_url": "https://s3.amazonaws.com/...",
  "recording_type": "video",
  "duration_seconds": 2700
}
```

**Get Transcript**
```
GET /api/v1/interviews/{interview_id}/transcript
```

**Get Notes**
```
GET /api/v1/interviews/{interview_id}/notes
```

**Get Analytics**
```
GET /api/v1/interviews/{interview_id}/analytics
```

### Comparison

**Compare Candidates**
```
POST /api/v1/interviews/compare
Content-Type: application/json

{
  "interview_ids": [1, 2, 3]
}
```

### Requirement Summary

**Get Requirement Summary**
```
GET /api/v1/interviews/requirement/{requirement_id}/summary
```

Returns:
```json
{
  "requirement_id": 1,
  "total_interviews": 5,
  "completed_interviews": 4,
  "avg_rating": 3.8,
  "interviews": [...]
}
```

## Usage Examples

### 1. Schedule and Conduct AI Chat Interview

```python
from services.interview_service import InterviewService
from schemas.interview import InterviewCreate
from models.enums import InterviewType

# Schedule interview
interview_data = InterviewCreate(
    candidate_id=1,
    requirement_id=1,
    interview_type=InterviewType.AI_CHAT,
    duration_minutes=45
)
interview = await service.schedule_interview(interview_data)

# Start chat interview
result = await service.start_chat_interview(
    interview_id=interview.id,
    requirement_id=1,
    candidate_id=1,
    candidate_profile=candidate_data,
    requirement_context=requirement_data
)

# Submit responses
for question in questions:
    evaluation = await service.submit_response(
        interview_id=interview.id,
        question_id=question.id,
        response_text="Candidate response...",
        requirement_context=requirement_data
    )

# Complete interview
await service.complete_interview(interview.id)

# Generate scorecard
feedback = await service.generate_scorecard(
    interview_id=interview.id,
    requirement_id=1,
    candidate_id=1,
    candidate_name="John Doe",
    requirement_title="Senior Developer",
    candidate_profile=candidate_data
)
```

### 2. Process Recording and Extract Insights

```python
# Process recording
recording = await service.process_recording(
    interview_id=1,
    recording_url="https://s3.amazonaws.com/recording.mp4",
    recording_type="video",
    duration_seconds=2700
)

# Generate transcript (done automatically during processing)
transcript = await intelligence_agent.process_recording(
    recording_url=recording.recording_url,
    interview_id=1,
    recording_id=recording.id
)

# Extract competencies
competencies = await intelligence_agent.extract_competencies(
    transcript=transcript,
    requirement_skills=["Python", "Django", "PostgreSQL", "AWS"]
)

# Analyze sentiment
sentiment = await intelligence_agent.analyze_sentiment(transcript)

# Generate analytics
analytics = await intelligence_agent.generate_interview_analytics(
    interview_id=1,
    transcript=transcript
)

# Detect bias
bias_report = await intelligence_agent.detect_bias(transcript)
```

### 3. Compare Multiple Candidates

```python
# Compare 3 candidates
comparison = await intelligence_agent.compare_candidates(
    interview_ids=[1, 2, 3],
    candidate_data=[
        {"name": "Alice Smith", "id": 1, "current_title": "Senior Dev"},
        {"name": "Bob Jones", "id": 2, "current_title": "Mid-level Dev"},
        {"name": "Carol White", "id": 3, "current_title": "Senior Dev"}
    ]
)

print(f"Rankings: {comparison.rankings}")
print(f"Strengths by candidate: {comparison.strengths_by_candidate}")
```

## Configuration

Set the following environment variables:

```bash
# Anthropic API
ANTHROPIC_API_KEY=sk-...

# Interview settings
INTERVIEW_QUESTION_COUNT=10
INTERVIEW_DEFAULT_DURATION_MINUTES=45

# Recording/transcription settings
RECORDING_STORAGE_BUCKET=hr-platform-recordings
RECORDING_MAX_SIZE_MB=500
```

## Error Handling

The module includes comprehensive error handling:

```python
try:
    interview = await service.schedule_interview(interview_data)
except ValueError as e:
    # Invalid candidate or requirement ID
    handle_validation_error(e)
except Exception as e:
    # Unexpected error
    logger.error(f"Error: {str(e)}")
    raise HTTPException(status_code=500, detail="Failed to schedule interview")
```

## Performance Considerations

1. **Question Generation**: Uses Claude API - typically 2-5 seconds per request
2. **Response Evaluation**: Real-time scoring - typically 1-2 seconds per response
3. **Recording Processing**: Asynchronous task - depends on recording length
4. **Transcript Analysis**: Asynchronous task - batched for efficiency
5. **Database Indexing**: Interviews indexed by candidate_id, requirement_id, status

## Security Considerations

1. **API Key Management**: Anthropic API key stored in environment variables
2. **Recording Storage**: Recordings stored in secure S3 bucket with encryption
3. **Database Access**: All database operations use SQLAlchemy ORM with parameterized queries
4. **Audit Logging**: All interview operations are logged for compliance

## Future Enhancements

1. **Multi-language Support**: Support for interviews in languages other than English
2. **Custom Competency Models**: Allow customers to define custom competencies
3. **Interview Templates**: Pre-built question templates for common roles
4. **Real-time Interview**: Live interview mode with AI interviewer
5. **Video Analysis**: Extract body language, eye contact, and confidence indicators
6. **Skill Gap Analysis**: Identify specific skill gaps for training recommendations
7. **Candidate Pooling**: Archive and compare candidates over time

## Troubleshooting

### Issue: Interview questions not generating

**Solution**: Verify Anthropic API key is set and valid. Check logs for API errors.

### Issue: Recording processing stuck

**Solution**: Check recording URL accessibility. Verify file size is within limits. Check storage permissions.

### Issue: Low bias detection confidence

**Solution**: Provide longer transcripts (5+ minutes). Ensure clear audio quality. Check if interview includes diverse question types.

## Support

For issues or questions about the Interview Module:
1. Check the API documentation in this file
2. Review error logs for specific error messages
3. Verify configuration settings
4. Contact the development team

## Version History

- **v1.0.0** (2024-02-13): Initial release
  - Interview Agent with question generation and response evaluation
  - Interview Intelligence Agent with recording processing and analytics
  - REST API with full interview lifecycle management
  - Scorecard generation and feedback submission
  - Candidate comparison and analytics
