import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, date
from abc import abstractmethod
from agents.base_agent import BaseAgent
from agents.events import EventType
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from models.match import MatchScore
from models.candidate import Candidate
from models.requirement import Requirement
from config import settings

logger = logging.getLogger(__name__)

# Skill synonyms mapping - expanded from Jobright.ai patterns
SKILL_SYNONYMS: Dict[str, List[str]] = {
    "javascript": ["js", "es6", "node.js", "nodejs"],
    "python": ["py", "django", "flask", "fastapi"],
    "java": ["spring", "spring boot"],
    "c#": ["csharp", "dotnet", ".net", "asp.net"],
    "c++": ["cpp"],
    "typescript": ["ts"],
    "react": ["reactjs"],
    "angular": ["angularjs", "ng"],
    "vue": ["vuejs"],
    "node": ["nodejs", "node.js"],
    "sql": ["mysql", "postgresql", "postgres", "oracle", "mssql", "t-sql"],
    "nosql": ["mongodb", "cassandra", "redis", "dynamo", "elasticsearch"],
    "mongodb": ["mongo"],
    "postgresql": ["postgres", "psql"],
    "mysql": ["mariadb"],
    "aws": ["amazon web services"],
    "gcp": ["google cloud", "google cloud platform"],
    "azure": ["microsoft azure"],
    "docker": ["containerization", "containers"],
    "kubernetes": ["k8s"],
    "git": ["github", "gitlab", "bitbucket"],
    "ci/cd": ["continuous integration", "continuous deployment", "jenkins", "gitlab ci", "github actions"],
    "devops": ["infrastructure as code", "iac"],
    "testing": ["jest", "mocha", "pytest", "unittest", "jasmine"],
    "html": ["html5"],
    "css": ["scss", "sass", "less"],
    "rest": ["restful", "rest api"],
    "graphql": ["gql"],
    "api": ["web api", "rest api"],
    "machine learning": ["ml", "deep learning", "ai", "artificial intelligence"],
    "tensorflow": ["tf"],
    "pytorch": ["torch"],
    "data science": ["data analysis", "analytics"],
    "pandas": [],
    "numpy": [],
    "scipy": [],
    "scikit-learn": ["sklearn"],
    "excel": ["spreadsheet"],
    "tableau": ["data visualization"],
    "power bi": ["powerbi", "business intelligence", "bi"],
    "agile": ["scrum", "kanban"],
    "jira": [],
    "confluence": [],
    "linux": ["unix"],
    "windows": ["windows server"],
    "macos": ["mac os", "osx"],
    "ios": [],
    "android": [],
    "react native": [],
    "flutter": [],
    "swift": [],
    "kotlin": [],
    "scala": [],
    "go": ["golang"],
    "rust": [],
    "ruby": ["rails", "ruby on rails"],
    "php": ["laravel", "symfony"],
    "r": ["r programming"],
    "matlab": [],
    "salesforce": ["sfdc"],
    "sap": [],
    "oracle": ["oracle database"],
    "communication": ["interpersonal", "soft skills", "presentation"],
    "leadership": ["management", "team management"],
    "project management": ["pm", "pmp"],
    "problem solving": ["analytical thinking"],
    "attention to detail": ["detail-oriented"],
    "time management": ["deadline-driven"],
    "collaboration": ["teamwork", "cooperation"],
    "aws s3": ["s3"],
    "aws lambda": ["lambda"],
    "aws rds": ["rds"],
    "aws ec2": ["ec2"],
    "microservices": ["microservice architecture"],
    "rest api": ["rest", "restful"],
    "soap": [],
    "messaging": ["rabbitmq", "kafka", "activemq"],
    "rabbitmq": ["amqp"],
    "kafka": [],
    "redis": ["caching", "cache"],
    "memcached": ["caching"],
    "elasticsearch": ["search"],
    "solr": [],
    "neo4j": ["graph database"],
    "dynamodb": ["nosql", "dynamo"],
    "html/css": ["html", "css"],
    "javascript/typescript": ["js", "ts"],
}

# Skill relationships - skills that are related but not synonymous
SKILL_RELATIONS: Dict[str, List[str]] = {
    "javascript": ["typescript", "node.js", "react", "angular", "vue", "html", "css"],
    "python": ["django", "flask", "fastapi", "data science", "machine learning"],
    "java": ["spring", "spring boot", "microservices", "android"],
    "react": ["javascript", "typescript", "html", "css", "webpack"],
    "angular": ["typescript", "javascript", "html", "css", "rxjs"],
    "vue": ["javascript", "typescript", "html", "css"],
    "node.js": ["javascript", "typescript", "rest api", "express", "mongodb"],
    "aws": ["devops", "docker", "kubernetes", "ci/cd", "terraform"],
    "docker": ["kubernetes", "devops", "ci/cd"],
    "kubernetes": ["docker", "devops", "microservices"],
    "machine learning": ["python", "data science", "tensorflow", "pytorch"],
    "data science": ["python", "sql", "machine learning", "pandas", "numpy"],
    "devops": ["docker", "kubernetes", "ci/cd", "aws", "linux"],
    "sql": ["database", "nosql", "postgresql", "mysql"],
    "rest api": ["api", "json", "http", "web services"],
    "microservices": ["docker", "kubernetes", "api", "message queues"],
    "testing": ["javascript", "python", "java", "ci/cd"],
    "git": ["github", "gitlab", "version control"],
    "linux": ["devops", "aws", "docker", "kubernetes"],
}


class MatchingAgent(BaseAgent):
    """Agent for matching candidates to job requirements using bidirectional scoring."""

    def __init__(self):
        """Initialize the matching agent."""
        super().__init__(agent_name="MatchingAgent", agent_version="1.0.0")
        self.skill_synonyms = SKILL_SYNONYMS
        self.skill_relations = SKILL_RELATIONS
        self.weights = settings.matching_default_weights
        self.weights["culture"] = 0.0  # Will be calculated from interview feedback

    async def on_start(self) -> None:
        """Initialize matching agent."""
        logger.info(
            f"Matching Agent started with weights: skill={self.weights['skill']}, "
            f"experience={self.weights['experience']}, education={self.weights['education']}"
        )

    async def on_stop(self) -> None:
        """Cleanup matching agent resources."""
        logger.info("Matching Agent stopped")

    def normalize_skill(self, skill: str) -> str:
        """Normalize skill name to lowercase and strip whitespace."""
        return skill.lower().strip()

    def calculate_skill_match(self, required_skill: str, candidate_skills: List[Dict[str, Any]]) -> Tuple[float, str]:
        """
        Calculate skill match score between required skill and candidate skills.

        Uses hierarchy:
        1. Exact match: 1.0
        2. Synonym match: 0.9
        3. Related skill: 0.7
        4. Partial match: 0.5
        5. No match: 0.0

        Args:
            required_skill: Required skill name
            candidate_skills: List of candidate skills with proficiency info

        Returns:
            Tuple of (match_score, match_type)
        """
        normalized_required = self.normalize_skill(required_skill)
        candidate_skill_names = [self.normalize_skill(s.get("skill", "")) for s in candidate_skills]

        # Exact match
        if normalized_required in candidate_skill_names:
            return 1.0, "exact"

        # Check synonyms
        synonyms = self.skill_synonyms.get(normalized_required, [])
        for synonym in synonyms:
            if self.normalize_skill(synonym) in candidate_skill_names:
                return 0.9, "synonym"

        # Check related skills
        related_skills = self.skill_relations.get(normalized_required, [])
        for related in related_skills:
            if self.normalize_skill(related) in candidate_skill_names:
                return 0.7, "related"

        # Partial match (substring)
        for candidate_skill in candidate_skill_names:
            if (normalized_required in candidate_skill) or (candidate_skill in normalized_required):
                return 0.5, "partial"

        return 0.0, "none"

    def score_skills(self, required_skills: List[str], candidate_skills: List[Dict[str, Any]]) -> Tuple[float, List[str], List[str]]:
        """
        Score candidate against required skills.

        Returns weighted average of skill matches and tracks missing/standout skills.

        Args:
            required_skills: List of required skills
            candidate_skills: List of candidate skills

        Returns:
            Tuple of (skill_score, missing_skills, standout_skills)
        """
        if not required_skills:
            return 1.0, [], []

        skill_scores = []
        missing_skills = []
        standout_skills = []

        candidate_skill_names = [self.normalize_skill(s.get("skill", "")) for s in candidate_skills]

        for required_skill in required_skills:
            score, match_type = self.calculate_skill_match(required_skill, candidate_skills)
            skill_scores.append(score)
            if score == 0.0:
                missing_skills.append(required_skill)

        # Identify standout skills (candidate has skills not in requirements)
        required_normalized = [self.normalize_skill(s) for s in required_skills]
        for candidate_skill_dict in candidate_skills:
            skill_name = self.normalize_skill(candidate_skill_dict.get("skill", ""))
            if skill_name and skill_name not in required_normalized:
                standout_skills.append(candidate_skill_dict.get("skill", skill_name))

        # Calculate average skill score
        skill_score = sum(skill_scores) / len(skill_scores) if skill_scores else 0.0

        return skill_score, missing_skills, standout_skills

    def score_experience(
        self,
        candidate_experience_years: Optional[float],
        required_min_years: Optional[float],
        required_max_years: Optional[float],
    ) -> float:
        """
        Score candidate experience against requirement range.

        Perfect score (1.0) if experience is within range.
        Partial score if outside range but close.

        Args:
            candidate_experience_years: Candidate's total years of experience
            required_min_years: Minimum required years
            required_max_years: Maximum required years

        Returns:
            Experience score (0.0 to 1.0)
        """
        if candidate_experience_years is None:
            return 0.5  # Neutral score if unknown

        if required_min_years is None and required_max_years is None:
            return 1.0  # No requirement, full score

        min_years = required_min_years or 0
        max_years = required_max_years or float("inf")

        # Within range
        if min_years <= candidate_experience_years <= max_years:
            return 1.0

        # Below minimum
        if candidate_experience_years < min_years:
            gap = min_years - candidate_experience_years
            return max(0.0, 1.0 - (gap * 0.1))  # 10% penalty per year below

        # Above maximum
        if candidate_experience_years > max_years:
            gap = candidate_experience_years - max_years
            return max(0.0, 1.0 - (gap * 0.05))  # 5% penalty per year above

        return 0.5

    def score_education(self, candidate_education: List[Dict[str, Any]], required_level: Optional[str]) -> float:
        """
        Score candidate education against requirement.

        Levels: High School < Associate < Bachelor < Master < PhD

        Args:
            candidate_education: List of candidate education records
            required_level: Required education level

        Returns:
            Education score (0.0 to 1.0)
        """
        if not required_level:
            return 1.0

        education_hierarchy = {
            "high school": 1,
            "associate": 2,
            "bachelor": 3,
            "master": 4,
            "phd": 5,
        }

        required_level_normalized = required_level.lower()
        required_rank = education_hierarchy.get(required_level_normalized, 0)

        if not candidate_education:
            return 0.0 if required_rank > 0 else 1.0

        # Get highest education from candidate
        max_candidate_rank = 0
        for edu in candidate_education:
            degree = self.normalize_skill(edu.get("degree", ""))
            for edu_level, rank in education_hierarchy.items():
                if edu_level in degree:
                    max_candidate_rank = max(max_candidate_rank, rank)
                    break

        if max_candidate_rank == 0:
            return 0.5  # Unknown education, neutral score

        if max_candidate_rank >= required_rank:
            return 1.0

        # Calculate partial score for below requirement
        gap = required_rank - max_candidate_rank
        return max(0.0, 1.0 - (gap * 0.3))

    def score_location(
        self,
        candidate_city: Optional[str],
        candidate_state: Optional[str],
        candidate_country: Optional[str],
        requirement_city: Optional[str],
        requirement_state: Optional[str],
        requirement_country: Optional[str],
        requirement_work_mode: Optional[str],
    ) -> float:
        """
        Score candidate location match against requirement.

        Remote: 1.0 if candidate willing
        Same country: 1.0
        Same state: 0.8
        Different location: 0.0-0.5 (depends on relocation willingness)

        Args:
            candidate_city: Candidate city
            candidate_state: Candidate state
            candidate_country: Candidate country
            requirement_city: Required city
            requirement_state: Required state
            requirement_country: Required country
            requirement_work_mode: Remote/Onsite/Hybrid

        Returns:
            Location score (0.0 to 1.0)
        """
        if requirement_work_mode and requirement_work_mode.lower() == "remote":
            return 1.0

        # No location requirement
        if not requirement_country and not requirement_state and not requirement_city:
            return 1.0

        # Normalize for comparison
        cand_country = (candidate_country or "").lower().strip()
        req_country = (requirement_country or "").lower().strip()
        cand_state = (candidate_state or "").lower().strip()
        req_state = (requirement_state or "").lower().strip()
        cand_city = (candidate_city or "").lower().strip()
        req_city = (requirement_city or "").lower().strip()

        # Same city (best match)
        if cand_city and req_city and cand_city == req_city:
            return 1.0

        # Same state
        if cand_state and req_state and cand_state == req_state:
            return 0.8

        # Same country
        if cand_country and req_country and cand_country == req_country:
            return 0.6

        # Different location
        return 0.3

    def score_rate(
        self,
        candidate_rate: Optional[float],
        requirement_rate_min: Optional[float],
        requirement_rate_max: Optional[float],
    ) -> float:
        """
        Score candidate rate against requirement budget.

        Within budget: 1.0
        Above budget: 0.0
        Below budget: 1.0 (candidate is cheaper)

        Args:
            candidate_rate: Candidate's desired rate
            requirement_rate_min: Minimum rate budget
            requirement_rate_max: Maximum rate budget

        Returns:
            Rate score (0.0 to 1.0)
        """
        if not candidate_rate:
            return 0.5  # Unknown rate

        if not requirement_rate_min and not requirement_rate_max:
            return 1.0  # No budget constraint

        rate_max = requirement_rate_max or float("inf")

        if candidate_rate <= rate_max:
            return 1.0

        # Penalize being over budget
        overage = candidate_rate - rate_max
        penalty = min(1.0, (overage / rate_max) * 0.5)
        return max(0.0, 1.0 - penalty)

    def score_availability(
        self,
        candidate_availability_date: Optional[date],
        requirement_start_date: Optional[date],
    ) -> float:
        """
        Score candidate availability against requirement start date.

        Available before or on start date: 1.0
        Penalty for each week later

        Args:
            candidate_availability_date: Date candidate is available
            requirement_start_date: Required start date

        Returns:
            Availability score (0.0 to 1.0)
        """
        if not candidate_availability_date or not requirement_start_date:
            return 1.0  # Unknown availability

        if candidate_availability_date <= requirement_start_date:
            return 1.0

        # Calculate days late
        days_late = (candidate_availability_date - requirement_start_date).days
        weeks_late = days_late / 7

        # 5% penalty per week late, max 1.0
        penalty = min(1.0, weeks_late * 0.05)
        return max(0.0, 1.0 - penalty)

    def score_culture(self, interview_feedback: Optional[List[Dict[str, Any]]]) -> float:
        """
        Score candidate culture fit based on interview feedback.

        Derives from feedback scores in candidate interviews.

        Args:
            interview_feedback: List of interview feedback records

        Returns:
            Culture score (0.0 to 1.0)
        """
        if not interview_feedback or not isinstance(interview_feedback, list):
            return 0.5  # Neutral if no feedback

        culture_scores = []
        for feedback in interview_feedback:
            if isinstance(feedback, dict):
                if "culture_fit_score" in feedback:
                    culture_scores.append(feedback["culture_fit_score"])

        if not culture_scores:
            return 0.5

        return sum(culture_scores) / len(culture_scores)

    async def calculate_match_score(
        self,
        requirement: Requirement,
        candidate: Candidate,
        interview_feedback: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive match score between candidate and requirement.

        Args:
            requirement: Requirement object
            candidate: Candidate object
            interview_feedback: Optional interview feedback for culture scoring

        Returns:
            Dictionary containing:
            - overall_score: Weighted combination of all scores
            - skill_score: Skills match
            - experience_score: Experience match
            - education_score: Education match
            - location_score: Location match
            - rate_score: Rate match
            - availability_score: Availability match
            - culture_score: Culture fit
            - missing_skills: Skills required but not present
            - standout_qualities: Skills present beyond requirements
            - score_breakdown: Component breakdown
        """
        # Score each component
        skill_score, missing_skills, standout_qualities = self.score_skills(
            requirement.skills_required or [],
            candidate.skills or [],
        )

        experience_score = self.score_experience(
            candidate.total_experience_years,
            requirement.experience_min,
            requirement.experience_max,
        )

        education_score = self.score_education(
            candidate.education or [],
            requirement.education_level,
        )

        location_score = self.score_location(
            candidate.location_city,
            candidate.location_state,
            candidate.location_country,
            requirement.location_city,
            requirement.location_state,
            requirement.location_country,
            requirement.work_mode,
        )

        rate_score = self.score_rate(
            candidate.desired_rate,
            requirement.rate_min,
            requirement.rate_max,
        )

        availability_score = self.score_availability(
            candidate.availability_date,
            requirement.start_date,
        )

        culture_score = self.score_culture(interview_feedback)

        # Calculate overall weighted score
        overall_score = (
            self.weights["skill"] * skill_score
            + self.weights["experience"] * experience_score
            + self.weights["education"] * education_score
            + self.weights["location"] * location_score
            + self.weights["rate"] * rate_score
            + self.weights["availability"] * availability_score
            + self.weights["culture"] * culture_score
        )

        score_breakdown = {
            "skill": round(skill_score, 3),
            "experience": round(experience_score, 3),
            "education": round(education_score, 3),
            "location": round(location_score, 3),
            "rate": round(rate_score, 3),
            "availability": round(availability_score, 3),
            "culture": round(culture_score, 3),
        }

        return {
            "overall_score": round(overall_score, 3),
            "skill_score": round(skill_score, 3),
            "experience_score": round(experience_score, 3),
            "education_score": round(education_score, 3),
            "location_score": round(location_score, 3),
            "rate_score": round(rate_score, 3),
            "availability_score": round(availability_score, 3),
            "culture_score": round(culture_score, 3),
            "missing_skills": missing_skills,
            "standout_qualities": standout_qualities,
            "score_breakdown": score_breakdown,
        }

    async def match_requirement_to_candidates(
        self,
        session: AsyncSession,
        requirement_id: int,
        limit: int = 50,
        min_score: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """
        Match a requirement against all active candidates.

        Returns ranked list of matches above minimum score.

        Args:
            session: Database session
            requirement_id: Requirement ID
            limit: Maximum number of results to return
            min_score: Minimum match score threshold

        Returns:
            List of matches sorted by score (highest first)
        """
        # Get requirement
        stmt = select(Requirement).where(Requirement.id == requirement_id)
        result = await session.execute(stmt)
        requirement = result.scalar_one_or_none()

        if not requirement:
            logger.warning(f"Requirement {requirement_id} not found")
            return []

        # Get all active candidates
        stmt = select(Candidate).where(Candidate.is_active == True)
        result = await session.execute(stmt)
        candidates = result.scalars().all()

        matches = []
        for candidate in candidates:
            score_data = await self.calculate_match_score(requirement, candidate)

            if score_data["overall_score"] >= min_score:
                matches.append({
                    "candidate_id": candidate.id,
                    "candidate_name": candidate.full_name,
                    "candidate_email": candidate.email,
                    **score_data,
                })

        # Sort by overall score descending
        matches.sort(key=lambda x: x["overall_score"], reverse=True)

        return matches[:limit]

    async def match_candidate_to_requirements(
        self,
        session: AsyncSession,
        candidate_id: int,
        limit: int = 50,
        min_score: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """
        Match a candidate against all active requirements.

        Returns ranked list of matches above minimum score.

        Args:
            session: Database session
            candidate_id: Candidate ID
            limit: Maximum number of results to return
            min_score: Minimum match score threshold

        Returns:
            List of matches sorted by score (highest first)
        """
        # Get candidate
        stmt = select(Candidate).where(Candidate.id == candidate_id)
        result = await session.execute(stmt)
        candidate = result.scalar_one_or_none()

        if not candidate:
            logger.warning(f"Candidate {candidate_id} not found")
            return []

        # Get all active requirements
        stmt = select(Requirement).where(
            and_(
                Requirement.is_active == True,
                Requirement.status == "active",
            )
        )
        result = await session.execute(stmt)
        requirements = result.scalars().all()

        matches = []
        for requirement in requirements:
            score_data = await self.calculate_match_score(requirement, candidate)

            if score_data["overall_score"] >= min_score:
                matches.append({
                    "requirement_id": requirement.id,
                    "requirement_title": requirement.title,
                    **score_data,
                })

        # Sort by overall score descending
        matches.sort(key=lambda x: x["overall_score"], reverse=True)

        return matches[:limit]

    async def batch_match_all(
        self,
        session: AsyncSession,
        min_score: float = 0.5,
    ) -> Dict[str, Any]:
        """
        Match all active requirements against all active candidates.

        Creates or updates MatchScore records.

        Args:
            session: Database session
            min_score: Minimum score threshold to save match

        Returns:
            Dictionary with batch operation stats
        """
        # Get all active requirements
        stmt = select(Requirement).where(
            and_(
                Requirement.is_active == True,
                Requirement.status == "active",
            )
        )
        result = await session.execute(stmt)
        requirements = result.scalars().all()

        # Get all active candidates
        stmt = select(Candidate).where(Candidate.is_active == True)
        result = await session.execute(stmt)
        candidates = result.scalars().all()

        stats = {
            "total_requirements": len(requirements),
            "total_candidates": len(candidates),
            "matches_created": 0,
            "matches_updated": 0,
            "errors": 0,
        }

        for requirement in requirements:
            for candidate in candidates:
                try:
                    score_data = await self.calculate_match_score(requirement, candidate)

                    if score_data["overall_score"] < min_score:
                        continue

                    # Check if match exists
                    stmt = select(MatchScore).where(
                        and_(
                            MatchScore.requirement_id == requirement.id,
                            MatchScore.candidate_id == candidate.id,
                        )
                    )
                    result = await session.execute(stmt)
                    existing_match = result.scalar_one_or_none()

                    if existing_match:
                        # Update existing match
                        existing_match.overall_score = score_data["overall_score"]
                        existing_match.skill_score = score_data["skill_score"]
                        existing_match.experience_score = score_data["experience_score"]
                        existing_match.education_score = score_data["education_score"]
                        existing_match.location_score = score_data["location_score"]
                        existing_match.rate_score = score_data["rate_score"]
                        existing_match.availability_score = score_data["availability_score"]
                        existing_match.culture_score = score_data["culture_score"]
                        existing_match.missing_skills = score_data["missing_skills"]
                        existing_match.standout_qualities = score_data["standout_qualities"]
                        existing_match.score_breakdown = score_data["score_breakdown"]
                        existing_match.matched_at = datetime.utcnow()
                        stats["matches_updated"] += 1
                    else:
                        # Create new match
                        match = MatchScore(
                            requirement_id=requirement.id,
                            candidate_id=candidate.id,
                            overall_score=score_data["overall_score"],
                            skill_score=score_data["skill_score"],
                            experience_score=score_data["experience_score"],
                            education_score=score_data["education_score"],
                            location_score=score_data["location_score"],
                            rate_score=score_data["rate_score"],
                            availability_score=score_data["availability_score"],
                            culture_score=score_data["culture_score"],
                            missing_skills=score_data["missing_skills"],
                            standout_qualities=score_data["standout_qualities"],
                            score_breakdown=score_data["score_breakdown"],
                        )
                        session.add(match)
                        stats["matches_created"] += 1

                except Exception as e:
                    logger.error(f"Error matching requirement {requirement.id} to candidate {candidate.id}: {str(e)}")
                    stats["errors"] += 1

        # Commit all changes
        try:
            await session.commit()
            logger.info(f"Batch matching completed: {stats}")
        except Exception as e:
            logger.error(f"Error committing batch matches: {str(e)}")
            await session.rollback()
            stats["errors"] += 1

        return stats

    async def recalculate_requirement_matches(
        self,
        session: AsyncSession,
        requirement_id: int,
    ) -> Dict[str, Any]:
        """
        Recalculate all match scores for a specific requirement.

        Args:
            session: Database session
            requirement_id: Requirement ID

        Returns:
            Operation statistics
        """
        # Get requirement
        stmt = select(Requirement).where(Requirement.id == requirement_id)
        result = await session.execute(stmt)
        requirement = result.scalar_one_or_none()

        if not requirement:
            logger.warning(f"Requirement {requirement_id} not found")
            return {"error": "Requirement not found"}

        # Get all active candidates
        stmt = select(Candidate).where(Candidate.is_active == True)
        result = await session.execute(stmt)
        candidates = result.scalars().all()

        stats = {
            "requirement_id": requirement_id,
            "matches_updated": 0,
            "matches_created": 0,
            "errors": 0,
        }

        for candidate in candidates:
            try:
                score_data = await self.calculate_match_score(requirement, candidate)

                # Check if match exists
                stmt = select(MatchScore).where(
                    and_(
                        MatchScore.requirement_id == requirement.id,
                        MatchScore.candidate_id == candidate.id,
                    )
                )
                result = await session.execute(stmt)
                existing_match = result.scalar_one_or_none()

                if existing_match:
                    existing_match.overall_score = score_data["overall_score"]
                    existing_match.skill_score = score_data["skill_score"]
                    existing_match.experience_score = score_data["experience_score"]
                    existing_match.education_score = score_data["education_score"]
                    existing_match.location_score = score_data["location_score"]
                    existing_match.rate_score = score_data["rate_score"]
                    existing_match.availability_score = score_data["availability_score"]
                    existing_match.culture_score = score_data["culture_score"]
                    existing_match.missing_skills = score_data["missing_skills"]
                    existing_match.standout_qualities = score_data["standout_qualities"]
                    existing_match.score_breakdown = score_data["score_breakdown"]
                    existing_match.matched_at = datetime.utcnow()
                    stats["matches_updated"] += 1
                else:
                    match = MatchScore(
                        requirement_id=requirement.id,
                        candidate_id=candidate.id,
                        overall_score=score_data["overall_score"],
                        skill_score=score_data["skill_score"],
                        experience_score=score_data["experience_score"],
                        education_score=score_data["education_score"],
                        location_score=score_data["location_score"],
                        rate_score=score_data["rate_score"],
                        availability_score=score_data["availability_score"],
                        culture_score=score_data["culture_score"],
                        missing_skills=score_data["missing_skills"],
                        standout_qualities=score_data["standout_qualities"],
                        score_breakdown=score_data["score_breakdown"],
                    )
                    session.add(match)
                    stats["matches_created"] += 1

            except Exception as e:
                logger.error(f"Error calculating match for candidate {candidate.id}: {str(e)}")
                stats["errors"] += 1

        try:
            await session.commit()
        except Exception as e:
            logger.error(f"Error committing matches: {str(e)}")
            await session.rollback()
            stats["errors"] += 1

        return stats
