"""Test endpoints for running and monitoring test suites."""
import logging
from typing import Dict, Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from agents.test_agent import TestAgent
from models.user import User
from models.enums import UserRole

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tests", tags=["testing"])

# Global test agent instance
test_agent = TestAgent()
test_runs: Dict[str, Dict[str, Any]] = {}


@router.on_event("startup")
async def startup_test_agent():
    """Initialize test agent on startup."""
    await test_agent.initialize()


@router.on_event("shutdown")
async def shutdown_test_agent():
    """Shutdown test agent on shutdown."""
    await test_agent.shutdown()


@router.post("/run-all", name="Run All Tests")
async def run_all_tests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Run full test suite.

    Returns:
        Test results with breakdown by category
    """
    # Only admins can run tests
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can run tests")

    logger.info(f"Full test suite started by user {current_user.id}")

    try:
        results = await test_agent.run_full_suite(db)

        run_id = f"run_{datetime.utcnow().isoformat()}"
        test_runs[run_id] = results

        return {
            "run_id": run_id,
            "status": "completed",
            **results,
        }

    except Exception as e:
        logger.error(f"Error running full test suite: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Test execution failed: {str(e)}")


@router.post("/smoke", name="Run Smoke Tests")
async def run_smoke_tests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Run smoke tests (health checks).

    Returns:
        Quick health check results
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can run tests")

    logger.info(f"Smoke tests started by user {current_user.id}")

    try:
        results = await test_agent.run_smoke_tests(db)

        run_id = f"smoke_{datetime.utcnow().isoformat()}"
        test_runs[run_id] = results

        return {
            "run_id": run_id,
            "status": "completed",
            **results,
        }

    except Exception as e:
        logger.error(f"Error running smoke tests: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Smoke tests failed: {str(e)}")


@router.post("/integration", name="Run Integration Tests")
async def run_integration_tests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Run integration tests (end-to-end workflows).

    Returns:
        Integration test results
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can run tests")

    logger.info(f"Integration tests started by user {current_user.id}")

    try:
        results = await test_agent.run_integration_tests(db)

        run_id = f"integration_{datetime.utcnow().isoformat()}"
        test_runs[run_id] = results

        return {
            "run_id": run_id,
            "status": "completed",
            **results,
        }

    except Exception as e:
        logger.error(f"Error running integration tests: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Integration tests failed: {str(e)}")


@router.post("/agent", name="Run Agent Tests")
async def run_agent_tests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Run agent-specific tests.

    Returns:
        Agent test results
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can run tests")

    logger.info(f"Agent tests started by user {current_user.id}")

    try:
        results = await test_agent.run_agent_tests(db)

        run_id = f"agent_{datetime.utcnow().isoformat()}"
        test_runs[run_id] = results

        return {
            "run_id": run_id,
            "status": "completed",
            **results,
        }

    except Exception as e:
        logger.error(f"Error running agent tests: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Agent tests failed: {str(e)}")


@router.post("/api", name="Run API Tests")
async def run_api_tests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Run API endpoint tests.

    Returns:
        API test results
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can run tests")

    logger.info(f"API tests started by user {current_user.id}")

    try:
        results = await test_agent.run_api_tests(db)

        run_id = f"api_{datetime.utcnow().isoformat()}"
        test_runs[run_id] = results

        return {
            "run_id": run_id,
            "status": "completed",
            **results,
        }

    except Exception as e:
        logger.error(f"Error running API tests: {str(e)}")
        raise HTTPException(status_code=500, detail=f"API tests failed: {str(e)}")


@router.get("/results/{run_id}", name="Get Test Results")
async def get_test_results(
    run_id: str,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get test run results.

    Args:
        run_id: Test run ID

    Returns:
        Test results
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can view test results")

    if run_id not in test_runs:
        raise HTTPException(status_code=404, detail=f"Test run {run_id} not found")

    return {
        "run_id": run_id,
        "results": test_runs[run_id],
    }


@router.get("/history", name="Get Test History")
async def get_test_history(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get test run history.

    Args:
        limit: Maximum number of runs to return

    Returns:
        List of recent test runs
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can view test history")

    runs = list(test_runs.items())[-limit:]

    return {
        "total_runs": len(test_runs),
        "recent_runs": [
            {
                "run_id": run_id,
                "passed": run_data.get("passed", 0),
                "failed": run_data.get("failed", 0),
                "total": run_data.get("total", 0),
                "duration_seconds": run_data.get("duration_seconds", 0),
            }
            for run_id, run_data in runs
        ],
    }


@router.post("/generate-report", name="Generate Test Report")
async def generate_test_report(
    run_id: str,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Generate detailed test report.

    Args:
        run_id: Test run ID

    Returns:
        Detailed test report with recommendations
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can generate reports")

    if run_id not in test_runs:
        raise HTTPException(status_code=404, detail=f"Test run {run_id} not found")

    report = await test_agent.generate_test_report(test_runs[run_id])

    return {
        "run_id": run_id,
        "report": report,
    }


@router.get("/status", name="Get Test Agent Status")
async def get_test_agent_status(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get test agent status.

    Returns:
        Test agent health status
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can view test status")

    health = await test_agent.health_check()

    return {
        "test_agent": health,
        "total_runs": len(test_runs),
        "last_run": (
            list(test_runs.keys())[-1] if test_runs else None
        ),
    }
