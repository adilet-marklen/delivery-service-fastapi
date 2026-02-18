from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Основные настройки сервиса."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "delivery-service-fastapi"
    debug: bool = False

    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "delivery_service"
    postgres_user: str = "delivery_user"
    postgres_password: str = "delivery_password"

    redis_host: str = "redis"
    redis_port: int = 6379

    celery_broker_url: str = "redis://redis:6379/0"

    @property
    def database_url_async(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def database_url_sync(self) -> str:
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
