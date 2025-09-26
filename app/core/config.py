from typing import Optional
import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    app_name: str = "logflow"
    intercept_handler_logging: bool = True
    log_level: str = "INFO"

    # Postgres
    postgres_user: str = "logs"
    postgres_password: str = "logs"
    postgres_db: str = "logs"
    postgres_host: str = "db"
    postgres_port: int = 5432
    database_url: Optional[str] = None  # Если задана, используется как есть

    # MinIO
    minio_endpoint_host: str = "minio"
    minio_endpoint_port: int = 9000
    minio_access_key: str = "minio"
    minio_secret_key: str = "minio12345"
    minio_secure: bool = False
    minio_bucket: str = "logs"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def database_url_async(self) -> str:
        if self.database_url:
            return self.database_url
        host = self.postgres_host_effective
        port = self.postgres_port_effective
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{host}:{port}/{self.postgres_db}"
        )

    @staticmethod
    def is_running_in_docker() -> bool:
        """Проверяет, запущено ли приложение в Docker-контейнере."""
        return os.path.exists("/.dockerenv")

    @property
    def postgres_host_effective(self) -> str:
        """Корректный host БД с учётом среды (docker/локально)."""
        if self.is_running_in_docker():
            return self.postgres_host
        # При локальном запуске, если host остался контейнерным значением, подменим на localhost
        if self.postgres_host in {"db", "postgres"}:
            return "localhost"
        return self.postgres_host

    @property
    def minio_endpoint_effective(self) -> str:
        """Корректный endpoint MinIO вида host:port с учётом среды."""
        endpoint_host = self.minio_endpoint_host
        endpoint_port = self.minio_endpoint_port
        if self.is_running_in_docker():
            return f"{endpoint_host}:{endpoint_port}"
        return f"localhost:{endpoint_port}"

    @property
    def postgres_port_effective(self) -> int:
        """Корректный порт БД с учётом среды (в Docker всегда внутренний 5432)."""
        if self.is_running_in_docker():
            return 5432
        return self.postgres_port


settings = Settings()
