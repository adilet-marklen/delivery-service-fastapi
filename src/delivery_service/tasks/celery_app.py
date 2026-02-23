from celery import Celery
from celery.schedules import crontab

from delivery_service.core.config import settings

celery_app = Celery(
    "delivery_service",
    broker=settings.redis_dsn,
    include=[
        "delivery_service.tasks.calculate",
        "delivery_service.tasks.delivery_cost_tasks",
    ],
)

celery_app.conf.update(
    result_backend=settings.redis_dsn,
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "calculate-delivery-costs-every-5-minutes": {
            "task": "calculate_delivery_costs",
            "schedule": crontab(minute="*/5"),
            "kwargs": {"batch_size": 500},
        }
    },
)
