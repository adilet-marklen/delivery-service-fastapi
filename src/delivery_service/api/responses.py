from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    data: T
    meta: dict[str, Any] | None = None


class ErrorBody(BaseModel):
    code: str
    message: str
    details: Any | None = None


class ErrorResponse(BaseModel):
    error: ErrorBody


def ok(data: T, meta: dict[str, Any] | None = None) -> SuccessResponse[T]:
    return SuccessResponse(data=data, meta=meta)


def error(*, code: str, message: str, details: Any | None = None) -> ErrorResponse:
    return ErrorResponse(error=ErrorBody(code=code, message=message, details=details))
