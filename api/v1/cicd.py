import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from services.cicd_service import CICDService
from schemas.cicd import (
    EnvironmentCreate, EnvironmentUpdate, EnvironmentResponse,
    ReleaseCreate, ReleaseUpdate, ReleaseResponse,
    DeploymentCreate, DeploymentResponse, RollbackRequest,
    FeatureFlagCreate, FeatureFlagUpdate, FeatureFlagResponse,
    ChangelogRequest, VersionTrackingResponse, DeploymentAnalytics,
    PreDeployValidation,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cicd", tags=["cicd"])
cicd_service = CICDService()


@router.on_event("startup")
async def startup():
    """Initialize CI/CD service on startup."""
    await cicd_service.initialize()


@router.on_event("shutdown")
async def shutdown():
    """Shutdown CI/CD service."""
    await cicd_service.shutdown()


# ── Deployments ──

@router.post("/deployments", response_model=Dict[str, Any])
async def create_deployment(
    deploy_data: DeploymentCreate,
    db: Session = Depends(get_db),
    current_user_id: int = 1,
):
    """Create a deployment."""
    try:
        result = await cicd_service.create_deployment(db, deploy_data.model_dump(), current_user_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating deployment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/deployments", response_model=List[Dict[str, Any]])
async def list_deployments(
    environment_id: Optional[int] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List deployments."""
    try:
        deployments = await cicd_service.list_deployments(db, environment_id, limit)
        return deployments
    except Exception as e:
        logger.error(f"Error listing deployments: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/deployments/{deployment_id}", response_model=Dict[str, Any])
async def get_deployment(
    deployment_id: int,
    db: Session = Depends(get_db),
):
    """Get a deployment."""
    try:
        deployment = await cicd_service.get_deployment(db, deployment_id)
        if not deployment:
            raise HTTPException(status_code=404, detail="Deployment not found")
        return deployment
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting deployment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/deployments/{deployment_id}/execute", response_model=Dict[str, Any])
async def execute_deployment(
    deployment_id: int,
    db: Session = Depends(get_db),
):
    """Execute a deployment."""
    try:
        result = await cicd_service.execute_deployment(db, deployment_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"Error executing deployment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/deployments/{deployment_id}/rollback", response_model=Dict[str, Any])
async def rollback_deployment(
    deployment_id: int,
    rollback_data: RollbackRequest,
    db: Session = Depends(get_db),
):
    """Rollback a deployment."""
    try:
        result = await cicd_service.rollback_deployment(db, deployment_id, rollback_data.reason)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error rolling back deployment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/deployments/{deployment_id}/validate", response_model=PreDeployValidation)
async def validate_deployment(
    deployment_id: int,
    db: Session = Depends(get_db),
):
    """Validate pre-deployment requirements."""
    try:
        result = await cicd_service.validate_pre_deploy(db, deployment_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error validating deployment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Releases ──

@router.post("/releases", response_model=Dict[str, Any])
async def create_release(
    release_data: ReleaseCreate,
    db: Session = Depends(get_db),
    current_user_id: int = 1,
):
    """Create a release."""
    try:
        result = await cicd_service.create_release(db, release_data.model_dump(), current_user_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating release: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/releases", response_model=List[Dict[str, Any]])
async def list_releases(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List releases."""
    try:
        releases = await cicd_service.list_releases(db, limit)
        return releases
    except Exception as e:
        logger.error(f"Error listing releases: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/releases/{release_id}", response_model=Dict[str, Any])
async def get_release(
    release_id: int,
    db: Session = Depends(get_db),
):
    """Get a release."""
    try:
        release = await cicd_service.get_release(db, release_id)
        if not release:
            raise HTTPException(status_code=404, detail="Release not found")
        return release
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting release: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/releases/{release_id}", response_model=Dict[str, Any])
async def update_release(
    release_id: int,
    update_data: ReleaseUpdate,
    db: Session = Depends(get_db),
):
    """Update a release."""
    try:
        result = await cicd_service.update_release(db, release_id, update_data.model_dump(exclude_unset=True))
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating release: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/releases/changelog", response_model=Dict[str, Any])
async def generate_changelog(
    changelog_data: ChangelogRequest,
    db: Session = Depends(get_db),
):
    """Generate changelog between versions."""
    try:
        result = await cicd_service.generate_changelog(
            db, changelog_data.from_version, changelog_data.to_version
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating changelog: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Environments ──

@router.post("/environments", response_model=Dict[str, Any])
async def create_environment(
    env_data: EnvironmentCreate,
    db: Session = Depends(get_db),
):
    """Create an environment."""
    try:
        result = await cicd_service.create_or_update_environment(db, env_data.model_dump())
        return result
    except Exception as e:
        logger.error(f"Error creating environment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/environments", response_model=List[Dict[str, Any]])
async def list_environments(db: Session = Depends(get_db)):
    """List all environments."""
    try:
        environments = await cicd_service.list_environments(db)
        return environments
    except Exception as e:
        logger.error(f"Error listing environments: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/environments/{environment_id}", response_model=Dict[str, Any])
async def get_environment(
    environment_id: int,
    db: Session = Depends(get_db),
):
    """Get an environment."""
    try:
        environment = await cicd_service.get_environment(db, environment_id)
        if not environment:
            raise HTTPException(status_code=404, detail="Environment not found")
        return environment
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting environment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/environments/{environment_id}", response_model=Dict[str, Any])
async def update_environment(
    environment_id: int,
    update_data: EnvironmentUpdate,
    db: Session = Depends(get_db),
):
    """Update an environment."""
    try:
        env = await cicd_service.get_environment(db, environment_id)
        if not env:
            raise HTTPException(status_code=404, detail="Environment not found")

        updated_data = env | update_data.model_dump(exclude_unset=True)
        result = await cicd_service.create_or_update_environment(db, updated_data)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating environment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/environments/{environment_id}/health-check", response_model=Dict[str, Any])
async def run_health_check(
    environment_id: int,
    db: Session = Depends(get_db),
):
    """Run health check on environment."""
    try:
        result = await cicd_service.run_health_check(db, environment_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error running health check: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Feature Flags ──

@router.post("/feature-flags", response_model=Dict[str, Any])
async def create_feature_flag(
    flag_data: FeatureFlagCreate,
    db: Session = Depends(get_db),
    current_user_id: int = 1,
):
    """Create a feature flag."""
    try:
        result = await cicd_service.create_or_update_feature_flag(
            db, flag_data.model_dump(), current_user_id
        )
        return result
    except Exception as e:
        logger.error(f"Error creating feature flag: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feature-flags", response_model=List[Dict[str, Any]])
async def list_feature_flags(db: Session = Depends(get_db)):
    """List feature flags."""
    try:
        flags = await cicd_service.list_feature_flags(db)
        return flags
    except Exception as e:
        logger.error(f"Error listing feature flags: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feature-flags/{flag_id}", response_model=Dict[str, Any])
async def get_feature_flag(
    flag_id: int,
    db: Session = Depends(get_db),
):
    """Get a feature flag."""
    try:
        flag = await cicd_service.get_feature_flag(db, flag_id)
        if not flag:
            raise HTTPException(status_code=404, detail="Feature flag not found")
        return flag
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting feature flag: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/feature-flags/{flag_id}", response_model=Dict[str, Any])
async def update_feature_flag(
    flag_id: int,
    update_data: FeatureFlagUpdate,
    db: Session = Depends(get_db),
):
    """Update a feature flag."""
    try:
        # For simple toggle
        if update_data.is_enabled is not None:
            result = await cicd_service.toggle_feature_flag(db, flag_id, update_data.is_enabled)
        else:
            flag = await cicd_service.get_feature_flag(db, flag_id)
            if not flag:
                raise HTTPException(status_code=404, detail="Feature flag not found")

            updated_data = flag | update_data.model_dump(exclude_unset=True)
            result = await cicd_service.create_or_update_feature_flag(db, updated_data, flag["created_by"])

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating feature flag: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Analytics ──

@router.get("/analytics", response_model=DeploymentAnalytics)
async def get_deployment_analytics(db: Session = Depends(get_db)):
    """Get deployment analytics."""
    try:
        analytics = await cicd_service.get_deployment_analytics(db)
        return analytics
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Version Tracking ──

@router.post("/version-tracking", response_model=VersionTrackingResponse)
async def track_version(
    component: str,
    version: str,
    db: Session = Depends(get_db),
):
    """Track component version."""
    try:
        result = await cicd_service.track_version(db, component, version)
        return result
    except Exception as e:
        logger.error(f"Error tracking version: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
