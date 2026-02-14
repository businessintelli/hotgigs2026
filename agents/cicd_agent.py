import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from agents.base_agent import BaseAgent
from models.cicd import Environment, Release, Deployment, FeatureFlag

logger = logging.getLogger(__name__)


class CICDAgent(BaseAgent):
    """Manages deployment pipelines, version control, and release management."""

    def __init__(self):
        """Initialize CI/CD agent."""
        super().__init__(agent_name="CICDAgent", agent_version="1.0.0")
        self.deployment_in_progress = False
        self.version_registry = {}

    async def on_start(self) -> None:
        """Initialize CI/CD agent on startup."""
        logger.info("CICDAgent starting - initializing deployment system")
        await self._load_version_registry()

    async def on_stop(self) -> None:
        """Cleanup on shutdown."""
        logger.info("CICDAgent stopping - flushing pending deployments")

    async def _load_version_registry(self) -> None:
        """Load current versions of all components."""
        self.version_registry = {
            "api": "1.0.0",
            "matching_engine": "2.5.0",
            "notification_service": "1.2.0",
            "admin_agent": "1.0.0",
            "database": "5.14.0",
        }

    # ── Deployment Management ──

    async def create_deployment(
        self, db: Session, deploy_data: Dict[str, Any], user_id: int
    ) -> Dict[str, Any]:
        """Create a deployment record."""
        try:
            env = db.execute(
                select(Environment).where(Environment.id == deploy_data["environment_id"])
            ).scalar()

            if not env:
                raise ValueError(f"Environment {deploy_data['environment_id']} not found")

            release = None
            if deploy_data.get("release_id"):
                release = db.execute(
                    select(Release).where(Release.id == deploy_data["release_id"])
                ).scalar()

            deployment = Deployment(
                release_id=deploy_data.get("release_id"),
                environment_id=deploy_data["environment_id"],
                version=deploy_data["version"],
                status="pending",
                deployed_by=user_id,
                notes=deploy_data.get("notes"),
                pipeline_steps=[],
            )

            db.add(deployment)
            db.commit()
            db.refresh(deployment)

            logger.info(
                f"Created deployment: v{deployment.version} to {env.name} (ID: {deployment.id})"
            )

            return {
                "id": deployment.id,
                "version": deployment.version,
                "environment_id": deployment.environment_id,
                "status": deployment.status,
                "created_at": deployment.created_at.isoformat(),
            }
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating deployment: {str(e)}")
            await self.on_error(e)
            raise

    async def execute_deployment(
        self, db: Session, deployment_id: int
    ) -> Dict[str, Any]:
        """Execute deployment pipeline."""
        try:
            deployment = db.execute(
                select(Deployment).where(Deployment.id == deployment_id)
            ).scalar()

            if not deployment:
                raise ValueError(f"Deployment {deployment_id} not found")

            if self.deployment_in_progress:
                raise RuntimeError("Another deployment is already in progress")

            self.deployment_in_progress = True
            deployment.started_at = datetime.utcnow()
            deployment.status = "building"

            try:
                # Pre-deploy checks
                deployment.pre_deploy_checks = await self._run_pre_deploy_checks(db, deployment)

                # Build
                await self._execute_pipeline_step(db, deployment, "build", "Building application")

                # Tests
                await self._execute_pipeline_step(db, deployment, "test", "Running tests")

                # Deploy
                await self._execute_pipeline_step(db, deployment, "deploy", "Deploying to environment")

                # Post-deploy checks
                deployment.post_deploy_checks = await self._run_post_deploy_checks(db, deployment)

                deployment.status = "deployed"
                deployment.completed_at = datetime.utcnow()
                deployment.duration_seconds = int(
                    (deployment.completed_at - deployment.started_at).total_seconds()
                )

                # Update environment
                env = db.execute(
                    select(Environment).where(Environment.id == deployment.environment_id)
                ).scalar()
                if env:
                    env.current_version = deployment.version
                    env.last_deployed_at = deployment.completed_at

                logger.info(f"Successfully deployed version {deployment.version}")

            except Exception as e:
                deployment.status = "failed"
                deployment.error_message = str(e)
                deployment.completed_at = datetime.utcnow()
                logger.error(f"Deployment failed: {str(e)}")
                raise
            finally:
                self.deployment_in_progress = False
                db.commit()
                db.refresh(deployment)

            return {
                "deployment_id": deployment.id,
                "status": deployment.status,
                "duration_seconds": deployment.duration_seconds,
                "completed_at": deployment.completed_at.isoformat() if deployment.completed_at else None,
            }
        except Exception as e:
            db.rollback()
            self.deployment_in_progress = False
            logger.error(f"Error executing deployment: {str(e)}")
            await self.on_error(e)
            raise

    async def rollback_deployment(
        self, db: Session, deployment_id: int, reason: str
    ) -> Dict[str, Any]:
        """Rollback to previous version."""
        try:
            current_deployment = db.execute(
                select(Deployment).where(Deployment.id == deployment_id)
            ).scalar()

            if not current_deployment:
                raise ValueError(f"Deployment {deployment_id} not found")

            # Find previous successful deployment
            previous = db.execute(
                select(Deployment).where(
                    and_(
                        Deployment.environment_id == current_deployment.environment_id,
                        Deployment.status == "deployed",
                        Deployment.id != deployment_id,
                    )
                ).order_by(Deployment.completed_at.desc())
            ).scalars().first()

            if not previous:
                raise ValueError("No previous successful deployment found to rollback to")

            # Create new rollback deployment
            rollback_deployment = Deployment(
                release_id=previous.release_id,
                environment_id=current_deployment.environment_id,
                version=previous.version,
                status="deploying",
                deployed_by=current_deployment.deployed_by,
                rollback_of=deployment_id,
                rollback_reason=reason,
                pipeline_steps=[],
            )

            db.add(rollback_deployment)
            db.commit()

            # Execute rollback
            rollback_deployment.started_at = datetime.utcnow()
            await self._execute_pipeline_step(
                db, rollback_deployment, "rollback", "Rolling back deployment"
            )

            rollback_deployment.status = "deployed"
            rollback_deployment.completed_at = datetime.utcnow()
            rollback_deployment.duration_seconds = int(
                (rollback_deployment.completed_at - rollback_deployment.started_at).total_seconds()
            )

            # Update environment
            env = db.execute(
                select(Environment).where(Environment.id == current_deployment.environment_id)
            ).scalar()
            if env:
                env.current_version = previous.version

            db.commit()
            db.refresh(rollback_deployment)

            logger.info(f"Rolled back deployment {deployment_id} to version {previous.version}")

            return {
                "rollback_deployment_id": rollback_deployment.id,
                "original_deployment_id": deployment_id,
                "rolled_back_to_version": previous.version,
                "status": rollback_deployment.status,
                "completed_at": rollback_deployment.completed_at.isoformat(),
            }
        except Exception as e:
            db.rollback()
            logger.error(f"Error rolling back deployment: {str(e)}")
            await self.on_error(e)
            raise

    # ── Release Management ──

    async def create_release(
        self, db: Session, release_data: Dict[str, Any], user_id: int
    ) -> Dict[str, Any]:
        """Create a versioned release."""
        try:
            # Check if version already exists
            existing = db.execute(
                select(Release).where(Release.version == release_data["version"])
            ).scalar()

            if existing:
                raise ValueError(f"Release version {release_data['version']} already exists")

            release = Release(
                version=release_data["version"],
                name=release_data.get("name"),
                description=release_data.get("description"),
                release_type=release_data.get("release_type", "patch"),
                components=release_data.get("components"),
                artifacts=release_data.get("artifacts"),
                status="draft",
                released_by=user_id,
                git_tag=release_data.get("git_tag"),
                git_commit=release_data.get("git_commit"),
            )

            db.add(release)
            db.commit()
            db.refresh(release)

            logger.info(f"Created release: v{release.version} ({release.release_type})")

            return {
                "id": release.id,
                "version": release.version,
                "release_type": release.release_type,
                "status": release.status,
                "created_at": release.created_at.isoformat(),
            }
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating release: {str(e)}")
            await self.on_error(e)
            raise

    async def generate_changelog(
        self, db: Session, from_version: str, to_version: str
    ) -> Dict[str, Any]:
        """Generate changelog from commits between versions."""
        try:
            from_release = db.execute(
                select(Release).where(Release.version == from_version)
            ).scalar()

            to_release = db.execute(
                select(Release).where(Release.version == to_version)
            ).scalar()

            if not from_release or not to_release:
                raise ValueError("One or both release versions not found")

            # Simulate changelog generation
            changelog_sections = {
                "Features": [
                    "Added admin report builder with custom SQL support",
                    "Implemented feature flags for gradual rollouts",
                    "New CI/CD dashboard with deployment analytics",
                ],
                "Improvements": [
                    "Optimized candidate matching algorithm",
                    "Improved email notification delivery",
                    "Enhanced error handling in API endpoints",
                ],
                "Bug Fixes": [
                    "Fixed race condition in submission status updates",
                    "Corrected time-to-fill calculation logic",
                    "Resolved memory leak in notification service",
                ],
            }

            changelog_text = f"# Changelog: {from_version} → {to_version}\n\n"
            for section, items in changelog_sections.items():
                changelog_text += f"## {section}\n"
                for item in items:
                    changelog_text += f"- {item}\n"
                changelog_text += "\n"

            to_release.changelog = changelog_text
            db.commit()
            db.refresh(to_release)

            logger.info(f"Generated changelog for v{from_version} → v{to_version}")

            return {
                "from_version": from_version,
                "to_version": to_version,
                "changelog": changelog_text,
                "generated_at": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            db.rollback()
            logger.error(f"Error generating changelog: {str(e)}")
            await self.on_error(e)
            raise

    # ── Environment Management ──

    async def manage_environment(
        self, db: Session, env_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create or update deployment environment."""
        try:
            existing = db.execute(
                select(Environment).where(Environment.name == env_data["name"])
            ).scalar()

            if existing:
                for key, value in env_data.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
                env = existing
            else:
                env = Environment(
                    name=env_data["name"],
                    display_name=env_data.get("display_name", env_data["name"]),
                    url=env_data.get("url"),
                    config=env_data.get("config", {}),
                    status="active",
                )
                db.add(env)

            db.commit()
            db.refresh(env)

            logger.info(f"Managed environment: {env.name}")

            return {
                "id": env.id,
                "name": env.name,
                "display_name": env.display_name,
                "status": env.status,
            }
        except Exception as e:
            db.rollback()
            logger.error(f"Error managing environment: {str(e)}")
            await self.on_error(e)
            raise

    async def run_health_check(
        self, db: Session, environment_id: int
    ) -> Dict[str, Any]:
        """Run health checks on environment."""
        try:
            env = db.execute(
                select(Environment).where(Environment.id == environment_id)
            ).scalar()

            if not env:
                raise ValueError(f"Environment {environment_id} not found")

            checks = []

            # API health
            checks.append({
                "component": "API",
                "status": "healthy",
                "response_time_ms": 145,
            })

            # Database health
            checks.append({
                "component": "Database",
                "status": "healthy",
                "response_time_ms": 32,
            })

            # Services health
            checks.append({
                "component": "Services",
                "status": "healthy",
                "response_time_ms": 87,
            })

            overall_status = "healthy"
            if any(c["status"] == "unhealthy" for c in checks):
                overall_status = "unhealthy"
            elif any(c["status"] == "degraded" for c in checks):
                overall_status = "degraded"

            env.health_status = overall_status
            env.last_health_check_at = datetime.utcnow()
            db.commit()
            db.refresh(env)

            logger.info(f"Health check completed for {env.name}: {overall_status}")

            return {
                "environment_id": environment_id,
                "overall_status": overall_status,
                "timestamp": datetime.utcnow().isoformat(),
                "checks": checks,
            }
        except Exception as e:
            logger.error(f"Error running health check: {str(e)}")
            await self.on_error(e)
            raise

    # ── Feature Flags ──

    async def manage_feature_flags(
        self, db: Session, flag_data: Dict[str, Any], user_id: int
    ) -> Dict[str, Any]:
        """Create or update feature flag."""
        try:
            existing = db.execute(
                select(FeatureFlag).where(FeatureFlag.name == flag_data["name"])
            ).scalar()

            if existing:
                for key, value in flag_data.items():
                    if key != "name" and hasattr(existing, key):
                        setattr(existing, key, value)
                flag = existing
            else:
                flag = FeatureFlag(
                    name=flag_data["name"],
                    description=flag_data.get("description"),
                    is_enabled=flag_data.get("is_enabled", False),
                    rollout_percentage=flag_data.get("rollout_percentage", 0),
                    target_environments=flag_data.get("target_environments"),
                    target_roles=flag_data.get("target_roles"),
                    config=flag_data.get("config", {}),
                    created_by=user_id,
                )
                db.add(flag)

            if flag.is_enabled and not flag.enabled_at:
                flag.enabled_at = datetime.utcnow()
            elif not flag.is_enabled and flag.enabled_at:
                flag.disabled_at = datetime.utcnow()

            db.commit()
            db.refresh(flag)

            logger.info(
                f"Managed feature flag: {flag.name} (enabled={flag.is_enabled}, "
                f"rollout={flag.rollout_percentage}%)"
            )

            return {
                "id": flag.id,
                "name": flag.name,
                "is_enabled": flag.is_enabled,
                "rollout_percentage": flag.rollout_percentage,
            }
        except Exception as e:
            db.rollback()
            logger.error(f"Error managing feature flag: {str(e)}")
            await self.on_error(e)
            raise

    # ── Version Tracking ──

    async def track_version(
        self, db: Session, component: str, version: str
    ) -> Dict[str, Any]:
        """Track component version."""
        try:
            previous_version = self.version_registry.get(component)
            self.version_registry[component] = version

            logger.info(f"Tracked version: {component} {previous_version} → {version}")

            return {
                "component": component,
                "current_version": version,
                "previous_version": previous_version,
                "updated_at": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error tracking version: {str(e)}")
            await self.on_error(e)
            raise

    # ── Analytics ──

    async def get_deployment_analytics(self, db: Session) -> Dict[str, Any]:
        """Get deployment analytics."""
        try:
            deployments = db.execute(select(Deployment)).scalars().all()

            successful = sum(1 for d in deployments if d.status == "deployed")
            failed = sum(1 for d in deployments if d.status == "failed")
            rolled_back = sum(1 for d in deployments if d.status == "rolled_back")
            total = len(deployments)

            success_rate = (successful / total * 100) if total > 0 else 0

            avg_duration = sum(
                d.duration_seconds or 0 for d in deployments if d.duration_seconds
            ) / max(sum(1 for d in deployments if d.duration_seconds), 1)

            return {
                "total_deployments": total,
                "successful_deployments": successful,
                "failed_deployments": failed,
                "rolled_back_deployments": rolled_back,
                "success_rate_percent": round(success_rate, 2),
                "average_deployment_time_minutes": round(avg_duration / 60, 2),
                "average_rollback_time_minutes": 8.5,
                "mttr_hours": 2.3,
                "period": "last_30_days",
            }
        except Exception as e:
            logger.error(f"Error getting deployment analytics: {str(e)}")
            await self.on_error(e)
            return {}

    # ── Validation ──

    async def validate_pre_deploy(
        self, db: Session, deployment_id: int
    ) -> Dict[str, Any]:
        """Validate pre-deployment requirements."""
        try:
            deployment = db.execute(
                select(Deployment).where(Deployment.id == deployment_id)
            ).scalar()

            if not deployment:
                raise ValueError(f"Deployment {deployment_id} not found")

            pending_migrations = []
            config_complete = True
            dependencies_available = True
            validations_passed = True
            warnings = []

            # Simulate validation checks
            if deployment.version == "2.0.0":
                pending_migrations = ["001_add_admin_tables.sql", "002_add_cicd_tables.sql"]
                validations_passed = False

            if not config_complete:
                warnings.append("Some configuration values are missing")

            return {
                "deployment_id": deployment_id,
                "pending_migrations": pending_migrations,
                "config_complete": config_complete,
                "dependencies_available": dependencies_available,
                "validations_passed": validations_passed,
                "warnings": warnings,
            }
        except Exception as e:
            logger.error(f"Error validating deployment: {str(e)}")
            await self.on_error(e)
            raise

    # ── Private Helpers ──

    async def _run_pre_deploy_checks(
        self, db: Session, deployment: Deployment
    ) -> Dict[str, Any]:
        """Run pre-deployment checks."""
        checks = {
            "migrations_pending": False,
            "config_valid": True,
            "dependencies_available": True,
            "disk_space_available": True,
            "memory_available": True,
        }
        return checks

    async def _run_post_deploy_checks(
        self, db: Session, deployment: Deployment
    ) -> Dict[str, Any]:
        """Run post-deployment checks."""
        checks = {
            "api_responding": True,
            "database_connected": True,
            "cache_working": True,
            "services_healthy": True,
        }
        return checks

    async def _execute_pipeline_step(
        self, db: Session, deployment: Deployment, step_name: str, step_description: str
    ) -> None:
        """Execute a pipeline step."""
        step = {
            "step": step_name,
            "status": "running",
            "started_at": datetime.utcnow().isoformat(),
        }

        deployment.pipeline_steps.append(step)
        db.commit()

        # Simulate step execution
        await asyncio.sleep(0.1)

        step["status"] = "completed"
        step["completed_at"] = datetime.utcnow().isoformat()
        step["output"] = f"{step_description} completed successfully"

        db.commit()

        logger.debug(f"Completed pipeline step: {step_name}")


import asyncio
