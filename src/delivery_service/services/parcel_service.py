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
        session_id: str,
        name: str,
        weight_kg: float,
        content_type_id: int,
        content_value_usd: float,
    ) -> Parcel:
        parcel = Parcel(
            session_id=session_id,
            name=name,
            weight_kg=weight_kg,
            content_type_id=content_type_id,
            content_value_usd=content_value_usd,
        )
        self.session.add(parcel)
        await self.session.commit()
        await self.session.refresh(parcel)
        return parcel

    async def get_by_id_for_session(self, *, parcel_id: int, session_id: str) -> Parcel | None:
        query = (
            select(Parcel)
            .options(selectinload(Parcel.content_type))
            .where(Parcel.id == parcel_id, Parcel.session_id == session_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_for_session(
        self, *, session_id: str, page: int, size: int, filters: ParcelFilters
    ) -> tuple[list[Parcel], int]:
        conditions = [Parcel.session_id == session_id]
        if filters.parcel_type_id is not None:
            conditions.append(Parcel.content_type_id == filters.parcel_type_id)
        if filters.has_delivery_cost is True:
            conditions.append(Parcel.delivery_cost_rub.is_not(None))
        if filters.has_delivery_cost is False:
            conditions.append(Parcel.delivery_cost_rub.is_(None))

        count_query = select(func.count(Parcel.id)).where(*conditions)
        total = int((await self.session.execute(count_query)).scalar_one())

        query = (
            select(Parcel)
            .options(selectinload(Parcel.content_type))
            .where(*conditions)
            .order_by(Parcel.id.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all()), total
