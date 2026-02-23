from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class SuccessResponse(BaseModel):
    data: Any
    meta: dict[str, Any] | None = None


class ErrorBody(BaseModel):
    code: str
    message: str
    details: Any | None = None


class ErrorResponse(BaseModel):
    error: ErrorBody


def ok(data: Any, meta: dict[str, Any] | None = None) -> SuccessResponse:
    return SuccessResponse(data=data, meta=meta)


def error(*, code: str, message: str, details: Any | None = None) -> ErrorResponse:
    return ErrorResponse(error=ErrorBody(code=code, message=message, details=details))
