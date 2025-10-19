import asyncio
import sys
from typing import Dict, Any
from app.db.session import AsyncSessionLocal
from app.services.fx_rate_service import FxRateService
from app.utils.message_broker import message_broker
from app.utils.telegram_logger import telegram_logger
from app.core.config import settings


async def update_fx_rates(data: Dict[str, Any]) -> None:
    async with AsyncSessionLocal() as db:
        try:
            fx_service = FxRateService()

            currencies = ["USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD"]
            total_count = 0

            for base_currency in currencies:
                count = await fx_service.update_rates_from_api(db, base_currency)
                total_count += count

            await db.commit()

            await telegram_logger.log_success(
                f"FX rates updated: {total_count} rates imported"
            )

        except Exception as e:
            await telegram_logger.log_error(f"FX worker error: {str(e)}")


async def periodic_update() -> None:
    while True:
        try:
            await update_fx_rates({"action": "update_rates"})
            await asyncio.sleep(settings.fx_update_interval_seconds)
        except Exception as e:
            await telegram_logger.log_error(f"FX periodic update error: {str(e)}")
            await asyncio.sleep(60)


async def main() -> None:
    await telegram_logger.log_info("FX rate worker started")

    try:
        await message_broker.connect()

        periodic_task = asyncio.create_task(periodic_update())

        await message_broker.consume_messages(
            settings.rabbitmq_fx_update_queue,
            update_fx_rates,
            prefetch_count=1,
        )

        await periodic_task

    except KeyboardInterrupt:
        await telegram_logger.log_info("FX rate worker stopped")
    except Exception as e:
        await telegram_logger.log_critical(f"FX rate worker crashed: {str(e)}")
    finally:
        await message_broker.close()


if __name__ == "__main__":
    asyncio.run(main())
