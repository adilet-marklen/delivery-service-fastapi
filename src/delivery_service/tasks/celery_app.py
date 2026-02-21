from celery import Celery

from delivery_service.core.config import settings

celery_app = Celery(
    "delivery_service",
    broker=settings.redis_dsn,
    include=["delivery_service.tasks.delivery_cost_tasks"],
)
