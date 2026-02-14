# HR Automation Platform - Phase 1

Enterprise-scale HR automation platform designed to handle 500+ requirements and thousands of candidates.

## Features

- **Requirement Management**: Create and manage open positions with detailed skills, experience, and rate requirements
- **Candidate Management**: Track candidates from sourcing through placement
- **Resume Parsing**: Automated resume parsing and skills extraction
- **AI-Powered Matching**: Intelligent candidate-to-requirement matching with detailed scoring
- **Interview Management**: Schedule and track interviews with feedback collection
- **Submission Tracking**: Manage candidate submissions to customers
- **Offer Management**: Create, track, and manage job offers and onboarding
- **Supplier Management**: Track third-party supplier performance and submissions
- **User Management**: Role-based access control (Admin, Manager, Recruiter, Viewer)
- **Audit Logging**: Complete audit trail for compliance

## Technology Stack

- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with async SQLAlchemy 2.0
- **Event Bus**: Redis (pub/sub) + RabbitMQ (task queues)
- **Authentication**: JWT
- **Search**: Elasticsearch (future integration)
- **Storage**: S3 (resumes, offer letters)
- **Email**: SendGrid
- **AI Integration**: OpenAI + Anthropic APIs

## Project Structure

```
hr_platform/
├── config/              # Configuration and settings
├── database/            # Database connection and models
├── models/              # SQLAlchemy ORM models
├── schemas/             # Pydantic request/response schemas
├── agents/              # Event-driven agent system
├── api/                 # FastAPI routes and endpoints
├── services/            # Business logic layer
└── utils/               # Utilities and helpers
```

## Setup and Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 13+
- Redis 6+
- RabbitMQ 3.9+
- Docker and Docker Compose (optional)

### Local Development

1. Clone the repository
2. Copy `.env.example` to `.env` and configure
3. Create Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run database migrations:
   ```bash
   alembic upgrade head
   ```

6. Start the development server:
   ```bash
   uvicorn api.main:app --reload
   ```

### Docker Deployment

```bash
docker-compose up -d
```

This will start:
- FastAPI application on port 8000
- PostgreSQL on port 5432
- Redis on port 6379
- RabbitMQ on port 5672

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "Description"
```

Apply migrations:
```bash
alembic upgrade head
```

## Environment Variables

See `.env.example` for all required configuration variables.

## License

Proprietary - All rights reserved
