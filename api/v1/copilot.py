"""AI Copilot API endpoints."""

import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db
from schemas.copilot import (
    ChatRequest,
    ChatResponse,
    CopilotConversationCreate,
    CopilotConversationUpdate,
    CopilotConversationResponse,
    CopilotInsightResponse,
    RequirementAnalysisResponse,
    CandidateComparisonResponse,
    PipelineHealthResponse,
    CandidateSuggestionResponse,
    MarketInsightsResponse,
    OutreachEmailResponse,
    CandidateSummaryResponse,
    GeneratedInsightResponse,
)
from schemas.common import PaginatedResponse
from services.copilot_service import (
    CopilotConversationService,
    CopilotMessageService,
    CopilotInsightService,
)
from agents.copilot_agent import CopilotAgent
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/copilot", tags=["copilot"])
copilot_agent = CopilotAgent(anthropic_api_key=settings.anthropic_api_key)


# ===== CONVERSATION ENDPOINTS =====


@router.post("/conversations", response_model=CopilotConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation_data: CopilotConversationCreate,
    user_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
) -> CopilotConversationResponse:
    """Create new copilot conversation.

    Args:
        conversation_data: Conversation creation data
        user_id: User ID
        db: Database session

    Returns:
        Created conversation
    """
    try:
        service = CopilotConversationService(db)
        conversation = await service.create_conversation(conversation_data, user_id)
        return CopilotConversationResponse.from_orm(conversation)
    except Exception as e:
        logger.error(f"Error creating conversation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation",
        )


@router.get("/conversations/{conversation_id}", response_model=CopilotConversationResponse)
async def get_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
) -> CopilotConversationResponse:
    """Get conversation by ID.

    Args:
        conversation_id: Conversation ID
        db: Database session

    Returns:
        Conversation data
    """
    try:
        service = CopilotConversationService(db)
        conversation = await service.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )
        return CopilotConversationResponse.from_orm(conversation)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get conversation",
        )


@router.get("/conversations", response_model=PaginatedResponse[CopilotConversationResponse])
async def list_conversations(
    user_id: int = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[CopilotConversationResponse]:
    """List user's conversations.

    Args:
        user_id: User ID
        skip: Skip count
        limit: Result limit
        db: Database session

    Returns:
        Paginated conversations
    """
    try:
        service = CopilotConversationService(db)
        conversations, total = await service.get_conversations(
            user_id=user_id,
            skip=skip,
            limit=limit,
        )
        return PaginatedResponse(
            total=total,
            skip=skip,
            limit=limit,
            items=[CopilotConversationResponse.from_orm(c) for c in conversations],
        )
    except Exception as e:
        logger.error(f"Error listing conversations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list conversations",
        )


@router.put("/conversations/{conversation_id}", response_model=CopilotConversationResponse)
async def update_conversation(
    conversation_id: int,
    conversation_data: CopilotConversationUpdate,
    db: AsyncSession = Depends(get_db),
) -> CopilotConversationResponse:
    """Update conversation.

    Args:
        conversation_id: Conversation ID
        conversation_data: Update data
        db: Database session

    Returns:
        Updated conversation
    """
    try:
        service = CopilotConversationService(db)
        conversation = await service.update_conversation(
            conversation_id, conversation_data
        )
        return CopilotConversationResponse.from_orm(conversation)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error updating conversation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update conversation",
        )


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete conversation.

    Args:
        conversation_id: Conversation ID
        db: Database session
    """
    try:
        service = CopilotConversationService(db)
        await service.delete_conversation(conversation_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error deleting conversation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete conversation",
        )


# ===== CHAT ENDPOINTS =====


@router.post("/chat", response_model=ChatResponse)
async def chat(
    user_id: int = Query(...),
    chat_request: ChatRequest = None,
    message: str = Query(None),
    conversation_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    """Send message to copilot.

    Args:
        user_id: User ID
        chat_request: Chat request (if provided as body)
        message: Message text (if provided as query)
        conversation_id: Optional existing conversation
        db: Database session

    Returns:
        Chat response
    """
    try:
        # Support both request body and query string
        if chat_request:
            msg = chat_request.message
            conv_id = chat_request.conversation_id or conversation_id
        elif message:
            msg = message
            conv_id = conversation_id
        else:
            raise ValueError("Message is required")

        response = await copilot_agent.chat(
            db=db,
            user_id=user_id,
            message=msg,
            conversation_id=conv_id,
        )

        return ChatResponse(**response)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat",
        )


# ===== INSIGHT ENDPOINTS =====


@router.get("/insights", response_model=PaginatedResponse[CopilotInsightResponse])
async def list_insights(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    conversation_id: Optional[int] = None,
    insight_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[CopilotInsightResponse]:
    """List insights with filtering.

    Args:
        skip: Skip count
        limit: Result limit
        conversation_id: Filter by conversation
        insight_type: Filter by type
        entity_id: Filter by entity
        db: Database session

    Returns:
        Paginated insights
    """
    try:
        service = CopilotInsightService(db)
        insights, total = await service.get_insights(
            conversation_id=conversation_id,
            insight_type=insight_type,
            entity_id=entity_id,
            skip=skip,
            limit=limit,
        )
        return PaginatedResponse(
            total=total,
            skip=skip,
            limit=limit,
            items=[CopilotInsightResponse.from_orm(i) for i in insights],
        )
    except Exception as e:
        logger.error(f"Error listing insights: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list insights",
        )


@router.get("/insights/{insight_id}", response_model=CopilotInsightResponse)
async def get_insight(
    insight_id: int,
    db: AsyncSession = Depends(get_db),
) -> CopilotInsightResponse:
    """Get insight by ID.

    Args:
        insight_id: Insight ID
        db: Database session

    Returns:
        Insight data
    """
    try:
        service = CopilotInsightService(db)
        insight = await service.get_insight(insight_id)
        if not insight:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Insight not found",
            )
        return CopilotInsightResponse.from_orm(insight)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting insight: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get insight",
        )


@router.post("/insights/{insight_id}/mark-read", response_model=CopilotInsightResponse)
async def mark_insight_read(
    insight_id: int,
    db: AsyncSession = Depends(get_db),
) -> CopilotInsightResponse:
    """Mark insight as read.

    Args:
        insight_id: Insight ID
        db: Database session

    Returns:
        Updated insight
    """
    try:
        service = CopilotInsightService(db)
        insight = await service.mark_insight_read(insight_id)
        return CopilotInsightResponse.from_orm(insight)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error marking insight read: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark insight read",
        )


@router.get("/insights/unread")
async def get_unread_insights(
    conversation_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[CopilotInsightResponse]:
    """Get unread insights.

    Args:
        conversation_id: Optional filter by conversation
        skip: Skip count
        limit: Result limit
        db: Database session

    Returns:
        Paginated unread insights
    """
    try:
        service = CopilotInsightService(db)
        insights, total = await service.get_unread_insights(
            conversation_id=conversation_id,
            skip=skip,
            limit=limit,
        )
        return PaginatedResponse(
            total=total,
            skip=skip,
            limit=limit,
            items=[CopilotInsightResponse.from_orm(i) for i in insights],
        )
    except Exception as e:
        logger.error(f"Error getting unread insights: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get unread insights",
        )


# ===== COPILOT ANALYSIS ENDPOINTS =====


@router.get("/analyze/requirement/{requirement_id}", response_model=RequirementAnalysisResponse)
async def analyze_requirement(
    requirement_id: int,
    db: AsyncSession = Depends(get_db),
) -> RequirementAnalysisResponse:
    """Analyze requirement.

    Args:
        requirement_id: Requirement ID
        db: Database session

    Returns:
        Analysis data
    """
    try:
        analysis = await copilot_agent.analyze_requirement(db, requirement_id)
        return RequirementAnalysisResponse(**analysis)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error analyzing requirement: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze requirement",
        )


@router.post("/compare/candidates", response_model=CandidateComparisonResponse)
async def compare_candidates(
    candidate_ids: List[int] = Query(...),
    requirement_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
) -> CandidateComparisonResponse:
    """Compare candidates for requirement.

    Args:
        candidate_ids: List of candidate IDs
        requirement_id: Requirement ID
        db: Database session

    Returns:
        Comparison data
    """
    try:
        comparison = await copilot_agent.compare_candidates(
            db, candidate_ids, requirement_id
        )
        return CandidateComparisonResponse(**comparison)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error comparing candidates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to compare candidates",
        )


@router.get("/pipeline-health", response_model=PipelineHealthResponse)
async def get_pipeline_health(
    requirement_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
) -> PipelineHealthResponse:
    """Get pipeline health metrics.

    Args:
        requirement_id: Optional requirement ID
        db: Database session

    Returns:
        Pipeline health data
    """
    try:
        health = await copilot_agent.pipeline_health(db, requirement_id)
        return PipelineHealthResponse(**health)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error getting pipeline health: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get pipeline health",
        )


@router.get("/suggest-candidates", response_model=List[CandidateSuggestionResponse])
async def suggest_candidates(
    requirement_id: int = Query(...),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
) -> List[CandidateSuggestionResponse]:
    """Get candidate suggestions for requirement.

    Args:
        requirement_id: Requirement ID
        limit: Max candidates
        db: Database session

    Returns:
        Suggested candidates
    """
    try:
        suggestions = await copilot_agent.suggest_candidates(
            db, requirement_id, limit
        )
        return [CandidateSuggestionResponse(**s) for s in suggestions]
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error suggesting candidates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to suggest candidates",
        )


@router.get("/market-insights", response_model=MarketInsightsResponse)
async def get_market_insights(
    skills: List[str] = Query(...),
    location: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> MarketInsightsResponse:
    """Get market insights for skills.

    Args:
        skills: List of skills
        location: Optional location
        db: Database session

    Returns:
        Market insights
    """
    try:
        insights = await copilot_agent.market_insights(db, skills, location)
        return MarketInsightsResponse(**insights)
    except Exception as e:
        logger.error(f"Error getting market insights: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get market insights",
        )


@router.get("/draft-outreach", response_model=OutreachEmailResponse)
async def draft_outreach(
    candidate_id: int = Query(...),
    requirement_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
) -> OutreachEmailResponse:
    """Draft outreach email for candidate.

    Args:
        candidate_id: Candidate ID
        requirement_id: Requirement ID
        db: Database session

    Returns:
        Email draft
    """
    try:
        email = await copilot_agent.draft_outreach(db, candidate_id, requirement_id)
        return OutreachEmailResponse(**email)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error drafting outreach: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to draft outreach",
        )


@router.get("/summarize-candidate/{candidate_id}", response_model=CandidateSummaryResponse)
async def summarize_candidate(
    candidate_id: int,
    db: AsyncSession = Depends(get_db),
) -> CandidateSummaryResponse:
    """Get candidate summary.

    Args:
        candidate_id: Candidate ID
        db: Database session

    Returns:
        Candidate summary
    """
    try:
        summary = await copilot_agent.summarize_candidate(db, candidate_id)
        return CandidateSummaryResponse(**summary)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error summarizing candidate: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to summarize candidate",
        )


@router.post("/generate-insight", response_model=GeneratedInsightResponse)
async def generate_insight(
    insight_type: str = Query(...),
    entity_id: int = Query(...),
    conversation_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
) -> GeneratedInsightResponse:
    """Generate and store insight.

    Args:
        insight_type: Type of insight
        entity_id: Entity ID
        conversation_id: Optional conversation
        db: Database session

    Returns:
        Generated insight
    """
    try:
        insight = await copilot_agent.generate_insight(
            db, insight_type, entity_id, conversation_id
        )
        return GeneratedInsightResponse(**insight)
    except Exception as e:
        logger.error(f"Error generating insight: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate insight",
        )
