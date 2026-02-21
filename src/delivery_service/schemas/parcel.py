from pydantic import BaseModel, ConfigDict, Field

from delivery_service.schemas.parcel_type import ParcelTypeOut


class ParcelCreate(BaseModel):
    name: str = Field(..., max_length=255)
    weight_kg: float = Field(..., gt=0)
    content_type_id: int
    content_value_usd: float = Field(..., ge=0)


class ParcelOut(BaseModel):
    id: int
    name: str
    weight_kg: float
    content_value_usd: float
    delivery_cost_rub: float | str
    content_type: ParcelTypeOut

    model_config = ConfigDict(from_attributes=True)


class ParcelCreateResult(BaseModel):
    id: int
