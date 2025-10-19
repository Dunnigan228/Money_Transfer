import asyncio
import sys
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.services.transfer_service import TransferService
from app.services.audit_service import AuditService
from app.utils.message_broker import message_broker
from app.utils.telegram_logger import telegram_logger
from app.core.config import settings


async def process_transfer(data: Dict[str, Any]) -> None:
    transfer_id = data.get("transfer_id")

    if not transfer_id:
        await telegram_logger.log_error("Transfer worker: Missing transfer_id")
        return

    async with AsyncSessionLocal() as db:
        try:
            transfer_service = TransferService()
            audit_service = AuditService()

            transfer = await transfer_service.get_transfer_by_id(db, transfer_id)

            if not transfer:
                await telegram_logger.log_error(
                    f"Transfer worker: Transfer {transfer_id} not found"
                )
                return

            await transfer_service.execute_transfer(db, transfer)

            await audit_service.log_action(
                db=db,
                action="transfer_completed",
                entity_type="transfer",
                entity_id=transfer.id,
                description=f"Transfer {transfer.id} completed successfully",
            )

            await db.commit()

            await telegram_logger.log_success(
                f"Transfer {transfer_id} completed: "
                f"{transfer.from_amount} {transfer.from_currency} → "
                f"{transfer.to_amount} {transfer.to_currency}"
            )

        except Exception as e:
            await telegram_logger.log_error(
                f"Transfer worker error for transfer {transfer_id}: {str(e)}"
            )


async def main() -> None:
    await telegram_logger.log_info("Transfer worker started")

    try:
        await message_broker.connect()
        await message_broker.consume_messages(
            settings.rabbitmq_transfer_queue,
            process_transfer,
            prefetch_count=5,
        )
    except KeyboardInterrupt:
        await telegram_logger.log_info("Transfer worker stopped")
    except Exception as e:
        await telegram_logger.log_critical(f"Transfer worker crashed: {str(e)}")
    finally:
        await message_broker.close()


if __name__ == "__main__":
    asyncio.run(main())
