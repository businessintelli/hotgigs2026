"""Candidate Rediscovery Agent for Metaview-inspired silver medalist resurfacing."""

import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from anthropic import AsyncAnthropic
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from agents.base_agent import BaseAgent
from models.candidate import Candidate
from models.requirement import Requirement
from models.match import MatchScore
from models.interview import Interview
from models.rediscovery import CandidateRediscovery, CompetencyProfile
from models.enums import CandidateStatus, MatchStatus

logger = logging.getLogger(__name__)


class CandidateRediscoveryAgent(BaseAgent):
    """Agent for discovering and re-engaging silver medalist candidates."""

    def __init__(self, anthropic_api_key: Optional[str] = None):
        """Initialize candidate rediscovery agent.

        Args:
            anthropic_api_key: Anthropic API key for LLM calls
        """
        super().__init__(
            agent_name="CandidateRediscoveryAgent", agent_version="1.0.0"
        )
        self.anthropic_client = (
            AsyncAnthropic(api_key=anthropic_api_key) if anthropic_api_key else None
        )

    async def find_silver_medalists(
        self,
        db: AsyncSession,
        requirement_id: int,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Find past candidates for similar requirements with scoring.

        Args:
            db: Database session
            requirement_id: Current requirement ID
            limit: Maximum candidates to return

        Returns:
            List of candidates ranked by rediscovery score
        """
        try:
            # Get current requirement
            current_req = await db.get(Requirement, requirement_id)
            if not current_req:
                raise ValueError(f"Requirement {requirement_id} not found")

            current_skills = set(current_req.skills_required or [])

            # Find candidates in TALENT_POOL status
            candidates_result = await db.execute(
                select(Candidate).where(
                    Candidate.status == CandidateStatus.TALENT_POOL
                )
            )
            candidates = candidates_result.scalars().all()

            rediscovery_candidates = []

            for candidate in candidates:
                candidate_skills = set(candidate.skills or [])

                # 1. Skill match score (35%)
                if current_skills and candidate_skills:
                    skill_overlap = len(current_skills & candidate_skills) / len(
                        current_skills
                    )
                else:
                    skill_overlap = 0
                skill_match = skill_overlap * 100

                # 2. Historical interview score (40%)
                interview_result = await db.execute(
                    select(Interview).where(
                        Interview.candidate_id == candidate.id
                    ).order_by(desc(Interview.created_at)).limit(5)
                )
                interviews = interview_result.scalars().all()

                interview_scores = [
                    (i.ai_score if i.ai_score else 0) for i in interviews if i.ai_score
                ]
                interview_history_score = (
                    sum(interview_scores) / len(interview_scores)
                    if interview_scores
                    else 0
                ) * 100

                # 3. Recency score (15%) - candidates contacted recently score higher
                if candidate.last_contacted_at:
                    days_since = (
                        datetime.utcnow().date() - candidate.last_contacted_at
                    ).days
                    recency_score = max(0, 100 - (days_since / 30 * 20))
                else:
                    recency_score = 50  # Default for never contacted

                # 4. Engagement bonus (10%)
                engagement_score = (candidate.engagement_score or 0) * 20  # 0-5 becomes 0-100

                # Composite rediscovery score
                rediscovery_score = (
                    skill_match * 0.35
                    + interview_history_score * 0.40
                    + recency_score * 0.15
                    + engagement_score * 0.10
                )

                # Get competency profile
                comp_result = await db.execute(
                    select(CompetencyProfile).where(
                        CompetencyProfile.candidate_id == candidate.id
                    )
                )
                competency = comp_result.scalar_one_or_none()

                candidate_data = {
                    "candidate_id": candidate.id,
                    "candidate_name": f"{candidate.first_name} {candidate.last_name}",
                    "email": candidate.email,
                    "current_title": candidate.current_title,
                    "current_company": candidate.current_company,
                    "rediscovery_score": rediscovery_score,
                    "skill_match_score": skill_match,
                    "interview_history_score": interview_history_score,
                    "recency_score": recency_score,
                    "engagement_score": engagement_score,
                    "last_contacted_at": candidate.last_contacted_at,
                    "years_of_experience": candidate.total_experience_years,
                    "competency_profile": (
                        competency.competency_details if competency else {}
                    ),
                }

                rediscovery_candidates.append(candidate_data)

            # Sort by score and limit
            rediscovery_candidates.sort(
                key=lambda x: x["rediscovery_score"], reverse=True
            )
            result = rediscovery_candidates[:limit]

            logger.info(f"Found {len(result)} silver medalists for requirement {requirement_id}")
            return result

        except Exception as e:
            logger.error(f"Error finding silver medalists: {str(e)}")
            return []

    async def build_competency_index(
        self, db: AsyncSession, candidate_id: int
    ) -> Dict[str, Any]:
        """Build aggregated competency profile from interview feedback.

        Args:
            db: Database session
            candidate_id: Candidate ID

        Returns:
            Competency profile dictionary
        """
        try:
            candidate = await db.get(Candidate, candidate_id)
            if not candidate:
                raise ValueError(f"Candidate {candidate_id} not found")

            # Get all interviews and feedback
            interviews_result = await db.execute(
                select(Interview).where(
                    Interview.candidate_id == candidate_id
                ).order_by(desc(Interview.created_at))
            )
            interviews = interviews_result.scalars().all()

            # Aggregate competency ratings
            competency_ratings = {
                "technical_proficiency": [],
                "communication": [],
                "problem_solving": [],
                "leadership": [],
                "culture_fit": [],
                "domain_expertise": [],
                "adaptability": [],
            }

            assessment_evidence = {}

            for interview in interviews:
                if not interview.scorecard_data:
                    continue

                scorecard = (
                    interview.scorecard_data
                    if isinstance(interview.scorecard_data, dict)
                    else json.loads(interview.scorecard_data)
                )

                # Extract ratings from scorecard
                competencies = scorecard.get("competencies", [])
                for comp in competencies:
                    comp_name = comp.get("name", "").lower().replace(" ", "_")
                    if comp_name in competency_ratings:
                        rating = comp.get("rating", 0)
                        competency_ratings[comp_name].append(rating)

                        # Track evidence
                        if comp_name not in assessment_evidence:
                            assessment_evidence[comp_name] = []
                        assessment_evidence[comp_name].append({
                            "interview_id": interview.id,
                            "interview_date": interview.scheduled_at.isoformat() if interview.scheduled_at else None,
                            "evidence": comp.get("evidence", []),
                        })

            # Calculate averages
            competency_averages = {}
            for competency, ratings in competency_ratings.items():
                if ratings:
                    competency_averages[competency] = sum(ratings) / len(ratings)
                    competency_averages[f"{competency}_count"] = len(ratings)

            # Create or update profile
            profile_result = await db.execute(
                select(CompetencyProfile).where(
                    CompetencyProfile.candidate_id == candidate_id
                )
            )
            profile = profile_result.scalar_one_or_none()

            if not profile:
                profile = CompetencyProfile(candidate_id=candidate_id)

            profile.technical_proficiency = competency_averages.get(
                "technical_proficiency"
            )
            profile.communication = competency_averages.get("communication")
            profile.problem_solving = competency_averages.get("problem_solving")
            profile.leadership = competency_averages.get("leadership")
            profile.culture_fit = competency_averages.get("culture_fit")
            profile.domain_expertise = competency_averages.get("domain_expertise")
            profile.adaptability = competency_averages.get("adaptability")
            profile.assessment_count = len(interviews)
            profile.last_assessed_at = (
                interviews[0].scheduled_at if interviews else None
            )

            profile.competency_details = {
                "averages": competency_averages,
                "evidence": assessment_evidence,
            }

            db.add(profile)
            await db.commit()
            await db.refresh(profile)

            logger.info(
                f"Built competency profile for candidate {candidate_id}"
            )

            return {
                "candidate_id": candidate_id,
                "averages": competency_averages,
                "assessment_count": len(interviews),
                "last_assessed": profile.last_assessed_at.isoformat() if profile.last_assessed_at else None,
            }

        except Exception as e:
            await db.rollback()
            logger.error(f"Error building competency index: {str(e)}")
            raise

    async def detect_reengagement_opportunities(
        self,
        db: AsyncSession,
        days_inactive: int = 90,
    ) -> List[Dict[str, Any]]:
        """Find inactive talent pool candidates with good scores.

        Args:
            db: Database session
            days_inactive: Days without contact

        Returns:
            List of reengagement opportunities
        """
        try:
            cutoff_date = (
                datetime.utcnow().date() - timedelta(days=days_inactive)
            )

            # Find candidates in talent pool not contacted recently with good history
            candidates_result = await db.execute(
                select(Candidate).where(
                    and_(
                        Candidate.status == CandidateStatus.TALENT_POOL,
                        Candidate.last_contacted_at <= cutoff_date
                        | (Candidate.last_contacted_at == None),  # noqa: E712
                        Candidate.engagement_score >= 3.0,
                    )
                ).order_by(desc(Candidate.engagement_score)).limit(100)
            )
            candidates = candidates_result.scalars().all()

            opportunities = []

            for candidate in candidates:
                # Get recent interview scores
                interviews_result = await db.execute(
                    select(Interview).where(
                        Interview.candidate_id == candidate.id
                    ).order_by(desc(Interview.created_at)).limit(3)
                )
                interviews = interviews_result.scalars().all()

                avg_score = (
                    sum(i.ai_score for i in interviews if i.ai_score) / len(interviews)
                    if interviews
                    else 0
                )

                if avg_score >= 3.0:
                    days_inactive_actual = (
                        (datetime.utcnow().date() - candidate.last_contacted_at).days
                        if candidate.last_contacted_at
                        else 999
                    )

                    opportunity = {
                        "candidate_id": candidate.id,
                        "candidate_name": f"{candidate.first_name} {candidate.last_name}",
                        "email": candidate.email,
                        "days_inactive": days_inactive_actual,
                        "avg_interview_score": avg_score,
                        "engagement_score": candidate.engagement_score,
                        "skills": candidate.skills,
                        "current_title": candidate.current_title,
                    }
                    opportunities.append(opportunity)

            logger.info(f"Found {len(opportunities)} reengagement opportunities")
            return opportunities

        except Exception as e:
            logger.error(f"Error detecting reengagement opportunities: {str(e)}")
            return []

    async def generate_reengagement_message(
        self,
        db: AsyncSession,
        candidate_id: int,
        requirement_id: int,
    ) -> str:
        """Generate personalized re-engagement email using LLM.

        Args:
            db: Database session
            candidate_id: Candidate ID
            requirement_id: Requirement ID

        Returns:
            Generated email message
        """
        try:
            candidate = await db.get(Candidate, candidate_id)
            requirement = await db.get(Requirement, requirement_id)

            if not candidate or not requirement:
                raise ValueError("Candidate or requirement not found")

            if not self.anthropic_client:
                return "Re-engagement email generation requires Anthropic API key"

            # Get competency profile
            comp_result = await db.execute(
                select(CompetencyProfile).where(
                    CompetencyProfile.candidate_id == candidate_id
                )
            )
            competency = comp_result.scalar_one_or_none()

            prompt = f"""Generate a personalized re-engagement email to attract a past candidate back to apply.

Candidate Profile:
- Name: {candidate.first_name} {candidate.last_name}
- Current Role: {candidate.current_title or 'Unknown'}
- Current Company: {candidate.current_company or 'Unknown'}
- Years of Experience: {candidate.total_experience_years or 'Unknown'}
- Last Contacted: {candidate.last_contacted_at or 'Never'}
- Skills: {', '.join(candidate.skills or [])}
- Engagement Score: {candidate.engagement_score or 0}/5

Competency Highlights:
{json.dumps(competency.competency_details if competency else {}, indent=2)}

New Opportunity:
- Position: {requirement.title}
- Location: {requirement.location_city or 'Remote'}, {requirement.location_country or ''}
- Required Skills: {', '.join(requirement.skills_required or [])}
- Experience Required: {requirement.experience_min}-{requirement.experience_max} years
- Salary Range: ${requirement.rate_min}-${requirement.rate_max} {requirement.rate_type or 'annual'}

Generate a warm, personalized email (200-300 words) that:
1. Acknowledges their past interest/experience
2. Mentions specific strengths based on competency profile
3. Explains why this role is a great fit
4. Creates urgency without pressure
5. Includes clear next steps"""

            message = await self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}],
            )

            email_content = message.content[0].text
            logger.info(f"Generated reengagement message for candidate {candidate_id}")
            return email_content

        except Exception as e:
            logger.error(f"Error generating reengagement message: {str(e)}")
            return ""

    async def score_rediscovery_match(
        self,
        db: AsyncSession,
        candidate_id: int,
        requirement_id: int,
    ) -> Dict[str, Any]:
        """Calculate comprehensive rediscovery match score.

        Args:
            db: Database session
            candidate_id: Candidate ID
            requirement_id: Requirement ID

        Returns:
            Score breakdown dictionary
        """
        try:
            candidate = await db.get(Candidate, candidate_id)
            requirement = await db.get(Requirement, requirement_id)

            if not candidate or not requirement:
                raise ValueError("Candidate or requirement not found")

            # 1. Skill match
            candidate_skills = set(candidate.skills or [])
            required_skills = set(requirement.skills_required or [])

            if candidate_skills and required_skills:
                skill_match = len(candidate_skills & required_skills) / len(
                    required_skills
                )
            else:
                skill_match = 0

            # 2. Interview history score
            interviews_result = await db.execute(
                select(Interview).where(
                    Interview.candidate_id == candidate_id
                ).order_by(desc(Interview.created_at)).limit(5)
            )
            interviews = interviews_result.scalars().all()
            interview_scores = [
                (i.ai_score if i.ai_score else 0) for i in interviews if i.ai_score
            ]
            interview_score = (
                sum(interview_scores) / len(interview_scores) / 5.0
                if interview_scores
                else 0
            )

            # 3. Recency score
            if candidate.last_contacted_at:
                days_since = (
                    datetime.utcnow().date() - candidate.last_contacted_at
                ).days
                recency = max(0, 1.0 - (days_since / 180))
            else:
                recency = 0.5

            # 4. Experience match
            if candidate.total_experience_years and requirement.experience_min:
                if (
                    requirement.experience_min
                    <= candidate.total_experience_years
                    <= (requirement.experience_max or 999)
                ):
                    experience_match = 1.0
                else:
                    experience_match = 0.5
            else:
                experience_match = 0.5

            # Final scores
            rediscovery_score = (
                skill_match * 35
                + interview_score * 40
                + recency * 15
                + experience_match * 10
            )

            result = {
                "candidate_id": candidate_id,
                "requirement_id": requirement_id,
                "rediscovery_score": min(100, rediscovery_score),
                "skill_match_score": min(100, skill_match * 100),
                "interview_history_score": min(100, interview_score * 100),
                "recency_score": min(100, recency * 100),
                "engagement_score": min(100, (candidate.engagement_score or 0) * 20),
                "score_breakdown": {
                    "skill_weight": 0.35,
                    "interview_weight": 0.40,
                    "recency_weight": 0.15,
                    "engagement_weight": 0.10,
                },
            }

            return result

        except Exception as e:
            logger.error(f"Error calculating rediscovery score: {str(e)}")
            raise

    async def get_rediscovery_analytics(
        self, db: AsyncSession
    ) -> Dict[str, Any]:
        """Get rediscovery analytics and pool statistics.

        Args:
            db: Database session

        Returns:
            Analytics dictionary
        """
        try:
            # Total talent pool
            pool_result = await db.execute(
                select(func.count(Candidate.id)).where(
                    Candidate.status == CandidateStatus.TALENT_POOL
                )
            )
            pool_size = pool_result.scalar() or 0

            # High potential candidates (3+ avg score and 3+ interviews)
            high_potential_result = await db.execute(
                select(func.count(Candidate.id)).where(
                    and_(
                        Candidate.status == CandidateStatus.TALENT_POOL,
                        Candidate.engagement_score >= 3.0,
                    )
                )
            )
            high_potential = high_potential_result.scalar() or 0

            # Average time in pool
            candidates_result = await db.execute(
                select(Candidate).where(
                    Candidate.status == CandidateStatus.TALENT_POOL
                )
            )
            candidates = candidates_result.scalars().all()

            time_in_pool = []
            for cand in candidates:
                if cand.last_contacted_at:
                    days = (datetime.utcnow().date() - cand.last_contacted_at).days
                    time_in_pool.append(days)

            avg_time_in_pool = (
                sum(time_in_pool) / len(time_in_pool) if time_in_pool else 0
            )

            # Re-engagement success rate (contacted and resubmitted)
            rediscovery_result = await db.execute(
                select(func.count(CandidateRediscovery.id)).where(
                    CandidateRediscovery.status.in_(["resubmitted"])
                )
            )
            successful = rediscovery_result.scalar() or 0

            total_rediscoveries_result = await db.execute(
                select(func.count(CandidateRediscovery.id))
            )
            total_rediscoveries = total_rediscoveries_result.scalar() or 1

            success_rate = successful / total_rediscoveries

            # Top skills in pool
            all_skills = {}
            for cand in candidates:
                for skill in cand.skills or []:
                    all_skills[skill] = all_skills.get(skill, 0) + 1

            top_skills = sorted(
                all_skills.items(), key=lambda x: x[1], reverse=True
            )[:10]

            # Contacted this period
            week_ago = datetime.utcnow().date() - timedelta(days=7)
            contacted_result = await db.execute(
                select(func.count(CandidateRediscovery.id)).where(
                    and_(
                        CandidateRediscovery.contacted_at >= week_ago,
                        CandidateRediscovery.status.in_(["contacted", "responded"]),
                    )
                )
            )
            contacted_this_week = contacted_result.scalar() or 0

            analytics = {
                "total_talent_pool_size": pool_size,
                "high_potential_candidates": high_potential,
                "avg_time_in_talent_pool_days": avg_time_in_pool,
                "re_engagement_success_rate": success_rate,
                "avg_rediscovery_score": 0,  # Would need more data
                "candidates_by_status": {
                    "identified": 0,
                    "contacted": 0,
                    "responded": 0,
                },
                "top_skills_in_pool": [skill for skill, _ in top_skills],
                "candidates_contacted_this_period": contacted_this_week,
            }

            return analytics

        except Exception as e:
            logger.error(f"Error getting rediscovery analytics: {str(e)}")
            return {}

    async def auto_rediscover(
        self, db: AsyncSession, requirement_id: int
    ) -> List[CandidateRediscovery]:
        """Auto-trigger rediscovery when new requirement is created.

        Args:
            db: Database session
            requirement_id: New requirement ID

        Returns:
            List of created CandidateRediscovery records
        """
        try:
            # Find silver medalists for this requirement
            candidates = await self.find_silver_medalists(
                db, requirement_id, limit=20
            )

            rediscoveries = []

            for cand_data in candidates:
                # Create rediscovery record
                rediscovery = CandidateRediscovery(
                    candidate_id=cand_data["candidate_id"],
                    requirement_id=requirement_id,
                    rediscovery_score=cand_data["rediscovery_score"],
                    skill_match_score=cand_data["skill_match_score"],
                    interview_history_score=cand_data["interview_history_score"],
                    recency_score=cand_data["recency_score"],
                    engagement_score=cand_data["engagement_score"],
                    score_breakdown=cand_data,
                    status="identified",
                )

                db.add(rediscovery)
                rediscoveries.append(rediscovery)

            await db.commit()
            logger.info(
                f"Auto-discovered {len(rediscoveries)} candidates for requirement {requirement_id}"
            )

            return rediscoveries

        except Exception as e:
            await db.rollback()
            logger.error(f"Error auto-discovering candidates: {str(e)}")
            return []

    async def on_start(self) -> None:
        """Called when agent starts."""
        logger.info("Candidate Rediscovery Agent started")

    async def on_stop(self) -> None:
        """Called when agent stops."""
        logger.info("Candidate Rediscovery Agent stopped")
