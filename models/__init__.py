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
    # Import Job Enums
    ImportJobType,
    ImportJobStatus,
    # Custom Reports Enums
    ReportType,
    DeliveryMethod,
    ExportFormat,
    ReportScheduleStatus,
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
# Import automation before alerts to register Notification from automation (newer version)
from .automation import (
    SavedSearch,
    AutomationRule,
    Notification,
)
from .alerts import AlertRule, NotificationPreference
# Note: alerts.Notification is not imported here to avoid table name conflicts
# Services that need alerts.Notification will import it directly from models.alerts
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
from .import_job import ImportJob
from .custom_reports import SavedReport, ReportSchedule

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
    # Import Job Enums
    "ImportJobType",
    "ImportJobStatus",
    # Custom Reports Enums
    "ReportType",
    "DeliveryMethod",
    "ExportFormat",
    "ReportScheduleStatus",
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
    "NotificationPreference",
    # Note: Notification is exported from automation (newer version)
    # alerts.Notification is imported directly by alerts_service.py to avoid conflicts
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
    # Background Jobs
    "ImportJob",
    # Custom Reports
    "SavedReport",
    "ReportSchedule",
    # Automation Models (Notification from automation, not alerts)
    "Notification",
]
from models.rate_card import RateCard, RateCardEntry
from models.compliance import ComplianceRequirement, ComplianceRecord, ComplianceScore
from models.sla import SLAConfiguration, SLABreachRecord
from models.expense import ExpenseEntry
