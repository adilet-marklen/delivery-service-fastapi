from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from delivery_service.db.models.parcel import Parcel
from delivery_service.schemas.common import ParcelFilters


class ParcelService:
    """Бизнес-логика по посылкам (создание, выборки, фильтры)."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        user_id: UUID,
        title: str,
        weight_kg: float,
        type_id: int,
        declared_cost_usd: float,
    ) -> Parcel:
        parcel = Parcel(
            user_id=user_id,
            title=title,
            weight_kg=weight_kg,
            type_id=type_id,
            declared_cost_usd=declared_cost_usd,
        )
        self.session.add(parcel)
        await self.session.commit()
        await self.session.refresh(parcel)
        return parcel

    async def get_by_id_for_user(self, *, parcel_id: UUID, user_id: UUID) -> Parcel | None:
        query = (
            select(Parcel)
            .options(selectinload(Parcel.type))
            .where(Parcel.id == parcel_id, Parcel.user_id == user_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_for_user(
        self, *, user_id: UUID, page: int, size: int, filters: ParcelFilters
    ) -> tuple[list[Parcel], int]:
        conditions = [Parcel.user_id == user_id]
        if filters.parcel_type_id is not None:
            conditions.append(Parcel.type_id == filters.parcel_type_id)
        if filters.has_delivery_cost is True:
            conditions.append(Parcel.delivery_cost_rub.is_not(None))
        if filters.has_delivery_cost is False:
            conditions.append(Parcel.delivery_cost_rub.is_(None))

        count_query = select(func.count(Parcel.id)).where(*conditions)
        total = int((await self.session.execute(count_query)).scalar_one())

        query = (
            select(Parcel)
            .options(selectinload(Parcel.type))
            .where(*conditions)
            .order_by(Parcel.created_at.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all()), total
