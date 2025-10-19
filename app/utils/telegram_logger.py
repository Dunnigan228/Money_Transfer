import asyncio
from typing import Optional
from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.enums import ParseMode
from app.core.config import settings


class TelegramLogger:

    def __init__(self):
        self.bot: Optional[Bot] = None
        self.enabled = settings.telegram_logging_enabled

        if self.enabled and settings.telegram_bot_token:
            self.bot = Bot(token=settings.telegram_bot_token)
            self.admin_chat_id = settings.telegram_admin_chat_id

    async def send_message(self, message: str, level: str = "INFO") -> bool:
        if not self.enabled or not self.bot or not self.admin_chat_id:
            return False

        try:
            emoji_map = {
                "INFO": "ℹ️",
                "WARNING": "⚠️",
                "ERROR": "❌",
                "CRITICAL": "🚨",
                "SUCCESS": "✅",
            }

            emoji = emoji_map.get(level.upper(), "📝")
            formatted_message = f"{emoji} *{level}*\n\n{message}"

            await self.bot.send_message(
                chat_id=self.admin_chat_id,
                text=formatted_message,
                parse_mode=ParseMode.MARKDOWN,
            )
            return True

        except TelegramAPIError as e:
            print(f"Failed to send Telegram message: {e}")
            return False

    async def log_info(self, message: str) -> None:
        await self.send_message(message, "INFO")

    async def log_warning(self, message: str) -> None:
        await self.send_message(message, "WARNING")

    async def log_error(self, message: str) -> None:
        await self.send_message(message, "ERROR")

    async def log_critical(self, message: str) -> None:
        await self.send_message(message, "CRITICAL")

    async def log_success(self, message: str) -> None:
        await self.send_message(message, "SUCCESS")


telegram_logger = TelegramLogger()
