from __future__ import annotations

import logging
from decimal import Decimal, InvalidOperation

import httpx
import redis.asyncio as redis

from delivery_service.api.errors import AppError
from delivery_service.clients.cbr import CBRClient
from delivery_service.core.config import settings

logger = logging.getLogger(__name__)

USD_RUB_CACHE_KEY = "usd_rub_rate"
USD_RUB_TTL_SECONDS = 600


def _parse_decimal(raw: str | None) -> Decimal | None:
    if raw is None:
        return None
    try:
        return Decimal(raw)
    except (InvalidOperation, TypeError, ValueError):
        return None


async def get_usd_rub_rate() -> Decimal:
    redis_client = redis.Redis.from_url(settings.redis_dsn, decode_responses=True)
    cbr_client = CBRClient()

    try:
        cached_raw = await redis_client.get(USD_RUB_CACHE_KEY)
        cached_rate = _parse_decimal(cached_raw)
        if cached_rate is not None:
            logger.info("USD/RUB cache hit: %s", cached_rate)
            return cached_rate
    except (redis.ConnectionError, redis.TimeoutError):
        logger.warning("Redis недоступен при чтении курса", exc_info=True)

    last_error: str | None = None
    try:
        fresh_rate = await cbr_client.fetch_usd_rub_rate()
        try:
            await redis_client.setex(USD_RUB_CACHE_KEY, USD_RUB_TTL_SECONDS, str(fresh_rate))
        except (redis.ConnectionError, redis.TimeoutError):
            logger.warning("Redis недоступен при записи курса", exc_info=True)
        logger.info("USD/RUB fetched from CBR: %s", fresh_rate)
        return fresh_rate
    except (httpx.RequestError, httpx.HTTPStatusError, AppError) as exc:
        last_error = str(exc)
        try:
            fallback_raw = await redis_client.get(USD_RUB_CACHE_KEY)
            fallback_rate = _parse_decimal(fallback_raw)
            if fallback_rate is not None:
                logger.warning("USD/RUB fallback to cached value: %s", fallback_rate)
                return fallback_rate
        except (redis.ConnectionError, redis.TimeoutError):
            logger.warning("Redis недоступен при fallback чтении курса", exc_info=True)

        raise AppError(
            status_code=502,
            code="usd_rate_unavailable",
            message="Не удалось получить курс USD/RUB",
            details={"reason": last_error} if last_error else None,
        )
    finally:
        await redis_client.close()
