"""Agreement & Document Repository Models — MSA, NDA, SOW, PO, and custom agreements.

Extends the base contract system with company-specific template management,
signatory authority configuration, e-signature workflows with review/change
request capabilities, and a full document repository per organization.
"""
import enum
from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, DateTime, Date, Numeric, Boolean,
    ForeignKey, Text, Enum as SAEnum, JSON,
)
from sqlalchemy.orm import relationship
from models.base import BaseModel


# ═══════════════════════════════════════════════════════════════
#  ENUMS
# ═══════════════════════════════════════════════════════════════

class AgreementType(str, enum.Enum):
    msa = "msa"                         # Master Service Agreement
    nda = "nda"                         # Non-Disclosure Agreement
    sow = "sow"                         # Statement of Work
    po = "po"                           # Purchase Order
    amendment = "amendment"             # Amendment to existing agreement
    addendum = "addendum"               # Addendum
    non_compete = "non_compete"         # Non-Compete Agreement
    ip_assignment = "ip_assignment"     # IP Assignment
    consulting = "consulting"           # Consulting Agreement
    staffing = "staffing"               # Staffing Agreement
    rate_card = "rate_card"             # Rate Card Agreement
    terms_conditions = "terms_conditions"  # General T&C
    custom = "custom"                   # Custom Agreement


class AgreementStatus(str, enum.Enum):
    draft = "draft"
    pending_review = "pending_review"
    changes_requested = "changes_requested"
    approved = "approved"
    pending_signature = "pending_signature"
    partially_signed = "partially_signed"
    fully_executed = "fully_executed"
    active = "active"
    expired = "expired"
    terminated = "terminated"
    voided = "voided"


class SignatureStatus(str, enum.Enum):
    pending = "pending"
    viewed = "viewed"
    signed = "signed"
    declined = "declined"
    change_requested = "change_requested"


class ChangeRequestStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"
    withdrawn = "withdrawn"


class TemplateCategory(str, enum.Enum):
    supplier = "supplier"
    client = "client"
    associate = "associate"
    partner = "partner"
    internal = "internal"
    general = "general"


# ═══════════════════════════════════════════════════════════════
#  SIGNATORY AUTHORITY (Company Admin configurable)
# ═══════════════════════════════════════════════════════════════

class SignatoryAuthority(BaseModel):
    __tablename__ = "signatory_authorities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(Integer, nullable=False)
    name = Column(String(200), nullable=False)
    designation = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False)
    phone = Column(String(50), nullable=True)
    signature_image = Column(Text, nullable=True)  # Base64 signature image
    initials_image = Column(Text, nullable=True)    # Base64 initials
    is_default = Column(Boolean, default=False)
    can_sign_types = Column(JSON, nullable=True)    # ["msa","nda","sow"] or null = all
    max_contract_value = Column(Numeric(14, 2), nullable=True)  # Signing authority limit
    is_active = Column(Boolean, default=True)


# ═══════════════════════════════════════════════════════════════
#  AGREEMENT TEMPLATE REPOSITORY (Company-specific)
# ═══════════════════════════════════════════════════════════════

class AgreementTemplate(BaseModel):
    __tablename__ = "agreement_templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    name = Column(String(300), nullable=False)
    agreement_type = Column(SAEnum(AgreementType), nullable=False)
    category = Column(SAEnum(TemplateCategory), default=TemplateCategory.general)
    description = Column(Text, nullable=True)
    content_html = Column(Text, nullable=False)     # Template with {{placeholders}}
    variables = Column(JSON, nullable=True)          # [{key, label, type, required, default}]
    header_html = Column(Text, nullable=True)        # Company letterhead
    footer_html = Column(Text, nullable=True)        # Footer with legal notices
    version = Column(String(20), default="1.0")
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)      # Default template for this type
    requires_witness = Column(Boolean, default=False)
    requires_notary = Column(Boolean, default=False)
    auto_sign_sender = Column(Boolean, default=True)  # Auto-apply sender's signature
    default_signatory_id = Column(Integer, ForeignKey("signatory_authorities.id"), nullable=True)
    tags = Column(JSON, nullable=True)
    created_by = Column(Integer, nullable=True)
    last_modified_by = Column(Integer, nullable=True)
    usage_count = Column(Integer, default=0)


# ═══════════════════════════════════════════════════════════════
#  AGREEMENT (Instance of a template sent to parties)
# ═══════════════════════════════════════════════════════════════

class Agreement(BaseModel):
    __tablename__ = "agreements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    agreement_number = Column(String(50), nullable=False, unique=True)
    template_id = Column(Integer, ForeignKey("agreement_templates.id"), nullable=True)
    agreement_type = Column(SAEnum(AgreementType), nullable=False)
    title = Column(String(500), nullable=False)
    status = Column(SAEnum(AgreementStatus), default=AgreementStatus.draft)

    # Parties
    sender_org_name = Column(String(300), nullable=False)
    sender_name = Column(String(200), nullable=False)
    sender_email = Column(String(200), nullable=False)
    sender_designation = Column(String(200), nullable=True)
    sender_address = Column(Text, nullable=True)
    sender_phone = Column(String(50), nullable=True)
    sender_signatory_id = Column(Integer, ForeignKey("signatory_authorities.id"), nullable=True)

    recipient_type = Column(String(50), nullable=True)  # company, individual
    recipient_org_name = Column(String(300), nullable=True)
    recipient_name = Column(String(200), nullable=False)
    recipient_email = Column(String(200), nullable=False)
    recipient_designation = Column(String(200), nullable=True)
    recipient_address = Column(Text, nullable=True)
    recipient_phone = Column(String(50), nullable=True)

    # Content
    content_html = Column(Text, nullable=False)
    metadata_json = Column(JSON, nullable=True)  # Filled variables, custom fields

    # Dates
    effective_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)
    signing_deadline = Column(DateTime, nullable=True)

    # Financial
    contract_value = Column(Numeric(14, 2), nullable=True)
    currency = Column(String(3), default="USD")

    # References
    parent_agreement_id = Column(Integer, ForeignKey("agreements.id"), nullable=True)
    client_id = Column(Integer, nullable=True)
    supplier_id = Column(Integer, nullable=True)
    associate_id = Column(Integer, nullable=True)

    # Signature tracking
    sender_signed = Column(Boolean, default=False)
    sender_signed_at = Column(DateTime, nullable=True)
    sender_signature_data = Column(Text, nullable=True)
    recipient_signed = Column(Boolean, default=False)
    recipient_signed_at = Column(DateTime, nullable=True)
    recipient_signature_data = Column(Text, nullable=True)
    recipient_signatory_name = Column(String(200), nullable=True)
    recipient_signatory_designation = Column(String(200), nullable=True)

    # Document
    document_path = Column(String(500), nullable=True)  # Generated PDF path
    sent_at = Column(DateTime, nullable=True)
    viewed_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)


# ═══════════════════════════════════════════════════════════════
#  CHANGE REQUESTS (Recipient requests modifications)
# ═══════════════════════════════════════════════════════════════

class AgreementChangeRequest(BaseModel):
    __tablename__ = "agreement_change_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agreement_id = Column(Integer, ForeignKey("agreements.id"), nullable=False)
    requested_by_email = Column(String(200), nullable=False)
    requested_by_name = Column(String(200), nullable=False)
    section = Column(String(200), nullable=True)      # Which section
    original_text = Column(Text, nullable=True)
    proposed_text = Column(Text, nullable=True)
    reason = Column(Text, nullable=True)
    status = Column(SAEnum(ChangeRequestStatus), default=ChangeRequestStatus.pending)
    reviewed_by = Column(String(200), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    review_notes = Column(Text, nullable=True)


# ═══════════════════════════════════════════════════════════════
#  AUDIT TRAIL
# ═══════════════════════════════════════════════════════════════

class AgreementAuditTrail(BaseModel):
    __tablename__ = "agreement_audit_trails"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agreement_id = Column(Integer, ForeignKey("agreements.id"), nullable=False)
    action = Column(String(100), nullable=False)
    actor_name = Column(String(200), nullable=False)
    actor_email = Column(String(200), nullable=False)
    ip_address = Column(String(50), nullable=True)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
