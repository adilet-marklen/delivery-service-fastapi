from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from delivery_service.db.base import Base

if TYPE_CHECKING:
    from delivery_service.db.models.parcel import Parcel


class ParcelType(Base):
    """Справочник типов посылок (одежда, электроника, разное)."""

    __tablename__ = "parcel_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    parcels: Mapped[list[Parcel]] = relationship("Parcel", back_populates="type")
