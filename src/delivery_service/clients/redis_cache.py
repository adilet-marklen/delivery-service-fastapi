from __future__ import annotations

import json
from datetime import timedelta

import redis

from delivery_service.core.config import settings


class RedisCache:
    def __init__(self) -> None:
        self._client = redis.Redis.from_url(settings.redis_dsn, decode_responses=True)

    def set_json(self, key: str, value: object, ttl: timedelta) -> None:
        self._client.setex(key, int(ttl.total_seconds()), json.dumps(value))

    def get_json(self, key: str) -> object | None:
        raw = self._client.get(key)
        if raw is None:
            return None
        return json.loads(raw)
