from .base import BaseModel, TenantBaseModel
from .enums import (
    OrganizationType,
    OrgOnboardingStatus,
    RequirementStatus,
    CandidateStatus,
    MatchStatus,
    InterviewType,
    InterviewStatus,
    SubmissionStatus,
    OfferStatus,
    OnboardingStatus,
    SupplierTier,
    UserRole,
    Priority,
    DistributionStatus,
    VMSSubmissionStatus,
    MSPReviewDecision,
    ClientFeedbackDecision,
    PlacementStatus,
    TimesheetFrequency,
    AuditAction,
    RateCardStatus,
    ComplianceStatus,
    ComplianceType,
    SLAMetric,
    SLASeverity,
    ExpenseStatus,
    ExpenseCategory,
    # Phase 2 Enums
    ActivityType,
    NoteType,
    CommunicationDirection,
    CommunicationChannel,
    # Phase 3 Enums
    JobOrderPriority,
    JobOrderDistribution,
    JobOrderStatus,
    OnboardingTaskType,
    OnboardingTaskStatus,
    InterviewRecommendation,
    # Phase 4 Enums
    SearchType,
    TriggerEvent,
    ActionType,
    NotificationType,
    NotificationCategory,
)
from .organization import Organization
from .customer import Customer
from .requirement import Requirement
from .candidate import Candidate
from .resume import Resume, ParsedResume
from .match import MatchScore
from .interview import Interview, InterviewFeedback
from .interview_intelligence import (
    InterviewRecording,
    InterviewTranscript,
    InterviewNote,
    CompetencyScore,
    InterviewAnalytics,
    InterviewQuestion,
    InterviewResponse,
)
from .submission import Submission
from .offer import Offer, Onboarding
from .supplier import Supplier, SupplierPerformance
from .user import User
from .audit import AuditLog
from .harvest import HarvestSource, HarvestJob, HarvestResult, CandidateSourceMapping
from .marketing import MarketingCampaign, Hotlist, CampaignDistribution, EmailCampaignTracking
from .alerts import AlertRule, Notification, NotificationPreference
from .tenant_management import (
    OrganizationMembership,
    OrganizationInvitation,
    OrganizationSettings,
    TenantAuditLog,
)
from .msp_workflow import (
    RequirementDistribution,
    SupplierCandidateSubmission,
    MSPReview,
    ClientFeedback,
    PlacementRecord,
)
from .crm import (
    CandidateActivity,
    CandidateNote,
    CandidateTag,
    CandidateTagAssociation,
    CommunicationLog,
)
from .ats import (
    JobOrder,
    OfferWorkflow,
    OnboardingTask,
    InterviewFeedback,
)
from .automation import (
    SavedSearch,
    AutomationRule,
    Notification,
)

__all__ = [
    "BaseModel",
    "TenantBaseModel",
    # Enums
    "OrganizationType",
    "OrgOnboardingStatus",
    "RequirementStatus",
    "CandidateStatus",
    "MatchStatus",
    "InterviewType",
    "InterviewStatus",
    "SubmissionStatus",
    "OfferStatus",
    "OnboardingStatus",
    "SupplierTier",
    "UserRole",
    "Priority",
    "DistributionStatus",
    "VMSSubmissionStatus",
    "MSPReviewDecision",
    "ClientFeedbackDecision",
    "PlacementStatus",
    "TimesheetFrequency",
    "AuditAction",
    "RateCardStatus",
    "ComplianceStatus",
    "ComplianceType",
    "SLAMetric",
    "SLASeverity",
    "ExpenseStatus",
    "ExpenseCategory",
    # Phase 2 Enums
    "ActivityType",
    "NoteType",
    "CommunicationDirection",
    "CommunicationChannel",
    # Phase 3 Enums
    "JobOrderPriority",
    "JobOrderDistribution",
    "JobOrderStatus",
    "OnboardingTaskType",
    "OnboardingTaskStatus",
    "InterviewRecommendation",
    # Phase 4 Enums
    "SearchType",
    "TriggerEvent",
    "ActionType",
    "NotificationType",
    "NotificationCategory",
    # Core entities
    "Organization",
    "Customer",
    "Requirement",
    "Candidate",
    "Resume",
    "ParsedResume",
    "MatchScore",
    "Interview",
    "InterviewFeedback",
    "InterviewRecording",
    "InterviewTranscript",
    "InterviewNote",
    "CompetencyScore",
    "InterviewAnalytics",
    "InterviewQuestion",
    "InterviewResponse",
    "Submission",
    "Offer",
    "Onboarding",
    "Supplier",
    "SupplierPerformance",
    "User",
    "AuditLog",
    "HarvestSource",
    "HarvestJob",
    "HarvestResult",
    "CandidateSourceMapping",
    "MarketingCampaign",
    "Hotlist",
    "CampaignDistribution",
    "EmailCampaignTracking",
    "AlertRule",
    "Notification",
    "NotificationPreference",
    # Tenant management
    "OrganizationMembership",
    "OrganizationInvitation",
    "OrganizationSettings",
    "TenantAuditLog",
    # VMS/MSP workflow
    "RequirementDistribution",
    "SupplierCandidateSubmission",
    "MSPReview",
    "ClientFeedback",
    "PlacementRecord",
    "RateCard",
    "RateCardEntry",
    "ComplianceRequirement",
    "ComplianceRecord",
    "ComplianceScore",
    "SLAConfiguration",
    "SLABreachRecord",
    "ExpenseEntry",
    # Phase 2: CRM Models
    "CandidateActivity",
    "CandidateNote",
    "CandidateTag",
    "CandidateTagAssociation",
    "CommunicationLog",
    # Phase 3: ATS Models
    "JobOrder",
    "OfferWorkflow",
    "OnboardingTask",
    # Phase 4: Automation & Search
    "SavedSearch",
    "AutomationRule",
    "Notification",
]
from models.rate_card import RateCard, RateCardEntry
from models.compliance import ComplianceRequirement, ComplianceRecord, ComplianceScore
from models.sla import SLAConfiguration, SLABreachRecord
from models.expense import ExpenseEntry
from models.automation import SavedSearch, AutomationRule, Notification
