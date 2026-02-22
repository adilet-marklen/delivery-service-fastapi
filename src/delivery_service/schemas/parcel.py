from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from delivery_service.schemas.parcel_type import ParcelTypeOut


class ParcelCreate(BaseModel):
    title: str = Field(..., max_length=255)
    weight_kg: float = Field(..., gt=0)
    type_id: int
    declared_cost_usd: float = Field(..., ge=0)


class ParcelOut(BaseModel):
    id: UUID
    title: str
    weight_kg: float
    declared_cost_usd: float
    delivery_cost_rub: float | str
    type: ParcelTypeOut

    model_config = ConfigDict(from_attributes=True)


class ParcelCreateResult(BaseModel):
    id: UUID
