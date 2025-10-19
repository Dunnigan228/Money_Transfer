import asyncio
import sys
from typing import Dict, Any
from app.utils.message_broker import message_broker
from app.utils.telegram_logger import telegram_logger
from app.core.config import settings


async def send_notification(data: Dict[str, Any]) -> None:
    user_id = data.get("user_id")
    message = data.get("message")
    notification_type = data.get("type", "info")

    if not user_id or not message:
        await telegram_logger.log_error("Notification worker: Missing data")
        return

    try:

        level_map = {
            "info": "INFO",
            "warning": "WARNING",
            "error": "ERROR",
            "success": "SUCCESS",
        }

        level = level_map.get(notification_type, "INFO")

        print(f"[Notification] User {user_id}: {message}")

        await telegram_logger.send_message(
            f"Notification to User {user_id}:\n{message}",
            level,
        )

    except Exception as e:
        await telegram_logger.log_error(
            f"Notification worker error: {str(e)}"
        )


async def main() -> None:
    await telegram_logger.log_info("Notification worker started")

    try:
        await message_broker.connect()
        await message_broker.consume_messages(
            settings.rabbitmq_notification_queue,
            send_notification,
            prefetch_count=10,
        )
    except KeyboardInterrupt:
        await telegram_logger.log_info("Notification worker stopped")
    except Exception as e:
        await telegram_logger.log_critical(f"Notification worker crashed: {str(e)}")
    finally:
        await message_broker.close()


if __name__ == "__main__":
    asyncio.run(main())
