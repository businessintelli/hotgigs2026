"""
Pydantic schemas for E2E Testing Agent API responses.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class TestStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"
    ERROR = "error"


class TestSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class TestCategory(str, Enum):
    API_ENDPOINT = "api_endpoint"
    FRONTEND_PAGE = "frontend_page"
    FRONTEND_BUILD = "frontend_build"
    IMPORT_VALIDATION = "import_validation"
    ROUTE_VALIDATION = "route_validation"
    MODEL_VALIDATION = "model_validation"
    SCHEMA_VALIDATION = "schema_validation"
    LOG_ANALYSIS = "log_analysis"
    DEPENDENCY_CHECK = "dependency_check"
    SECURITY_CHECK = "security_check"


class TestResultResponse(BaseModel):
    """Single test result with all details."""

    test_id: str
    category: str
    name: str
    status: str  # passed/failed/warning/skipped/error
    severity: str  # critical/high/medium/low/info
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)
    duration_ms: float = 0
    recommendation: str = ""
    file_path: str = ""
    line_number: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "test_id": "api_auth_login",
                "category": "api_endpoint",
                "name": "POST /api/v1/auth/login",
                "status": "passed",
                "severity": "info",
                "message": "Route registered: POST /api/v1/auth/login",
                "details": {
                    "path": "/api/v1/auth/login",
                    "methods": ["POST"],
                    "function": "login",
                },
                "duration_ms": 2.5,
                "recommendation": "",
                "file_path": "",
                "line_number": 0,
            }
        }


class RecommendationResponse(BaseModel):
    """Single fix recommendation."""

    test_id: str
    severity: str
    category: str
    name: str
    issue: str
    recommendation: str
    file_path: str = ""

    class Config:
        json_schema_extra = {
            "example": {
                "test_id": "page_MissingComponent",
                "severity": "high",
                "category": "frontend_page",
                "name": "Page: MissingComponent",
                "issue": "File not found: /path/to/MissingComponent.tsx",
                "recommendation": "Create the missing page component or remove from App.tsx imports",
                "file_path": "/path/to/MissingComponent.tsx",
            }
        }


class TestReportResponse(BaseModel):
    """Complete test report with all results and recommendations."""

    report_id: str
    run_type: str  # full, api_only, frontend_only, log_analysis, quick_smoke
    started_at: str
    completed_at: str
    duration_seconds: float
    total_tests: int
    passed: int
    failed: int
    warnings: int
    skipped: int
    errors: int
    pass_rate: float
    results: List[Dict[str, Any]]
    summary: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    category_breakdown: Dict[str, Dict[str, int]]

    class Config:
        json_schema_extra = {
            "example": {
                "report_id": "test_20260309_143022",
                "run_type": "quick_smoke",
                "started_at": "2026-03-09T14:30:22.123456",
                "completed_at": "2026-03-09T14:30:28.456789",
                "duration_seconds": 6.333,
                "total_tests": 485,
                "passed": 470,
                "failed": 2,
                "warnings": 13,
                "skipped": 0,
                "errors": 0,
                "pass_rate": 96.9,
                "results": [],
                "summary": {
                    "total": 485,
                    "passed": 470,
                    "failed": 2,
                    "warnings": 13,
                    "errors": 0,
                    "pass_rate": 96.9,
                    "health_score": 92.0,
                },
                "recommendations": [],
                "category_breakdown": {},
            }
        }


class TestRunRequest(BaseModel):
    """Request body for test runs."""

    run_type: str = Field(
        default="quick_smoke",
        description="Type of test run: full, quick_smoke, api_only, frontend_only",
    )
    categories: Optional[List[str]] = Field(
        default=None,
        description="Optional list of test categories to run (if None, all relevant categories)",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "run_type": "quick_smoke",
                "categories": None,
            }
        }


class TestHistoryItem(BaseModel):
    """Single entry in test history."""

    report_id: str
    run_type: str
    timestamp: str
    pass_rate: float
    total: int
    passed: int
    failed: int
    warnings: int
    errors: int
    health_score: float = 0

    class Config:
        json_schema_extra = {
            "example": {
                "report_id": "test_20260309_143022",
                "run_type": "quick_smoke",
                "timestamp": "2026-03-09T14:30:22",
                "pass_rate": 96.9,
                "total": 485,
                "passed": 470,
                "failed": 2,
                "warnings": 13,
                "errors": 0,
                "health_score": 92.0,
            }
        }


class TestHealthResponse(BaseModel):
    """Quick health check response."""

    status: str  # healthy, warning, critical
    health_score: float  # 0-100
    last_test_timestamp: str
    last_test_duration_seconds: float
    critical_issues: int
    high_priority_issues: int
    pass_rate: float

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "health_score": 92.0,
                "last_test_timestamp": "2026-03-09T14:30:22",
                "last_test_duration_seconds": 6.333,
                "critical_issues": 0,
                "high_priority_issues": 2,
                "pass_rate": 96.9,
            }
        }


class TestCoverageResponse(BaseModel):
    """Test coverage summary by module/category."""

    total_modules: int
    tested_modules: int
    coverage_percentage: float
    by_category: Dict[str, Dict[str, int]]
    untested_modules: List[str]

    class Config:
        json_schema_extra = {
            "example": {
                "total_modules": 52,
                "tested_modules": 48,
                "coverage_percentage": 92.3,
                "by_category": {
                    "api_endpoint": {
                        "total": 479,
                        "tested": 479,
                        "coverage": 100,
                    },
                    "frontend_page": {
                        "total": 40,
                        "tested": 40,
                        "coverage": 100,
                    },
                },
                "untested_modules": ["deprecated_module_1", "deprecated_module_2"],
            }
        }


class TestJobResponse(BaseModel):
    """Response for async test job creation."""

    job_id: str
    run_type: str
    status: str  # queued, running, completed, failed
    created_at: str
    estimated_completion_seconds: float

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "job_abc123def456",
                "run_type": "full",
                "status": "queued",
                "created_at": "2026-03-09T14:30:22",
                "estimated_completion_seconds": 120.0,
            }
        }
