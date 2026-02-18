from delivery_service.services.delivery_cost_service import DeliveryCostService


def test_calculate_cost_rub() -> None:
    service = DeliveryCostService()
    result = service.calculate_cost_rub(weight_kg=10, content_value_usd=200, usd_rub=90)
    assert result == 630.0


def test_calculate_cost_rub_returns_float() -> None:
    service = DeliveryCostService()
    result = service.calculate_cost_rub(weight_kg=0.5, content_value_usd=10, usd_rub=90)
    assert isinstance(result, float)
