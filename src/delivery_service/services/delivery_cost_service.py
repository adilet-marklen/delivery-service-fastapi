from delivery_service.db.models.parcel import Parcel


class DeliveryCostService:
    """Считает стоимость доставки по формуле из ТЗ."""

    def calculate_cost_rub(self, *, weight_kg: float, content_value_usd: float, usd_rub: float) -> float:
        base = weight_kg * 0.5 + content_value_usd * 0.01
        return float(base * usd_rub)

    def calculate_for_parcel(self, parcel: Parcel, usd_rub: float) -> float:
        return self.calculate_cost_rub(
            weight_kg=float(parcel.weight_kg),
            content_value_usd=float(parcel.content_value_usd),
            usd_rub=usd_rub,
        )

