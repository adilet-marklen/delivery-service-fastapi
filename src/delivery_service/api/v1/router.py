from fastapi import APIRouter

from delivery_service.api.v1 import parcel_types, parcels

api_router = APIRouter()
api_router.include_router(parcels.router, prefix="/parcels", tags=["parcels"])
api_router.include_router(parcel_types.router, prefix="/parcel-types", tags=["parcel-types"])
