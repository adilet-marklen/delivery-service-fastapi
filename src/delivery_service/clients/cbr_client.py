from __future__ import annotations

import httpx

from delivery_service.core.config import settings


class CBRClient:
    """Забирает курс USD/RUB по HTTP и возвращает числом."""

    async def get_usd_rub_rate(self) -> float:
        async with httpx.AsyncClient() as client:
            response = await client.get(settings.cbr_url, timeout=5.0)
            response.raise_for_status()
            data = response.json()
            return float(data["Valute"]["USD"]["Value"])
