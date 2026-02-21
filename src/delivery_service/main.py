from fastapi import FastAPI

from delivery_service.api.v1.router import api_router
from delivery_service.core.config import settings
from delivery_service.core.logging import setup_logging


def create_app() -> FastAPI:
    """Создаёт и настраивает FastAPI-приложение."""
    setup_logging()
    app = FastAPI(title=settings.app_name)
    app.include_router(api_router, prefix="/api/v1")
    return app


app = create_app()
