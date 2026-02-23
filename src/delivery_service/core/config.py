from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Типизированные настройки приложения из переменных окружения."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="DELIVERY_",
        extra="ignore",
    )

    app_name: str = "delivery-service-fastapi"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    db_dsn: str = (
        "postgresql+asyncpg://delivery_user:delivery_password@postgres:5432/delivery_service"
    )
    redis_dsn: str = "redis://redis:6379/0"
    cbr_url: str = "https://www.cbr-xml-daily.ru/daily_json.js"
    log_level: str = "INFO"
    session_cookie_name: str = "delivery_session_id"
    debug: bool = False

    @property
    def db_dsn_sync(self) -> str:
        """DSN для синхронных задач (alembic)."""
        return self.db_dsn.replace("+asyncpg", "+psycopg2")

    @property
    def safe_log_fields(self) -> dict[str, str | int]:
        """Поля, которые безопасно писать в лог при старте."""
        return {
            "app_host": self.app_host,
            "app_port": self.app_port,
            "log_level": self.log_level,
            "cbr_url": self.cbr_url,
            "session_cookie_name": self.session_cookie_name,
        }


settings = Settings()
