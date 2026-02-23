from decimal import Decimal
from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import update

from delivery_service.db.models.parcel import Parcel

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]


async def test_create_parcel_validation_error(client, parcel_type_ids: dict[str, int]) -> None:
    response = await client.post(
        "/api/v1/parcels/",
        json={
            "title": "",
            "weight_kg": -1,
            "type_id": parcel_type_ids["electronics"],
            "declared_cost_usd": 100,
        },
    )

    assert response.status_code == 422


async def test_create_parcel_success(client, parcel_type_ids: dict[str, int]) -> None:
    response = await client.post(
        "/api/v1/parcels/",
        json={
            "title": "parcel_electronics",
            "weight_kg": 1.5,
            "type_id": parcel_type_ids["electronics"],
            "declared_cost_usd": 120,
        },
    )

    assert response.status_code == 201
    data = response.json()["data"]
    assert data["id"]
    assert data["title"] == "parcel_electronics"
    assert data["delivery_cost"] == "Не рассчитано"


async def test_list_parcels_pagination_and_filters(
    client,
    db_session,
    parcel_type_ids: dict[str, int],
) -> None:
    created_ids: list[str] = []

    first = await client.post(
        "/api/v1/parcels/",
        json={
            "title": "parcel_clothes",
            "weight_kg": 2.0,
            "type_id": parcel_type_ids["clothes"],
            "declared_cost_usd": 90,
        },
    )
    created_ids.append(first.json()["data"]["id"])

    second = await client.post(
        "/api/v1/parcels/",
        json={
            "title": "parcel_electronics",
            "weight_kg": 1.0,
            "type_id": parcel_type_ids["electronics"],
            "declared_cost_usd": 150,
        },
    )
    created_ids.append(second.json()["data"]["id"])

    response_all = await client.get("/api/v1/parcels/?page=1&size=1")
    assert response_all.status_code == 200
    assert response_all.json()["data"]["total"] == 2
    assert len(response_all.json()["data"]["items"]) == 1

    response_type = await client.get(f"/api/v1/parcels/?type_id={parcel_type_ids['electronics']}")
    assert response_type.status_code == 200
    assert response_type.json()["data"]["total"] == 1
    assert response_type.json()["data"]["items"][0]["type_name"] == "electronics"

    response_without_cost = await client.get("/api/v1/parcels/?has_delivery_cost=false")
    assert response_without_cost.status_code == 200
    assert response_without_cost.json()["data"]["total"] == 2

    await db_session.execute(
        update(Parcel)
        .where(Parcel.id == UUID(created_ids[0]))
        .values(delivery_cost_rub=Decimal("777.77"))
    )
    await db_session.commit()

    response_with_cost = await client.get("/api/v1/parcels/?has_delivery_cost=true")
    assert response_with_cost.status_code == 200
    assert response_with_cost.json()["data"]["total"] == 1
    assert response_with_cost.json()["data"]["items"][0]["delivery_cost_rub"] == "777.77"


async def test_get_parcel_by_id_forbidden_for_other_user(
    app,
    client,
    parcel_type_ids: dict[str, int],
) -> None:
    create_response = await client.post(
        "/api/v1/parcels/",
        json={
            "title": "parcel_for_user_a",
            "weight_kg": 1.2,
            "type_id": parcel_type_ids["other"],
            "declared_cost_usd": 50,
        },
    )
    parcel_id = create_response.json()["data"]["id"]

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as another_client:
        response = await another_client.get(f"/api/v1/parcels/{parcel_id}")

    assert response.status_code == 404
    error = response.json()["error"]
    assert error["code"] == "parcel_not_found"
