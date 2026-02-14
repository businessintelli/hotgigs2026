from datetime import datetime
from typing import Optional
from sqlalchemy import Column, DateTime, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column
from database.base import Base


class BaseModel(Base):
    """Base model with common fields for all entities."""

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
