from __future__ import annotations

import asyncio
import logging
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import select

from delivery_service.cache.rates import get_usd_rub_rate
from delivery_service.db.models.parcel import Parcel
from delivery_service.db.session import async_session
from delivery_service.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)

WEIGHT_COEFF = Decimal("0.5")
DECLARED_COST_COEFF = Decimal("0.01")
MONEY_QUANT = Decimal("0.01")


def _calculate_cost_rub(
    *,
    weight_kg: Decimal,
    declared_cost_usd: Decimal,
    usd_rub: Decimal,
) -> Decimal:
    base = weight_kg * WEIGHT_COEFF + declared_cost_usd * DECLARED_COST_COEFF
    return (base * usd_rub).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


async def _process_unprocessed_parcels(batch_size: int) -> int:
    processed = 0
    usd_rub_rate = await get_usd_rub_rate()

    async with async_session() as session:
        while True:
            async with session.begin():
                query = (
                    select(Parcel)
                    .where(Parcel.delivery_cost_rub.is_(None))
                    .order_by(Parcel.created_at.asc())
                    .limit(batch_size)
                    .with_for_update(skip_locked=True)
                )
                parcels = list((await session.execute(query)).scalars().all())

                if not parcels:
                    break

                for parcel in parcels:
                    parcel.delivery_cost_rub = _calculate_cost_rub(
                        weight_kg=Decimal(str(parcel.weight_kg)),
                        declared_cost_usd=Decimal(str(parcel.declared_cost_usd)),
                        usd_rub=usd_rub_rate,
                    )

                processed += len(parcels)

    return processed


@celery_app.task(name="calculate_delivery_costs")
def calculate_delivery_costs(batch_size: int = 500) -> int:
    processed = asyncio.run(_process_unprocessed_parcels(batch_size=batch_size))
    logger.info("calculate_delivery_costs finished: processed=%s", processed)
    return processed
