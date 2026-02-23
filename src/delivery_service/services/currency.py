from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from decimal import Decimal, InvalidOperation

import httpx
import redis

from delivery_service.clients.cbr_client import CBRClient
from delivery_service.clients.redis_cache import RedisCache

USD_RUB_CACHE_KEY = "currency:usd_rub"
USD_RUB_TTL = timedelta(minutes=10)
MAX_ATTEMPTS = 3
BASE_DELAY_SECONDS = 0.3

logger = logging.getLogger(__name__)


async def get_usd_rub_rate() -> Decimal:
    cache = RedisCache()
    cbr_client = CBRClient()

    try:
        cached = cache.get_json(USD_RUB_CACHE_KEY)
    except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError):
        logger.warning("Ошибка чтения из Redis, переходим к запросу в CBR", exc_info=True)
        cached = None

    if cached is not None:
        try:
            return Decimal(str(cached))
        except (InvalidOperation, TypeError, ValueError):
            logger.warning(
                "Некорректное значение USD/RUB в кеше: %r, переходим к CBR",
                cached,
                exc_info=True,
            )

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            rate = Decimal(str(await cbr_client.get_usd_rub_rate()))
            try:
                cache.set_json(USD_RUB_CACHE_KEY, str(rate), USD_RUB_TTL)
            except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError):
                logger.warning(
                    "Ошибка записи курса в Redis (rate=%s)",
                    rate,
                    exc_info=True,
                )
            return rate
        except (httpx.RequestError, httpx.HTTPStatusError) as exc:
            if attempt >= MAX_ATTEMPTS:
                raise
            delay = BASE_DELAY_SECONDS * (2 ** (attempt - 1))
            logger.warning(
                "Ошибка запроса к CBR (попытка=%s/%s), повтор через %.2fs: %r",
                attempt,
                MAX_ATTEMPTS,
                delay,
                exc,
            )
            await asyncio.sleep(delay)

    raise RuntimeError("Не удалось получить курс USD/RUB после повторных попыток")
