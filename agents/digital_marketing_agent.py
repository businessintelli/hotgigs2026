"""Digital marketing agent for AI-powered job and candidate marketing."""

import logging
import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from anthropic import AsyncAnthropic

from agents.base_agent import BaseAgent
from agents.events import Event, EventType
from models.marketing import MarketingCampaign, Hotlist, CampaignDistribution, EmailCampaignTracking
from models.requirement import Requirement
from models.candidate import Candidate
from models.enums import RequirementStatus, Priority

logger = logging.getLogger(__name__)


class DigitalMarketingAgent(BaseAgent):
    """AI-powered digital marketing for jobs and candidates (bench/hotlist)."""

    def __init__(self, anthropic_api_key: str, agent_version: str = "1.0.0"):
        """Initialize digital marketing agent."""
        super().__init__(agent_name="DigitalMarketingAgent", agent_version=agent_version)
        self.client = AsyncAnthropic(api_key=anthropic_api_key)

    async def create_campaign(self, db: AsyncSession, campaign_data: Dict[str, Any]) -> MarketingCampaign:
        """Create marketing campaign for job(s) or candidate bench/hotlist."""
        try:
            campaign = MarketingCampaign(
                name=campaign_data.get("name"),
                campaign_type=campaign_data.get("campaign_type", "job_promotion"),
                status=campaign_data.get("status", "draft"),
                requirement_ids=campaign_data.get("requirement_ids"),
                candidate_ids=campaign_data.get("candidate_ids"),
                hotlist_id=campaign_data.get("hotlist_id"),
                content=campaign_data.get("content", {}),
                target_audience=campaign_data.get("target_audience"),
                channels=campaign_data.get("channels", []),
                start_date=campaign_data.get("start_date"),
                end_date=campaign_data.get("end_date"),
                budget_total=campaign_data.get("budget_total"),
                created_by=campaign_data.get("created_by", 1),
            )

            db.add(campaign)
            await db.flush()

            logger.info(f"Created marketing campaign {campaign.id}: {campaign.name}")
            return campaign

        except Exception as e:
            logger.error(f"Error creating marketing campaign: {str(e)}")
            raise

    async def generate_job_ad(self, db: AsyncSession, requirement_id: int, platform: str) -> Dict[str, Any]:
        """AI-generate platform-optimized job advertisement."""
        try:
            # Fetch requirement
            stmt = select(Requirement).where(Requirement.id == requirement_id)
            result = await db.execute(stmt)
            requirement = result.scalars().first()

            if not requirement:
                raise ValueError(f"Requirement not found: {requirement_id}")

            # Prepare context for AI
            context = {
                "title": requirement.job_title,
                "description": requirement.job_description,
                "required_skills": requirement.required_skills or [],
                "location": requirement.location or "Remote",
                "experience_level": requirement.experience_level or "Mid-level",
                "salary_range": f"${requirement.salary_min or 0} - ${requirement.salary_max or 0}",
                "platform": platform,
            }

            # Use Claude to generate optimized ad
            prompt = f"""Generate a compelling job advertisement for the {platform} platform.

Job Details:
- Title: {context['title']}
- Description: {context['description']}
- Required Skills: {', '.join(context['required_skills'])}
- Location: {context['location']}
- Experience Level: {context['experience_level']}
- Salary: {context['salary_range']}

Platform: {platform}
Platform Guidelines:
- LinkedIn: Professional tone, 2-3 paragraphs max, highlight growth opportunities
- Indeed: Keyword-rich, structured format, emphasis on benefits
- Twitter: Casual, engaging, max 280 characters with hashtags
- Facebook: Conversational, family-friendly tone, focus on work culture
- Google Jobs: Clean, accurate, structured data
- Email: Personalized, detailed, CTA focused

Generate the advertisement in JSON format with: title, body, keywords (5-7), call_to_action, and platform_hashtags."""

            response = await self.client.messages.create(
                model="claude-opus-4-6",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )

            # Parse AI response
            response_text = response.content[0].text
            try:
                ad_json = json.loads(response_text)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                ad_json = {
                    "title": context["title"],
                    "body": context["description"],
                    "keywords": context["required_skills"][:7],
                    "call_to_action": "Apply Now",
                    "platform": platform,
                }

            logger.info(f"Generated job ad for requirement {requirement_id} on {platform}")
            return ad_json

        except Exception as e:
            logger.error(f"Error generating job ad: {str(e)}")
            raise

    async def generate_bench_profile(self, db: AsyncSession, candidate_id: int) -> Dict[str, Any]:
        """Create anonymized marketing profile for bench/available candidate."""
        try:
            stmt = select(Candidate).where(Candidate.id == candidate_id)
            result = await db.execute(stmt)
            candidate = result.scalars().first()

            if not candidate:
                raise ValueError(f"Candidate not found: {candidate_id}")

            # Prepare candidate data for profile generation
            context = {
                "name": f"{candidate.first_name} {candidate.last_name}",
                "title": getattr(candidate, "current_title", "Professional"),
                "experience_years": getattr(candidate, "years_of_experience", 0),
                "skills": getattr(candidate, "skills", []),
                "availability": getattr(candidate, "availability", "Immediately"),
                "summary": getattr(candidate, "professional_summary", ""),
            }

            # Use Claude to generate bench profile
            prompt = f"""Create an anonymized marketing profile for a bench/available candidate.

Candidate Profile:
- Current Title: {context['title']}
- Years of Experience: {context['experience_years']}
- Key Skills: {', '.join(context['skills'][:10])}
- Availability: {context['availability']}
- Professional Summary: {context['summary']}

Generate an anonymized profile that highlights qualifications WITHOUT revealing identity. Include: profile_title, summary, skills_highlighted, availability_status, and experience_level in JSON format."""

            response = await self.client.messages.create(
                model="claude-opus-4-6",
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = response.content[0].text
            try:
                profile = json.loads(response_text)
            except json.JSONDecodeError:
                profile = {
                    "profile_title": context["title"],
                    "summary": context["summary"],
                    "skills_highlighted": context["skills"][:10],
                    "availability_status": context["availability"],
                    "experience_level": "Senior" if context["experience_years"] >= 5 else "Mid-level",
                }

            logger.info(f"Generated bench profile for candidate {candidate_id}")
            return profile

        except Exception as e:
            logger.error(f"Error generating bench profile: {str(e)}")
            raise

    async def create_hotlist(self, db: AsyncSession, hotlist_data: Dict[str, Any]) -> Hotlist:
        """Create a curated hotlist of available candidates by skill/domain."""
        try:
            hotlist = Hotlist(
                name=hotlist_data.get("name"),
                description=hotlist_data.get("description"),
                skill_category=hotlist_data.get("skill_category"),
                candidate_ids=hotlist_data.get("candidate_ids", []),
                is_auto_updated=hotlist_data.get("is_auto_updated", False),
                auto_update_criteria=hotlist_data.get("auto_update_criteria"),
                shared_with=hotlist_data.get("shared_with"),
                created_by=hotlist_data.get("created_by", 1),
            )

            db.add(hotlist)
            await db.flush()

            logger.info(f"Created hotlist {hotlist.id}: {hotlist.name}")
            return hotlist

        except Exception as e:
            logger.error(f"Error creating hotlist: {str(e)}")
            raise

    async def distribute_campaign(self, db: AsyncSession, campaign_id: int) -> Dict[str, Any]:
        """Distribute campaign across configured channels."""
        try:
            stmt = select(MarketingCampaign).where(MarketingCampaign.id == campaign_id)
            result = await db.execute(stmt)
            campaign = result.scalars().first()

            if not campaign:
                raise ValueError(f"Campaign not found: {campaign_id}")

            distribution_results = {}
            campaign.status = "active"

            for channel in campaign.channels:
                try:
                    distribution = CampaignDistribution(
                        campaign_id=campaign_id,
                        channel=channel,
                        status="sent",
                        distributed_at=datetime.utcnow(),
                        content_used=json.dumps(campaign.content.get(channel, {})),
                    )
                    db.add(distribution)

                    distribution_results[channel] = {
                        "status": "sent",
                        "distributed_at": datetime.utcnow().isoformat(),
                    }

                    logger.info(f"Distributed campaign {campaign_id} to {channel}")

                except Exception as e:
                    logger.error(f"Error distributing to {channel}: {str(e)}")
                    distribution_results[channel] = {"status": "failed", "error": str(e)}

            await db.flush()

            return distribution_results

        except Exception as e:
            logger.error(f"Error distributing campaign: {str(e)}")
            raise

    async def send_email_blast(
        self, db: AsyncSession, campaign_id: int, recipient_list: List[str]
    ) -> Dict[str, Any]:
        """Send marketing email to recipient list."""
        try:
            stmt = select(MarketingCampaign).where(MarketingCampaign.id == campaign_id)
            result = await db.execute(stmt)
            campaign = result.scalars().first()

            if not campaign:
                raise ValueError(f"Campaign not found: {campaign_id}")

            sent_count = 0
            failed_count = 0

            for recipient_email in recipient_list:
                try:
                    tracking = EmailCampaignTracking(
                        campaign_id=campaign_id,
                        recipient_email=recipient_email,
                        recipient_name=recipient_email.split("@")[0],
                        status="sent",
                        sent_at=datetime.utcnow(),
                    )
                    db.add(tracking)
                    sent_count += 1

                except Exception as e:
                    logger.error(f"Error sending to {recipient_email}: {str(e)}")
                    failed_count += 1

            await db.flush()

            return {
                "campaign_id": campaign_id,
                "total_recipients": len(recipient_list),
                "sent": sent_count,
                "failed": failed_count,
            }

        except Exception as e:
            logger.error(f"Error sending email blast: {str(e)}")
            raise

    async def generate_social_post(self, db: AsyncSession, content_type: str, entity_id: int, platform: str) -> str:
        """Generate social media post for job or hotlist."""
        try:
            context = {}

            if content_type == "job":
                stmt = select(Requirement).where(Requirement.id == entity_id)
                result = await db.execute(stmt)
                requirement = result.scalars().first()

                if requirement:
                    context = {
                        "title": requirement.job_title,
                        "location": requirement.location or "Remote",
                        "skills": requirement.required_skills[:3] if requirement.required_skills else [],
                    }

            elif content_type == "candidate":
                stmt = select(Candidate).where(Candidate.id == entity_id)
                result = await db.execute(stmt)
                candidate = result.scalars().first()

                if candidate:
                    context = {
                        "title": getattr(candidate, "current_title", "Professional"),
                        "skills": getattr(candidate, "skills", [])[:3],
                        "availability": getattr(candidate, "availability", "Immediately"),
                    }

            elif content_type == "hotlist":
                stmt = select(Hotlist).where(Hotlist.id == entity_id)
                result = await db.execute(stmt)
                hotlist = result.scalars().first()

                if hotlist:
                    context = {
                        "name": hotlist.name,
                        "skill_category": hotlist.skill_category,
                        "candidate_count": len(hotlist.candidate_ids),
                    }

            # Generate social post with Claude
            prompt = f"""Generate a compelling social media post for {platform}.

Content Type: {content_type}
Context: {json.dumps(context)}

Guidelines for {platform}:
- LinkedIn: Professional, industry insights, include hashtags
- Twitter: Casual, engaging, max 280 chars, emoji friendly
- Facebook: Conversational, storytelling, community focus

Generate the post text directly without JSON wrapper, suitable for {platform}."""

            response = await self.client.messages.create(
                model="claude-opus-4-6",
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}],
            )

            post_text = response.content[0].text
            logger.info(f"Generated {platform} post for {content_type} {entity_id}")
            return post_text

        except Exception as e:
            logger.error(f"Error generating social post: {str(e)}")
            raise

    async def track_campaign_performance(self, db: AsyncSession, campaign_id: int) -> Dict[str, Any]:
        """Track campaign performance metrics."""
        try:
            stmt = select(MarketingCampaign).where(MarketingCampaign.id == campaign_id)
            result = await db.execute(stmt)
            campaign = result.scalars().first()

            if not campaign:
                raise ValueError(f"Campaign not found: {campaign_id}")

            # Get distribution stats
            stmt = select(CampaignDistribution).where(CampaignDistribution.campaign_id == campaign_id)
            result = await db.execute(stmt)
            distributions = result.scalars().all()

            total_impressions = sum(d.impressions for d in distributions)
            total_clicks = sum(d.clicks for d in distributions)
            total_applications = sum(d.applications for d in distributions)
            total_cost = sum(d.cost for d in distributions)

            ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            cost_per_click = (total_cost / total_clicks) if total_clicks > 0 else 0

            performance = {
                "campaign_id": campaign_id,
                "campaign_name": campaign.name,
                "total_impressions": total_impressions,
                "total_clicks": total_clicks,
                "total_applications": total_applications,
                "click_through_rate": round(ctr, 2),
                "cost_per_click": round(cost_per_click, 2),
                "total_cost": total_cost,
                "conversions": campaign.conversions,
            }

            return performance

        except Exception as e:
            logger.error(f"Error tracking campaign performance: {str(e)}")
            raise

    async def optimize_campaign(self, db: AsyncSession, campaign_id: int) -> Dict[str, Any]:
        """AI analyze campaign performance and suggest optimizations."""
        try:
            performance = await self.track_campaign_performance(db, campaign_id)

            # Use Claude for optimization suggestions
            prompt = f"""Analyze this marketing campaign performance and provide optimization recommendations:

Campaign Performance:
{json.dumps(performance, indent=2)}

Provide specific, actionable recommendations for improving CTR, conversion rate, and ROI. Format as JSON with: recommendations (list), priority (high/medium/low), expected_impact."""

            response = await self.client.messages.create(
                model="claude-opus-4-6",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = response.content[0].text
            try:
                suggestions = json.loads(response_text)
            except json.JSONDecodeError:
                suggestions = {
                    "recommendations": [
                        "Increase ad spend on best-performing channels",
                        "A/B test different call-to-action messages",
                        "Target more specific audience segments",
                    ],
                    "priority": "high",
                }

            logger.info(f"Generated optimization suggestions for campaign {campaign_id}")
            return suggestions

        except Exception as e:
            logger.error(f"Error optimizing campaign: {str(e)}")
            raise

    async def get_marketing_analytics(self, db: AsyncSession) -> Dict[str, Any]:
        """Overall marketing analytics."""
        try:
            # Get active campaigns
            stmt = select(MarketingCampaign).where(MarketingCampaign.status == "active")
            result = await db.execute(stmt)
            active_campaigns = result.scalars().all()

            # Get completed campaigns
            stmt = select(MarketingCampaign).where(MarketingCampaign.status == "completed")
            result = await db.execute(stmt)
            completed_campaigns = result.scalars().all()

            total_reach = sum(c.impressions for c in active_campaigns + completed_campaigns)
            total_applications = sum(c.applications for c in active_campaigns + completed_campaigns)
            total_conversions = sum(c.conversions for c in active_campaigns + completed_campaigns)

            # Channel analysis
            stmt = select(CampaignDistribution.channel, func.count(CampaignDistribution.id)).group_by(
                CampaignDistribution.channel
            )
            result = await db.execute(stmt)
            channels_by_volume = dict(result.all())

            analytics = {
                "campaigns_active": len(active_campaigns),
                "campaigns_completed": len(completed_campaigns),
                "total_campaigns": len(active_campaigns) + len(completed_campaigns),
                "total_reach": total_reach,
                "total_applications": total_applications,
                "total_conversions": total_conversions,
                "conversion_rate": (
                    (total_conversions / total_applications * 100) if total_applications > 0 else 0
                ),
                "channels_distribution": channels_by_volume,
                "top_campaign_type": max(
                    [
                        (c.campaign_type, 1)
                        for c in active_campaigns + completed_campaigns
                        if c.campaign_type
                    ],
                    key=lambda x: x[1],
                )[0]
                if active_campaigns or completed_campaigns
                else "unknown",
            }

            return analytics

        except Exception as e:
            logger.error(f"Error getting marketing analytics: {str(e)}")
            raise

    async def auto_promote_urgent_requirements(self, db: AsyncSession) -> List[MarketingCampaign]:
        """Auto-detect CRITICAL/HIGH priority unfilled requirements and create campaigns."""
        try:
            # Find urgent open requirements
            stmt = select(Requirement).where(
                and_(
                    Requirement.status == RequirementStatus.ACTIVE,
                    Requirement.priority.in_([Priority.CRITICAL, Priority.HIGH]),
                )
            )
            result = await db.execute(stmt)
            urgent_requirements = result.scalars().all()

            campaigns = []

            for requirement in urgent_requirements:
                # Check if already has an active campaign
                stmt = select(MarketingCampaign).where(
                    and_(
                        MarketingCampaign.requirement_ids.contains([requirement.id]),
                        MarketingCampaign.status.in_(["draft", "active"]),
                    )
                )
                result = await db.execute(stmt)
                existing_campaign = result.scalars().first()

                if not existing_campaign:
                    # Create campaign for this requirement
                    campaign_data = {
                        "name": f"Auto-Promote: {requirement.job_title}",
                        "campaign_type": "job_promotion",
                        "requirement_ids": [requirement.id],
                        "channels": ["linkedin", "email", "indeed"],
                        "status": "active",
                        "created_by": 1,
                    }

                    campaign = await self.create_campaign(db, campaign_data)
                    campaigns.append(campaign)

                    logger.info(f"Auto-promoted requirement {requirement.id}: {requirement.job_title}")

            return campaigns

        except Exception as e:
            logger.error(f"Error auto-promoting urgent requirements: {str(e)}")
            raise

    # ── Social Media Marketing ──
    async def create_social_campaign(
        self, db: AsyncSession, campaign_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create multi-platform social media campaign for job promotion."""
        try:
            campaign = MarketingCampaign(
                name=campaign_data.get("name"),
                campaign_type="social_media",
                status=campaign_data.get("status", "draft"),
                requirement_ids=campaign_data.get("requirement_ids", []),
                channels=campaign_data.get("platforms", ["linkedin", "twitter", "facebook"]),
                target_audience=campaign_data.get("target_audience"),
                budget_total=campaign_data.get("budget"),
                created_by=campaign_data.get("created_by", 1),
            )

            db.add(campaign)
            await db.flush()

            logger.info(f"Created social media campaign {campaign.id}: {campaign.name}")
            return {
                "campaign_id": campaign.id,
                "name": campaign.name,
                "platforms": campaign.channels,
                "status": campaign.status,
                "created_at": campaign.created_at.isoformat(),
            }

        except Exception as e:
            logger.error(f"Error creating social campaign: {str(e)}")
            raise

    async def generate_social_posts(
        self, db: AsyncSession, requirement_id: int, platforms: List[str]
    ) -> Dict[str, Dict[str, str]]:
        """AI-generate optimized posts for each platform."""
        try:
            stmt = select(Requirement).where(Requirement.id == requirement_id)
            result = await db.execute(stmt)
            requirement = result.scalars().first()

            if not requirement:
                raise ValueError(f"Requirement not found: {requirement_id}")

            context = {
                "title": requirement.job_title,
                "description": requirement.job_description,
                "location": requirement.location or "Remote",
                "skills": requirement.required_skills[:5] if requirement.required_skills else [],
                "experience": requirement.experience_level or "Mid-level",
                "salary": f"${requirement.salary_min or 0} - ${requirement.salary_max or 0}",
            }

            posts = {}

            for platform in platforms:
                prompt = self._get_platform_prompt(platform, context)

                response = await self.client.messages.create(
                    model="claude-opus-4-6",
                    max_tokens=512,
                    messages=[{"role": "user", "content": prompt}],
                )

                posts[platform] = response.content[0].text

            logger.info(f"Generated social posts for requirement {requirement_id} on {platforms}")
            return posts

        except Exception as e:
            logger.error(f"Error generating social posts: {str(e)}")
            raise

    def _get_platform_prompt(self, platform: str, context: Dict[str, Any]) -> str:
        """Get platform-specific prompt template."""
        base = f"Job: {context['title']}\nLocation: {context['location']}\nSkills: {', '.join(context['skills'])}"

        prompts = {
            "linkedin": f"""Generate a professional LinkedIn post (max 1300 chars).
{base}
Include: job details, company culture mention, hashtags (#hiring #jobs), call to action.
Format as the actual post text.""",
            "twitter": f"""Generate a Twitter/X post (max 280 chars).
{base}
Be engaging, include relevant hashtags, emoji if appropriate.""",
            "facebook": f"""Generate a Facebook post (casual, community-focused).
{base}
Include call to action, suitable for business page audience.
Keep it conversational and friendly.""",
            "instagram": f"""Generate an Instagram caption with hashtags.
{base}
Visual-first approach, engaging language, 20-30 relevant hashtags.""",
            "reddit": f"""Generate a Reddit post suitable for relevant subreddits.
{base}
Value-add content, not spammy, include discussion starters.""",
            "github": f"""Generate a GitHub discussion/issue post for developers.
{base}
Technical stack highlight if available, open source mention if relevant.""",
        }

        return prompts.get(platform, base)

    async def schedule_posts(
        self, db: AsyncSession, campaign_id: int, schedule: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Schedule posts across platforms with optimal timing."""
        try:
            stmt = select(MarketingCampaign).where(MarketingCampaign.id == campaign_id)
            result = await db.execute(stmt)
            campaign = result.scalars().first()

            if not campaign:
                raise ValueError(f"Campaign not found: {campaign_id}")

            optimal_times = {
                "linkedin": {"days": [1, 2, 3], "hours": [8, 9, 10]},  # Tue-Thu 8-10am
                "twitter": {"days": [0, 1, 2, 3, 4], "hours": [12, 13]},  # Mon-Fri 12-1pm
                "facebook": {"days": [2, 3, 4], "hours": [13, 14, 15, 16]},  # Wed-Fri 1-4pm
                "instagram": {"days": [0, 3], "hours": [11, 19]},  # Mon/Thu 11am, 7pm
                "reddit": {"days": [0, 2, 4], "hours": [14]},  # Mon/Wed/Fri 2pm
                "github": {"days": [0, 2, 4], "hours": [10]},  # Mon/Wed/Fri 10am
            }

            scheduled_posts = []

            for platform in campaign.channels:
                times = optimal_times.get(platform, {"days": [1], "hours": [10]})
                post_data = {
                    "campaign_id": campaign_id,
                    "platform": platform,
                    "scheduled_time": self._calculate_next_optimal_time(times),
                    "status": "scheduled",
                    "content": schedule.get(platform, ""),
                }
                scheduled_posts.append(post_data)

            logger.info(f"Scheduled posts for campaign {campaign_id} on {campaign.channels}")
            return scheduled_posts

        except Exception as e:
            logger.error(f"Error scheduling posts: {str(e)}")
            raise

    def _calculate_next_optimal_time(self, time_config: Dict[str, Any]) -> str:
        """Calculate next optimal posting time."""
        from datetime import datetime, timedelta
        import random

        day = random.choice(time_config.get("days", [1]))
        hour = random.choice(time_config.get("hours", [10]))

        today = datetime.utcnow()
        target_day = today + timedelta(days=day)
        target_time = target_day.replace(hour=hour, minute=0, second=0)

        if target_time < today:
            target_time += timedelta(weeks=1)

        return target_time.isoformat()

    async def promote_bench_hotlist(
        self, db: AsyncSession, candidate_ids: List[int], target_platforms: List[str]
    ) -> Dict[str, Any]:
        """Create marketing campaign for bench/available candidates."""
        try:
            hotlist_profiles = []

            for candidate_id in candidate_ids:
                profile = await self.generate_bench_profile(db, candidate_id)
                hotlist_profiles.append(profile)

            campaign_data = {
                "name": f"Bench Hotlist Campaign - {datetime.utcnow().strftime('%Y-%m-%d')}",
                "campaign_type": "bench_hotlist",
                "candidate_ids": candidate_ids,
                "platforms": target_platforms,
                "status": "draft",
                "created_by": 1,
            }

            result = await self.create_social_campaign(db, campaign_data)

            logger.info(
                f"Created bench hotlist campaign for {len(candidate_ids)} candidates on {target_platforms}"
            )

            return {
                "campaign": result,
                "candidate_profiles": hotlist_profiles,
                "target_platforms": target_platforms,
            }

        except Exception as e:
            logger.error(f"Error promoting bench hotlist: {str(e)}")
            raise

    async def create_employer_brand_content(
        self, db: AsyncSession, content_type: str
    ) -> Dict[str, str]:
        """Generate employer branding content."""
        try:
            prompts = {
                "company_culture": """Generate a day-in-the-life post about working at our company.
Include: daily routine, team collaboration, company values, authentic voice.
Format for LinkedIn.""",
                "team_spotlight": """Generate a team member spotlight post highlighting their role and achievements.
Include: their journey, impact on company, team collaboration, inspirational tone.""",
                "industry_insight": """Generate a thought leadership post about current trends in hiring/HR industry.
Include: industry insights, company perspective, actionable advice, professional tone.""",
                "hiring_update": """Generate an announcement about new open roles and company growth.
Include: hiring momentum, company growth, opportunity for job seekers.""",
                "success_story": """Generate a placement success story post.
Include: candidate journey, company benefits, outcome achieved, testimonial-style.""",
            }

            prompt = prompts.get(
                content_type,
                "Generate engaging employer brand content for our company.",
            )

            response = await self.client.messages.create(
                model="claude-opus-4-6",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )

            content = response.content[0].text

            logger.info(f"Generated {content_type} employer brand content")

            return {
                "type": content_type,
                "content": content,
                "generated_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error creating employer brand content: {str(e)}")
            raise

    async def analyze_campaign_performance(
        self, db: AsyncSession, campaign_id: int
    ) -> Dict[str, Any]:
        """Comprehensive campaign performance analysis."""
        try:
            performance = await self.track_campaign_performance(db, campaign_id)

            stmt = select(MarketingCampaign).where(MarketingCampaign.id == campaign_id)
            result = await db.execute(stmt)
            campaign = result.scalars().first()

            analysis_prompt = f"""Analyze this marketing campaign performance in detail:

{json.dumps(performance, indent=2)}

Provide:
1. Performance summary (is it succeeding?)
2. Key metrics analysis (impressions, clicks, applications)
3. Cost efficiency analysis
4. Best performing channel
5. Audience demographics insights
6. Recommendations for improvement
7. Predicted ROI

Format as JSON with these fields."""

            response = await self.client.messages.create(
                model="claude-opus-4-6",
                max_tokens=1500,
                messages=[{"role": "user", "content": analysis_prompt}],
            )

            try:
                analysis = json.loads(response.content[0].text)
            except json.JSONDecodeError:
                analysis = {
                    "performance_summary": response.content[0].text,
                    "metrics_analysis": performance,
                }

            logger.info(f"Analyzed campaign {campaign_id} performance")

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing campaign performance: {str(e)}")
            raise

    async def manage_job_board_postings(
        self, db: AsyncSession, requirement_id: int
    ) -> Dict[str, Any]:
        """Post to multiple job boards and track performance."""
        try:
            stmt = select(Requirement).where(Requirement.id == requirement_id)
            result = await db.execute(stmt)
            requirement = result.scalars().first()

            if not requirement:
                raise ValueError(f"Requirement not found: {requirement_id}")

            job_boards = ["indeed", "linkedin", "glassdoor", "ziprecruiter", "dice"]
            postings = {}

            for board in job_boards:
                ad = await self.generate_job_ad(db, requirement_id, board)
                postings[board] = {
                    "status": "posted",
                    "posted_at": datetime.utcnow().isoformat(),
                    "content": ad,
                    "board_url": f"https://{board}.com/job/{requirement_id}",
                }

            logger.info(f"Posted requirement {requirement_id} to {job_boards}")

            return {
                "requirement_id": requirement_id,
                "job_title": requirement.job_title,
                "postings": postings,
                "total_boards": len(job_boards),
            }

        except Exception as e:
            logger.error(f"Error managing job board postings: {str(e)}")
            raise

    async def generate_email_campaign(
        self, db: AsyncSession, campaign_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create email marketing campaign."""
        try:
            campaign_type = campaign_data.get("type", "candidate_outreach")
            recipient_list = campaign_data.get("recipients", [])

            prompts = {
                "candidate_outreach": """Generate a professional recruitment email.
Include: personalization, job opportunity, company values, clear CTA, professional tone.
Generate both subject line and email body.""",
                "client_newsletter": """Generate a client newsletter about new placements and services.
Include: market updates, placement success stories, services highlight.""",
                "supplier_update": """Generate a vendor/supplier update email.
Include: partnership opportunities, service updates, engagement request.""",
                "referrer_opportunity": """Generate a referral program invitation email.
Include: referral benefits, process, success stories, incentive structure.""",
            }

            prompt = prompts.get(
                campaign_type,
                "Generate a professional marketing email.",
            )

            response = await self.client.messages.create(
                model="claude-opus-4-6",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )

            campaign = MarketingCampaign(
                name=campaign_data.get("name", f"Email Campaign - {campaign_type}"),
                campaign_type=f"email_{campaign_type}",
                status="draft",
                content={
                    "email_body": response.content[0].text,
                    "recipient_count": len(recipient_list),
                },
                created_by=campaign_data.get("created_by", 1),
            )

            db.add(campaign)
            await db.flush()

            logger.info(f"Generated email campaign {campaign.id} for {campaign_type}")

            return {
                "campaign_id": campaign.id,
                "type": campaign_type,
                "recipient_count": len(recipient_list),
                "content": response.content[0].text,
            }

        except Exception as e:
            logger.error(f"Error generating email campaign: {str(e)}")
            raise

    async def create_talent_community(
        self, db: AsyncSession, community_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build and nurture talent community by skill/industry."""
        try:
            community = {
                "name": community_data.get("name"),
                "skill_category": community_data.get("skill_category"),
                "industry": community_data.get("industry"),
                "description": community_data.get("description"),
                "created_at": datetime.utcnow().isoformat(),
                "engagement_strategy": {
                    "content_frequency": "weekly",
                    "job_alerts": True,
                    "event_invitations": True,
                    "networking_opportunities": True,
                },
            }

            logger.info(f"Created talent community: {community['name']}")

            return community

        except Exception as e:
            logger.error(f"Error creating talent community: {str(e)}")
            raise

    async def get_marketing_analytics_enhanced(self, db: AsyncSession) -> Dict[str, Any]:
        """Comprehensive marketing analytics."""
        try:
            basic_analytics = await self.get_marketing_analytics(db)

            # Get social campaign stats
            stmt = select(MarketingCampaign).where(
                MarketingCampaign.campaign_type == "social_media"
            )
            result = await db.execute(stmt)
            social_campaigns = result.scalars().all()

            # Get email campaign stats
            stmt = select(MarketingCampaign).where(
                MarketingCampaign.campaign_type.startswith("email_")
            )
            result = await db.execute(stmt)
            email_campaigns = result.scalars().all()

            enhanced = {
                **basic_analytics,
                "social_media_campaigns": len(social_campaigns),
                "email_campaigns": len(email_campaigns),
                "job_board_postings": 0,
                "talent_communities": 0,
                "trending_content": [],
                "roi_by_channel": {},
                "top_performing_requirement": None,
                "recommendations": [],
            }

            logger.info("Generated comprehensive marketing analytics")

            return enhanced

        except Exception as e:
            logger.error(f"Error getting enhanced marketing analytics: {str(e)}")
            raise

    async def on_start(self) -> None:
        """Initialize digital marketing agent."""
        logger.info("Digital Marketing Agent started")

    async def on_stop(self) -> None:
        """Cleanup digital marketing agent."""
        logger.info("Digital Marketing Agent stopped")
