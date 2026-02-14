"""Job Post Intelligence Agent for AI-powered job posting generation."""

import logging
import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from anthropic import AsyncAnthropic
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from agents.base_agent import BaseAgent
from models.job_post import JobPost, JobPostAnalytics
from models.requirement import Requirement

logger = logging.getLogger(__name__)


class JobPostAgent(BaseAgent):
    """Agent for generating and optimizing AI-powered job postings."""

    def __init__(self, anthropic_api_key: Optional[str] = None):
        """Initialize job post agent.

        Args:
            anthropic_api_key: Anthropic API key for LLM calls
        """
        super().__init__(agent_name="JobPostAgent", agent_version="1.0.0")
        self.anthropic_client = (
            AsyncAnthropic(api_key=anthropic_api_key) if anthropic_api_key else None
        )

    async def generate_job_post(
        self,
        db: AsyncSession,
        requirement_id: int,
        style: str = "professional",
    ) -> Dict[str, Any]:
        """Generate full job posting from requirement data.

        Args:
            db: Database session
            requirement_id: Requirement ID
            style: Writing style (professional, casual, technical)

        Returns:
            Generated job post data
        """
        try:
            requirement = await db.get(Requirement, requirement_id)
            if not requirement:
                raise ValueError(f"Requirement {requirement_id} not found")

            if not self.anthropic_client:
                raise ValueError("Anthropic API key required")

            # Prepare requirement context
            context = f"""Generate a compelling job posting with the following details:

Position: {requirement.title}
Description: {requirement.description or 'Not provided'}
Required Skills: {', '.join(requirement.skills_required or [])}
Preferred Skills: {', '.join(requirement.skills_preferred or [])}
Experience: {requirement.experience_min or 'N/A'} - {requirement.experience_max or 'N/A'} years
Education: {requirement.education_level or 'Not specified'}
Location: {requirement.location_city or 'Remote'}, {requirement.location_country or ''}
Work Mode: {requirement.work_mode or 'Not specified'}
Employment Type: {requirement.employment_type or 'Not specified'}
Salary Range: ${requirement.rate_min or 'N/A'} - ${requirement.rate_max or 'N/A'} {requirement.rate_type or 'per annum'}
Duration: {requirement.duration_months or 'Permanent'} months

Generate a {style} job posting in JSON format with these sections:
{{
    "title": "Optimized job title",
    "summary": "2-3 sentence overview",
    "responsibilities": ["array", "of", "key", "duties"],
    "qualifications_required": ["array", "of", "must-haves"],
    "qualifications_preferred": ["array", "of", "nice-to-haves"],
    "benefits": ["array", "of", "benefits"],
    "company_description": "Brief company overview"
}}

Make it engaging, clear, and optimized for attracting top talent."""

            message = await self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[{"role": "user", "content": context}],
            )

            response_text = message.content[0].text

            # Extract JSON from response
            start_idx = response_text.find("{")
            end_idx = response_text.rfind("}") + 1
            if start_idx >= 0 and end_idx > start_idx:
                job_data = json.loads(response_text[start_idx:end_idx])
            else:
                raise ValueError("Failed to parse LLM response")

            # Build full content
            content = f"""# {job_data.get('title', requirement.title)}

## Overview
{job_data.get('summary', '')}

## Responsibilities
{chr(10).join([f'- {r}' for r in job_data.get('responsibilities', [])])}

## Required Qualifications
{chr(10).join([f'- {q}' for q in job_data.get('qualifications_required', [])])}

## Preferred Qualifications
{chr(10).join([f'- {q}' for q in job_data.get('qualifications_preferred', [])])}

## What We Offer
{chr(10).join([f'- {b}' for b in job_data.get('benefits', [])])}

## About Our Company
{job_data.get('company_description', '')}"""

            post_dict = {
                "requirement_id": requirement_id,
                "title": job_data.get("title", requirement.title),
                "summary": job_data.get("summary", ""),
                "content": content,
                "responsibilities": job_data.get("responsibilities", []),
                "qualifications_required": job_data.get("qualifications_required", []),
                "qualifications_preferred": job_data.get("qualifications_preferred", []),
                "benefits": job_data.get("benefits", []),
                "salary_range_min": requirement.rate_min,
                "salary_range_max": requirement.rate_max,
                "status": "draft",
            }

            logger.info(f"Generated job post for requirement {requirement_id}")
            return post_dict

        except Exception as e:
            logger.error(f"Error generating job post: {str(e)}")
            raise

    async def optimize_for_seo(
        self,
        content: str,
        target_keywords: List[str],
    ) -> Dict[str, Any]:
        """Optimize job post for SEO.

        Args:
            content: Job post content
            target_keywords: Keywords to optimize for

        Returns:
            Optimization result with score and suggestions
        """
        try:
            content_lower = content.lower()

            # Calculate keyword density
            keyword_density = {}
            for keyword in target_keywords:
                keyword_lower = keyword.lower()
                count = content_lower.count(keyword_lower)
                word_count = len(content.split())
                density = (count / word_count) * 100 if word_count > 0 else 0
                keyword_density[keyword] = density

            # Title optimization
            lines = content.split("\n")
            title = lines[0].replace("# ", "") if lines else ""

            title_suggestions = []
            if len(title) < 30:
                title_suggestions.append("Title is too short; expand to 50-60 characters")
            if len(title) > 65:
                title_suggestions.append(
                    "Title is too long; shorten to 65 characters or less"
                )
            if not any(kw.lower() in title.lower() for kw in target_keywords):
                title_suggestions.append(
                    f"Include primary keyword in title (e.g., {target_keywords[0]})"
                )

            # SEO score calculation
            seo_score = 50  # Base score
            seo_score += min(20, len([k for k, d in keyword_density.items() if 1 <= d <= 5])) * 2
            seo_score -= len(title_suggestions) * 10
            seo_score = min(100, max(0, seo_score))

            # Structured data suggestions
            structured_suggestions = [
                "Add schema.org JobPosting markup",
                "Include company information in schema",
                "Add salary range in structured data",
                "Include location data in schema",
            ]

            result = {
                "seo_score": seo_score,
                "keyword_density": keyword_density,
                "title_suggestions": title_suggestions,
                "structured_data_suggestions": structured_suggestions,
                "improvements": [
                    f"Optimize keyword '{kw}' (current density: {d:.2f}%)"
                    for kw, d in keyword_density.items()
                    if d < 1 or d > 5
                ],
            }

            return result

        except Exception as e:
            logger.error(f"Error optimizing for SEO: {str(e)}")
            raise

    async def check_inclusive_language(
        self, content: str
    ) -> Dict[str, Any]:
        """Check for biased or exclusive language patterns.

        Args:
            content: Job post content

        Returns:
            Inclusivity check result with issues and suggestions
        """
        try:
            # Gendered language patterns
            gendered_words = {
                "aggressive": "assertive",
                "communicative": "clear",
                "ambitious": "driven",
                "bossy": "leader",
                "emotional": "passionate",
                "gossip": "discuss",
                "manipulative": "persuasive",
                "moody": "thoughtful",
                "whiny": "expressive",
            }

            # Age bias indicators
            age_bias_words = [
                "digital native",
                "millennial",
                "gen x",
                "gen z",
                "young",
                "energetic",
                "fast-paced",
                "cutting edge",
                "hip",
                "trendy",
            ]

            # Ability bias indicators
            ability_bias_words = [
                "must be able to work long hours",
                "high energy",
                "fast talker",
                "hearing required",
                "sight required",
                "able-bodied",
            ]

            content_lower = content.lower()
            found_gendered = []
            found_age_bias = []
            found_ability_bias = []
            issues = []

            for word, replacement in gendered_words.items():
                if word in content_lower:
                    found_gendered.append(word)
                    issues.append({
                        "text": word,
                        "issue_type": "gendered_language",
                        "severity": "medium",
                        "suggestion": f"Use '{replacement}' instead",
                    })

            for word in age_bias_words:
                if word in content_lower:
                    found_age_bias.append(word)
                    issues.append({
                        "text": word,
                        "issue_type": "age_bias",
                        "severity": "medium",
                        "suggestion": f"Remove or rephrase '{word}'",
                    })

            for word in ability_bias_words:
                if word in content_lower:
                    found_ability_bias.append(word)
                    issues.append({
                        "text": word,
                        "issue_type": "ability_bias",
                        "severity": "high",
                        "suggestion": f"Remove or rephrase '{word}'",
                    })

            # Inclusivity score
            inclusivity_score = 100
            inclusivity_score -= len(found_gendered) * 10
            inclusivity_score -= len(found_age_bias) * 15
            inclusivity_score -= len(found_ability_bias) * 20
            inclusivity_score = max(0, min(100, inclusivity_score))

            recommendations = [
                "Use gender-neutral language throughout",
                "Avoid age-related descriptors",
                "Focus on skills rather than physical ability",
                "Include statement about commitment to diversity",
                "Mention reasonable accommodations availability",
            ]

            result = {
                "inclusivity_score": inclusivity_score,
                "issues": issues,
                "gendered_words": found_gendered,
                "age_bias_indicators": found_age_bias,
                "ability_bias_indicators": found_ability_bias,
                "recommendations": recommendations,
            }

            return result

        except Exception as e:
            logger.error(f"Error checking inclusive language: {str(e)}")
            raise

    async def generate_from_text(
        self, freeform_text: str
    ) -> Dict[str, Any]:
        """Parse freeform requirement text into structured job post.

        Args:
            freeform_text: Unstructured requirement description

        Returns:
            Parsed job post data
        """
        try:
            if not self.anthropic_client:
                raise ValueError("Anthropic API key required")

            prompt = f"""Parse the following job requirement text and extract structured information.
Return JSON with these fields:

{{
    "title": "Job title",
    "summary": "2-3 sentence summary",
    "description": "Full description",
    "skills_required": ["skill1", "skill2"],
    "skills_preferred": ["skill3", "skill4"],
    "experience_min": 2,
    "experience_max": 5,
    "location": "City, Country",
    "employment_type": "Full-time/Contract/Part-time",
    "work_mode": "Remote/On-site/Hybrid",
    "salary_min": 50000,
    "salary_max": 80000,
    "salary_type": "annual"
}}

Requirement Text:
{freeform_text}"""

            message = await self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = message.content[0].text

            # Extract JSON
            start_idx = response_text.find("{")
            end_idx = response_text.rfind("}") + 1
            if start_idx >= 0 and end_idx > start_idx:
                parsed = json.loads(response_text[start_idx:end_idx])
            else:
                raise ValueError("Failed to parse LLM response")

            logger.info("Successfully parsed freeform requirement text")
            return parsed

        except Exception as e:
            logger.error(f"Error generating from text: {str(e)}")
            raise

    async def suggest_salary_range(
        self,
        db: AsyncSession,
        skills: List[str],
        location: str,
        experience_years: int,
    ) -> Dict[str, Any]:
        """Suggest competitive salary range based on historical data.

        Args:
            db: Database session
            skills: Required skills
            location: Job location
            experience_years: Years of experience required

        Returns:
            Salary suggestion with market data
        """
        try:
            # Get historical offer data from requirements
            requirements_result = await db.execute(
                select(Requirement).where(
                    Requirement.location_city == location.split(",")[0]
                    if location
                    else True
                )
            )
            requirements = requirements_result.scalars().all()

            # Aggregate salary data
            salary_data = []
            for req in requirements:
                if req.rate_min and req.rate_max:
                    salary_data.append((req.rate_min, req.rate_max))

            if salary_data:
                avg_min = sum(s[0] for s in salary_data) / len(salary_data)
                avg_max = sum(s[1] for s in salary_data) / len(salary_data)
            else:
                # Default market rates based on experience
                base_salary = 50000
                avg_min = base_salary + (experience_years * 5000)
                avg_max = avg_min + 30000

            # Adjust based on skills level
            skill_multiplier = 1.0
            if "machine learning" in [s.lower() for s in skills]:
                skill_multiplier = 1.25
            elif "cloud" in [s.lower() for s in skills]:
                skill_multiplier = 1.15
            elif "leadership" in [s.lower() for s in skills]:
                skill_multiplier = 1.10

            suggested_min = int(avg_min * skill_multiplier)
            suggested_max = int(avg_max * skill_multiplier)

            # Location adjustment
            location_lower = location.lower()
            if any(city in location_lower for city in ["san francisco", "new york", "london"]):
                adjustment = 1.15
            elif any(city in location_lower for city in ["chicago", "boston", "denver"]):
                adjustment = 1.05
            else:
                adjustment = 1.0

            suggested_min = int(suggested_min * adjustment)
            suggested_max = int(suggested_max * adjustment)

            result = {
                "suggested_min": suggested_min,
                "suggested_max": suggested_max,
                "currency": "USD",
                "rate_type": "annual",
                "market_data_points": len(salary_data),
                "confidence_level": min(0.95, len(salary_data) * 0.1),
                "comparable_roles": [
                    f"Senior {skill}" for skill in skills[:3]
                ],
                "location": location,
                "experience_level": f"{experience_years} years",
            }

            logger.info(f"Suggested salary range: ${suggested_min}-${suggested_max}")
            return result

        except Exception as e:
            logger.error(f"Error suggesting salary range: {str(e)}")
            raise

    async def create_multi_board_versions(
        self, db: AsyncSession, job_post_id: int
    ) -> Dict[str, Any]:
        """Create optimized versions for different job boards.

        Args:
            db: Database session
            job_post_id: Job post ID

        Returns:
            Dictionary with board-specific versions
        """
        try:
            job_post = await db.get(JobPost, job_post_id)
            if not job_post:
                raise ValueError(f"Job post {job_post_id} not found")

            if not self.anthropic_client:
                raise ValueError("Anthropic API key required")

            prompt = f"""Optimize this job post for different job boards.
Original title: {job_post.title}
Original content: {job_post.content}

Create JSON with optimized versions for: linkedin, indeed, company_career_page

{{
    "linkedin": {{
        "title": "LinkedIn-optimized title",
        "content": "LinkedIn-formatted content",
        "format_notes": "LinkedIn recommendations"
    }},
    "indeed": {{
        "title": "Indeed-optimized title",
        "content": "Indeed-formatted content",
        "format_notes": "Indeed recommendations"
    }},
    "company_career_page": {{
        "title": "Career page title",
        "content": "Career page content",
        "format_notes": "Career page recommendations"
    }}
}}"""

            message = await self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = message.content[0].text

            # Extract JSON
            start_idx = response_text.find("{")
            end_idx = response_text.rfind("}") + 1
            if start_idx >= 0 and end_idx > start_idx:
                board_versions = json.loads(response_text[start_idx:end_idx])
            else:
                board_versions = {}

            logger.info(f"Created multi-board versions for job post {job_post_id}")
            return board_versions

        except Exception as e:
            logger.error(f"Error creating multi-board versions: {str(e)}")
            raise

    async def on_start(self) -> None:
        """Called when agent starts."""
        logger.info("Job Post Agent started")

    async def on_stop(self) -> None:
        """Called when agent stops."""
        logger.info("Job Post Agent stopped")
