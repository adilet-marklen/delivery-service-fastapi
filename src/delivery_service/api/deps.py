from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import cast
from uuid import UUID

from fastapi import Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.api.errors import AppError
from delivery_service.db.session import get_session


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Даёт SQLAlchemy-сессию на время запроса."""
    async for session in get_session():
        yield session


def get_user_id(request: Request) -> UUID:
    user_id_any = getattr(request.state, "user_id", None)

    if not user_id_any:
        raise AppError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="session_not_initialized",
            message="Идентификатор сессии не инициализирован",
        )

    return cast(UUID, user_id_any)
