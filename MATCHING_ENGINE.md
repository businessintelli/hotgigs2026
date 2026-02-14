# Matching Engine Module

## Overview

The Matching Engine is a comprehensive module for the HR platform that combines bidirectional candidate-requirement matching with advanced resume analysis and parsing. It's inspired by Jobright.ai's matching algorithm and extends it with custom scoring logic and AI-powered resume tailoring.

## Architecture

The Matching Engine consists of several components:

```
┌─────────────────────────────────────────────────────────┐
│                   Matching Engine                        │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Agents (agents/)                                 │   │
│  │ ├── matching_agent.py         (Core matching)    │   │
│  │ ├── resume_tailoring_agent.py (AI rewriting)     │   │
│  │ └── resume_parser_agent.py    (NLP parsing)      │   │
│  └──────────────────────────────────────────────────┘   │
│                          ↓                               │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Services (services/)                             │   │
│  │ ├── matching_service.py       (Orchestration)    │   │
│  │ └── resume_service.py         (File management)  │   │
│  └──────────────────────────────────────────────────┘   │
│                          ↓                               │
│  ┌──────────────────────────────────────────────────┐   │
│  │ API Endpoints (api/v1/)                          │   │
│  │ ├── matching.py       (/api/v1/matching/*)       │   │
│  │ └── resumes.py        (/api/v1/resumes/*)        │   │
│  └──────────────────────────────────────────────────┘   │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

## Key Components

### 1. Matching Agent (`agents/matching_agent.py`)

The core matching algorithm that calculates bidirectional compatibility scores.

#### Scoring Algorithm (7 Components)

The matching engine uses a 7-component weighted scoring system:

```
Overall Score =
    0.35 * Skill Score +
    0.25 * Experience Score +
    0.15 * Education Score +
    0.10 * Location Score +
    0.10 * Rate Score +
    0.05 * Availability Score +
    0.00 * Culture Score (calculated from feedback)
```

**Score Weights** (configurable via API):
- **Skill Score (35%)**: Exact, synonym, related, or partial skill matching
- **Experience Score (25%)**: Years of experience vs. required range
- **Education Score (15%)**: Degree level alignment
- **Location Score (10%)**: Geographic fit (remote, same city/state/country)
- **Rate Score (10%)**: Compensation within budget
- **Availability Score (5%)**: Start date alignment
- **Culture Score (0%)**: Derived from interview feedback

#### Skill Matching Logic

The agent uses a 4-tier matching hierarchy:

1. **Exact Match (1.0)**: "JavaScript" matches "JavaScript"
2. **Synonym Match (0.9)**: "JS" matches "JavaScript" (from SKILL_SYNONYMS dict)
3. **Related Skill (0.7)**: "React" matches requirement for "JavaScript" (from SKILL_RELATIONS dict)
4. **Partial Match (0.5)**: "Script" partially matches "JavaScript"
5. **No Match (0.0)**: No match found

#### Built-in Skill Dictionaries

The agent includes comprehensive skill mappings:

**SKILL_SYNONYMS** (100+ mappings):
- `"javascript": ["js", "es6", "node.js", "nodejs"]`
- `"python": ["py", "django", "flask", "fastapi"]`
- `"react": ["reactjs"]`
- `"aws": ["amazon web services"]`
- ... and many more

**SKILL_RELATIONS** (30+ relationships):
- `"javascript": ["typescript", "node.js", "react", "angular", "vue", "html", "css"]`
- `"python": ["django", "flask", "fastapi", "data science", "machine learning"]`
- `"microservices": ["docker", "kubernetes", "api", "message queues"]`
- ... and more

#### Methods

**Core Matching Methods:**
- `match_requirement_to_candidates()`: Find all candidates for a requirement
- `match_candidate_to_requirements()`: Find all requirements for a candidate
- `batch_match_all()`: Match all active requirements to all candidates
- `calculate_match_score()`: Detailed score calculation for a pair
- `recalculate_requirement_matches()`: Refresh all matches for a requirement

**Component Scoring Methods:**
- `score_skills()`: Skills matching with missing/standout analysis
- `score_experience()`: Years of experience alignment
- `score_education()`: Education level matching
- `score_location()`: Geographic fit
- `score_rate()`: Compensation alignment
- `score_availability()`: Start date alignment
- `score_culture()`: Culture fit from feedback

### 2. Resume Tailoring Agent (`agents/resume_tailoring_agent.py`)

AI-powered resume optimization using Claude API for intelligent rewriting and ATS optimization.

#### Key Features

**Resume Tailoring:**
- Analyzes job description to identify key skills and keywords
- Intelligently rewrites experience bullets to emphasize relevant skills
- Reorders work experience by relevance to job
- Adds missing keywords where truthful (no fabrication)
- Uses Claude API for semantic understanding

**Keyword Gap Analysis:**
- Compares resume content to job description
- Identifies missing hard skills
- Identifies missing soft skills
- Calculates keyword density percentage
- Shows coverage of JD requirements

**ATS Compatibility Scoring (0-100):**
- **Formatting Score**: No special characters, standard fonts, proper structure
- **Keywords Score**: Technical keywords and action verbs present
- **Structure Score**: Clear sections (Experience, Skills, Education)
- **Length Score**: Optimal 250-1000 word range
- **Readability Score**: Bullet points, whitespace, line length

#### ATS Score Components

```python
ATS Score Breakdown:
- Formatting (25%): Special characters, fonts, structure
- Keywords (25%): Industry-specific terms and action verbs
- Structure (20%): Section headers and organization
- Length (15%): Word count optimization
- Readability (15%): Scannable format and spacing
```

#### Methods

- `generate_tailored_resume()`: AI-powered resume rewriting
- `analyze_keyword_gaps()`: Gap analysis between resume and JD
- `calculate_ats_compatibility_score()`: Full ATS scoring
- `tailor_resume_for_requirement()`: Complete tailoring workflow
- `get_ats_score()`: ATS score calculation

### 3. Resume Parser Agent (`agents/resume_parser_agent.py`)

NLP-based resume parsing using spaCy and regex patterns.

#### Extraction Capabilities

**Contact Information:**
- Name (with confidence scoring)
- Email (regex-based)
- Phone number
- LinkedIn URL
- Location (city, state, country)

**Skills Extraction:**
- 50+ skill categories (programming languages, frameworks, databases, etc.)
- Proficiency level inference
- Extraction confidence scores
- Category classification

**Work Experience:**
- Company name
- Job title
- Start and end dates
- Current position detection
- Responsibilities (bullet-point extraction)

**Education:**
- Degree type (Bachelor, Master, PhD, etc.)
- Field of study
- Institution name
- Graduation year
- GPA (if present)

**Certifications:**
- Certification names
- Issuing organizations
- Confidence scores

#### Parser Features

- **Multi-format Support**: PDF and DOCX files
- **Confidence Scoring**: Each extracted field has a confidence score
- **Duplicate Detection**: Fuzzy name matching and email deduplication
- **Flexible Parsing**: Works with various resume formats
- **Fallback Patterns**: Handles missing or unconventional sections

#### Methods

- `extract_text_from_file()`: PDF/DOCX text extraction
- `extract_contact_info()`: Contact information extraction
- `extract_skills()`: Skill extraction with proficiency levels
- `extract_work_experience()`: Experience section parsing
- `extract_education()`: Education information extraction
- `extract_certifications()`: Certification extraction
- `parse_resume()`: Complete parsing workflow
- `check_duplicate_candidate()`: Duplicate detection

### 4. Matching Service (`services/matching_service.py`)

Service layer orchestrating matching operations and database interactions.

#### Key Operations

- **Requirement Matching**: Match all candidates to a requirement
- **Candidate Matching**: Match all requirements to a candidate
- **Batch Operations**: Match all active requirements and candidates
- **Score Management**: Get, update, and override match scores
- **Weight Configuration**: Update matching algorithm weights
- **Redis Caching**: Cache frequently accessed results

#### Methods

- `match_requirement_to_candidates()`: Find candidates for requirement
- `match_candidate_to_requirements()`: Find requirements for candidate
- `get_match_score()`: Retrieve specific match score
- `get_requirement_matches()`: Paginated requirement matches
- `update_match_weights()`: Update algorithm weights
- `batch_match_all()`: Batch matching operation
- `recalculate_requirement_matches()`: Refresh requirement matches
- `override_match()`: Manual score override
- `cache_match_results()`: Redis caching
- `get_cached_matches()`: Retrieve cached results

### 5. Resume Service (`services/resume_service.py`)

File management and processing for resume operations.

#### Key Operations

- **File Upload**: Secure upload with validation
- **Resume Parsing**: Trigger parser agent
- **Data Storage**: Store parsed results
- **Tailoring**: Generate tailored versions
- **ATS Scoring**: Calculate compatibility
- **Skill Search**: Find resumes by skills
- **Version Management**: Resume versioning

#### Methods

- `upload_resume()`: File upload and storage
- `parse_resume()`: Parsing workflow
- `get_parsed_resume()`: Retrieve parsed data
- `tailor_resume()`: Generate tailored version
- `get_ats_score()`: ATS score calculation
- `search_resumes_by_skills()`: Skill-based search
- `get_candidate_resumes()`: List candidate's resumes
- `delete_resume()`: File deletion
- `create_resume_version()`: Version creation

## API Endpoints

### Matching Endpoints (`/api/v1/matching/`)

#### POST `/requirement/{requirement_id}/match`
Match all candidates to a requirement.

**Query Parameters:**
- `limit` (int): Max results (default: 50)
- `min_score` (float): Minimum score threshold (default: 0.5)

**Response:**
```json
{
  "requirement_id": 1,
  "matches_found": 25,
  "matches": [
    {
      "candidate_id": 123,
      "candidate_name": "John Doe",
      "candidate_email": "john@example.com",
      "overall_score": 0.92,
      "skill_score": 0.95,
      "experience_score": 0.88,
      "education_score": 0.85,
      "location_score": 1.0,
      "rate_score": 0.90,
      "availability_score": 1.0,
      "culture_score": 0.0,
      "missing_skills": ["Kubernetes"],
      "standout_qualities": ["Machine Learning", "AWS"],
      "score_breakdown": {...}
    }
  ],
  "timestamp": "2024-02-13T10:00:00"
}
```

#### POST `/candidate/{candidate_id}/match`
Match all requirements to a candidate.

**Query Parameters:**
- `limit` (int): Max results (default: 50)
- `min_score` (float): Minimum score threshold (default: 0.5)

#### GET `/scores/{requirement_id}/{candidate_id}`
Get specific match score between candidate and requirement.

**Response:**
```json
{
  "requirement_id": 1,
  "candidate_id": 123,
  "overall_score": 0.92,
  "skill_score": 0.95,
  "experience_score": 0.88,
  "education_score": 0.85,
  "location_score": 1.0,
  "rate_score": 0.90,
  "availability_score": 1.0,
  "culture_score": 0.0,
  "missing_skills": ["Kubernetes"],
  "standout_qualities": ["Machine Learning"],
  "score_breakdown": {...},
  "matched_at": "2024-02-13T09:45:00"
}
```

#### GET `/scores/{requirement_id}`
Get paginated match scores for a requirement.

**Query Parameters:**
- `limit` (int): Results per page (default: 50)
- `offset` (int): Pagination offset (default: 0)

#### PUT `/config`
Update matching algorithm weights.

**Request Body:**
```json
{
  "skill": 0.35,
  "experience": 0.25,
  "education": 0.15,
  "location": 0.10,
  "rate": 0.10,
  "availability": 0.05,
  "culture": 0.0
}
```

**Validation:** Weights must sum to 1.0

#### POST `/batch`
Execute batch matching for all active requirements and candidates.

**Query Parameters:**
- `min_score` (float): Minimum score to save (default: 0.5)

**Response:**
```json
{
  "total_requirements": 50,
  "total_candidates": 1000,
  "matches_created": 15000,
  "matches_updated": 5000,
  "errors": 2,
  "timestamp": "2024-02-13T10:15:00"
}
```

#### POST `/recalculate/{requirement_id}`
Recalculate all matches for a specific requirement.

#### PUT `/override/{requirement_id}/{candidate_id}`
Manually override a match score.

**Request Body:**
```json
{
  "overall_score": 0.95,
  "notes": "Strong candidate, manual adjustment due to portfolio review"
}
```

### Resume Endpoints (`/api/v1/resumes/`)

#### POST `/upload`
Upload resume file for candidate.

**Query Parameters:**
- `candidate_id` (int): Required
- `is_primary` (bool): Primary resume flag (default: true)

**Form Data:**
- `file`: Resume file (PDF or DOCX)

**Response:**
```json
{
  "id": 456,
  "candidate_id": 123,
  "file_name": "john_doe_resume.pdf",
  "file_type": "pdf",
  "file_size": 245000,
  "is_primary": true,
  "uploaded_at": "2024-02-13T09:30:00"
}
```

#### POST `/{resume_id}/parse`
Parse resume to extract structured data.

**Response:**
```json
{
  "resume_id": 456,
  "parsed_resume_id": 789,
  "parsing_confidence": 0.87,
  "extraction_stats": {
    "skills_extracted": 15,
    "experiences_extracted": 3,
    "education_entries": 2,
    "certifications_found": 1,
    "contact_fields_found": 4
  },
  "parsed_at": "2024-02-13T09:32:00"
}
```

#### GET `/{resume_id}/parsed`
Get parsed resume data.

**Response:**
```json
{
  "id": 789,
  "resume_id": 456,
  "parsed_data": {
    "contact": {
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "(555) 123-4567",
      "linkedin": "https://linkedin.com/in/johndoe",
      "location": "San Francisco, CA"
    },
    "skills": [
      {"skill": "Python", "proficiency": "expert", "category": "programming_languages"},
      {"skill": "Django", "proficiency": "proficient", "category": "backend_frameworks"}
    ],
    "experience": [
      {
        "company": "Tech Company",
        "title": "Senior Developer",
        "start_date": "Jan 2020",
        "end_date": "Present",
        "responsibilities": ["Led team of 5 developers", "Architected microservices platform"]
      }
    ],
    "education": [
      {
        "degree": "Bachelor",
        "field": "Computer Science",
        "institution": "Stanford University",
        "graduation_year": "2018"
      }
    ],
    "certifications": [
      {"certification": "AWS Certified Solutions Architect"}
    ]
  },
  "parsing_confidence": 0.87,
  "parser_version": "1.0.0",
  "parsed_at": "2024-02-13T09:32:00"
}
```

#### POST `/{resume_id}/tailor`
Tailor resume for a specific job requirement.

**Query Parameters:**
- `requirement_id` (int): Target job requirement ID

**Response:**
```json
{
  "resume_id": 456,
  "requirement_id": 1,
  "requirement_title": "Senior Python Developer",
  "tailored_resume": "John Doe\n...[tailored content]...",
  "tailoring_analysis": "Key matches found in Django and AWS experience...",
  "keywords_emphasized": ["Python", "Django", "AWS", "Microservices"],
  "gap_analysis": {
    "missing_hard_skills": ["Kubernetes"],
    "missing_soft_skills": [],
    "covered_hard_skills": ["Python", "Django", "AWS"],
    "keyword_density": 85.5
  },
  "ats_scores": {
    "original": 78,
    "tailored": 92,
    "improvement": 14
  },
  "ats_recommendations": ["Use standard bullet points", "Enhance keyword density"],
  "generated_at": "2024-02-13T09:35:00"
}
```

#### GET `/{resume_id}/ats-score`
Get ATS compatibility score.

**Response:**
```json
{
  "resume_id": 456,
  "overall_score": 78.5,
  "max_score": 100,
  "components": {
    "formatting": 85.0,
    "keywords": 72.0,
    "structure": 80.0,
    "length": 75.0,
    "readability": 70.0
  },
  "recommendations": [
    "Add more action verbs and industry-specific keywords",
    "Use standard bullet points instead of special characters",
    "Break long paragraphs into bullet points"
  ]
}
```

#### GET `/search`
Search resumes by skills.

**Query Parameters:**
- `skills` (list): Skills to search for
- `match_all` (bool): Require all skills (default: false)

**Response:**
```json
[
  {
    "resume_id": 456,
    "candidate_id": 123,
    "matched_skills": ["Python", "Django"],
    "all_skills": ["Python", "Django", "JavaScript", "React", "AWS"]
  }
]
```

#### GET `/candidate/{candidate_id}`
Get all resumes for a candidate.

#### DELETE `/{resume_id}`
Delete a resume and its parsed data.

## Configuration

### Environment Variables

```env
# Matching Configuration
MATCHING_SKILL_WEIGHT=0.35
MATCHING_EXPERIENCE_WEIGHT=0.25
MATCHING_EDUCATION_WEIGHT=0.15
MATCHING_LOCATION_WEIGHT=0.10
MATCHING_RATE_WEIGHT=0.10
MATCHING_AVAILABILITY_WEIGHT=0.05

# API Keys
ANTHROPIC_API_KEY=sk-... (for resume tailoring)

# File Storage
RESUME_UPLOAD_DIR=/tmp/resumes
```

### Programmatic Configuration

```python
from agents.matching_agent import MatchingAgent

agent = MatchingAgent()
agent.weights = {
    "skill": 0.40,
    "experience": 0.25,
    "education": 0.15,
    "location": 0.10,
    "rate": 0.10,
    "availability": 0.0,
}
```

## Usage Examples

### Example 1: Match Candidates to a Job Requirement

```python
import asyncio
from database import SessionLocal
from services.matching_service import MatchingService

async def match_candidates_for_job():
    async with SessionLocal() as session:
        service = MatchingService()

        # Find top 20 candidates for requirement #5
        results = await service.match_requirement_to_candidates(
            session,
            requirement_id=5,
            limit=20,
            min_score=0.7
        )

        for match in results["matches"]:
            print(f"{match['candidate_name']}: {match['overall_score']}")
            print(f"  Skills: {match['skill_score']}")
            print(f"  Missing: {', '.join(match['missing_skills'])}")
            print()

asyncio.run(match_candidates_for_job())
```

### Example 2: Tailor Resume for Job

```python
import asyncio
from services.resume_service import ResumeService

async def tailor_candidate_resume():
    service = ResumeService()

    async with SessionLocal() as session:
        # Tailor resume #10 for requirement #5
        result = await service.tailor_resume(
            session,
            resume_id=10,
            requirement_id=5
        )

        print(f"ATS Score Improvement: {result['ats_scores']['improvement']}")
        print(f"New ATS Score: {result['ats_scores']['tailored']}")
        print("\nRecommendations:")
        for rec in result['ats_recommendations']:
            print(f"  - {rec}")

asyncio.run(tailor_candidate_resume())
```

### Example 3: Batch Matching

```python
import asyncio
from database import SessionLocal
from services.matching_service import MatchingService

async def batch_match_all():
    async with SessionLocal() as session:
        service = MatchingService()

        # Match all active requirements to all candidates
        stats = await service.batch_match_all(session, min_score=0.5)

        print(f"Created: {stats['matches_created']} new matches")
        print(f"Updated: {stats['matches_updated']} existing matches")
        print(f"Errors: {stats['errors']}")

asyncio.run(batch_match_all())
```

### Example 4: Parse Resume

```python
import asyncio
from database import SessionLocal
from services.resume_service import ResumeService

async def parse_resume():
    service = ResumeService()

    async with SessionLocal() as session:
        # Parse uploaded resume
        result = await service.parse_resume(session, resume_id=10)

        # Get parsed data
        parsed = await service.get_parsed_resume(session, resume_id=10)

        print(f"Parsing Confidence: {parsed['parsing_confidence']:.1%}")
        print(f"Skills Found: {len(parsed['skills_extracted'])}")
        print(f"Experience: {len(parsed['experience_extracted'])} roles")

        # Get ATS score
        ats = await service.get_ats_score(session, resume_id=10)
        print(f"ATS Score: {ats['overall_score']}/100")

asyncio.run(parse_resume())
```

## Performance Considerations

### Optimization Strategies

1. **Caching**: Match results are cached in Redis with 1-hour TTL
2. **Batch Processing**: Use batch matching for large-scale operations
3. **Skill Indexes**: Skills are indexed for faster lookup
4. **Lazy Loading**: Resume parsing only happens on-demand
5. **Connection Pooling**: Database connections are pooled

### Performance Metrics

- **Single Match Score**: 5-50ms
- **Requirement Matching (100 candidates)**: 500-2000ms
- **Resume Parsing**: 1-5 seconds (depends on file size)
- **Resume Tailoring**: 3-10 seconds (with API call)
- **Batch Matching (5000 pairs)**: 30-60 seconds

## Error Handling

The module includes comprehensive error handling:

```python
HTTPException(
    status_code=404,
    detail="Match not found"
)

HTTPException(
    status_code=400,
    detail="Weights must sum to 1.0"
)

HTTPException(
    status_code=500,
    detail="Error in batch matching"
)
```

## Testing

Example test cases:

```python
import pytest
from agents.matching_agent import MatchingAgent

@pytest.fixture
def agent():
    return MatchingAgent()

def test_skill_synonym_matching(agent):
    score, match_type = agent.calculate_skill_match(
        "JavaScript",
        [{"skill": "JS", "level": "expert"}]
    )
    assert score == 0.9
    assert match_type == "synonym"

def test_score_experience(agent):
    score = agent.score_experience(5.0, 3.0, 7.0)
    assert score == 1.0  # Within range

def test_score_location(agent):
    score = agent.score_location(
        "San Francisco", "CA", "USA",
        "San Francisco", "CA", "USA",
        "onsite"
    )
    assert score == 1.0
```

## Extending the Engine

### Adding Custom Skill Synonyms

```python
from agents.matching_agent import MatchingAgent

agent = MatchingAgent()
agent.skill_synonyms["custom_skill"] = ["alias1", "alias2"]
```

### Adding Custom Scoring Logic

```python
class CustomMatchingAgent(MatchingAgent):
    async def calculate_match_score(self, requirement, candidate, feedback=None):
        score_data = await super().calculate_match_score(
            requirement, candidate, feedback
        )

        # Add custom logic
        if candidate.referral_source == "employee":
            score_data["overall_score"] *= 1.1

        return score_data
```

### Custom Resume Parsing

```python
class CustomResumeParser(ResumeParserAgent):
    def extract_skills(self, text):
        skills = super().extract_skills(text)

        # Add custom extraction logic
        return skills
```

## Troubleshooting

### Common Issues

1. **Low matching scores**: Check if SKILL_SYNONYMS includes target skills
2. **Resume parsing failures**: Ensure file is valid PDF/DOCX
3. **Anthropic API errors**: Check ANTHROPIC_API_KEY is set
4. **ATS score too low**: Review formatting - check for special characters

### Debug Logging

Enable debug logging to troubleshoot:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("matching_agent")
logger.setLevel(logging.DEBUG)
```

## Future Enhancements

- [ ] Machine learning-based skill relationship discovery
- [ ] Integration with LinkedIn/GitHub APIs for extended candidate data
- [ ] Automatic weight optimization based on historical hiring outcomes
- [ ] Support for non-English resumes with translation
- [ ] Video interview analysis for culture fit scoring
- [ ] Integration with external ATS systems
- [ ] Real-time matching as candidates/requirements are added
- [ ] Predictive analytics for placement success
