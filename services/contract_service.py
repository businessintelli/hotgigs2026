import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from models.contract import Contract, ContractTemplate, ContractSignature, ContractAuditTrail
from models.enums import ContractStatus, ContractSignatureStatus
from schemas.contract import (
    ContractSchema,
    ContractCreateSchema,
    ContractUpdateSchema,
    ContractDetailSchema,
)

logger = logging.getLogger(__name__)


class ContractService:
    """Service layer for contract operations."""

    @staticmethod
    async def create_contract(
        db: AsyncSession, contract_data: ContractCreateSchema, user_id: int
    ) -> ContractSchema:
        """Create a new contract.

        Args:
            db: Database session
            contract_data: Contract creation schema
            user_id: ID of creating user

        Returns:
            ContractSchema

        Raises:
            ValueError: If data invalid
        """
        try:
            contract = Contract(
                template_id=contract_data.template_id,
                contract_type=contract_data.contract_type,
                title=contract_data.title,
                content=contract_data.content,
                parties=[p.dict() for p in contract_data.parties],
                candidate_id=contract_data.candidate_id,
                customer_id=contract_data.customer_id,
                supplier_id=contract_data.supplier_id,
                requirement_id=contract_data.requirement_id,
                offer_id=contract_data.offer_id,
                effective_date=contract_data.effective_date,
                expiry_date=contract_data.expiry_date,
                auto_renew=contract_data.auto_renew,
                renewal_terms=contract_data.renewal_terms,
                signing_order=contract_data.signing_order,
                signing_deadline=contract_data.signing_deadline,
                extra_metadata=contract_data.metadata,
                created_by_id=user_id,
            )

            db.add(contract)
            await db.flush()

            # Add audit trail
            audit = ContractAuditTrail(
                contract_id=contract.id,
                action="created",
                actor_email="user",
                details={"contract_type": contract.contract_type},
            )
            db.add(audit)

            await db.commit()
            logger.info(f"Created contract {contract.id}")

            return ContractSchema.from_orm(contract)

        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating contract: {str(e)}")
            raise

    @staticmethod
    async def get_contract(db: AsyncSession, contract_id: int) -> Optional[ContractDetailSchema]:
        """Fetch contract with full details.

        Args:
            db: Database session
            contract_id: ID of contract

        Returns:
            ContractDetailSchema or None

        Raises:
            Exception: If database error occurs
        """
        try:
            contract = await db.get(Contract, contract_id)
            if not contract:
                return None

            await db.refresh(contract, ["signatures", "audit_trail"])

            return ContractDetailSchema.from_orm(contract)

        except Exception as e:
            logger.error(f"Error fetching contract: {str(e)}")
            raise

    @staticmethod
    async def list_contracts(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        contract_type: Optional[str] = None,
        candidate_id: Optional[int] = None,
    ) -> tuple[List[ContractSchema], int]:
        """List contracts with filtering.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Number of records to return
            status: Filter by status
            contract_type: Filter by type
            candidate_id: Filter by candidate

        Returns:
            Tuple of (contracts list, total count)

        Raises:
            Exception: If database error occurs
        """
        try:
            filters = []

            if status:
                filters.append(Contract.status == status)
            if contract_type:
                filters.append(Contract.contract_type == contract_type)
            if candidate_id:
                filters.append(Contract.candidate_id == candidate_id)

            # Get total count
            count_query = select(Contract)
            if filters:
                count_query = count_query.where(and_(*filters))
            count_result = await db.execute(count_query)
            total = len(count_result.scalars().all())

            # Get paginated results
            query = select(Contract)
            if filters:
                query = query.where(and_(*filters))
            query = query.offset(skip).limit(limit).order_by(Contract.created_at.desc())

            result = await db.execute(query)
            contracts = result.scalars().all()

            return (
                [ContractSchema.from_orm(c) for c in contracts],
                total,
            )

        except Exception as e:
            logger.error(f"Error listing contracts: {str(e)}")
            raise

    @staticmethod
    async def update_contract(
        db: AsyncSession, contract_id: int, update_data: ContractUpdateSchema
    ) -> ContractSchema:
        """Update a draft contract.

        Args:
            db: Database session
            contract_id: ID of contract
            update_data: Update schema

        Returns:
            Updated ContractSchema

        Raises:
            ValueError: If contract not found or not draft
        """
        try:
            contract = await db.get(Contract, contract_id)
            if not contract:
                raise ValueError(f"Contract {contract_id} not found")

            if contract.status != ContractStatus.DRAFT.value:
                raise ValueError("Only draft contracts can be updated")

            update_dict = update_data.dict(exclude_unset=True)
            if "parties" in update_dict and update_dict["parties"]:
                update_dict["parties"] = [
                    p.dict() if hasattr(p, "dict") else p
                    for p in update_dict["parties"]
                ]

            for key, value in update_dict.items():
                if value is not None and hasattr(contract, key):
                    setattr(contract, key, value)

            await db.commit()
            logger.info(f"Updated contract {contract_id}")

            return ContractSchema.from_orm(contract)

        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating contract: {str(e)}")
            raise

    @staticmethod
    async def add_signers(
        db: AsyncSession,
        contract_id: int,
        signers: List[Dict[str, Any]],
    ) -> List[ContractSignature]:
        """Add signers to a contract.

        Args:
            db: Database session
            contract_id: ID of contract
            signers: List of signer data

        Returns:
            List of created signatures

        Raises:
            ValueError: If contract not found
        """
        try:
            contract = await db.get(Contract, contract_id)
            if not contract:
                raise ValueError(f"Contract {contract_id} not found")

            created_signatures = []
            signing_order = 1

            for signer in signers:
                signature = ContractSignature(
                    contract_id=contract_id,
                    signer_name=signer.get("signer_name"),
                    signer_email=signer.get("signer_email"),
                    signer_role=signer.get("signer_role"),
                    signing_token=ContractService._generate_token(),
                    token_expires_at=datetime.utcnow() + timedelta(days=30),
                    status=ContractSignatureStatus.PENDING.value,
                    signing_order=signing_order,
                )
                db.add(signature)
                created_signatures.append(signature)

                if contract.signing_order == "sequential":
                    signing_order += 1

            # Update contract status
            contract.status = ContractStatus.PENDING_SIGNATURE.value

            await db.commit()
            logger.info(f"Added {len(signers)} signers to contract {contract_id}")

            return created_signatures

        except Exception as e:
            await db.rollback()
            logger.error(f"Error adding signers: {str(e)}")
            raise

    @staticmethod
    async def get_signing_status(
        db: AsyncSession, contract_id: int
    ) -> Dict[str, Any]:
        """Get signing status for contract.

        Args:
            db: Database session
            contract_id: ID of contract

        Returns:
            Signing status dictionary

        Raises:
            ValueError: If contract not found
        """
        try:
            contract = await db.get(Contract, contract_id)
            if not contract:
                raise ValueError(f"Contract {contract_id} not found")

            await db.refresh(contract, ["signatures"])

            signatures = contract.signatures
            total = len(signatures)
            signed = sum(1 for s in signatures if s.status == ContractSignatureStatus.SIGNED.value)
            pending = sum(1 for s in signatures if s.status == ContractSignatureStatus.PENDING.value)

            progress = (signed / total * 100) if total > 0 else 0

            return {
                "contract_id": contract_id,
                "status": contract.status,
                "total_signers": total,
                "signed": signed,
                "pending": pending,
                "progress": round(progress, 2),
                "signatures": [
                    {
                        "signer_email": s.signer_email,
                        "status": s.status,
                        "signed_at": s.signed_at.isoformat() if s.signed_at else None,
                    }
                    for s in signatures
                ],
            }

        except Exception as e:
            logger.error(f"Error getting signing status: {str(e)}")
            raise

    @staticmethod
    async def get_expiring_contracts(
        db: AsyncSession, days_ahead: int = 30
    ) -> List[ContractSchema]:
        """Get contracts expiring soon.

        Args:
            db: Database session
            days_ahead: Days to look ahead

        Returns:
            List of expiring contracts

        Raises:
            Exception: If database error occurs
        """
        try:
            cutoff = datetime.utcnow().date() + timedelta(days=days_ahead)

            query = select(Contract).where(
                and_(
                    Contract.expiry_date.isnot(None),
                    Contract.expiry_date <= cutoff,
                    Contract.status == ContractStatus.COMPLETED.value,
                )
            )

            result = await db.execute(query)
            contracts = result.scalars().all()

            return [ContractSchema.from_orm(c) for c in contracts]

        except Exception as e:
            logger.error(f"Error getting expiring contracts: {str(e)}")
            raise

    @staticmethod
    async def get_audit_trail(
        db: AsyncSession, contract_id: int
    ) -> List[Dict[str, Any]]:
        """Get audit trail for contract.

        Args:
            db: Database session
            contract_id: ID of contract

        Returns:
            List of audit entries

        Raises:
            ValueError: If contract not found
        """
        try:
            contract = await db.get(Contract, contract_id)
            if not contract:
                raise ValueError(f"Contract {contract_id} not found")

            query = select(ContractAuditTrail).where(
                ContractAuditTrail.contract_id == contract_id
            ).order_by(ContractAuditTrail.timestamp.desc())

            result = await db.execute(query)
            entries = result.scalars().all()

            return [
                {
                    "action": e.action,
                    "actor_email": e.actor_email,
                    "timestamp": e.timestamp.isoformat(),
                    "details": e.details,
                }
                for e in entries
            ]

        except Exception as e:
            logger.error(f"Error getting audit trail: {str(e)}")
            raise

    @staticmethod
    async def get_templates(
        db: AsyncSession,
        is_active: bool = True,
    ) -> List[Dict[str, Any]]:
        """Get available contract templates.

        Args:
            db: Database session
            is_active: Filter to active templates

        Returns:
            List of templates

        Raises:
            Exception: If database error occurs
        """
        try:
            query = select(ContractTemplate)
            if is_active:
                query = query.where(ContractTemplate.is_active == True)

            result = await db.execute(query)
            templates = result.scalars().all()

            return [
                {
                    "id": t.id,
                    "name": t.name,
                    "template_type": t.template_type,
                    "version": t.version,
                }
                for t in templates
            ]

        except Exception as e:
            logger.error(f"Error getting templates: {str(e)}")
            raise

    @staticmethod
    def _generate_token() -> str:
        """Generate signing token."""
        import secrets
        return secrets.token_urlsafe(32)
