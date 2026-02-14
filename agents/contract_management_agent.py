import logging
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from agents.base_agent import BaseAgent
from models.contract import (
    Contract,
    ContractTemplate,
    ContractSignature,
    ContractAuditTrail,
)
from schemas.contract import (
    ContractSchema,
    ContractFromTemplateSchema,
    ContractSignerSchema,
    ContractVoidSchema,
    ContractRenewSchema,
)
from models.enums import (
    ContractStatus,
    ContractType,
    ContractSignatureStatus,
    ContractAuditAction,
)

logger = logging.getLogger(__name__)


class ContractManagementAgent(BaseAgent):
    """Manages contract lifecycle including e-signatures and document management."""

    def __init__(self):
        """Initialize contract management agent."""
        super().__init__("ContractManagementAgent", "1.0.0")
        self.signing_token_expiry_days = 30

    async def create_contract(
        self, db: AsyncSession, contract_data: Dict[str, Any], user_id: int
    ) -> Contract:
        """Create a new contract from provided data.

        Args:
            db: Database session
            contract_data: Contract data dictionary
            user_id: ID of user creating the contract

        Returns:
            Created Contract object

        Raises:
            ValueError: If contract data is invalid
        """
        try:
            # Extract and validate data
            contract_type = contract_data.get("contract_type", ContractType.CUSTOM.value)
            title = contract_data.get("title")
            content = contract_data.get("content")
            parties = contract_data.get("parties", [])

            if not title or not content:
                raise ValueError("Title and content are required")

            # Create contract
            contract = Contract(
                contract_type=contract_type,
                title=title,
                content=content,
                parties=parties,
                status=ContractStatus.DRAFT.value,
                candidate_id=contract_data.get("candidate_id"),
                customer_id=contract_data.get("customer_id"),
                supplier_id=contract_data.get("supplier_id"),
                requirement_id=contract_data.get("requirement_id"),
                offer_id=contract_data.get("offer_id"),
                effective_date=contract_data.get("effective_date"),
                expiry_date=contract_data.get("expiry_date"),
                auto_renew=contract_data.get("auto_renew", False),
                renewal_terms=contract_data.get("renewal_terms"),
                signing_order=contract_data.get("signing_order", "parallel"),
                metadata=contract_data.get("metadata", {}),
                created_by_id=user_id,
            )

            db.add(contract)
            await db.flush()

            # Log to audit trail
            await self._add_audit_trail(
                db,
                contract.id,
                ContractAuditAction.CREATED.value,
                user_id,
                {"contract_type": contract_type, "title": title},
            )

            await db.commit()
            logger.info(f"Created contract {contract.id} of type {contract_type}")

            await self.emit_event(
                event_type="contract_created",
                entity_type="contract",
                entity_id=contract.id,
                payload={"contract_type": contract_type, "title": title},
                user_id=user_id,
            )

            return contract

        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating contract: {str(e)}")
            raise

    async def generate_from_template(
        self,
        db: AsyncSession,
        template_type: str,
        context: Dict[str, Any],
        user_id: int,
    ) -> str:
        """Generate contract content from template using LLM.

        Args:
            db: Database session
            template_type: Type of template to use
            context: Context data for template rendering
            user_id: ID of user generating contract

        Returns:
            Generated contract content

        Raises:
            ValueError: If template not found
        """
        try:
            # Fetch template
            query = select(ContractTemplate).where(
                and_(
                    ContractTemplate.template_type == template_type,
                    ContractTemplate.is_active == True,
                )
            )
            result = await db.execute(query)
            template = result.scalars().first()

            if not template:
                raise ValueError(f"Template not found for type: {template_type}")

            # Use Anthropic API to generate contract from template
            try:
                from anthropic import Anthropic

                client = Anthropic()
                prompt = f"""You are a professional contract writer.
Generate a contract based on the following template and context.

Template Type: {template_type}
Template Content:
{template.content}

Context Data:
{self._format_context(context)}

Generate a professional, complete contract document incorporating all provided information.
Ensure all placeholders are filled with actual values from the context."""

                message = client.messages.create(
                    model="claude-opus-4-6",
                    max_tokens=4096,
                    messages=[{"role": "user", "content": prompt}],
                )

                generated_content = message.content[0].text
                logger.info(f"Generated contract from template {template_type}")

                return generated_content

            except ImportError:
                # Fallback: simple template rendering
                logger.warning("Anthropic SDK not available, using simple template rendering")
                return self._simple_template_render(template.content, context)

        except Exception as e:
            logger.error(f"Error generating contract from template: {str(e)}")
            raise

    async def send_for_signature(
        self,
        db: AsyncSession,
        contract_id: int,
        signers: List[Dict[str, Any]],
        user_id: int,
    ) -> Dict[str, Any]:
        """Send contract to signers with e-signature links.

        Args:
            db: Database session
            contract_id: ID of contract
            signers: List of signer data
            user_id: ID of user sending contract

        Returns:
            Dictionary with sending results

        Raises:
            ValueError: If contract not found or invalid
        """
        try:
            # Fetch contract
            contract = await db.get(Contract, contract_id)
            if not contract:
                raise ValueError(f"Contract {contract_id} not found")

            signing_order = 1
            created_signatures = []

            for signer in signers:
                # Generate unique signing token
                signing_token = self._generate_signing_token()
                token_expires_at = datetime.utcnow() + timedelta(
                    days=self.signing_token_expiry_days
                )

                # Create signature record
                signature = ContractSignature(
                    contract_id=contract_id,
                    signer_name=signer.get("signer_name"),
                    signer_email=signer.get("signer_email"),
                    signer_role=signer.get("signer_role"),
                    signing_token=signing_token,
                    token_expires_at=token_expires_at,
                    status=ContractSignatureStatus.PENDING.value,
                    signing_order=signing_order,
                )

                db.add(signature)
                created_signatures.append(signature)

                if contract.signing_order == "sequential":
                    signing_order += 1

            # Update contract status
            contract.status = ContractStatus.PENDING_SIGNATURE.value
            contract.signing_deadline = (
                datetime.utcnow() + timedelta(days=30)
                if not contract.signing_deadline
                else contract.signing_deadline
            )

            await db.flush()

            # Log audit
            await self._add_audit_trail(
                db,
                contract_id,
                ContractAuditAction.SENT.value,
                user_id,
                {"signer_count": len(signers)},
            )

            await db.commit()

            logger.info(f"Sent contract {contract_id} to {len(signers)} signers")

            # Emit event
            await self.emit_event(
                event_type="contract_sent_for_signature",
                entity_type="contract",
                entity_id=contract_id,
                payload={"signer_count": len(signers)},
                user_id=user_id,
            )

            return {
                "contract_id": contract_id,
                "signer_count": len(signers),
                "status": "sent",
                "signing_deadline": contract.signing_deadline.isoformat(),
            }

        except Exception as e:
            await db.rollback()
            logger.error(f"Error sending contract for signature: {str(e)}")
            raise

    async def process_signature(
        self,
        db: AsyncSession,
        contract_id: int,
        signer_id: int,
        signature_data: Dict[str, Any],
        signer_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> ContractSignature:
        """Process an e-signature submission.

        Args:
            db: Database session
            contract_id: ID of contract
            signer_id: ID of signature record
            signature_data: Signature data dictionary
            signer_ip: IP address of signer
            user_agent: User agent string

        Returns:
            Updated ContractSignature

        Raises:
            ValueError: If signature invalid or expired
        """
        try:
            # Fetch signature
            signature = await db.get(ContractSignature, signer_id)
            if not signature:
                raise ValueError(f"Signature {signer_id} not found")

            if signature.contract_id != contract_id:
                raise ValueError("Signature does not belong to this contract")

            # Check if already signed
            if signature.status == ContractSignatureStatus.SIGNED.value:
                raise ValueError("Signature already recorded")

            # Check token expiry
            if datetime.utcnow() > signature.token_expires_at:
                signature.status = ContractSignatureStatus.EXPIRED.value
                await db.commit()
                raise ValueError("Signing token has expired")

            # Record signature
            signature.status = ContractSignatureStatus.SIGNED.value
            signature.signed_at = datetime.utcnow()
            signature.signature_data = signature_data.get("signature_image")
            signature.signature_ip = signer_ip
            signature.signature_user_agent = user_agent

            # Log audit
            await self._add_audit_trail(
                db,
                contract_id,
                ContractAuditAction.SIGNED.value,
                None,
                {"signer_email": signature.signer_email, "ip": signer_ip},
            )

            # Check if all required signatures are done
            contract = await db.get(Contract, contract_id)
            all_signed = await self._check_all_signed(db, contract_id)

            if all_signed:
                contract.status = ContractStatus.COMPLETED.value
                contract.completed_at = datetime.utcnow()

                # Log completion
                await self._add_audit_trail(
                    db,
                    contract_id,
                    ContractAuditAction.COMPLETED.value,
                    None,
                    {},
                )

                await self.emit_event(
                    event_type="contract_completed",
                    entity_type="contract",
                    entity_id=contract_id,
                    payload={"all_signed": True},
                )
            else:
                contract.status = ContractStatus.PARTIALLY_SIGNED.value

            await db.commit()

            logger.info(
                f"Processed signature {signer_id} for contract {contract_id}"
            )

            await self.emit_event(
                event_type="contract_signature_received",
                entity_type="contract",
                entity_id=contract_id,
                payload={"signer_email": signature.signer_email},
            )

            return signature

        except Exception as e:
            await db.rollback()
            logger.error(f"Error processing signature: {str(e)}")
            raise

    async def void_contract(
        self,
        db: AsyncSession,
        contract_id: int,
        reason: str,
        user_id: int,
    ) -> Contract:
        """Void/cancel a contract.

        Args:
            db: Database session
            contract_id: ID of contract
            reason: Reason for voiding
            user_id: ID of user voiding contract

        Returns:
            Updated Contract

        Raises:
            ValueError: If contract cannot be voided
        """
        try:
            contract = await db.get(Contract, contract_id)
            if not contract:
                raise ValueError(f"Contract {contract_id} not found")

            if contract.status == ContractStatus.COMPLETED.value:
                raise ValueError("Cannot void a completed contract")

            contract.status = ContractStatus.VOIDED.value
            contract.voided_at = datetime.utcnow()
            contract.void_reason = reason

            # Log audit
            await self._add_audit_trail(
                db,
                contract_id,
                ContractAuditAction.VOIDED.value,
                user_id,
                {"reason": reason},
            )

            await db.commit()

            logger.info(f"Voided contract {contract_id}: {reason}")

            await self.emit_event(
                event_type="contract_voided",
                entity_type="contract",
                entity_id=contract_id,
                payload={"reason": reason},
                user_id=user_id,
            )

            return contract

        except Exception as e:
            await db.rollback()
            logger.error(f"Error voiding contract: {str(e)}")
            raise

    async def renew_contract(
        self,
        db: AsyncSession,
        contract_id: int,
        new_terms: Dict[str, Any],
        user_id: int,
    ) -> Contract:
        """Create renewal from existing contract with updated terms.

        Args:
            db: Database session
            contract_id: ID of contract to renew
            new_terms: New terms for renewal
            user_id: ID of user renewing contract

        Returns:
            New Contract with renewal terms

        Raises:
            ValueError: If contract not found or cannot be renewed
        """
        try:
            original = await db.get(Contract, contract_id)
            if not original:
                raise ValueError(f"Contract {contract_id} not found")

            if original.status != ContractStatus.COMPLETED.value:
                raise ValueError("Only completed contracts can be renewed")

            # Create new contract from original
            renewal_contract = Contract(
                contract_type=original.contract_type,
                title=f"{original.title} (Renewal)",
                content=original.content,
                parties=original.parties,
                status=ContractStatus.DRAFT.value,
                candidate_id=original.candidate_id,
                customer_id=original.customer_id,
                supplier_id=original.supplier_id,
                requirement_id=original.requirement_id,
                offer_id=original.offer_id,
                auto_renew=new_terms.get("auto_renew", original.auto_renew),
                renewal_terms=new_terms,
                signing_order=original.signing_order,
                metadata={
                    **original.metadata,
                    "renewal_from_contract_id": contract_id,
                },
                created_by_id=user_id,
            )

            # Update dates if provided
            if "effective_date" in new_terms:
                renewal_contract.effective_date = new_terms["effective_date"]
            if "expiry_date" in new_terms:
                renewal_contract.expiry_date = new_terms["expiry_date"]

            db.add(renewal_contract)
            await db.flush()

            # Log audit on original
            await self._add_audit_trail(
                db,
                contract_id,
                "renewed",
                user_id,
                {"renewal_contract_id": renewal_contract.id},
            )

            await db.commit()

            logger.info(f"Created renewal contract {renewal_contract.id} from {contract_id}")

            await self.emit_event(
                event_type="contract_renewed",
                entity_type="contract",
                entity_id=contract_id,
                payload={"renewal_contract_id": renewal_contract.id},
                user_id=user_id,
            )

            return renewal_contract

        except Exception as e:
            await db.rollback()
            logger.error(f"Error renewing contract: {str(e)}")
            raise

    async def get_expiring_contracts(
        self, db: AsyncSession, days_ahead: int = 30
    ) -> List[Contract]:
        """Find contracts expiring within X days.

        Args:
            db: Database session
            days_ahead: Number of days to look ahead

        Returns:
            List of expiring contracts

        Raises:
            Exception: If database error occurs
        """
        try:
            cutoff_date = datetime.utcnow().date() + timedelta(days=days_ahead)

            query = select(Contract).where(
                and_(
                    Contract.expiry_date.isnot(None),
                    Contract.expiry_date <= cutoff_date,
                    Contract.status == ContractStatus.COMPLETED.value,
                )
            )

            result = await db.execute(query)
            contracts = result.scalars().all()

            logger.info(f"Found {len(contracts)} expiring contracts within {days_ahead} days")
            return contracts

        except Exception as e:
            logger.error(f"Error fetching expiring contracts: {str(e)}")
            raise

    async def generate_signing_link(
        self, db: AsyncSession, contract_id: int, signer_email: str
    ) -> str:
        """Generate secure signing URL for signer.

        Args:
            db: Database session
            contract_id: ID of contract
            signer_email: Email of signer

        Returns:
            Signing URL

        Raises:
            ValueError: If signer not found
        """
        try:
            query = select(ContractSignature).where(
                and_(
                    ContractSignature.contract_id == contract_id,
                    ContractSignature.signer_email == signer_email,
                )
            )
            result = await db.execute(query)
            signature = result.scalars().first()

            if not signature:
                raise ValueError(f"Signer {signer_email} not found for contract")

            # Generate URL with token
            base_url = "https://api.hrplatform.com"
            signing_url = f"{base_url}/contracts/{contract_id}/sign?token={signature.signing_token}"

            logger.info(f"Generated signing link for {signer_email}")
            return signing_url

        except Exception as e:
            logger.error(f"Error generating signing link: {str(e)}")
            raise

    async def verify_signature(
        self, db: AsyncSession, signature_id: int
    ) -> Dict[str, Any]:
        """Verify signature authenticity with audit trail.

        Args:
            db: Database session
            signature_id: ID of signature to verify

        Returns:
            Verification details

        Raises:
            ValueError: If signature not found
        """
        try:
            signature = await db.get(ContractSignature, signature_id)
            if not signature:
                raise ValueError(f"Signature {signature_id} not found")

            contract = await db.get(Contract, signature.contract_id)

            # Fetch audit entries for this contract
            query = select(ContractAuditTrail).where(
                ContractAuditTrail.contract_id == signature.contract_id
            )
            result = await db.execute(query)
            audit_entries = result.scalars().all()

            return {
                "signature_id": signature_id,
                "signer_email": signature.signer_email,
                "signed_at": signature.signed_at.isoformat() if signature.signed_at else None,
                "signature_ip": signature.signature_ip,
                "status": signature.status,
                "contract_id": contract.id,
                "contract_title": contract.title,
                "audit_trail": [
                    {
                        "action": entry.action,
                        "timestamp": entry.timestamp.isoformat(),
                        "actor_email": entry.actor_email,
                    }
                    for entry in audit_entries
                ],
            }

        except Exception as e:
            logger.error(f"Error verifying signature: {str(e)}")
            raise

    async def get_contract_analytics(self, db: AsyncSession) -> Dict[str, Any]:
        """Get contract analytics across platform.

        Args:
            db: Database session

        Returns:
            Analytics dictionary

        Raises:
            Exception: If database error occurs
        """
        try:
            # Total contracts
            total_result = await db.execute(select(Contract))
            total_contracts = len(total_result.scalars().all())

            # By status
            status_query = select(Contract.status).distinct()
            status_result = await db.execute(status_query)
            statuses = status_result.scalars().all()

            by_status = {}
            for status in statuses:
                count_query = select(Contract).where(Contract.status == status)
                count_result = await db.execute(count_query)
                by_status[status] = len(count_result.scalars().all())

            # Calculate metrics
            completed_contracts = by_status.get(ContractStatus.COMPLETED.value, 0)
            completion_rate = (
                (completed_contracts / total_contracts * 100) if total_contracts > 0 else 0
            )

            expiring = await self.get_expiring_contracts(db, 30)
            expiring_count = len(expiring)

            logger.info("Generated contract analytics")

            return {
                "total_contracts": total_contracts,
                "by_status": by_status,
                "completion_rate": round(completion_rate, 2),
                "expiring_soon_count": expiring_count,
                "avg_contract_value": 0,  # Would require pricing data
                "total_revenue": 0,  # Would require pricing data
            }

        except Exception as e:
            logger.error(f"Error generating contract analytics: {str(e)}")
            raise

    # Helper methods

    def _generate_signing_token(self) -> str:
        """Generate a secure signing token."""
        return secrets.token_urlsafe(32)

    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context for LLM prompt."""
        result = []
        for key, value in context.items():
            result.append(f"{key}: {value}")
        return "\n".join(result)

    def _simple_template_render(
        self, template: str, context: Dict[str, Any]
    ) -> str:
        """Simple template rendering using string replacement."""
        result = template
        for key, value in context.items():
            placeholder = "{{" + key + "}}"
            result = result.replace(placeholder, str(value))
        return result

    async def _add_audit_trail(
        self,
        db: AsyncSession,
        contract_id: int,
        action: str,
        actor_id: Optional[int],
        details: Dict[str, Any],
    ) -> None:
        """Add entry to contract audit trail."""
        audit = ContractAuditTrail(
            contract_id=contract_id,
            action=action,
            actor_email="system" if actor_id is None else "user",
            details=details,
        )
        db.add(audit)

    async def _check_all_signed(self, db: AsyncSession, contract_id: int) -> bool:
        """Check if all required signatures are complete."""
        query = select(ContractSignature).where(
            ContractSignature.contract_id == contract_id
        )
        result = await db.execute(query)
        signatures = result.scalars().all()

        # Check if all signatures are complete
        required_count = len(signatures)
        signed_count = sum(
            1 for s in signatures if s.status == ContractSignatureStatus.SIGNED.value
        )

        return required_count > 0 and required_count == signed_count
