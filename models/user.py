from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, JSON, Enum, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import BaseModel
from models.enums import UserRole


class User(BaseModel):
    """Platform user model — multi-tenant aware."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(
        Enum(UserRole),
        default=UserRole.VIEWER,
        nullable=False,
        index=True,
    )
    # Multi-tenancy: primary organization
    organization_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("organizations.id"), nullable=True, index=True
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    extra_metadata: Mapped[Optional[dict]] = mapped_column("metadata", JSON, default=dict)

    # Relationship to primary organization
    organization = relationship("Organization", backref="users", foreign_keys=[organization_id])

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role}, org={self.organization_id})>"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
