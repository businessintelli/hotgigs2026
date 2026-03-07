from enum import Enum


class OrganizationType(str, Enum):
    """Type of organization in the MSP ecosystem."""
    MSP = "msp"
    CLIENT = "client"
    SUPPLIER = "supplier"


class OrgOnboardingStatus(str, Enum):
    """Onboarding status for organizations."""
    NEW = "new"
    PENDING_REVIEW = "pending_review"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    OFFBOARDED = "offboarded"


class RequirementStatus(str, Enum):
    """Status of a job requirement."""
    DRAFT = "draft"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    FILLED = "filled"
    CANCELLED = "cancelled"
    CLOSED = "closed"


class CandidateStatus(str, Enum):
    """Status of a candidate in the pipeline."""
    SOURCED = "sourced"
    PARSED = "parsed"
    MATCHED = "matched"
    SCREENING = "screening"
    SCORED = "scored"
    READY_FOR_SUBMISSION = "ready_for_submission"
    SUBMITTED = "submitted"
    CUSTOMER_REVIEW = "customer_review"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEW_COMPLETE = "interview_complete"
    SELECTED = "selected"
    OFFER_EXTENDED = "offer_extended"
    OFFER_ACCEPTED = "offer_accepted"
    OFFER_DECLINED = "offer_declined"
    ONBOARDING = "onboarding"
    PLACED = "placed"
    REJECTED = "rejected"
    BACKOUT = "backout"
    TALENT_POOL = "talent_pool"


class MatchStatus(str, Enum):
    """Status of a candidate-requirement match."""
    PENDING = "pending"
    MATCHED = "matched"
    SHORTLISTED = "shortlisted"
    REJECTED = "rejected"


class InterviewType(str, Enum):
    """Type of interview."""
    AI_CHAT = "ai_chat"
    AI_VIDEO = "ai_video"
    PHONE_SCREEN = "phone_screen"
    VIDEO_CUSTOMER = "video_customer"
    ONSITE = "onsite"
    PANEL = "panel"


class InterviewStatus(str, Enum):
    """Status of an interview."""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class SubmissionStatus(str, Enum):
    """Status of a candidate submission."""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    SUBMITTED = "submitted"
    UNDER_CUSTOMER_REVIEW = "under_customer_review"
    SHORTLISTED = "shortlisted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class OfferStatus(str, Enum):
    """Status of a job offer."""
    DRAFT = "draft"
    SENT = "sent"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    NEGOTIATING = "negotiating"
    EXPIRED = "expired"
    REVOKED = "revoked"


class OnboardingStatus(str, Enum):
    """Status of candidate onboarding."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BACKOUT = "backout"


class SupplierTier(str, Enum):
    """Tier of a supplier."""
    PLATINUM = "platinum"
    GOLD = "gold"
    SILVER = "silver"
    BRONZE = "bronze"
    NEW = "new"
    STANDARD = "standard"


class UserRole(str, Enum):
    """Role of a platform user — expanded for multi-tenant VMS/MSP."""
    # Platform-level
    PLATFORM_ADMIN = "platform_admin"
    # MSP roles
    MSP_ADMIN = "msp_admin"
    MSP_MANAGER = "msp_manager"
    MSP_RECRUITER = "msp_recruiter"
    # Client roles
    CLIENT_ADMIN = "client_admin"
    CLIENT_MANAGER = "client_manager"
    CLIENT_VIEWER = "client_viewer"
    # Supplier roles
    SUPPLIER_ADMIN = "supplier_admin"
    SUPPLIER_RECRUITER = "supplier_recruiter"
    SUPPLIER_VIEWER = "supplier_viewer"
    # Legacy (keep for backward compatibility)
    ADMIN = "admin"
    MANAGER = "manager"
    RECRUITER = "recruiter"
    VIEWER = "viewer"


class Priority(str, Enum):
    """Priority level."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ContractStatus(str, Enum):
    """Status of a contract."""
    DRAFT = "draft"
    PENDING_SIGNATURE = "pending_signature"
    PARTIALLY_SIGNED = "partially_signed"
    COMPLETED = "completed"
    EXPIRED = "expired"
    VOIDED = "voided"


class ContractType(str, Enum):
    """Type of contract."""
    NDA = "nda"
    MSA = "msa"
    EMPLOYMENT_AGREEMENT = "employment_agreement"
    SOW = "sow"
    NON_COMPETE = "non_compete"
    CONSULTING_AGREEMENT = "consulting_agreement"
    CUSTOM = "custom"


class ContractSignatureStatus(str, Enum):
    """Status of a contract signature."""
    PENDING = "pending"
    SIGNED = "signed"
    DECLINED = "declined"
    EXPIRED = "expired"


class ContractAuditAction(str, Enum):
    """Actions tracked in contract audit trail."""
    CREATED = "created"
    SENT = "sent"
    VIEWED = "viewed"
    SIGNED = "signed"
    DECLINED = "declined"
    VOIDED = "voided"
    COMPLETED = "completed"
    REMINDED = "reminded"


class VideoType(str, Enum):
    """Type of candidate video."""
    INTRO = "intro"
    SKILLS_DEMO = "skills_demo"
    PROJECT_WALKTHROUGH = "project_walkthrough"


class AvailabilityStatus(str, Enum):
    """Candidate availability status."""
    IMMEDIATELY = "immediately"
    TWO_WEEKS = "2_weeks"
    ONE_MONTH = "1_month"
    NOT_LOOKING = "not_looking"


class ReferrerTier(str, Enum):
    """Tier of a referrer based on performance."""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


class ReferralStatus(str, Enum):
    """Status of a referral."""
    REFERRED = "referred"
    SCREENING = "screening"
    INTERVIEWED = "interviewed"
    SUBMITTED = "submitted"
    PLACED = "placed"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class BonusMilestone(str, Enum):
    """Referral bonus milestones."""
    INTERVIEWED = "interviewed"
    SUBMITTED = "submitted"
    PLACED = "placed"
    RETAINED_30D = "retained_30d"
    RETAINED_90D = "retained_90d"


class BonusStatus(str, Enum):
    """Status of a referral bonus."""
    PENDING = "pending"
    APPROVED = "approved"
    PAID = "paid"
    CANCELLED = "cancelled"


class TimesheetStatus(str, Enum):
    """Status of a timesheet."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"


class InvoiceStatus(str, Enum):
    """Status of an invoice."""
    DRAFT = "draft"
    SENT = "sent"
    VIEWED = "viewed"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    OVERDUE = "overdue"
    VOID = "void"


class PaymentStatus(str, Enum):
    """Status of a payment."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentType(str, Enum):
    """Type of payment."""
    CONTRACTOR_PAY = "contractor_pay"
    REFERRAL_BONUS = "referral_bonus"
    SUPPLIER_COMMISSION = "supplier_commission"
    EXPENSE_REIMBURSEMENT = "expense_reimbursement"


class PaymentMethodType(str, Enum):
    """Type of payment method."""
    BANK_ACCOUNT = "bank_account"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    WIRE = "wire"
    CHECK = "check"


class MessagingPlatform(str, Enum):
    """Messaging platform type."""
    SLACK = "slack"
    TEAMS = "teams"


class QBSyncStatus(str, Enum):
    """QuickBooks sync status."""
    PENDING = "pending"
    SYNCED = "synced"
    ERROR = "error"


# --- VMS/MSP Workflow Enums ---

class DistributionStatus(str, Enum):
    """Status of requirement distribution to a supplier."""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    FILLED = "filled"
    DECLINED = "declined"


class VMSSubmissionStatus(str, Enum):
    """Status of a supplier submission through the VMS pipeline."""
    SUBMITTED = "submitted"
    UNDER_MSP_REVIEW = "under_msp_review"
    MSP_APPROVED = "msp_approved"
    MSP_REJECTED = "msp_rejected"
    CHANGES_REQUESTED = "changes_requested"
    SUBMITTED_TO_CLIENT = "submitted_to_client"
    CLIENT_SHORTLISTED = "client_shortlisted"
    CLIENT_REJECTED = "client_rejected"
    INTERVIEW = "interview"
    OFFER = "offer"
    PLACED = "placed"
    WITHDRAWN = "withdrawn"


class MSPReviewDecision(str, Enum):
    """MSP review decision on a supplier submission."""
    APPROVE = "approve"
    REJECT = "reject"
    REQUEST_CHANGES = "request_changes"


class ClientFeedbackDecision(str, Enum):
    """Client feedback on MSP-submitted candidate."""
    SHORTLIST = "shortlist"
    REJECT = "reject"
    INTERVIEW = "interview"
    HOLD = "hold"


class PlacementStatus(str, Enum):
    """Status of a placement."""
    ACTIVE = "active"
    COMPLETED = "completed"
    TERMINATED = "terminated"
    EXTENDED = "extended"


class TimesheetFrequency(str, Enum):
    """Timesheet submission frequency."""
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"


class AuditAction(str, Enum):
    """Audit trail action types."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    SWITCH_ORG = "switch_org"
    DISTRIBUTE = "distribute"
    SUBMIT = "submit"
    REVIEW = "review"
    APPROVE = "approve"
    REJECT = "reject"
    FORWARD = "forward"
    FEEDBACK = "feedback"
