from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Any, Dict
from enum import Enum
import json


class EventType(str, Enum):
    """All event types in the system."""

    # Requirement events
    REQUIREMENT_CREATED = "requirement.created"
    REQUIREMENT_UPDATED = "requirement.updated"
    REQUIREMENT_ACTIVATED = "requirement.activated"
    REQUIREMENT_CLOSED = "requirement.closed"

    # Candidate events
    CANDIDATE_CREATED = "candidate.created"
    CANDIDATE_UPDATED = "candidate.updated"
    RESUME_UPLOADED = "resume.uploaded"
    RESUME_PARSED = "resume.parsed"

    # Match events
    MATCH_COMPUTED = "match.computed"
    MATCH_SHORTLISTED = "match.shortlisted"
    MATCH_REJECTED = "match.rejected"

    # Interview events
    INTERVIEW_SCHEDULED = "interview.scheduled"
    INTERVIEW_STARTED = "interview.started"
    INTERVIEW_COMPLETED = "interview.completed"
    INTERVIEW_CANCELLED = "interview.cancelled"
    FEEDBACK_GENERATED = "feedback.generated"

    # Submission events
    SUBMISSION_CREATED = "submission.created"
    SUBMISSION_APPROVED = "submission.approved"
    SUBMISSION_SENT = "submission.sent"
    SUBMISSION_REJECTED = "submission.rejected"
    SUBMISSION_WITHDRAWN = "submission.withdrawn"

    # Offer events
    OFFER_CREATED = "offer.created"
    OFFER_SENT = "offer.sent"
    OFFER_ACCEPTED = "offer.accepted"
    OFFER_DECLINED = "offer.declined"
    OFFER_NEGOTIATING = "offer.negotiating"

    # Onboarding events
    ONBOARDING_STARTED = "onboarding.started"
    ONBOARDING_COMPLETED = "onboarding.completed"
    ONBOARDING_BACKOUT = "onboarding.backout"
    PLACEMENT_CONFIRMED = "placement.confirmed"

    # Supplier events
    SUPPLIER_REQUIREMENT_DISTRIBUTED = "supplier.requirement_distributed"
    SUPPLIER_SUBMISSION_RECEIVED = "supplier.submission_received"

    # System events
    SYSTEM_HEALTH_CHECK = "system.health_check"
    SYSTEM_ERROR = "system.error"


class Event(BaseModel):
    """Base event model."""

    event_type: EventType = Field(description="Type of event")
    event_id: str = Field(description="Unique event identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    source_agent: str = Field(description="Name of the agent that emitted the event")
    entity_id: int = Field(description="ID of the entity related to the event")
    entity_type: str = Field(description="Type of entity (requirement, candidate, etc.)")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Event-specific data")
    correlation_id: Optional[str] = Field(default=None, description="Correlation ID for tracing")
    user_id: Optional[int] = Field(default=None, description="User who triggered the event")
    retry_count: int = Field(default=0, ge=0, description="Number of retries")
    max_retries: int = Field(default=3, ge=0, description="Maximum number of retries")

    def to_json(self) -> str:
        """Serialize event to JSON string."""
        return self.model_dump_json()

    @classmethod
    def from_json(cls, json_str: str) -> "Event":
        """Deserialize event from JSON string."""
        return cls(**json.loads(json_str))

    @property
    def should_retry(self) -> bool:
        """Check if event should be retried."""
        return self.retry_count < self.max_retries


class RequirementCreatedEvent(Event):
    """Emitted when a requirement is created."""

    event_type: EventType = EventType.REQUIREMENT_CREATED


class RequirementUpdatedEvent(Event):
    """Emitted when a requirement is updated."""

    event_type: EventType = EventType.REQUIREMENT_UPDATED


class RequirementActivatedEvent(Event):
    """Emitted when a requirement is activated."""

    event_type: EventType = EventType.REQUIREMENT_ACTIVATED


class CandidateCreatedEvent(Event):
    """Emitted when a candidate is created."""

    event_type: EventType = EventType.CANDIDATE_CREATED


class ResumeUploadedEvent(Event):
    """Emitted when a resume is uploaded."""

    event_type: EventType = EventType.RESUME_UPLOADED


class ResumeParsedEvent(Event):
    """Emitted when a resume is parsed."""

    event_type: EventType = EventType.RESUME_PARSED


class MatchComputedEvent(Event):
    """Emitted when a match score is computed."""

    event_type: EventType = EventType.MATCH_COMPUTED


class InterviewScheduledEvent(Event):
    """Emitted when an interview is scheduled."""

    event_type: EventType = EventType.INTERVIEW_SCHEDULED


class InterviewCompletedEvent(Event):
    """Emitted when an interview is completed."""

    event_type: EventType = EventType.INTERVIEW_COMPLETED


class FeedbackGeneratedEvent(Event):
    """Emitted when interview feedback is generated."""

    event_type: EventType = EventType.FEEDBACK_GENERATED


class SubmissionCreatedEvent(Event):
    """Emitted when a submission is created."""

    event_type: EventType = EventType.SUBMISSION_CREATED


class SubmissionSentEvent(Event):
    """Emitted when a submission is sent to customer."""

    event_type: EventType = EventType.SUBMISSION_SENT


class OfferSentEvent(Event):
    """Emitted when an offer is sent."""

    event_type: EventType = EventType.OFFER_SENT


class OfferAcceptedEvent(Event):
    """Emitted when an offer is accepted."""

    event_type: EventType = EventType.OFFER_ACCEPTED


class OnboardingStartedEvent(Event):
    """Emitted when onboarding starts."""

    event_type: EventType = EventType.ONBOARDING_STARTED


class PlacementConfirmedEvent(Event):
    """Emitted when placement is confirmed."""

    event_type: EventType = EventType.PLACEMENT_CONFIRMED


class SupplierRequirementDistributedEvent(Event):
    """Emitted when a requirement is distributed to suppliers."""

    event_type: EventType = EventType.SUPPLIER_REQUIREMENT_DISTRIBUTED
