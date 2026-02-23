import pytest

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]


async def test_get_parcel_types_returns_seeded_types(client, db_seeded) -> None:
    response = await client.get("/api/v1/parcel-types/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["meta"]["total"] == 3
    assert [item["name"] for item in payload["data"]] == ["clothes", "electronics", "other"]
