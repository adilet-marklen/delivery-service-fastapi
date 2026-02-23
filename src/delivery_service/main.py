import logging
from time import perf_counter
from uuid import uuid4

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.api.errors import AppError
from delivery_service.api.responses import SuccessResponse, error, ok
from delivery_service.api.v1.router import api_router
from delivery_service.core.config import settings
from delivery_service.core.logging import clear_request_id, set_request_id, setup_logging
from delivery_service.db.session import get_session
from delivery_service.middlewares.session import register_session_middleware


def create_app() -> FastAPI:
    setup_logging(settings.log_level)
    logger = logging.getLogger(__name__)
    logger.info("Загружены настройки приложения: %s", settings.safe_log_fields)
    app = FastAPI(title=settings.app_name)
    register_session_middleware(app)

    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        request_id = request.headers.get("X-Request-Id") or uuid4().hex
        request.state.request_id = request_id
        set_request_id(request_id)
        started_at = perf_counter()
        try:
            response = await call_next(request)
            response.headers["X-Request-Id"] = request_id
            latency_ms = (perf_counter() - started_at) * 1000
            logger.info(
                "%s %s -> %s %.2fms",
                request.method,
                request.url.path,
                response.status_code,
                latency_ms,
            )
            return response
        except Exception:
            latency_ms = (perf_counter() - started_at) * 1000
            logger.exception(
                "%s %s -> %s %.2fms",
                request.method,
                request.url.path,
                500,
                latency_ms,
            )
            raise
        finally:
            clear_request_id()

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=error(code=exc.code, message=exc.message, details=exc.details).model_dump(
                exclude_none=True
            ),
            headers={"X-Request-Id": getattr(request.state, "request_id", "")},
        )

    @app.exception_handler(Exception)
    async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Необработанная ошибка: %s", exc)
        return JSONResponse(
            status_code=500,
            content=error(code="internal_error", message="Внутренняя ошибка сервера").model_dump(
                exclude_none=True
            ),
            headers={"X-Request-Id": getattr(request.state, "request_id", "")},
        )

    @app.get("/health", response_model=SuccessResponse, tags=["health"])
    async def health() -> SuccessResponse:
        return ok({"status": "ok"})

    @app.get("/db-ping", response_model=SuccessResponse, tags=["health"])
    async def db_ping(session: AsyncSession = Depends(get_session)) -> SuccessResponse:
        result = await session.execute(text("SELECT 1"))
        return ok({"db": "ok", "result": result.scalar_one()})

    app.include_router(api_router, prefix="/api/v1")
    return app


app = create_app()
