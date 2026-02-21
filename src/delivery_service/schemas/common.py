from pydantic import BaseModel, Field


class Pagination(BaseModel):
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)


class ParcelFilters(BaseModel):
    parcel_type_id: int | None = None
    has_delivery_cost: bool | None = None
