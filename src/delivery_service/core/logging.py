from __future__ import annotations

import logging
from contextvars import ContextVar
from logging.config import dictConfig

_request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = _request_id_ctx.get()
        return True


def set_request_id(request_id: str) -> None:
    _request_id_ctx.set(request_id)


def clear_request_id() -> None:
    _request_id_ctx.set("-")


def setup_logging(level: str = "INFO") -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {
                "request_id": {
                    "()": "delivery_service.core.logging.RequestIdFilter",
                }
            },
            "formatters": {
                "default": {
                    "format": (
                        "%(asctime)s | %(levelname)s | %(name)s | "
                        "request_id=%(request_id)s | %(message)s"
                    )
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": level.upper(),
                    "formatter": "default",
                    "filters": ["request_id"],
                }
            },
            "root": {
                "level": level.upper(),
                "handlers": ["console"],
            },
        }
    )
