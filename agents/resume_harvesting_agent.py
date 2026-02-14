"""Resume harvesting agent for multi-source candidate sourcing."""

import logging
import asyncio
import aiohttp
import hashlib
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from anthropic import AsyncAnthropic

from agents.base_agent import BaseAgent
from agents.events import Event, EventType
from models.harvest import HarvestSource, HarvestJob, HarvestResult, CandidateSourceMapping
from models.candidate import Candidate
from models.enums import CandidateStatus

logger = logging.getLogger(__name__)


class ResumeHarvestingAgent(BaseAgent):
    """Multi-source resume/candidate harvesting from job boards, social platforms, and communities."""

    def __init__(self, anthropic_api_key: str, agent_version: str = "1.0.0"):
        """Initialize harvesting agent."""
        super().__init__(agent_name="ResumeHarvestingAgent", agent_version=agent_version)
        self.client = AsyncAnthropic(api_key=anthropic_api_key)
        self.harvest_adapters = {
            "linkedin": self._harvest_linkedin,
            "dice": self._harvest_dice,
            "monster": self._harvest_monster,
            "indeed": self._harvest_indeed,
            "github": self._harvest_github,
            "stackoverflow": self._harvest_stackoverflow,
            "forums": self._harvest_forums,
        }

    async def configure_source(self, db: AsyncSession, source_config: Dict[str, Any]) -> HarvestSource:
        """Configure a harvesting source with API credentials and search parameters."""
        try:
            # Check if source already exists
            stmt = select(HarvestSource).where(HarvestSource.name == source_config.get("name"))
            result = await db.execute(stmt)
            existing_source = result.scalars().first()

            if existing_source:
                # Update existing source
                for key, value in source_config.items():
                    if hasattr(existing_source, key):
                        setattr(existing_source, key, value)
                logger.info(f"Updated harvest source: {source_config.get('name')}")
            else:
                # Create new source
                source = HarvestSource(
                    name=source_config["name"],
                    source_type=source_config.get("source_type", "job_board"),
                    api_endpoint=source_config.get("api_endpoint"),
                    api_key_encrypted=source_config.get("api_key_encrypted"),
                    api_secret_encrypted=source_config.get("api_secret_encrypted"),
                    rate_limit_per_hour=source_config.get("rate_limit_per_hour", 100),
                    rate_limit_per_day=source_config.get("rate_limit_per_day", 1000),
                    config=source_config.get("config", {}),
                )
                db.add(source)
                existing_source = source
                logger.info(f"Created harvest source: {source_config.get('name')}")

            await db.flush()
            return existing_source

        except Exception as e:
            logger.error(f"Error configuring harvest source: {str(e)}")
            raise

    async def search_candidates(
        self, db: AsyncSession, source_name: str, search_criteria: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Search for candidates on a specific source."""
        try:
            if source_name.lower() not in self.harvest_adapters:
                raise ValueError(f"Unknown source: {source_name}")

            # Get source config from database
            stmt = select(HarvestSource).where(HarvestSource.name == source_name.lower())
            result = await db.execute(stmt)
            source = result.scalars().first()

            if not source:
                raise ValueError(f"Source not configured: {source_name}")

            # Call appropriate adapter
            adapter = self.harvest_adapters[source_name.lower()]
            candidates = await adapter(db, source, search_criteria)

            logger.info(f"Found {len(candidates)} candidates from {source_name}")
            return candidates

        except Exception as e:
            logger.error(f"Error searching candidates on {source_name}: {str(e)}")
            raise

    async def _harvest_linkedin(
        self, db: AsyncSession, source: HarvestSource, criteria: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Search LinkedIn using API/scraping adapter."""
        # In production, use LinkedIn API or Bright Data/Apify scraping service
        candidates = []
        keywords = criteria.get("keywords", [])
        location = criteria.get("location", "")
        experience_level = criteria.get("experience_level", "")

        try:
            # Simulated LinkedIn API call
            # Replace with actual LinkedIn API integration
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {source.api_key_encrypted}"}
                params = {
                    "keywords": " ".join(keywords) if keywords else "",
                    "location": location,
                    "experience": experience_level,
                    "limit": 100,
                }

                # This is a placeholder - in production use LinkedIn API
                logger.info(f"LinkedIn search with params: {params}")

                # Return mock data structure
                candidates = [
                    {
                        "source": "linkedin",
                        "source_profile_id": f"li_{i}",
                        "source_profile_url": f"https://linkedin.com/in/user{i}",
                        "name": f"Candidate {i}",
                        "title": criteria.get("job_title", "Software Engineer"),
                        "company": "Tech Corp",
                        "location": location,
                        "skills": keywords,
                        "experience_years": 5 + i,
                        "profile_summary": f"Experienced professional with {5 + i} years in tech",
                        "raw_data": {
                            "headline": f"Software Engineer at Tech Corp",
                            "summary": "Experienced tech professional",
                            "location": location,
                        },
                    }
                    for i in range(5)
                ]

        except Exception as e:
            logger.error(f"Error harvesting LinkedIn: {str(e)}")

        return candidates

    async def _harvest_dice(self, db: AsyncSession, source: HarvestSource, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search Dice job board for candidate profiles."""
        # Dice API integration
        candidates = []
        try:
            keywords = criteria.get("keywords", [])
            location = criteria.get("location", "")

            async with aiohttp.ClientSession() as session:
                # Dice API endpoint
                url = source.api_endpoint or "https://api.dice.com/search"
                params = {"keywords": " ".join(keywords), "location": location}

                # In production, make actual API call with error handling
                candidates = [
                    {
                        "source": "dice",
                        "source_profile_id": f"dice_{i}",
                        "source_profile_url": f"https://dice.com/profile/user{i}",
                        "name": f"Candidate {i}",
                        "title": criteria.get("job_title", "Developer"),
                        "location": location,
                        "skills": keywords,
                        "experience_years": 3 + i,
                        "raw_data": {"keywords": keywords, "location": location},
                    }
                    for i in range(3)
                ]

        except Exception as e:
            logger.error(f"Error harvesting Dice: {str(e)}")

        return candidates

    async def _harvest_monster(self, db: AsyncSession, source: HarvestSource, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search Monster resume database."""
        candidates = []
        try:
            keywords = criteria.get("keywords", [])
            candidates = [
                {
                    "source": "monster",
                    "source_profile_id": f"monster_{i}",
                    "source_profile_url": f"https://monster.com/profile/{i}",
                    "name": f"Candidate {i}",
                    "title": criteria.get("job_title", "Professional"),
                    "location": criteria.get("location", ""),
                    "skills": keywords,
                    "raw_data": {"source": "monster", "keywords": keywords},
                }
                for i in range(2)
            ]
        except Exception as e:
            logger.error(f"Error harvesting Monster: {str(e)}")

        return candidates

    async def _harvest_indeed(self, db: AsyncSession, source: HarvestSource, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search Indeed resume database."""
        candidates = []
        try:
            keywords = criteria.get("keywords", [])
            candidates = [
                {
                    "source": "indeed",
                    "source_profile_id": f"indeed_{i}",
                    "source_profile_url": f"https://indeed.com/resumes/{i}",
                    "name": f"Candidate {i}",
                    "title": criteria.get("job_title", "Professional"),
                    "location": criteria.get("location", ""),
                    "skills": keywords,
                    "raw_data": {"source": "indeed", "keywords": keywords},
                }
                for i in range(2)
            ]
        except Exception as e:
            logger.error(f"Error harvesting Indeed: {str(e)}")

        return candidates

    async def _harvest_github(self, db: AsyncSession, source: HarvestSource, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search GitHub for developers by language, contributions, repos."""
        candidates = []
        try:
            languages = criteria.get("languages", [])
            location = criteria.get("location", "")

            async with aiohttp.ClientSession() as session:
                # GitHub API
                url = "https://api.github.com/search/users"
                query_parts = [f"language:{lang}" for lang in languages]
                if location:
                    query_parts.append(f"location:{location}")
                query = " ".join(query_parts)

                headers = {"Accept": "application/vnd.github.v3+json"}
                if source.api_key_encrypted:
                    headers["Authorization"] = f"token {source.api_key_encrypted}"

                params = {"q": query, "sort": "repositories", "per_page": 10}

                # In production, make actual API call
                candidates = [
                    {
                        "source": "github",
                        "source_profile_id": f"gh_{i}",
                        "source_profile_url": f"https://github.com/user{i}",
                        "name": f"Developer {i}",
                        "username": f"dev_user_{i}",
                        "location": location,
                        "languages": languages,
                        "bio": f"Software developer with {3 + i} years experience",
                        "public_repos": 10 + i,
                        "followers": 50 + (i * 20),
                        "contribution_score": 75 + (i * 5),
                        "raw_data": {"languages": languages, "public_repos": 10 + i, "followers": 50 + (i * 20)},
                    }
                    for i in range(5)
                ]

        except Exception as e:
            logger.error(f"Error harvesting GitHub: {str(e)}")

        return candidates

    async def _harvest_stackoverflow(self, db: AsyncSession, source: HarvestSource, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search Stack Overflow users by reputation, tags, location."""
        candidates = []
        try:
            tags = criteria.get("tags", [])
            location = criteria.get("location", "")

            async with aiohttp.ClientSession() as session:
                url = "https://api.stackexchange.com/2.3/users"
                params = {"site": "stackoverflow", "order": "desc", "sort": "reputation"}

                # In production, make actual API call with tag filtering
                candidates = [
                    {
                        "source": "stackoverflow",
                        "source_profile_id": f"so_{i}",
                        "source_profile_url": f"https://stackoverflow.com/users/{i}",
                        "name": f"Expert {i}",
                        "reputation": 5000 + (i * 1000),
                        "tags": tags,
                        "badge_count": {"gold": 1 + i, "silver": 3 + i, "bronze": 10 + i},
                        "answers_count": 100 + (i * 50),
                        "location": location,
                        "raw_data": {"reputation": 5000 + (i * 1000), "tags": tags},
                    }
                    for i in range(5)
                ]

        except Exception as e:
            logger.error(f"Error harvesting Stack Overflow: {str(e)}")

        return candidates

    async def _harvest_forums(self, db: AsyncSession, source: HarvestSource, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search technical forums/communities (HackerNews, Dev.to, Medium)."""
        candidates = []
        try:
            keywords = criteria.get("keywords", [])

            # Search Dev.to, Medium, HackerNews for technical authors
            candidates = [
                {
                    "source": "forums",
                    "source_profile_id": f"forum_{i}",
                    "source_profile_url": f"https://dev.to/author{i}",
                    "name": f"Technical Author {i}",
                    "platform": "dev.to",
                    "articles_count": 10 + (i * 5),
                    "followers": 100 + (i * 50),
                    "topics": keywords,
                    "raw_data": {"platform": "dev.to", "articles": 10 + (i * 5), "followers": 100 + (i * 50)},
                }
                for i in range(3)
            ]

        except Exception as e:
            logger.error(f"Error harvesting forums: {str(e)}")

        return candidates

    async def deduplicate_candidates(self, db: AsyncSession, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect duplicate candidates across sources using email/name/linkedin fuzzy matching."""
        try:
            deduped = []
            seen = set()

            for candidate in candidates:
                # Create hash for deduplication
                name = candidate.get("name", "").lower().strip()
                email = candidate.get("email", "").lower().strip()
                source_profile_id = candidate.get("source_profile_id", "")

                # Check for duplicates in database
                hash_key = hashlib.md5(f"{name}_{email}".encode()).hexdigest()

                if hash_key not in seen:
                    # Check database for similar candidates
                    similarity_threshold = 0.85
                    is_duplicate = False

                    if email:
                        stmt = select(Candidate).where(Candidate.email == email)
                        result = await db.execute(stmt)
                        existing = result.scalars().first()
                        if existing:
                            is_duplicate = True

                    if not is_duplicate and name:
                        # Fuzzy matching on name
                        stmt = select(Candidate).where(
                            func.lower(Candidate.first_name + " " + Candidate.last_name).like(f"%{name}%")
                        )
                        result = await db.execute(stmt)
                        existing_candidates = result.scalars().all()

                        for existing in existing_candidates:
                            full_name = f"{existing.first_name} {existing.last_name}".lower()
                            similarity = SequenceMatcher(None, name, full_name).ratio()
                            if similarity > similarity_threshold:
                                is_duplicate = True
                                break

                    if not is_duplicate:
                        deduped.append(candidate)
                        seen.add(hash_key)

            logger.info(f"Deduplicated {len(candidates)} candidates to {len(deduped)}")
            return deduped

        except Exception as e:
            logger.error(f"Error deduplicating candidates: {str(e)}")
            return candidates

    async def enrich_candidate(self, db: AsyncSession, candidate_id: int, sources: Optional[List[str]] = None) -> Dict[str, Any]:
        """Cross-reference candidate across multiple sources to enrich profile."""
        try:
            stmt = select(Candidate).where(Candidate.id == candidate_id)
            result = await db.execute(stmt)
            candidate = result.scalars().first()

            if not candidate:
                raise ValueError(f"Candidate not found: {candidate_id}")

            enrichment = {
                "candidate_id": candidate_id,
                "enriched_at": datetime.utcnow().isoformat(),
                "sources": {},
            }

            # Get candidate's source mappings
            stmt = select(CandidateSourceMapping).where(CandidateSourceMapping.candidate_id == candidate_id)
            result = await db.execute(stmt)
            mappings = result.scalars().all()

            for mapping in mappings:
                if sources and mapping.source_id not in sources:
                    continue

                source_data = mapping.source_data or {}
                enrichment["sources"][mapping.source_id] = {
                    "profile_id": mapping.source_profile_id,
                    "profile_url": mapping.source_profile_url,
                    "enrichment_data": source_data,
                }

            logger.info(f"Enriched candidate {candidate_id} with {len(enrichment['sources'])} sources")
            return enrichment

        except Exception as e:
            logger.error(f"Error enriching candidate: {str(e)}")
            raise

    async def schedule_harvest(
        self, db: AsyncSession, source_name: str, criteria: Dict[str, Any], frequency: str
    ) -> HarvestJob:
        """Schedule recurring harvesting jobs."""
        try:
            stmt = select(HarvestSource).where(HarvestSource.name == source_name)
            result = await db.execute(stmt)
            source = result.scalars().first()

            if not source:
                raise ValueError(f"Source not found: {source_name}")

            next_run_at = datetime.utcnow()
            if frequency == "daily":
                next_run_at += timedelta(days=1)
            elif frequency == "weekly":
                next_run_at += timedelta(weeks=1)
            elif frequency == "monthly":
                next_run_at += timedelta(days=30)

            job = HarvestJob(
                source_id=source.id,
                search_criteria=criteria,
                frequency=frequency,
                status="scheduled",
                next_run_at=next_run_at,
            )

            db.add(job)
            await db.flush()

            logger.info(f"Scheduled harvest job {job.id} for source {source_name} with frequency {frequency}")
            return job

        except Exception as e:
            logger.error(f"Error scheduling harvest: {str(e)}")
            raise

    async def process_harvest_results(
        self, db: AsyncSession, job_id: int, raw_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Process raw results: normalize data, create/update candidates, trigger resume parsing."""
        try:
            stmt = select(HarvestJob).where(HarvestJob.id == job_id)
            result = await db.execute(stmt)
            job = result.scalars().first()

            if not job:
                raise ValueError(f"Harvest job not found: {job_id}")

            processed_results = []
            new_count = 0
            updated_count = 0
            duplicate_count = 0

            # Deduplicate first
            deduped = await self.deduplicate_candidates(db, raw_results)

            for candidate_data in deduped:
                try:
                    email = candidate_data.get("email")
                    name_parts = candidate_data.get("name", "").split(" ", 1)
                    first_name = name_parts[0]
                    last_name = name_parts[1] if len(name_parts) > 1 else ""

                    # Check if candidate exists
                    if email:
                        stmt = select(Candidate).where(Candidate.email == email)
                        result = await db.execute(stmt)
                        existing = result.scalars().first()
                    else:
                        existing = None

                    if existing:
                        candidate = existing
                        updated_count += 1
                        result_status = "processed"
                    else:
                        candidate = Candidate(
                            first_name=first_name,
                            last_name=last_name,
                            email=email or f"noemail_{candidate_data.get('source_profile_id')}@harvested.local",
                            status=CandidateStatus.SOURCED,
                        )
                        db.add(candidate)
                        await db.flush()
                        new_count += 1
                        result_status = "processed"

                    # Create/update source mapping
                    stmt = select(CandidateSourceMapping).where(
                        and_(
                            CandidateSourceMapping.candidate_id == candidate.id,
                            CandidateSourceMapping.source_id == job.source_id,
                        )
                    )
                    result = await db.execute(stmt)
                    mapping = result.scalars().first()

                    if not mapping:
                        mapping = CandidateSourceMapping(
                            candidate_id=candidate.id,
                            source_id=job.source_id,
                            source_profile_id=candidate_data.get("source_profile_id", ""),
                            source_profile_url=candidate_data.get("source_profile_url"),
                            source_data=candidate_data,
                            last_synced_at=datetime.utcnow(),
                        )
                        db.add(mapping)

                    # Create harvest result record
                    harvest_result = HarvestResult(
                        job_id=job_id,
                        source_id=job.source_id,
                        candidate_id=candidate.id,
                        raw_data=candidate_data,
                        source_profile_url=candidate_data.get("source_profile_url"),
                        source_profile_id=candidate_data.get("source_profile_id"),
                        status=result_status,
                        processed_at=datetime.utcnow(),
                    )
                    db.add(harvest_result)

                    processed_results.append({"candidate_id": candidate.id, "status": result_status})

                except Exception as e:
                    logger.error(f"Error processing candidate {candidate_data.get('name')}: {str(e)}")
                    duplicate_count += 1

            # Update job statistics
            job.candidates_found = len(raw_results)
            job.candidates_new = new_count
            job.candidates_updated = updated_count
            job.candidates_duplicate = duplicate_count
            job.status = "completed"
            job.completed_at = datetime.utcnow()

            await db.flush()

            logger.info(
                f"Processed harvest job {job_id}: {new_count} new, {updated_count} updated, {duplicate_count} duplicates"
            )

            return processed_results

        except Exception as e:
            logger.error(f"Error processing harvest results: {str(e)}")
            raise

    async def get_harvest_analytics(self, db: AsyncSession) -> Dict[str, Any]:
        """Analytics: candidates per source, quality scores, conversion rates, cost per candidate."""
        try:
            # Get total candidates harvested
            stmt = select(func.sum(HarvestSource.total_candidates_harvested))
            result = await db.execute(stmt)
            total_harvested = result.scalar() or 0

            # Get candidates by source
            stmt = select(HarvestSource.name, HarvestSource.total_candidates_harvested)
            result = await db.execute(stmt)
            candidates_by_source = {row[0]: row[1] for row in result.all()}

            # Get completed jobs
            stmt = select(HarvestJob).where(HarvestJob.status == "completed")
            result = await db.execute(stmt)
            completed_jobs = result.scalars().all()

            total_jobs = len(completed_jobs)
            total_new = sum(job.candidates_new for job in completed_jobs)
            total_duplicates = sum(job.candidates_duplicate for job in completed_jobs)

            avg_candidates_per_job = total_new / total_jobs if total_jobs > 0 else 0

            analytics = {
                "total_sources": len(candidates_by_source),
                "total_candidates_harvested": total_harvested,
                "total_new_candidates": total_new,
                "total_duplicate_candidates": total_duplicates,
                "candidates_by_source": candidates_by_source,
                "harvest_jobs_total": total_jobs,
                "average_candidates_per_job": avg_candidates_per_job,
                "quality_scores": {
                    "deduplication_effectiveness": (1 - (total_duplicates / total_new)) if total_new > 0 else 0,
                    "average_candidates_per_job": avg_candidates_per_job,
                },
            }

            return analytics

        except Exception as e:
            logger.error(f"Error getting harvest analytics: {str(e)}")
            raise

    async def on_start(self) -> None:
        """Initialize harvesting agent."""
        logger.info("Resume Harvesting Agent started")

    async def on_stop(self) -> None:
        """Cleanup harvesting agent."""
        logger.info("Resume Harvesting Agent stopped")
