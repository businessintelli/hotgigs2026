"""Background Check (BGC), Onboarding, and role-based task workflow models."""
from datetime import datetime, date
from typing import Optional
from sqlalchemy import (
    String, DateTime, Date, Enum, JSON, ForeignKey, Text, Float, Integer,
    Boolean, Index, func
)
from sqlalchemy.orm import Mapped, mapped_column
from models.base import BaseModel
import enum


# ── Enums ──────────────────────────────────────────────────

class BGCStatus(str, enum.Enum):
    NOT_INITIATED = "not_initiated"
    INITIATED = "initiated"
    IN_PROGRESS = "in_progress"
    PENDING_REVIEW = "pending_review"
    PASSED = "passed"
    FAILED = "failed"
    CONDITIONAL = "conditional"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class BGCType(str, enum.Enum):
    CRIMINAL = "criminal"
    EMPLOYMENT = "employment"
    EDUCATION = "education"
    CREDIT = "credit"
    DRUG_SCREEN = "drug_screen"
    REFERENCE = "reference"
    IDENTITY = "identity"
    PROFESSIONAL_LICENSE = "professional_license"
    MVR = "motor_vehicle_record"
    GLOBAL = "global_screening"


class BGCResponsibility(str, enum.Enum):
    """Who is responsible for initiating/coordinating/completing BGC."""
    MSP_COORDINATOR = "msp_coordinator"
    SUPPLIER_COORDINATOR = "supplier_coordinator"
    CLIENT_COORDINATOR = "client_coordinator"
    VENDOR_DIRECT = "vendor_direct"


class OnboardingTaskStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PENDING_REVIEW = "pending_review"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    OVERDUE = "overdue"
    SKIPPED = "skipped"


class OnboardingTaskType(str, enum.Enum):
    DOCUMENT_COLLECTION = "document_collection"
    FORM_COMPLETION = "form_completion"
    TRAINING = "training"
    SYSTEM_ACCESS = "system_access"
    EQUIPMENT_SETUP = "equipment_setup"
    BADGE_ISSUANCE = "badge_issuance"
    ORIENTATION = "orientation"
    POLICY_ACKNOWLEDGMENT = "policy_acknowledgment"
    DIRECT_DEPOSIT = "direct_deposit"
    EMERGENCY_CONTACT = "emergency_contact"
    NDA_SIGNING = "nda_signing"
    CUSTOM = "custom"


class TaskOwnerRole(str, enum.Enum):
    """Who is responsible for a given onboarding task."""
    MSP_COORDINATOR = "msp_coordinator"
    MSP_HR = "msp_hr"
    SUPPLIER_COORDINATOR = "supplier_coordinator"
    SUPPLIER_HR = "supplier_hr"
    CLIENT_HIRING_MANAGER = "client_hiring_manager"
    CLIENT_IT = "client_it"
    CLIENT_HR = "client_hr"
    CLIENT_FACILITIES = "client_facilities"
    CANDIDATE = "candidate"
    SYSTEM_ADMIN_MSP = "system_admin_msp"
    SYSTEM_ADMIN_SUPPLIER = "system_admin_supplier"
    SYSTEM_ADMIN_CLIENT = "system_admin_client"


class DocumentCategory(str, enum.Enum):
    IDENTIFICATION = "identification"
    WORK_AUTHORIZATION = "work_authorization"
    TAX_FORMS = "tax_forms"
    INSURANCE = "insurance"
    CERTIFICATION = "certification"
    NDA = "nda"
    CONTRACT = "contract"
    POLICY_ACK = "policy_acknowledgment"
    EMERGENCY_INFO = "emergency_info"
    BANK_INFO = "bank_info"
    OTHER = "other"


# ── BGC Models ─────────────────────────────────────────────

class BGCPackage(BaseModel):
    """
    Pre-defined BGC package configurations — which checks to run.
    MSP sets up packages; supplier executes the actual work.
    """
    __tablename__ = "bgc_packages"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    package_name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    check_types: Mapped[Optional[dict]] = mapped_column(JSON)  # list of BGCType values
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    client_org_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("organizations.id"), nullable=True
    )  # NULL = available to all clients
    estimated_days: Mapped[int] = mapped_column(Integer, default=5)
    cost_estimate: Mapped[Optional[float]] = mapped_column(Float)
    vendor_name: Mapped[Optional[str]] = mapped_column(String(200))
    vendor_api_config: Mapped[Optional[dict]] = mapped_column(JSON)
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))


class BGCRequest(BaseModel):
    """
    Individual BGC request for a candidate/placement.
    MSP coordinates; supplier does actual work.
    """
    __tablename__ = "bgc_requests"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id"), nullable=False, index=True
    )
    placement_id: Mapped[Optional[int]] = mapped_column(index=True)
    package_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("bgc_packages.id"), nullable=True
    )
    # Status
    status: Mapped[str] = mapped_column(
        Enum(BGCStatus), default=BGCStatus.NOT_INITIATED, index=True
    )
    # Responsibility assignment
    initiated_by_role: Mapped[str] = mapped_column(
        Enum(BGCResponsibility), default=BGCResponsibility.MSP_COORDINATOR
    )
    coordinated_by_role: Mapped[str] = mapped_column(
        Enum(BGCResponsibility), default=BGCResponsibility.MSP_COORDINATOR
    )
    executed_by_role: Mapped[str] = mapped_column(
        Enum(BGCResponsibility), default=BGCResponsibility.SUPPLIER_COORDINATOR
    )
    # User assignments
    initiated_by_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    coordinated_by_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    executed_by_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    # Dates
    initiated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    due_date: Mapped[Optional[date]] = mapped_column(Date)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    # Vendor
    vendor_name: Mapped[Optional[str]] = mapped_column(String(200))
    vendor_reference_id: Mapped[Optional[str]] = mapped_column(String(255))
    vendor_report_url: Mapped[Optional[str]] = mapped_column(Text)
    # Results
    overall_result: Mapped[Optional[str]] = mapped_column(String(50))  # pass/fail/conditional
    adjudication_notes: Mapped[Optional[str]] = mapped_column(Text)
    risk_level: Mapped[Optional[str]] = mapped_column(String(50))
    # Metadata
    supplier_org_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("organizations.id"), nullable=True, index=True
    )
    client_org_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("organizations.id"), nullable=True, index=True
    )
    cost_actual: Mapped[Optional[float]] = mapped_column(Float)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    __table_args__ = (
        Index("ix_bgc_req_candidate_status", "candidate_id", "status"),
        Index("ix_bgc_req_org_status", "organization_id", "status"),
    )


class BGCCheckItem(BaseModel):
    """Individual check within a BGC request (e.g., criminal check, drug screen)."""
    __tablename__ = "bgc_check_items"

    bgc_request_id: Mapped[int] = mapped_column(
        ForeignKey("bgc_requests.id"), nullable=False, index=True
    )
    check_type: Mapped[str] = mapped_column(Enum(BGCType), nullable=False)
    status: Mapped[str] = mapped_column(
        Enum(BGCStatus), default=BGCStatus.NOT_INITIATED
    )
    result: Mapped[Optional[str]] = mapped_column(String(50))
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    findings: Mapped[Optional[str]] = mapped_column(Text)
    vendor_reference: Mapped[Optional[str]] = mapped_column(String(255))
    notes: Mapped[Optional[str]] = mapped_column(Text)


# ── Onboarding Models ──────────────────────────────────────

class OnboardingTemplate(BaseModel):
    """
    Reusable onboarding task template — defines what tasks to create per placement.
    """
    __tablename__ = "onboarding_templates"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    template_name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    client_org_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("organizations.id"), nullable=True
    )
    tasks_config: Mapped[Optional[dict]] = mapped_column(JSON)  # Pre-defined task list with roles
    estimated_days_to_complete: Mapped[int] = mapped_column(Integer, default=7)
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))


class OnboardingTask(BaseModel):
    """
    Individual onboarding task assigned to specific roles.
    Role determines who does the work (MSP coordinator, supplier, client IT, etc.)
    """
    __tablename__ = "onboarding_tasks"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    placement_id: Mapped[int] = mapped_column(nullable=False, index=True)
    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id"), nullable=False, index=True
    )
    template_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("onboarding_templates.id"), nullable=True
    )
    # Task details
    task_name: Mapped[str] = mapped_column(String(300), nullable=False)
    task_type: Mapped[str] = mapped_column(
        Enum(OnboardingTaskType), nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(Text)
    instructions: Mapped[Optional[str]] = mapped_column(Text)
    # Status
    status: Mapped[str] = mapped_column(
        Enum(OnboardingTaskStatus), default=OnboardingTaskStatus.NOT_STARTED, index=True
    )
    priority: Mapped[int] = mapped_column(Integer, default=2)  # 1=critical, 2=high, 3=medium, 4=low
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    # Role-based assignment
    owner_role: Mapped[str] = mapped_column(
        Enum(TaskOwnerRole), nullable=False
    )
    assigned_to_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    assigned_to_org_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("organizations.id"), nullable=True
    )  # Which org handles this task
    # Dates
    due_date: Mapped[Optional[date]] = mapped_column(Date)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    # Follow-up
    follow_up_count: Mapped[int] = mapped_column(Integer, default=0)
    last_follow_up_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    next_follow_up_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    # Dependencies
    depends_on_task_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("onboarding_tasks.id"), nullable=True
    )
    blocks_start_date: Mapped[bool] = mapped_column(Boolean, default=False)  # Must complete before placement starts
    # Metadata
    notes: Mapped[Optional[str]] = mapped_column(Text)
    attachments: Mapped[Optional[dict]] = mapped_column(JSON)  # file references

    __table_args__ = (
        Index("ix_onb_task_placement_status", "placement_id", "status"),
        Index("ix_onb_task_owner", "owner_role", "assigned_to_user_id"),
    )


class OnboardingDocument(BaseModel):
    """
    Documents collected during onboarding — tracked by category and status.
    """
    __tablename__ = "onboarding_documents"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    placement_id: Mapped[int] = mapped_column(nullable=False, index=True)
    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id"), nullable=False, index=True
    )
    task_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("onboarding_tasks.id"), nullable=True
    )
    # Document info
    document_name: Mapped[str] = mapped_column(String(300), nullable=False)
    category: Mapped[str] = mapped_column(Enum(DocumentCategory), nullable=False)
    file_url: Mapped[Optional[str]] = mapped_column(Text)
    file_type: Mapped[Optional[str]] = mapped_column(String(50))
    file_size_bytes: Mapped[Optional[int]] = mapped_column(Integer)
    # Status
    is_received: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verified_by_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    # Dates
    required_by: Mapped[Optional[date]] = mapped_column(Date)
    received_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[Optional[date]] = mapped_column(Date)
    # Owner
    collected_by_role: Mapped[Optional[str]] = mapped_column(Enum(TaskOwnerRole))
    notes: Mapped[Optional[str]] = mapped_column(Text)
