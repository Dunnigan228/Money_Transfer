from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):

    app_name: str = Field(default="Money Transfer Service", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    debug: bool = Field(default=False, alias="DEBUG")
    environment: str = Field(default="production", alias="ENVIRONMENT")

    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")

    database_url: str = Field(
        default="sqlite+aiosqlite:///./money_transfer.db",
        alias="DATABASE_URL"
    )
    db_echo: bool = Field(default=False, alias="DB_ECHO")

    jwt_secret_key: str = Field(alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(
        default=30,
        alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    rabbitmq_url: str = Field(
        default="amqp://guest:guest@localhost:5672/",
        alias="RABBITMQ_URL"
    )
    rabbitmq_transfer_queue: str = Field(
        default="transfer_processing",
        alias="RABBITMQ_TRANSFER_QUEUE"
    )
    rabbitmq_notification_queue: str = Field(
        default="notifications",
        alias="RABBITMQ_NOTIFICATION_QUEUE"
    )
    rabbitmq_fx_update_queue: str = Field(
        default="fx_rate_updates",
        alias="RABBITMQ_FX_UPDATE_QUEUE"
    )

    redis_url: str = Field(
        default="redis://localhost:6379/0",
        alias="REDIS_URL"
    )

    frankfurter_api_url: str = Field(
        default="https://api.frankfurter.app",
        alias="FRANKFURTER_API_URL"
    )
    fx_update_interval_seconds: int = Field(
        default=3600,
        alias="FX_UPDATE_INTERVAL_SECONDS"
    )

    telegram_bot_token: str = Field(default="", alias="TELEGRAM_BOT_TOKEN")
    telegram_admin_chat_id: str = Field(default="", alias="TELEGRAM_ADMIN_CHAT_ID")
    telegram_logging_enabled: bool = Field(
        default=False,
        alias="TELEGRAM_LOGGING_ENABLED"
    )

    default_fixed_commission: float = Field(
        default=0.0,
        alias="DEFAULT_FIXED_COMMISSION"
    )
    default_percentage_commission: float = Field(
        default=0.01,
        alias="DEFAULT_PERCENTAGE_COMMISSION"
    )

    default_language: str = Field(default="en", alias="DEFAULT_LANGUAGE")
    supported_languages: str = Field(
        default="en,ru,kk",
        alias="SUPPORTED_LANGUAGES"
    )

    rate_limit_per_minute: int = Field(
        default=60,
        alias="RATE_LIMIT_PER_MINUTE"
    )
    bcrypt_rounds: int = Field(default=12, alias="BCRYPT_ROUNDS")

    @property
    def supported_languages_list(self) -> List[str]:
        return [lang.strip() for lang in self.supported_languages.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"


settings = Settings()
