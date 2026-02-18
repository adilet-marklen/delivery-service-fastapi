from typing import Any

from pydantic import BaseModel


class ResponseEnvelope(BaseModel):
    data: Any | None = None
    detail: str | None = None


def ok(data: Any) -> ResponseEnvelope:
    return ResponseEnvelope(data=data)


def message(detail: str) -> ResponseEnvelope:
    return ResponseEnvelope(detail=detail)
