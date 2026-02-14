import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from models.cicd import Environment, Release, Deployment, FeatureFlag
from agents.cicd_agent import CICDAgent

logger = logging.getLogger(__name__)


class CICDService:
    """Service layer for CI/CD operations."""

    def __init__(self):
        """Initialize CI/CD service."""
        self.agent = CICDAgent()

    async def initialize(self) -> None:
        """Initialize the service."""
        await self.agent.initialize()

    async def shutdown(self) -> None:
        """Shutdown the service."""
        await self.agent.shutdown()

    # ── Deployment Management ──

    async def create_deployment(
        self, db: Session, deploy_data: Dict[str, Any], user_id: int
    ) -> Dict[str, Any]:
        """Create a deployment."""
        return await self.agent.create_deployment(db, deploy_data, user_id)

    async def execute_deployment(self, db: Session, deployment_id: int) -> Dict[str, Any]:
        """Execute a deployment."""
        return await self.agent.execute_deployment(db, deployment_id)

    async def get_deployment(self, db: Session, deployment_id: int) -> Optional[Dict[str, Any]]:
        """Get a deployment."""
        try:
            deployment = db.execute(
                select(Deployment).where(Deployment.id == deployment_id)
            ).scalar()

            if not deployment:
                return None

            return {
                "id": deployment.id,
                "release_id": deployment.release_id,
                "environment_id": deployment.environment_id,
                "version": deployment.version,
                "status": deployment.status,
                "pipeline_steps": deployment.pipeline_steps,
                "pre_deploy_checks": deployment.pre_deploy_checks,
                "post_deploy_checks": deployment.post_deploy_checks,
                "started_at": deployment.started_at.isoformat() if deployment.started_at else None,
                "completed_at": deployment.completed_at.isoformat() if deployment.completed_at else None,
                "duration_seconds": deployment.duration_seconds,
                "deployed_by": deployment.deployed_by,
                "error_message": deployment.error_message,
                "notes": deployment.notes,
            }
        except Exception as e:
            logger.error(f"Error getting deployment: {str(e)}")
            return None

    async def list_deployments(
        self, db: Session, environment_id: Optional[int] = None, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """List deployments."""
        try:
            query = select(Deployment)

            if environment_id:
                query = query.where(Deployment.environment_id == environment_id)

            query = query.order_by(Deployment.created_at.desc()).limit(limit)
            deployments = db.execute(query).scalars().all()

            return [
                {
                    "id": d.id,
                    "version": d.version,
                    "environment_id": d.environment_id,
                    "status": d.status,
                    "started_at": d.started_at.isoformat() if d.started_at else None,
                    "completed_at": d.completed_at.isoformat() if d.completed_at else None,
                    "duration_seconds": d.duration_seconds,
                }
                for d in deployments
            ]
        except Exception as e:
            logger.error(f"Error listing deployments: {str(e)}")
            return []

    async def rollback_deployment(
        self, db: Session, deployment_id: int, reason: str
    ) -> Dict[str, Any]:
        """Rollback a deployment."""
        return await self.agent.rollback_deployment(db, deployment_id, reason)

    # ── Release Management ──

    async def create_release(
        self, db: Session, release_data: Dict[str, Any], user_id: int
    ) -> Dict[str, Any]:
        """Create a release."""
        return await self.agent.create_release(db, release_data, user_id)

    async def get_release(self, db: Session, release_id: int) -> Optional[Dict[str, Any]]:
        """Get a release."""
        try:
            release = db.execute(
                select(Release).where(Release.id == release_id)
            ).scalar()

            if not release:
                return None

            return {
                "id": release.id,
                "version": release.version,
                "name": release.name,
                "description": release.description,
                "changelog": release.changelog,
                "ai_changelog": release.ai_changelog,
                "release_type": release.release_type,
                "components": release.components,
                "artifacts": release.artifacts,
                "status": release.status,
                "released_at": release.released_at.isoformat() if release.released_at else None,
                "released_by": release.released_by,
                "git_tag": release.git_tag,
                "git_commit": release.git_commit,
            }
        except Exception as e:
            logger.error(f"Error getting release: {str(e)}")
            return None

    async def list_releases(self, db: Session, limit: int = 20) -> List[Dict[str, Any]]:
        """List releases."""
        try:
            releases = db.execute(
                select(Release).order_by(Release.created_at.desc()).limit(limit)
            ).scalars().all()

            return [
                {
                    "id": r.id,
                    "version": r.version,
                    "name": r.name,
                    "release_type": r.release_type,
                    "status": r.status,
                    "created_at": r.created_at.isoformat(),
                }
                for r in releases
            ]
        except Exception as e:
            logger.error(f"Error listing releases: {str(e)}")
            return []

    async def update_release(
        self, db: Session, release_id: int, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a release."""
        try:
            release = db.execute(
                select(Release).where(Release.id == release_id)
            ).scalar()

            if not release:
                raise ValueError(f"Release {release_id} not found")

            for key, value in updates.items():
                if hasattr(release, key):
                    setattr(release, key, value)

            db.commit()
            db.refresh(release)

            logger.info(f"Updated release: {release.version}")

            return {
                "id": release.id,
                "version": release.version,
                "status": release.status,
            }
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating release: {str(e)}")
            raise

    async def generate_changelog(
        self, db: Session, from_version: str, to_version: str
    ) -> Dict[str, Any]:
        """Generate changelog."""
        return await self.agent.generate_changelog(db, from_version, to_version)

    # ── Environment Management ──

    async def create_or_update_environment(
        self, db: Session, env_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create or update environment."""
        return await self.agent.manage_environment(db, env_data)

    async def get_environment(self, db: Session, environment_id: int) -> Optional[Dict[str, Any]]:
        """Get environment."""
        try:
            env = db.execute(
                select(Environment).where(Environment.id == environment_id)
            ).scalar()

            if not env:
                return None

            return {
                "id": env.id,
                "name": env.name,
                "display_name": env.display_name,
                "url": env.url,
                "config": env.config,
                "current_version": env.current_version,
                "last_deployed_at": env.last_deployed_at.isoformat() if env.last_deployed_at else None,
                "status": env.status,
                "health_status": env.health_status,
                "last_health_check_at": env.last_health_check_at.isoformat() if env.last_health_check_at else None,
            }
        except Exception as e:
            logger.error(f"Error getting environment: {str(e)}")
            return None

    async def list_environments(self, db: Session) -> List[Dict[str, Any]]:
        """List all environments."""
        try:
            envs = db.execute(select(Environment)).scalars().all()

            return [
                {
                    "id": e.id,
                    "name": e.name,
                    "display_name": e.display_name,
                    "status": e.status,
                    "health_status": e.health_status,
                    "current_version": e.current_version,
                }
                for e in envs
            ]
        except Exception as e:
            logger.error(f"Error listing environments: {str(e)}")
            return []

    async def run_health_check(self, db: Session, environment_id: int) -> Dict[str, Any]:
        """Run health check."""
        return await self.agent.run_health_check(db, environment_id)

    # ── Feature Flags ──

    async def create_or_update_feature_flag(
        self, db: Session, flag_data: Dict[str, Any], user_id: int
    ) -> Dict[str, Any]:
        """Create or update feature flag."""
        return await self.agent.manage_feature_flags(db, flag_data, user_id)

    async def get_feature_flag(self, db: Session, flag_id: int) -> Optional[Dict[str, Any]]:
        """Get feature flag."""
        try:
            flag = db.execute(
                select(FeatureFlag).where(FeatureFlag.id == flag_id)
            ).scalar()

            if not flag:
                return None

            return {
                "id": flag.id,
                "name": flag.name,
                "description": flag.description,
                "is_enabled": flag.is_enabled,
                "rollout_percentage": flag.rollout_percentage,
                "target_environments": flag.target_environments,
                "target_roles": flag.target_roles,
                "config": flag.config,
                "created_by": flag.created_by,
                "enabled_at": flag.enabled_at.isoformat() if flag.enabled_at else None,
                "disabled_at": flag.disabled_at.isoformat() if flag.disabled_at else None,
            }
        except Exception as e:
            logger.error(f"Error getting feature flag: {str(e)}")
            return None

    async def list_feature_flags(self, db: Session) -> List[Dict[str, Any]]:
        """List feature flags."""
        try:
            flags = db.execute(select(FeatureFlag)).scalars().all()

            return [
                {
                    "id": f.id,
                    "name": f.name,
                    "is_enabled": f.is_enabled,
                    "rollout_percentage": f.rollout_percentage,
                }
                for f in flags
            ]
        except Exception as e:
            logger.error(f"Error listing feature flags: {str(e)}")
            return []

    async def toggle_feature_flag(
        self, db: Session, flag_id: int, enabled: bool
    ) -> Dict[str, Any]:
        """Toggle feature flag."""
        try:
            flag = db.execute(
                select(FeatureFlag).where(FeatureFlag.id == flag_id)
            ).scalar()

            if not flag:
                raise ValueError(f"Flag {flag_id} not found")

            flag.is_enabled = enabled
            if enabled:
                flag.enabled_at = datetime.utcnow()
            else:
                flag.disabled_at = datetime.utcnow()

            db.commit()
            db.refresh(flag)

            logger.info(f"Toggled feature flag: {flag.name} = {enabled}")

            return {
                "id": flag.id,
                "name": flag.name,
                "is_enabled": flag.is_enabled,
            }
        except Exception as e:
            db.rollback()
            logger.error(f"Error toggling feature flag: {str(e)}")
            raise

    # ── Version Tracking ──

    async def track_version(
        self, db: Session, component: str, version: str
    ) -> Dict[str, Any]:
        """Track component version."""
        return await self.agent.track_version(db, component, version)

    # ── Analytics ──

    async def get_deployment_analytics(self, db: Session) -> Dict[str, Any]:
        """Get deployment analytics."""
        return await self.agent.get_deployment_analytics(db)

    # ── Validation ──

    async def validate_pre_deploy(self, db: Session, deployment_id: int) -> Dict[str, Any]:
        """Validate pre-deployment requirements."""
        return await self.agent.validate_pre_deploy(db, deployment_id)
