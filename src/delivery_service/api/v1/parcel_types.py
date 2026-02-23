from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.api.deps import get_db
from delivery_service.api.responses import SuccessResponse, ok
from delivery_service.schemas.parcels import ParcelTypeOut
from delivery_service.services.parcel_type_service import ParcelTypeService

router = APIRouter()


@router.get("/", response_model=SuccessResponse[list[ParcelTypeOut]])
async def list_parcel_types(
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[list[ParcelTypeOut]]:
    service = ParcelTypeService(db)
    parcel_types = await service.list_types()
    result = [ParcelTypeOut(id=item.id, name=item.name) for item in parcel_types]
    return ok(result, meta={"total": len(result)})
