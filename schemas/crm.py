"""CRM schemas for Candidate CRM module."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from models.enums import ActivityType, NoteType, CommunicationDirection, CommunicationChannel


# ── CandidateActivity Schemas ──

class CandidateActivityCreate(BaseModel):
    """Create candidate activity."""
    candidate_id: int
    activity_type: ActivityType
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    performed_by: Optional[int] = None
    metadata: Optional[dict] = Field(default_factory=dict)


class CandidateActivityUpdate(BaseModel):
    """Update candidate activity."""
    title: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[dict] = None


class CandidateActivityResponse(BaseModel):
    """Activity response."""
    id: int
    candidate_id: int
    activity_type: ActivityType
    title: str
    description: Optional[str]
    performed_by: Optional[int]
    metadata: Optional[dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── CandidateNote Schemas ──

class CandidateNoteCreate(BaseModel):
    """Create candidate note."""
    candidate_id: int
    author_id: int
    content: str = Field(..., min_length=1)
    note_type: NoteType = NoteType.GENERAL
    is_private: bool = False


class CandidateNoteUpdate(BaseModel):
    """Update candidate note."""
    content: Optional[str] = None
    note_type: Optional[NoteType] = None
    is_pinned: Optional[bool] = None
    is_private: Optional[bool] = None


class CandidateNoteResponse(BaseModel):
    """Note response."""
    id: int
    candidate_id: int
    author_id: int
    content: str
    note_type: NoteType
    is_pinned: bool
    is_private: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── CandidateTag Schemas ──

class CandidateTagCreate(BaseModel):
    """Create candidate tag."""
    name: str = Field(..., min_length=1, max_length=100)
    color: str = "3B82F6"
    description: Optional[str] = None


class CandidateTagUpdate(BaseModel):
    """Update candidate tag."""
    name: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None


class CandidateTagResponse(BaseModel):
    """Tag response."""
    id: int
    name: str
    color: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── CandidateTagAssociation Schemas ──

class CandidateTagAssociationCreate(BaseModel):
    """Assign tag to candidate."""
    candidate_id: int
    tag_id: int
    tagged_by: int


class CandidateTagAssociationResponse(BaseModel):
    """Tag association response."""
    id: int
    candidate_id: int
    tag_id: int
    tagged_by: int
    created_at: datetime

    class Config:
        from_attributes = True


# ── CommunicationLog Schemas ──

class CommunicationLogCreate(BaseModel):
    """Create communication log."""
    candidate_id: int
    direction: CommunicationDirection
    channel: CommunicationChannel
    subject: Optional[str] = None
    content: str = Field(..., min_length=1)
    sent_by: Optional[int] = None


class CommunicationLogUpdate(BaseModel):
    """Update communication log."""
    subject: Optional[str] = None
    content: Optional[str] = None


class CommunicationLogResponse(BaseModel):
    """Communication log response."""
    id: int
    candidate_id: int
    direction: CommunicationDirection
    channel: CommunicationChannel
    subject: Optional[str]
    content: str
    sent_by: Optional[int]
    sent_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# ── CRM Profile Summary ──

class CandidateCRMProfileResponse(BaseModel):
    """Complete CRM profile for a candidate."""
    candidate_id: int
    activities: List[CandidateActivityResponse]
    notes: List[CandidateNoteResponse]
    tags: List[CandidateTagResponse]
    communications: List[CommunicationLogResponse]
    profile_summary: dict = Field(
        default_factory=dict,
        description="Summary statistics (total_interactions, last_contact, etc.)",
    )
