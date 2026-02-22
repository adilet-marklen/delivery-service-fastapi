from collections.abc import AsyncGenerator
from uuid import UUID, uuid4

from fastapi import Header, Response
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.db.session import get_session

SESSION_HEADER = "X-Session-Id"


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Даёт SQLAlchemy-сессию на время запроса."""
    async for session in get_session():
        yield session


def get_session_id(
    response: Response, x_session_id: str | None = Header(default=None, alias=SESSION_HEADER)
) -> UUID:
    """Возвращает id сессии из заголовка или генерирует новый."""
    if x_session_id:
        return UUID(x_session_id)

    new_session_id = uuid4()
    response.headers[SESSION_HEADER] = str(new_session_id)
    return new_session_id
