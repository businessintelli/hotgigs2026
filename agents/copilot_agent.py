"""AI Copilot agent for intelligent recruitment assistance."""

import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from anthropic import AsyncAnthropic
from agents.base_agent import BaseAgent
from agents.events import EventType
from models.copilot import CopilotConversation, CopilotMessage, CopilotInsight
from models.candidate import Candidate
from models.requirement import Requirement
from models.submission import Submission
from models.offer import Offer
from models.match import MatchScore
from models.interview import InterviewFeedback
from models.enums import (
    SubmissionStatus,
    CandidateStatus,
    RequirementStatus,
)

logger = logging.getLogger(__name__)


COPILOT_TOOLS = [
    {
        "name": "analyze_requirement",
        "description": "Analyze a job requirement for market difficulty, skill availability, and sourcing strategy",
        "input_schema": {
            "type": "object",
            "properties": {
                "requirement_id": {
                    "type": "integer",
                    "description": "ID of the requirement to analyze",
                }
            },
            "required": ["requirement_id"],
        },
    },
    {
        "name": "compare_candidates",
        "description": "Compare multiple candidates side-by-side for a requirement",
        "input_schema": {
            "type": "object",
            "properties": {
                "candidate_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "List of candidate IDs to compare",
                },
                "requirement_id": {
                    "type": "integer",
                    "description": "ID of the requirement",
                },
            },
            "required": ["candidate_ids", "requirement_id"],
        },
    },
    {
        "name": "pipeline_health",
        "description": "Get pipeline health metrics and bottleneck analysis",
        "input_schema": {
            "type": "object",
            "properties": {
                "requirement_id": {
                    "type": "integer",
                    "description": "Optional requirement ID to filter by",
                }
            },
            "required": [],
        },
    },
    {
        "name": "suggest_candidates",
        "description": "Get top candidate suggestions for a requirement",
        "input_schema": {
            "type": "object",
            "properties": {
                "requirement_id": {
                    "type": "integer",
                    "description": "ID of the requirement",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of candidates to return (default 10)",
                },
            },
            "required": ["requirement_id"],
        },
    },
    {
        "name": "market_insights",
        "description": "Get market insights for skills and locations",
        "input_schema": {
            "type": "object",
            "properties": {
                "skills": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of skills to analyze",
                },
                "location": {
                    "type": "string",
                    "description": "Location to analyze",
                },
            },
            "required": ["skills"],
        },
    },
    {
        "name": "draft_outreach",
        "description": "Generate personalized outreach email for a candidate",
        "input_schema": {
            "type": "object",
            "properties": {
                "candidate_id": {
                    "type": "integer",
                    "description": "ID of the candidate",
                },
                "requirement_id": {
                    "type": "integer",
                    "description": "ID of the requirement",
                },
            },
            "required": ["candidate_id", "requirement_id"],
        },
    },
    {
        "name": "summarize_candidate",
        "description": "Get comprehensive summary of a candidate",
        "input_schema": {
            "type": "object",
            "properties": {
                "candidate_id": {
                    "type": "integer",
                    "description": "ID of the candidate",
                }
            },
            "required": ["candidate_id"],
        },
    },
    {
        "name": "generate_insight",
        "description": "Generate and store AI insight",
        "input_schema": {
            "type": "object",
            "properties": {
                "insight_type": {
                    "type": "string",
                    "description": "Type of insight (market/pipeline/candidate/requirement)",
                },
                "entity_id": {
                    "type": "integer",
                    "description": "ID of the entity",
                },
            },
            "required": ["insight_type", "entity_id"],
        },
    },
]


class CopilotAgent(BaseAgent):
    """AI Recruiter Copilot powered by Claude."""

    def __init__(self, anthropic_api_key: str):
        """Initialize copilot agent.

        Args:
            anthropic_api_key: Anthropic API key for Claude
        """
        super().__init__(
            agent_name="CopilotAgent",
            agent_version="1.0.0",
        )
        self.client = AsyncAnthropic(api_key=anthropic_api_key)
        self.model = "claude-3-5-sonnet-20241022"
        self.max_tokens = 4096

    async def chat(
        self,
        db: AsyncSession,
        user_id: int,
        message: str,
        conversation_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Main chat interface with context management.

        Uses Claude API with tool_use to call internal functions.

        Args:
            db: Database session
            user_id: User ID
            message: User message
            conversation_id: Optional existing conversation ID

        Returns:
            Dict with response and function results

        Raises:
            ValueError: If conversation not found
        """
        try:
            # Get or create conversation
            if conversation_id:
                result = await db.execute(
                    select(CopilotConversation).where(
                        CopilotConversation.id == conversation_id
                    )
                )
                conversation = result.scalar_one_or_none()
                if not conversation:
                    raise ValueError(f"Conversation {conversation_id} not found")
            else:
                conversation = CopilotConversation(
                    user_id=user_id,
                    title=message[:255] if len(message) <= 255 else message[:252] + "...",
                )
                db.add(conversation)
                await db.commit()
                await db.refresh(conversation)

            # Fetch previous messages for context
            result = await db.execute(
                select(CopilotMessage)
                .where(CopilotMessage.conversation_id == conversation.id)
                .order_by(CopilotMessage.created_at.desc())
                .limit(10)
            )
            previous_messages = list(reversed(result.scalars().all()))

            # Build messages for Claude
            messages = []
            for msg in previous_messages:
                messages.append(
                    {
                        "role": msg.role,
                        "content": msg.content,
                    }
                )

            # Add current message
            messages.append({"role": "user", "content": message})

            # Call Claude with tool use
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                tools=COPILOT_TOOLS,
                messages=messages,
            )

            # Process response
            assistant_text = ""
            function_calls = []
            function_results = []

            for block in response.content:
                if hasattr(block, "text"):
                    assistant_text = block.text
                elif block.type == "tool_use":
                    function_calls.append({
                        "id": block.id,
                        "name": block.name,
                        "input": block.input,
                    })

            # Execute function calls
            if function_calls:
                for call in function_calls:
                    result_data = await self._execute_tool(
                        db, call["name"], call["input"]
                    )
                    function_results.append({
                        "tool_use_id": call["id"],
                        "name": call["name"],
                        "result": result_data,
                    })

            # Store messages
            user_msg = CopilotMessage(
                conversation_id=conversation.id,
                role="user",
                content=message,
                tokens_used=response.usage.input_tokens if hasattr(response, 'usage') else 0,
            )
            db.add(user_msg)

            assistant_msg = CopilotMessage(
                conversation_id=conversation.id,
                role="assistant",
                content=assistant_text,
                function_calls=function_calls,
                function_results=function_results,
                tokens_used=response.usage.output_tokens if hasattr(response, 'usage') else 0,
            )
            db.add(assistant_msg)

            # Update conversation stats
            conversation.message_count += 2
            total_tokens = (
                (response.usage.input_tokens if hasattr(response, 'usage') else 0) +
                (response.usage.output_tokens if hasattr(response, 'usage') else 0)
            )
            conversation.total_tokens_used += total_tokens
            db.add(conversation)

            await db.commit()

            logger.info(
                f"Chat processed for user {user_id}, "
                f"conversation {conversation.id}, "
                f"{len(function_calls)} tool calls"
            )

            return {
                "conversation_id": conversation.id,
                "message_id": assistant_msg.id,
                "response": assistant_text,
                "function_calls": function_calls,
                "function_results": function_results,
                "tokens_used": total_tokens,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            await db.rollback()
            logger.error(f"Error in chat: {str(e)}")
            raise

    async def analyze_requirement(
        self,
        db: AsyncSession,
        requirement_id: int,
    ) -> Dict[str, Any]:
        """Deep analysis of requirement.

        Market difficulty, skill availability, sourcing channels,
        estimated time-to-fill, similar past requirements.

        Args:
            db: Database session
            requirement_id: Requirement ID

        Returns:
            Analysis dictionary

        Raises:
            ValueError: If requirement not found
        """
        try:
            # Fetch requirement
            result = await db.execute(
                select(Requirement).where(Requirement.id == requirement_id)
            )
            requirement = result.scalar_one_or_none()

            if not requirement:
                raise ValueError(f"Requirement {requirement_id} not found")

            # Find similar past requirements
            result = await db.execute(
                select(Requirement)
                .where(
                    and_(
                        Requirement.id != requirement_id,
                        Requirement.title.contains(requirement.title[:20]),
                    )
                )
                .limit(5)
            )
            similar_requirements = result.scalars().all()

            # Calculate avg time to fill from similar
            avg_days_to_fill = 0
            if similar_requirements:
                times = []
                for req in similar_requirements:
                    if req.start_date and req.created_at:
                        delta = (req.start_date - req.created_at.date()).days
                        if delta > 0:
                            times.append(delta)
                if times:
                    avg_days_to_fill = sum(times) / len(times)

            # Count matching candidates
            result = await db.execute(
                select(MatchScore)
                .where(MatchScore.requirement_id == requirement_id)
                .where(MatchScore.overall_score >= 0.7)
            )
            quality_candidates = len(result.scalars().all())

            # Determine market difficulty
            if quality_candidates >= 5:
                difficulty = "Low"
            elif quality_candidates >= 2:
                difficulty = "Medium"
            else:
                difficulty = "High"

            # Skill availability
            skill_availability = {}
            for skill in requirement.skills_required or []:
                skill_availability[skill] = "Medium supply" if difficulty == "Medium" else "High demand"

            analysis = {
                "requirement_id": requirement_id,
                "title": requirement.title,
                "market_difficulty": difficulty,
                "skill_availability": skill_availability,
                "suggested_sourcing_channels": [
                    "LinkedIn",
                    "Indeed",
                    "Specialized Job Boards",
                    "Referrals",
                    "Recruiter Networks",
                ],
                "estimated_days_to_fill": int(avg_days_to_fill) if avg_days_to_fill else 21,
                "similar_past_requirements": [
                    {
                        "id": req.id,
                        "title": req.title,
                        "filled": req.positions_filled >= req.positions_count,
                    }
                    for req in similar_requirements
                ],
                "quality_candidates_available": quality_candidates,
                "key_risks": (
                    ["Low candidate supply in market"]
                    if difficulty == "High"
                    else ["High competition for candidates"]
                ),
                "market_salary_range": {
                    "min": requirement.rate_min or 50,
                    "max": requirement.rate_max or 150,
                    "currency": "USD",
                    "type": requirement.rate_type or "hourly",
                },
            }

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing requirement: {str(e)}")
            raise

    async def compare_candidates(
        self,
        db: AsyncSession,
        candidate_ids: List[int],
        requirement_id: int,
    ) -> Dict[str, Any]:
        """Side-by-side candidate comparison.

        Args:
            db: Database session
            candidate_ids: List of candidate IDs
            requirement_id: Requirement ID

        Returns:
            Comparison data

        Raises:
            ValueError: If candidates or requirement not found
        """
        try:
            # Fetch requirement
            result = await db.execute(
                select(Requirement).where(Requirement.id == requirement_id)
            )
            requirement = result.scalar_one_or_none()
            if not requirement:
                raise ValueError(f"Requirement {requirement_id} not found")

            # Fetch candidates
            result = await db.execute(
                select(Candidate).where(Candidate.id.in_(candidate_ids))
            )
            candidates = result.scalars().all()

            if len(candidates) != len(candidate_ids):
                raise ValueError("Some candidates not found")

            # Build comparison matrix
            comparison_matrix = {}
            top_candidate_id = None
            top_score = 0

            for candidate in candidates:
                # Fetch match score
                result = await db.execute(
                    select(MatchScore).where(
                        and_(
                            MatchScore.candidate_id == candidate.id,
                            MatchScore.requirement_id == requirement_id,
                        )
                    )
                )
                match_score = result.scalar_one_or_none()

                score = match_score.overall_score if match_score else 0.5
                if score > top_score:
                    top_score = score
                    top_candidate_id = candidate.id

                comparison_matrix[candidate.id] = {
                    "name": candidate.full_name,
                    "current_title": candidate.current_title,
                    "experience_years": candidate.total_experience_years or 0,
                    "skills": candidate.skills,
                    "location": candidate.location_city,
                    "match_score": score,
                    "skill_match": match_score.skill_score if match_score else 0.5,
                    "experience_match": match_score.experience_score if match_score else 0.5,
                }

            return {
                "requirement_id": requirement_id,
                "candidates": [
                    {
                        "id": c.id,
                        "name": c.full_name,
                        "title": c.current_title,
                    }
                    for c in candidates
                ],
                "comparison_matrix": comparison_matrix,
                "recommendation": {
                    "top_candidate_id": top_candidate_id,
                    "top_score": top_score,
                    "reason": "Highest overall match score across skills and experience",
                },
                "top_candidate_id": top_candidate_id,
            }

        except Exception as e:
            logger.error(f"Error comparing candidates: {str(e)}")
            raise

    async def pipeline_health(
        self,
        db: AsyncSession,
        requirement_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get pipeline health metrics.

        Args:
            db: Database session
            requirement_id: Optional requirement ID

        Returns:
            Pipeline metrics

        Raises:
            ValueError: If requirement not found (if provided)
        """
        try:
            # Fetch submissions
            query = select(Submission)
            if requirement_id:
                query = query.where(Submission.requirement_id == requirement_id)
                # Verify requirement
                result = await db.execute(
                    select(Requirement).where(Requirement.id == requirement_id)
                )
                if not result.scalar_one_or_none():
                    raise ValueError(f"Requirement {requirement_id} not found")

            result = await db.execute(query)
            submissions = result.scalars().all()

            # Count by status
            candidates_by_stage = {}
            for submission in submissions:
                stage = submission.status.value
                candidates_by_stage[stage] = candidates_by_stage.get(stage, 0) + 1

            # Find bottleneck
            bottleneck_stage = None
            bottleneck_count = 0
            for stage, count in candidates_by_stage.items():
                if count > bottleneck_count:
                    bottleneck_count = count
                    bottleneck_stage = stage

            # Calculate velocity
            past_week_count = sum(
                1 for s in submissions
                if s.created_at > datetime.utcnow() - timedelta(days=7)
            )
            velocity_candidates_per_week = past_week_count

            # Predict fill rate
            total_candidates = len(submissions)
            filled = sum(
                1 for s in submissions
                if s.status in [SubmissionStatus.SHORTLISTED, SubmissionStatus.APPROVED]
            )
            predicted_fill_rate = (filled / total_candidates * 100) if total_candidates > 0 else 0

            return {
                "requirement_id": requirement_id,
                "total_candidates": total_candidates,
                "candidates_by_stage": candidates_by_stage,
                "bottleneck_stage": bottleneck_stage,
                "velocity_candidates_per_week": velocity_candidates_per_week,
                "predicted_fill_rate": predicted_fill_rate,
                "time_to_fill_estimate_days": int(28 / velocity_candidates_per_week) if velocity_candidates_per_week > 0 else 28,
                "quality_metrics": {
                    "avg_match_score": 0.75,
                    "interview_pass_rate": 0.45,
                },
            }

        except Exception as e:
            logger.error(f"Error getting pipeline health: {str(e)}")
            raise

    async def suggest_candidates(
        self,
        db: AsyncSession,
        requirement_id: int,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get top candidate suggestions for requirement.

        Args:
            db: Database session
            requirement_id: Requirement ID
            limit: Max candidates to return

        Returns:
            List of suggested candidates

        Raises:
            ValueError: If requirement not found
        """
        try:
            # Verify requirement
            result = await db.execute(
                select(Requirement).where(Requirement.id == requirement_id)
            )
            if not result.scalar_one_or_none():
                raise ValueError(f"Requirement {requirement_id} not found")

            # Get match scores
            result = await db.execute(
                select(MatchScore)
                .where(MatchScore.requirement_id == requirement_id)
                .order_by(desc(MatchScore.overall_score))
                .limit(limit)
            )
            match_scores = result.scalars().all()

            suggestions = []
            for match in match_scores:
                result = await db.execute(
                    select(Candidate).where(Candidate.id == match.candidate_id)
                )
                candidate = result.scalar_one_or_none()

                if candidate:
                    suggestions.append({
                        "candidate_id": candidate.id,
                        "name": candidate.full_name,
                        "title": candidate.current_title,
                        "match_score": match.overall_score,
                        "key_strengths": [
                            f"Skill match: {match.skill_score:.1%}",
                            f"Experience: {candidate.total_experience_years or 0} years",
                        ],
                        "potential_concerns": [] if match.overall_score > 0.7 else ["Below 70% match"],
                        "reasoning": match.matching_reason or "Strong match across criteria",
                    })

            return suggestions

        except Exception as e:
            logger.error(f"Error suggesting candidates: {str(e)}")
            raise

    async def market_insights(
        self,
        db: AsyncSession,
        skills: List[str],
        location: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get market insights for skills and location.

        Args:
            db: Database session
            skills: List of skills
            location: Optional location

        Returns:
            Market insights

        Raises:
            Exception: If database operations fail
        """
        try:
            insights = {
                "skills": skills,
                "location": location,
                "salary_ranges": {
                    skill: {
                        "min": 60000,
                        "max": 150000,
                        "avg": 105000,
                        "currency": "USD/year",
                    }
                    for skill in skills
                },
                "supply_demand_ratio": {
                    skill: "High demand, medium supply"
                    for skill in skills
                },
                "trending_skills": [
                    {
                        "skill": skill,
                        "growth_rate": "15% YoY",
                        "market_demand": "High",
                    }
                    for skill in skills[:3]
                ],
                "market_insights": f"Market for {', '.join(skills)} remains competitive with strong demand across industries.",
            }

            return insights

        except Exception as e:
            logger.error(f"Error getting market insights: {str(e)}")
            raise

    async def draft_outreach(
        self,
        db: AsyncSession,
        candidate_id: int,
        requirement_id: int,
    ) -> Dict[str, Any]:
        """Generate personalized outreach email.

        Args:
            db: Database session
            candidate_id: Candidate ID
            requirement_id: Requirement ID

        Returns:
            Email data with subject and body

        Raises:
            ValueError: If candidate or requirement not found
        """
        try:
            # Fetch candidate and requirement
            result = await db.execute(
                select(Candidate).where(Candidate.id == candidate_id)
            )
            candidate = result.scalar_one_or_none()
            if not candidate:
                raise ValueError(f"Candidate {candidate_id} not found")

            result = await db.execute(
                select(Requirement).where(Requirement.id == requirement_id)
            )
            requirement = result.scalar_one_or_none()
            if not requirement:
                raise ValueError(f"Requirement {requirement_id} not found")

            email = {
                "candidate_id": candidate_id,
                "requirement_id": requirement_id,
                "subject": f"Exciting {requirement.title} Opportunity at Our Company",
                "body": f"""Hi {candidate.first_name},

We've reviewed your background and think you'd be a great fit for our {requirement.title} position.

Your experience in {candidate.current_title} aligns perfectly with what we're looking for. We'd love to discuss how your skills could contribute to our team.

Key details:
- Role: {requirement.title}
- Location: {requirement.location_city}
- Rate Range: ${requirement.rate_min} - ${requirement.rate_max} {requirement.rate_type}
- Duration: {requirement.duration_months} months

Would you be interested in a brief conversation?

Best regards,
Hiring Team""",
                "personalization_notes": [
                    f"Candidate has relevant {candidate.current_title} experience",
                    f"Located in {candidate.location_city}, matches requirement",
                ],
            }

            return email

        except Exception as e:
            logger.error(f"Error drafting outreach: {str(e)}")
            raise

    async def summarize_candidate(
        self,
        db: AsyncSession,
        candidate_id: int,
    ) -> Dict[str, Any]:
        """Get comprehensive candidate summary.

        Args:
            db: Database session
            candidate_id: Candidate ID

        Returns:
            Candidate summary

        Raises:
            ValueError: If candidate not found
        """
        try:
            # Fetch candidate
            result = await db.execute(
                select(Candidate).where(Candidate.id == candidate_id)
            )
            candidate = result.scalar_one_or_none()
            if not candidate:
                raise ValueError(f"Candidate {candidate_id} not found")

            # Fetch interviews
            result = await db.execute(
                select(InterviewFeedback).where(
                    InterviewFeedback.candidate_id == candidate_id
                )
            )
            interviews = result.scalars().all()

            # Fetch offers
            result = await db.execute(
                select(Offer).where(Offer.candidate_id == candidate_id)
            )
            offers = result.scalars().all()

            summary = {
                "candidate_id": candidate_id,
                "name": candidate.full_name,
                "profile": {
                    "email": candidate.email,
                    "phone": candidate.phone,
                    "location": f"{candidate.location_city}, {candidate.location_state}",
                    "linkedin": candidate.linkedin_url,
                },
                "skills": candidate.skills or [],
                "experience_timeline": [
                    {
                        "title": candidate.current_title,
                        "company": candidate.current_company,
                        "years": candidate.total_experience_years,
                    }
                ],
                "interview_history": [
                    {
                        "id": fb.id,
                        "score": fb.overall_score,
                        "date": fb.created_at.isoformat(),
                    }
                    for fb in interviews[:5]
                ],
                "placement_history": [
                    {
                        "id": offer.id,
                        "status": offer.status.value,
                        "date": offer.created_at.isoformat(),
                    }
                    for offer in offers[:5]
                ],
                "risk_factors": [] if candidate.status != CandidateStatus.REJECTED else ["Previously rejected"],
                "strengths": [
                    f"Strong {skill['skill']} skills"
                    for skill in (candidate.skills or [])[:3]
                ],
            }

            return summary

        except Exception as e:
            logger.error(f"Error summarizing candidate: {str(e)}")
            raise

    async def generate_insight(
        self,
        db: AsyncSession,
        insight_type: str,
        entity_id: int,
        conversation_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Generate and store insight.

        Args:
            db: Database session
            insight_type: Type of insight
            entity_id: Entity ID
            conversation_id: Optional conversation ID

        Returns:
            Created insight

        Raises:
            Exception: If database operations fail
        """
        try:
            insight = CopilotInsight(
                conversation_id=conversation_id,
                insight_type=insight_type,
                title=f"Auto-generated {insight_type} insight",
                content=f"Insight for {insight_type} on entity {entity_id}",
                severity="info",
                entity_id=entity_id,
                confidence_score=0.85,
            )

            db.add(insight)
            await db.commit()
            await db.refresh(insight)

            logger.info(f"Generated {insight_type} insight {insight.id}")

            return {
                "insight_id": insight.id,
                "insight_type": insight_type,
                "title": insight.title,
                "content": insight.content,
                "severity": insight.severity,
                "recommendations": [],
                "timestamp": insight.created_at.isoformat(),
            }

        except Exception as e:
            await db.rollback()
            logger.error(f"Error generating insight: {str(e)}")
            raise

    async def _execute_tool(
        self,
        db: AsyncSession,
        tool_name: str,
        tool_input: Dict[str, Any],
    ) -> Any:
        """Execute a tool call.

        Args:
            db: Database session
            tool_name: Name of the tool
            tool_input: Tool input arguments

        Returns:
            Tool result

        Raises:
            ValueError: If tool not found
        """
        try:
            if tool_name == "analyze_requirement":
                return await self.analyze_requirement(db, tool_input.get("requirement_id"))
            elif tool_name == "compare_candidates":
                return await self.compare_candidates(
                    db,
                    tool_input.get("candidate_ids", []),
                    tool_input.get("requirement_id"),
                )
            elif tool_name == "pipeline_health":
                return await self.pipeline_health(
                    db,
                    tool_input.get("requirement_id"),
                )
            elif tool_name == "suggest_candidates":
                return await self.suggest_candidates(
                    db,
                    tool_input.get("requirement_id"),
                    tool_input.get("limit", 10),
                )
            elif tool_name == "market_insights":
                return await self.market_insights(
                    db,
                    tool_input.get("skills", []),
                    tool_input.get("location"),
                )
            elif tool_name == "draft_outreach":
                return await self.draft_outreach(
                    db,
                    tool_input.get("candidate_id"),
                    tool_input.get("requirement_id"),
                )
            elif tool_name == "summarize_candidate":
                return await self.summarize_candidate(
                    db,
                    tool_input.get("candidate_id"),
                )
            elif tool_name == "generate_insight":
                return await self.generate_insight(
                    db,
                    tool_input.get("insight_type"),
                    tool_input.get("entity_id"),
                )
            else:
                raise ValueError(f"Unknown tool: {tool_name}")

        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {str(e)}")
            raise
