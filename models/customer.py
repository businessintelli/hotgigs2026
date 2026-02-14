from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Date, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import BaseModel


class Customer(BaseModel):
    """Customer company model."""

    __tablename__ = "customers"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    industry: Mapped[Optional[str]] = mapped_column(String(100))
    website: Mapped[Optional[str]] = mapped_column(String(255))
    primary_contact_name: Mapped[Optional[str]] = mapped_column(String(255))
    primary_contact_email: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    primary_contact_phone: Mapped[Optional[str]] = mapped_column(String(20))
    address: Mapped[Optional[str]] = mapped_column(String(255))
    city: Mapped[Optional[str]] = mapped_column(String(100))
    state: Mapped[Optional[str]] = mapped_column(String(100))
    country: Mapped[Optional[str]] = mapped_column(String(100))
    contract_start_date: Mapped[Optional[datetime]] = mapped_column(Date)
    contract_end_date: Mapped[Optional[datetime]] = mapped_column(Date)
    billing_rate_type: Mapped[Optional[str]] = mapped_column(String(50))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    extra_metadata: Mapped[Optional[dict]] = mapped_column("metadata", JSON, default=dict)

    # Relationships
    requirements = relationship("Requirement", back_populates="customer", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="customer", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Customer(id={self.id}, name={self.name})>"
