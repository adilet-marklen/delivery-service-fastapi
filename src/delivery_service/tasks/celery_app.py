from celery import Celery

from delivery_service.core.config import settings

celery_app = Celery(
    "delivery_service",
    broker=settings.celery_broker_url,
    include=["delivery_service.tasks.delivery_cost_tasks"],
)
