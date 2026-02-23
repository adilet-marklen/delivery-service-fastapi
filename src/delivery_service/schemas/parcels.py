from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class ParcelCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    weight_kg: float = Field(gt=0)
    type_id: int = Field(gt=0)
    declared_cost_usd: Decimal = Field(ge=0)


class ParcelCreatedResponse(BaseModel):
    id: str


class ParcelTypeOut(BaseModel):
    id: int
    name: str


class ParcelOut(BaseModel):
    id: str
    title: str
    weight_kg: float
    type_id: int
    type_name: str
    declared_cost_usd: Decimal
    delivery_cost_rub: Decimal | None
    delivery_cost: str
    created_at: datetime
    updated_at: datetime


class ParcelListResponse(BaseModel):
    items: list[ParcelOut]
    total: int
    page: int
    size: int


class RecalculateDeliveryResponse(BaseModel):
    updated: int
