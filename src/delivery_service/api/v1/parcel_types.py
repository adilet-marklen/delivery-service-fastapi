from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.api.deps import get_db
from delivery_service.core.responses import ResponseEnvelope, ok
from delivery_service.schemas.parcel_type import ParcelTypeOut
from delivery_service.services.parcel_type_service import ParcelTypeService

router = APIRouter()


@router.get("/", response_model=ResponseEnvelope)
async def list_parcel_types(db: AsyncSession = Depends(get_db)) -> ResponseEnvelope:
    service = ParcelTypeService(db)
    parcel_types = await service.list_types()
    return ok([ParcelTypeOut.model_validate(item) for item in parcel_types])
