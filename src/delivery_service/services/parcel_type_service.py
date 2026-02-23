from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.db.models.parcel_type import ParcelType


class ParcelTypeService:
    """Бизнес-логика по справочнику типов посылок."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_types(self) -> list[ParcelType]:
        query = select(ParcelType).order_by(ParcelType.name.asc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def exists(self, type_id: int) -> bool:
        query = select(ParcelType.id).where(ParcelType.id == type_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None
