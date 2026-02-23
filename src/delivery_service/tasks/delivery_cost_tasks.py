import asyncio

from delivery_service.services.currency import get_usd_rub_rate
from delivery_service.tasks.celery_app import celery_app


@celery_app.task
def recalculate_delivery_costs() -> str:
    """Debug-friendly task entrypoint.

    Пока возвращает текущий USD/RUB курс, чтобы можно было проверить запуск задачи вручную.
    """
    return str(asyncio.run(get_usd_rub_rate()))
