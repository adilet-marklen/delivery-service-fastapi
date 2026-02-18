from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from delivery_service.db.base import Base

if TYPE_CHECKING:
    from delivery_service.db.models.parcel_type import ParcelType


class Parcel(Base):
    """Посылка, зарегистрированная в рамках пользовательской сессии."""

    __tablename__ = "parcels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    weight_kg: Mapped[float] = mapped_column(Numeric(10, 3), nullable=False)
    content_type_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("parcel_types.id", ondelete="RESTRICT"), nullable=False
    )
    content_value_usd: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    delivery_cost_rub: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    session_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)

    content_type: Mapped[ParcelType] = relationship("ParcelType", back_populates="parcels")
