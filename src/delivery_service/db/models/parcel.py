from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Numeric, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from delivery_service.db.base import Base

if TYPE_CHECKING:
    from delivery_service.db.models.parcel_type import ParcelType


class Parcel(Base):
    """Посылка пользователя."""

    __tablename__ = "parcels"
    __table_args__ = (
        Index("ix_parcels_user_id", "user_id"),
        Index("ix_parcels_type_id", "type_id"),
        Index(
            "ix_parcels_unprocessed_delivery_cost",
            "delivery_cost_rub",
            postgresql_where=text("delivery_cost_rub IS NULL"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    weight_kg: Mapped[float] = mapped_column(Numeric(10, 3), nullable=False)
    declared_cost_usd: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    type_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("parcel_types.id", ondelete="RESTRICT"), nullable=False
    )
    delivery_cost_rub: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        onupdate=text("now()"),
        nullable=False,
    )

    type: Mapped[ParcelType] = relationship("ParcelType", back_populates="parcels")
