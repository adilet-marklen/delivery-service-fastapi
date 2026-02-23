from __future__ import annotations

from decimal import Decimal, InvalidOperation

import httpx

from delivery_service.api.errors import AppError
from delivery_service.core.config import settings


class CBRClient:
    async def fetch_usd_rub_rate(self) -> Decimal:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(settings.cbr_url)
            response.raise_for_status()
            data = response.json()

        try:
            usd = data["Valute"]["USD"]["Value"]
            return Decimal(str(usd))
        except (KeyError, TypeError, InvalidOperation) as exc:
            raise AppError(
                status_code=502,
                code="cbr_response_invalid",
                message="Некорректный ответ сервиса курсов валют",
            ) from exc
