from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.api.deps import get_db, get_session_id
from delivery_service.core.responses import ResponseEnvelope, ok
from delivery_service.schemas.common import ParcelFilters
from delivery_service.schemas.parcel import ParcelCreate, ParcelCreateResult, ParcelOut
from delivery_service.services.parcel_service import ParcelService

router = APIRouter()


def _format_delivery_cost(cost: float | None) -> float | str:
    # Компромисс по ТЗ: если стоимость ещё не посчитана, API должно вернуть "Не рассчитано".
    # Поэтому поле delivery_cost_rub сейчас допускает float | str.
    if cost is None:
        return "Не рассчитано"
    return round(float(cost), 2)


def _to_schema(parcel) -> ParcelOut:
    return ParcelOut(
        id=parcel.id,
        name=parcel.name,
        weight_kg=float(parcel.weight_kg),
        content_value_usd=float(parcel.content_value_usd),
        delivery_cost_rub=_format_delivery_cost(parcel.delivery_cost_rub),
        content_type=parcel.content_type,
    )


@router.post("/", response_model=ResponseEnvelope, status_code=status.HTTP_201_CREATED)
async def create_parcel(
    payload: ParcelCreate,
    db: AsyncSession = Depends(get_db),
    session_id: str = Depends(get_session_id),
) -> ResponseEnvelope:
    service = ParcelService(db)
    parcel = await service.create(
        session_id=session_id,
        name=payload.name,
        weight_kg=payload.weight_kg,
        content_type_id=payload.content_type_id,
        content_value_usd=payload.content_value_usd,
    )
    return ok(ParcelCreateResult(id=parcel.id))


@router.get("/", response_model=ResponseEnvelope)
async def list_parcels(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    parcel_type_id: int | None = Query(default=None),
    has_delivery_cost: bool | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    session_id: str = Depends(get_session_id),
) -> ResponseEnvelope:
    service = ParcelService(db)
    filters = ParcelFilters(parcel_type_id=parcel_type_id, has_delivery_cost=has_delivery_cost)
    items, total = await service.list_for_session(
        session_id=session_id,
        page=page,
        size=size,
        filters=filters,
    )
    pages = ceil(total / size) if total else 0

    return ok(
        {
            "items": [_to_schema(item) for item in items],
            "total": total,
            "page": page,
            "size": size,
            "pages": pages,
        }
    )


@router.get("/{parcel_id}", response_model=ResponseEnvelope)
async def get_parcel(
    parcel_id: int,
    db: AsyncSession = Depends(get_db),
    session_id: str = Depends(get_session_id),
) -> ResponseEnvelope:
    service = ParcelService(db)
    parcel = await service.get_by_id_for_session(parcel_id=parcel_id, session_id=session_id)
    if parcel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Посылка не найдена")

    return ok(_to_schema(parcel))
