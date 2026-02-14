"""Conversational AI interface agent for role-based chat."""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from agents.base_agent import BaseAgent
from agents.events import EventType
from models.conversation import Conversation, ConversationMessage
from services.conversation_service import ConversationService
from schemas.conversation import ConversationCreate, ConversationMessageCreate

logger = logging.getLogger(__name__)


class ConversationalInterfaceAgent(BaseAgent):
    """Role-based conversational AI interface for all platform users."""

    ROLE_SYSTEM_PROMPTS = {
        "admin": "You are an AI assistant for HR platform administrators. You have access to all system features including user management, configuration, analytics, and security settings. Provide comprehensive guidance on platform operations.",
        "recruiter": "You are an AI recruiting assistant specialized in candidate sourcing, matching, pipeline management, and submission workflows. Help with candidate searches, requirement matching, and negotiation strategies.",
        "manager": "You are an AI assistant for hiring managers. Help with requirement creation, candidate review, interview scheduling, offer decisions, and team insights.",
        "candidate": "You are a career assistant for job candidates. Help with job search, application tracking, interview preparation, salary negotiation, and onboarding guidance.",
        "supplier": "You are an AI assistant for staffing suppliers and vendors. Help with requirement discovery, candidate submissions, performance tracking, and partnership management.",
        "referrer": "You are an AI assistant for referral partners. Help with opportunity discovery, referral submissions, earnings tracking, and referral guidance.",
    }

    ROLE_TOOLS = {
        "recruiter": [
            "search_candidates",
            "match_requirement",
            "schedule_interview",
            "create_submission",
            "generate_outreach",
            "check_pipeline",
            "negotiate_rate",
            "view_analytics",
        ],
        "manager": [
            "review_submissions",
            "approve_submission",
            "view_pipeline",
            "compare_candidates",
            "view_analytics",
            "schedule_interview",
            "make_offer_decision",
        ],
        "candidate": [
            "search_jobs",
            "update_profile",
            "check_application_status",
            "prepare_interview",
            "negotiate_rate",
            "view_offers",
        ],
        "supplier": [
            "view_requirements",
            "submit_candidate",
            "check_submissions",
            "view_performance",
            "generate_reports",
        ],
        "referrer": [
            "view_opportunities",
            "submit_referral",
            "check_earnings",
            "generate_referral_link",
            "view_referral_status",
        ],
        "admin": [
            "user_management",
            "system_configuration",
            "security_settings",
            "view_analytics",
            "generate_reports",
            "manage_permissions",
            "audit_logs",
        ],
    }

    ROLE_FEATURES = {
        "recruiter": {
            "candidate_search": True,
            "requirement_matching": True,
            "submission_workflow": True,
            "interview_scheduling": True,
            "rate_negotiation": True,
            "analytics": True,
        },
        "manager": {
            "requirement_management": True,
            "candidate_review": True,
            "submission_workflow": True,
            "interview_scheduling": True,
            "offer_management": True,
            "analytics": True,
        },
        "candidate": {
            "job_search": True,
            "profile_management": True,
            "application_tracking": True,
            "interview_preparation": True,
            "offer_review": True,
        },
        "supplier": {
            "requirement_discovery": True,
            "candidate_submission": True,
            "submission_tracking": True,
            "performance_metrics": True,
        },
        "referrer": {
            "opportunity_discovery": True,
            "referral_submission": True,
            "earnings_tracking": True,
            "referral_management": True,
        },
        "admin": {
            "user_management": True,
            "system_configuration": True,
            "security_management": True,
            "audit_logs": True,
            "analytics": True,
            "reporting": True,
        },
    }

    def __init__(self):
        """Initialize the conversational interface agent."""
        super().__init__(
            agent_name="ConversationalInterfaceAgent",
            agent_version="1.0.0",
        )
        self.max_conversation_length = 100
        self.max_message_length = 10000

    async def start_conversation(
        self,
        db: AsyncSession,
        user_id: int,
        user_role: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Conversation:
        """Start new conversation.

        Args:
            db: Database session
            user_id: User ID
            user_role: User's role
            context: Optional context (requirement_id, candidate_id, etc)

        Returns:
            Created conversation

        Raises:
            ValueError: If role not supported
        """
        try:
            if user_role not in self.ROLE_SYSTEM_PROMPTS:
                raise ValueError(f"Unsupported role: {user_role}")

            service = ConversationService(db)

            conversation_data = ConversationCreate(
                user_role=user_role,
                context=context,
            )

            conversation = await service.create_conversation(user_id, conversation_data)

            # Emit event
            await self.emit_event(
                event_type=EventType.CONVERSATION_STARTED,
                entity_type="Conversation",
                entity_id=conversation.id,
                payload={
                    "conversation_id": conversation.id,
                    "user_id": user_id,
                    "user_role": user_role,
                },
                user_id=user_id,
            )

            logger.info(f"Started conversation {conversation.id} for user {user_id} ({user_role})")
            return conversation

        except Exception as e:
            logger.error(f"Error starting conversation: {str(e)}")
            raise

    async def send_message(
        self,
        db: AsyncSession,
        conversation_id: int,
        user_id: int,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ConversationMessage:
        """Process user message and generate response.

        Args:
            db: Database session
            conversation_id: Conversation ID
            user_id: User ID sending message
            message: User message content
            metadata: Optional metadata

        Returns:
            User's message (model can add follow-up assistant message)

        Raises:
            ValueError: If conversation not found or message too long
        """
        try:
            if len(message) > self.max_message_length:
                raise ValueError(f"Message exceeds maximum length of {self.max_message_length}")

            service = ConversationService(db)

            # Get conversation
            conversation = await service.get_conversation(conversation_id)
            if not conversation:
                raise ValueError(f"Conversation {conversation_id} not found")

            # Check conversation length
            if conversation.message_count >= self.max_conversation_length:
                logger.warning(f"Conversation {conversation_id} at max length")

            # Add user message
            user_message = await service.add_message(
                conversation_id=conversation_id,
                role="user",
                content=message,
                metadata=metadata,
            )

            # Emit event
            await self.emit_event(
                event_type=EventType.MESSAGE_SENT,
                entity_type="ConversationMessage",
                entity_id=user_message.id,
                payload={
                    "conversation_id": conversation_id,
                    "message_id": user_message.id,
                    "message_length": len(message),
                },
                user_id=user_id,
            )

            logger.info(f"Added message to conversation {conversation_id}")
            return user_message

        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            raise

    async def generate_response(
        self,
        db: AsyncSession,
        conversation_id: int,
        user_id: int,
    ) -> ConversationMessage:
        """Generate AI response to latest user message.

        Note: In production, this would call Claude API with role-based system prompt
        and available tools. This is a placeholder implementation.

        Args:
            db: Database session
            conversation_id: Conversation ID
            user_id: User ID

        Returns:
            Assistant's response message

        Raises:
            ValueError: If conversation not found
        """
        try:
            service = ConversationService(db)

            # Get conversation
            conversation = await service.get_conversation(conversation_id)
            if not conversation:
                raise ValueError(f"Conversation {conversation_id} not found")

            # Get conversation history
            messages, _ = await service.get_conversation_messages(conversation_id, skip=0, limit=50)

            # Get system prompt for role
            system_prompt = self.ROLE_SYSTEM_PROMPTS.get(
                conversation.user_role,
                "You are a helpful assistant.",
            )

            # In production: Call Claude API with messages and system prompt
            # For now, return a placeholder response
            response_content = (
                f"I'm assisting you as a {conversation.user_role}. "
                f"I can help you with: {', '.join(self.ROLE_TOOLS.get(conversation.user_role, []))}. "
                f"What would you like to do?"
            )

            # Add assistant message
            assistant_message = await service.add_message(
                conversation_id=conversation_id,
                role="assistant",
                content=response_content,
                tokens_used=100,  # Placeholder
                processing_time_ms=500,
            )

            logger.info(f"Generated response for conversation {conversation_id}")
            return assistant_message

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise

    async def execute_tool(
        self,
        db: AsyncSession,
        user_id: int,
        user_role: str,
        tool_name: str,
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute platform tool based on user role and permissions.

        Args:
            db: Database session
            user_id: User ID
            user_role: User's role
            tool_name: Tool to execute
            params: Tool parameters

        Returns:
            Tool execution result

        Raises:
            ValueError: If tool not available for role
        """
        try:
            # Check if tool available for role
            available_tools = self.ROLE_TOOLS.get(user_role, [])
            if tool_name not in available_tools:
                raise ValueError(f"Tool {tool_name} not available for role {user_role}")

            # In production: Execute actual tool and return results
            # For now, return placeholder
            return {
                "status": "executed",
                "tool": tool_name,
                "result": f"Tool {tool_name} executed successfully",
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {str(e)}")
            raise

    async def get_role_tools(self, user_role: str) -> List[Dict[str, Any]]:
        """Get available tools for a role.

        Args:
            user_role: User's role

        Returns:
            List of available tools

        Raises:
            ValueError: If role not supported
        """
        try:
            if user_role not in self.ROLE_TOOLS:
                raise ValueError(f"Unsupported role: {user_role}")

            tools = self.ROLE_TOOLS[user_role]

            return [
                {
                    "name": tool,
                    "description": f"Tool: {tool}",
                    "available": True,
                }
                for tool in tools
            ]

        except Exception as e:
            logger.error(f"Error getting role tools: {str(e)}")
            raise

    async def get_conversation_history(
        self,
        db: AsyncSession,
        conversation_id: int,
    ) -> List[ConversationMessage]:
        """Get full conversation history.

        Args:
            db: Database session
            conversation_id: Conversation ID

        Returns:
            List of all messages

        Raises:
            ValueError: If conversation not found
        """
        try:
            service = ConversationService(db)

            conversation = await service.get_conversation(conversation_id)
            if not conversation:
                raise ValueError(f"Conversation {conversation_id} not found")

            return await service.get_conversation_history(conversation_id)

        except Exception as e:
            logger.error(f"Error getting conversation history: {str(e)}")
            raise

    async def summarize_conversation(
        self,
        db: AsyncSession,
        conversation_id: int,
    ) -> Dict[str, Any]:
        """Generate AI summary of conversation.

        Args:
            db: Database session
            conversation_id: Conversation ID

        Returns:
            Conversation summary

        Raises:
            ValueError: If conversation not found
        """
        try:
            service = ConversationService(db)

            conversation = await service.get_conversation(conversation_id)
            if not conversation:
                raise ValueError(f"Conversation {conversation_id} not found")

            # Get conversation history
            messages = await service.get_conversation_history(conversation_id)

            # In production: Use Claude to summarize
            summary = f"Conversation with {conversation.message_count} messages on {conversation.created_at.date()}"
            key_topics = ["general inquiry"]
            action_items = []

            return {
                "conversation_id": conversation_id,
                "title": conversation.title or "Untitled",
                "summary": summary,
                "key_topics": key_topics,
                "action_items": action_items,
                "message_count": conversation.message_count,
                "generated_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error summarizing conversation: {str(e)}")
            raise

    async def get_suggested_prompts(self, user_role: str) -> List[Dict[str, Any]]:
        """Get suggested prompts/quick actions for a role.

        Args:
            user_role: User's role

        Returns:
            List of suggested prompts

        Raises:
            ValueError: If role not supported
        """
        try:
            if user_role not in self.ROLE_SYSTEM_PROMPTS:
                raise ValueError(f"Unsupported role: {user_role}")

            prompts_by_role = {
                "recruiter": [
                    {
                        "title": "Find Similar Candidates",
                        "prompt": "Find candidates similar to the one I just screened",
                        "icon": "people",
                    },
                    {
                        "title": "Generate Job Description",
                        "prompt": "Generate a job description for a senior developer role",
                        "icon": "document",
                    },
                    {
                        "title": "Negotiate Rate",
                        "prompt": "Help me negotiate the best rate for this candidate",
                        "icon": "handshake",
                    },
                ],
                "manager": [
                    {
                        "title": "Compare Candidates",
                        "prompt": "Compare these two candidates for the senior role",
                        "icon": "comparison",
                    },
                    {
                        "title": "Schedule Interviews",
                        "prompt": "Find the best time to schedule interviews this week",
                        "icon": "calendar",
                    },
                    {
                        "title": "Review Analytics",
                        "prompt": "Show me our hiring pipeline analytics",
                        "icon": "chart",
                    },
                ],
                "candidate": [
                    {
                        "title": "Search Jobs",
                        "prompt": "Find developer jobs matching my skills",
                        "icon": "search",
                    },
                    {
                        "title": "Prepare for Interview",
                        "prompt": "Help me prepare for my interview tomorrow",
                        "icon": "briefcase",
                    },
                    {
                        "title": "Review Offer",
                        "prompt": "Review this job offer and suggest negotiation points",
                        "icon": "document",
                    },
                ],
                "supplier": [
                    {
                        "title": "Find Requirements",
                        "prompt": "Show me open requirements I can fill",
                        "icon": "search",
                    },
                    {
                        "title": "Submit Candidate",
                        "prompt": "Help me submit a candidate for a requirement",
                        "icon": "upload",
                    },
                    {
                        "title": "View Performance",
                        "prompt": "Show my performance metrics this month",
                        "icon": "chart",
                    },
                ],
                "referrer": [
                    {
                        "title": "View Opportunities",
                        "prompt": "Show me the latest job opportunities",
                        "icon": "lightbulb",
                    },
                    {
                        "title": "Check Earnings",
                        "prompt": "What are my referral earnings this month?",
                        "icon": "coins",
                    },
                    {
                        "title": "Share Referral Link",
                        "prompt": "Generate a referral link to share",
                        "icon": "share",
                    },
                ],
                "admin": [
                    {
                        "title": "User Management",
                        "prompt": "Show me active users and recent activity",
                        "icon": "users",
                    },
                    {
                        "title": "System Health",
                        "prompt": "Check system health and performance",
                        "icon": "server",
                    },
                    {
                        "title": "Security Alerts",
                        "prompt": "Show me recent security alerts",
                        "icon": "lock",
                    },
                ],
            }

            return prompts_by_role.get(user_role, [])

        except Exception as e:
            logger.error(f"Error getting suggested prompts: {str(e)}")
            raise
