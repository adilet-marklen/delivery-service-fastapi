import logging
from uuid import UUID, uuid4

from fastapi import FastAPI, Request

from delivery_service.core.config import settings

logger = logging.getLogger(__name__)


def register_session_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def session_middleware(request: Request, call_next):
        raw_cookie = request.cookies.get(settings.session_cookie_name)
        is_new_session = False

        try:
            user_id = UUID(raw_cookie) if raw_cookie else None
        except ValueError:
            user_id = None

        if user_id is None:
            user_id = uuid4()
            is_new_session = True

        request.state.user_id = user_id
        logger.info("Сессия пользователя: user_id=%s path=%s", user_id, request.url.path)

        response = await call_next(request)

        if is_new_session:
            response.set_cookie(
                key=settings.session_cookie_name,
                value=str(user_id),
                httponly=True,
                samesite="lax",
                secure=False,
                path="/",
            )

        return response
