from __future__ import annotations

import httpx


class CBRClient:
    """Забирает курс USD/RUB по HTTP и возвращает числом."""

    BASE_URL = "https://www.cbr-xml-daily.ru/daily_json.js"

    async def get_usd_rub_rate(self) -> float:
        async with httpx.AsyncClient() as client:
            response = await client.get(self.BASE_URL, timeout=5.0)
            response.raise_for_status()
            data = response.json()
            return float(data["Valute"]["USD"]["Value"])

