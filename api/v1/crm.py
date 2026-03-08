"""Candidate CRM API endpoints."""

import logging
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db
from schemas.crm import (
    CandidateActivityCreate,
    CandidateActivityResponse,
    CandidateNoteCreate,
    CandidateNoteUpdate,
    CandidateNoteResponse,
    CandidateTagCreate,
    CandidateTagResponse,
    CandidateTagAssociationCreate,
    CandidateTagAssociationResponse,
    CommunicationLogCreate,
    CommunicationLogResponse,
    CandidateCRMProfileResponse,
)
from schemas.common import PaginatedResponse
from models.crm import (
    CandidateActivity,
    CandidateNote,
    CandidateTag,
    CandidateTagAssociation,
    CommunicationLog,
)
from models.enums import NoteType, CommunicationChannel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/crm", tags=["Candidate CRM"])


# ── Activity Management ──

@router.post("/candidates/{candidate_id}/activities", response_model=CandidateActivityResponse, status_code=status.HTTP_201_CREATED)
async def log_activity(
    candidate_id: int,
    activity_data: CandidateActivityCreate,
    db: AsyncSession = Depends(get_db),
) -> CandidateActivityResponse:
    """Log an activity for a candidate.

    Args:
        candidate_id: Candidate ID
        activity_data: Activity data
        db: Database session

    Returns:
        Created activity
    """
    try:
        activity = CandidateActivity(
            candidate_id=candidate_id,
            activity_type=activity_data.activity_type,
            title=activity_data.title,
            description=activity_data.description,
            performed_by=activity_data.performed_by,
            metadata=activity_data.metadata or {},
        )
        db.add(activity)
        await db.commit()
        await db.refresh(activity)
        return CandidateActivityResponse.from_orm(activity)
    except Exception as e:
        logger.error(f"Error logging activity: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to log activity",
        )


@router.get("/candidates/{candidate_id}/timeline", response_model=PaginatedResponse[CandidateActivityResponse])
async def get_activity_timeline(
    candidate_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[CandidateActivityResponse]:
    """Get full activity timeline for a candidate (sorted by date desc).

    Args:
        candidate_id: Candidate ID
        skip: Skip count
        limit: Result limit
        db: Database session

    Returns:
        Paginated activities
    """
    try:
        from sqlalchemy import select, func, desc

        # Get total count
        count_query = select(func.count()).select_from(CandidateActivity).where(
            CandidateActivity.candidate_id == candidate_id
        )
        total = await db.scalar(count_query)

        # Get activities sorted by date descending
        query = select(CandidateActivity).where(
            CandidateActivity.candidate_id == candidate_id
        ).order_by(desc(CandidateActivity.created_at)).offset(skip).limit(limit)

        result = await db.execute(query)
        activities = result.scalars().all()

        return PaginatedResponse(
            total=total or 0,
            skip=skip,
            limit=limit,
            items=[CandidateActivityResponse.from_orm(a) for a in activities],
        )
    except Exception as e:
        logger.error(f"Error getting timeline: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get timeline",
        )


# ── Note Management ──

@router.post("/candidates/{candidate_id}/notes", response_model=CandidateNoteResponse, status_code=status.HTTP_201_CREATED)
async def add_note(
    candidate_id: int,
    note_data: CandidateNoteCreate,
    db: AsyncSession = Depends(get_db),
) -> CandidateNoteResponse:
    """Add a note to a candidate.

    Args:
        candidate_id: Candidate ID
        note_data: Note data
        db: Database session

    Returns:
        Created note
    """
    try:
        note = CandidateNote(
            candidate_id=candidate_id,
            author_id=note_data.author_id,
            content=note_data.content,
            note_type=note_data.note_type,
            is_private=note_data.is_private,
        )
        db.add(note)
        await db.commit()
        await db.refresh(note)
        return CandidateNoteResponse.from_orm(note)
    except Exception as e:
        logger.error(f"Error adding note: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add note",
        )


@router.get("/candidates/{candidate_id}/notes", response_model=PaginatedResponse[CandidateNoteResponse])
async def list_notes(
    candidate_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    note_type: Optional[NoteType] = None,
    pinned_only: bool = False,
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[CandidateNoteResponse]:
    """List notes for a candidate with filtering.

    Args:
        candidate_id: Candidate ID
        skip: Skip count
        limit: Result limit
        note_type: Filter by note type
        pinned_only: Show only pinned notes
        db: Database session

    Returns:
        Paginated notes
    """
    try:
        from sqlalchemy import select, func, desc

        # Build query
        query = select(CandidateNote).where(CandidateNote.candidate_id == candidate_id)

        if note_type:
            query = query.where(CandidateNote.note_type == note_type)

        if pinned_only:
            query = query.where(CandidateNote.is_pinned == True)

        # Get total
        count_query = select(func.count()).select_from(CandidateNote).where(
            CandidateNote.candidate_id == candidate_id
        )
        if note_type:
            count_query = count_query.where(CandidateNote.note_type == note_type)
        if pinned_only:
            count_query = count_query.where(CandidateNote.is_pinned == True)

        total = await db.scalar(count_query)

        # Execute query
        query = query.order_by(desc(CandidateNote.created_at)).offset(skip).limit(limit)
        result = await db.execute(query)
        notes = result.scalars().all()

        return PaginatedResponse(
            total=total or 0,
            skip=skip,
            limit=limit,
            items=[CandidateNoteResponse.from_orm(n) for n in notes],
        )
    except Exception as e:
        logger.error(f"Error listing notes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list notes",
        )


@router.put("/candidates/{candidate_id}/notes/{note_id}", response_model=CandidateNoteResponse)
async def update_note(
    candidate_id: int,
    note_id: int,
    note_data: CandidateNoteUpdate,
    db: AsyncSession = Depends(get_db),
) -> CandidateNoteResponse:
    """Update a note (pin/unpin, edit content).

    Args:
        candidate_id: Candidate ID
        note_id: Note ID
        note_data: Update data
        db: Database session

    Returns:
        Updated note
    """
    try:
        from sqlalchemy import select

        # Get note
        query = select(CandidateNote).where(
            CandidateNote.id == note_id,
            CandidateNote.candidate_id == candidate_id,
        )
        result = await db.execute(query)
        note = result.scalar_one_or_none()

        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found",
            )

        # Update fields
        if note_data.content is not None:
            note.content = note_data.content
        if note_data.note_type is not None:
            note.note_type = note_data.note_type
        if note_data.is_pinned is not None:
            note.is_pinned = note_data.is_pinned
        if note_data.is_private is not None:
            note.is_private = note_data.is_private

        await db.commit()
        await db.refresh(note)
        return CandidateNoteResponse.from_orm(note)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating note: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update note",
        )


# ── Tag Management ──

@router.post("/tags", response_model=CandidateTagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_data: CandidateTagCreate,
    db: AsyncSession = Depends(get_db),
) -> CandidateTagResponse:
    """Create a tag.

    Args:
        tag_data: Tag data
        db: Database session

    Returns:
        Created tag
    """
    try:
        tag = CandidateTag(
            name=tag_data.name,
            color=tag_data.color,
            description=tag_data.description,
        )
        db.add(tag)
        await db.commit()
        await db.refresh(tag)
        return CandidateTagResponse.from_orm(tag)
    except Exception as e:
        logger.error(f"Error creating tag: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create tag",
        )


@router.get("/tags", response_model=List[CandidateTagResponse])
async def list_tags(
    db: AsyncSession = Depends(get_db),
) -> List[CandidateTagResponse]:
    """List all tags.

    Args:
        db: Database session

    Returns:
        List of tags
    """
    try:
        from sqlalchemy import select

        query = select(CandidateTag).order_by(CandidateTag.name)
        result = await db.execute(query)
        tags = result.scalars().all()
        return [CandidateTagResponse.from_orm(t) for t in tags]
    except Exception as e:
        logger.error(f"Error listing tags: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list tags",
        )


@router.post("/candidates/{candidate_id}/tags", response_model=CandidateTagAssociationResponse, status_code=status.HTTP_201_CREATED)
async def assign_tag(
    candidate_id: int,
    assoc_data: CandidateTagAssociationCreate,
    db: AsyncSession = Depends(get_db),
) -> CandidateTagAssociationResponse:
    """Assign a tag to a candidate.

    Args:
        candidate_id: Candidate ID
        assoc_data: Association data
        db: Database session

    Returns:
        Created association
    """
    try:
        assoc = CandidateTagAssociation(
            candidate_id=candidate_id,
            tag_id=assoc_data.tag_id,
            tagged_by=assoc_data.tagged_by,
        )
        db.add(assoc)
        await db.commit()
        await db.refresh(assoc)
        return CandidateTagAssociationResponse.from_orm(assoc)
    except Exception as e:
        logger.error(f"Error assigning tag: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to assign tag",
        )


@router.delete("/candidates/{candidate_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_tag(
    candidate_id: int,
    tag_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Remove a tag from a candidate.

    Args:
        candidate_id: Candidate ID
        tag_id: Tag ID
        db: Database session
    """
    try:
        from sqlalchemy import select

        query = select(CandidateTagAssociation).where(
            CandidateTagAssociation.candidate_id == candidate_id,
            CandidateTagAssociation.tag_id == tag_id,
        )
        result = await db.execute(query)
        assoc = result.scalar_one_or_none()

        if not assoc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag association not found",
            )

        await db.delete(assoc)
        await db.commit()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing tag: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove tag",
        )


# ── Communication Management ──

@router.post("/candidates/{candidate_id}/communications", response_model=CommunicationLogResponse, status_code=status.HTTP_201_CREATED)
async def log_communication(
    candidate_id: int,
    comm_data: CommunicationLogCreate,
    db: AsyncSession = Depends(get_db),
) -> CommunicationLogResponse:
    """Log a communication with a candidate.

    Args:
        candidate_id: Candidate ID
        comm_data: Communication data
        db: Database session

    Returns:
        Created communication log
    """
    try:
        comm = CommunicationLog(
            candidate_id=candidate_id,
            direction=comm_data.direction,
            channel=comm_data.channel,
            subject=comm_data.subject,
            content=comm_data.content,
            sent_by=comm_data.sent_by,
            sent_at=datetime.utcnow(),
        )
        db.add(comm)
        await db.commit()
        await db.refresh(comm)
        return CommunicationLogResponse.from_orm(comm)
    except Exception as e:
        logger.error(f"Error logging communication: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to log communication",
        )


@router.get("/candidates/{candidate_id}/communications", response_model=PaginatedResponse[CommunicationLogResponse])
async def list_communications(
    candidate_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    channel: Optional[CommunicationChannel] = None,
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[CommunicationLogResponse]:
    """List communications for a candidate with filtering.

    Args:
        candidate_id: Candidate ID
        skip: Skip count
        limit: Result limit
        channel: Filter by channel
        db: Database session

    Returns:
        Paginated communications
    """
    try:
        from sqlalchemy import select, func, desc

        query = select(CommunicationLog).where(CommunicationLog.candidate_id == candidate_id)

        if channel:
            query = query.where(CommunicationLog.channel == channel)

        # Get total
        count_query = select(func.count()).select_from(CommunicationLog).where(
            CommunicationLog.candidate_id == candidate_id
        )
        if channel:
            count_query = count_query.where(CommunicationLog.channel == channel)

        total = await db.scalar(count_query)

        # Execute query
        query = query.order_by(desc(CommunicationLog.sent_at)).offset(skip).limit(limit)
        result = await db.execute(query)
        comms = result.scalars().all()

        return PaginatedResponse(
            total=total or 0,
            skip=skip,
            limit=limit,
            items=[CommunicationLogResponse.from_orm(c) for c in comms],
        )
    except Exception as e:
        logger.error(f"Error listing communications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list communications",
        )


# ── CRM Profile Summary ──

@router.get("/candidates/{candidate_id}/profile-summary", response_model=CandidateCRMProfileResponse)
async def get_profile_summary(
    candidate_id: int,
    db: AsyncSession = Depends(get_db),
) -> CandidateCRMProfileResponse:
    """Get complete CRM profile for a candidate.

    Args:
        candidate_id: Candidate ID
        db: Database session

    Returns:
        Complete CRM profile
    """
    try:
        from sqlalchemy import select, desc

        # Get recent activities (limit to 10)
        activities_query = select(CandidateActivity).where(
            CandidateActivity.candidate_id == candidate_id
        ).order_by(desc(CandidateActivity.created_at)).limit(10)
        activities_result = await db.execute(activities_query)
        activities = activities_result.scalars().all()

        # Get notes (limit to 10)
        notes_query = select(CandidateNote).where(
            CandidateNote.candidate_id == candidate_id
        ).order_by(desc(CandidateNote.created_at)).limit(10)
        notes_result = await db.execute(notes_query)
        notes = notes_result.scalars().all()

        # Get tags
        tags_query = select(CandidateTag).join(CandidateTagAssociation).where(
            CandidateTagAssociation.candidate_id == candidate_id
        )
        tags_result = await db.execute(tags_query)
        tags = tags_result.scalars().all()

        # Get communications (limit to 10)
        comms_query = select(CommunicationLog).where(
            CommunicationLog.candidate_id == candidate_id
        ).order_by(desc(CommunicationLog.sent_at)).limit(10)
        comms_result = await db.execute(comms_query)
        comms = comms_result.scalars().all()

        # Calculate summary stats
        summary_stats = {
            "total_activities": len(activities),
            "total_notes": len(notes),
            "total_tags": len(tags),
            "total_communications": len(comms),
            "last_activity": activities[0].created_at.isoformat() if activities else None,
            "last_note": notes[0].created_at.isoformat() if notes else None,
            "last_communication": comms[0].sent_at.isoformat() if comms else None,
        }

        return CandidateCRMProfileResponse(
            candidate_id=candidate_id,
            activities=[CandidateActivityResponse.from_orm(a) for a in activities],
            notes=[CandidateNoteResponse.from_orm(n) for n in notes],
            tags=[CandidateTagResponse.from_orm(t) for t in tags],
            communications=[CommunicationLogResponse.from_orm(c) for c in comms],
            profile_summary=summary_stats,
        )
    except Exception as e:
        logger.error(f"Error getting profile summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get profile summary",
        )
