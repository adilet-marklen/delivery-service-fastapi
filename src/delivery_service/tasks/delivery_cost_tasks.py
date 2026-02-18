from delivery_service.tasks.celery_app import celery_app


@celery_app.task
def recalculate_delivery_costs() -> None:
    return None
