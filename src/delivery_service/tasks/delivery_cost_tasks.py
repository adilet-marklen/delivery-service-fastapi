from delivery_service.tasks.calculate import calculate_delivery_costs
from delivery_service.tasks.celery_app import celery_app


@celery_app.task(name="recalculate_delivery_costs_now")
def recalculate_delivery_costs(batch_size: int = 500) -> int:
    """Ручной запуск пересчета вне beat-расписания."""
    return calculate_delivery_costs(batch_size=batch_size)
