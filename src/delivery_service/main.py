import logging
from uuid import uuid4

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.api.v1.router import api_router
from delivery_service.core.config import settings
from delivery_service.core.exceptions import DeliveryServiceError
from delivery_service.core.logging import setup_logging
from delivery_service.core.responses import ResponseEnvelope, ok
from delivery_service.db.session import get_session


def create_app() -> FastAPI:
    """Создаёт и настраивает FastAPI-приложение."""
    setup_logging(settings.log_level)
    logger = logging.getLogger(__name__)
    logger.info("Loaded settings: %s", settings.safe_log_fields)
    app = FastAPI(title=settings.app_name)

    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        request_id = request.headers.get("X-Request-Id") or uuid4().hex
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-Id"] = request_id
        return response

    @app.exception_handler(DeliveryServiceError)
    async def domain_error_handler(request: Request, exc: DeliveryServiceError) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content=ResponseEnvelope(detail=str(exc)).model_dump(),
            headers={"X-Request-Id": getattr(request.state, "request_id", "")},
        )

    @app.exception_handler(Exception)
    async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error: %s", exc)
        return JSONResponse(
            status_code=500,
            content=ResponseEnvelope(detail="Internal server error").model_dump(),
            headers={"X-Request-Id": getattr(request.state, "request_id", "")},
        )

    @app.get("/health", response_model=ResponseEnvelope, tags=["health"])
    async def health() -> ResponseEnvelope:
        return ok({"status": "ok"})

    @app.get("/db-ping", response_model=ResponseEnvelope, tags=["health"])
    async def db_ping(session: AsyncSession = Depends(get_session)) -> ResponseEnvelope:
        result = await session.execute(text("SELECT 1"))
        return ok({"db": "ok", "result": result.scalar_one()})

    app.include_router(api_router, prefix="/api/v1")
    return app


app = create_app()
