from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.api.deps import get_db, get_user_id
from delivery_service.api.errors import AppError
from delivery_service.api.responses import SuccessResponse, ok
from delivery_service.schemas.common import ParcelFilters
from delivery_service.schemas.parcels import (
    ParcelCreate,
    ParcelCreatedResponse,
    ParcelListResponse,
    ParcelOut,
)
from delivery_service.services.parcel_service import ParcelService

router = APIRouter()


def _format_delivery_cost(cost: float | None) -> str:
    # В ТЗ явно просят строку "Не рассчитано", поэтому держим отдельное текстовое поле.
    if cost is None:
        return "Не рассчитано"
    return f"{float(cost):.2f}"


def _to_schema(parcel) -> ParcelOut:
    return ParcelOut(
        id=str(parcel.id),
        title=parcel.title,
        weight_kg=float(parcel.weight_kg),
        declared_cost_usd=parcel.declared_cost_usd,
        type_id=parcel.type_id,
        type_name=parcel.type.name,
        delivery_cost_rub=parcel.delivery_cost_rub,
        delivery_cost=_format_delivery_cost(parcel.delivery_cost_rub),
        created_at=parcel.created_at,
        updated_at=parcel.updated_at,
    )


@router.post("/", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def create_parcel(
    payload: ParcelCreate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_user_id),
) -> SuccessResponse:
    service = ParcelService(db)
    parcel = await service.create(
        user_id=user_id,
        title=payload.title,
        weight_kg=payload.weight_kg,
        type_id=payload.type_id,
        declared_cost_usd=float(payload.declared_cost_usd),
    )
    return ok(ParcelCreatedResponse(id=str(parcel.id)))


@router.get("/", response_model=SuccessResponse)
async def list_parcels(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    parcel_type_id: int | None = Query(default=None),
    has_delivery_cost: bool | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_user_id),
) -> SuccessResponse:
    service = ParcelService(db)
    filters = ParcelFilters(parcel_type_id=parcel_type_id, has_delivery_cost=has_delivery_cost)
    items, total = await service.list_for_user(
        user_id=user_id,
        page=page,
        size=size,
        filters=filters,
    )
    return ok(
        ParcelListResponse(
            items=[_to_schema(item) for item in items],
            total=total,
            page=page,
            size=size,
        ),
        meta={"page": page, "size": size, "total": total},
    )


@router.get("/{parcel_id}", response_model=SuccessResponse)
async def get_parcel(
    parcel_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_user_id),
) -> SuccessResponse:
    service = ParcelService(db)
    parcel = await service.get_by_id_for_user(parcel_id=parcel_id, user_id=user_id)
    if parcel is None:
        raise AppError(
            status_code=status.HTTP_404_NOT_FOUND,
            code="parcel_not_found",
            message="Посылка не найдена",
        )

    return ok(_to_schema(parcel))
