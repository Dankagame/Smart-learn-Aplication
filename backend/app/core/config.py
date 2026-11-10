from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

POSTGRES_DRIVER_PREFIX = "postgresql+psycopg://"
POSTGRES_PLAIN_PREFIXES = ("postgres://", "postgresql://")


def normalize_database_url(url: str) -> str:
    for prefix in POSTGRES_PLAIN_PREFIXES:
        if url.startswith(prefix):
            return POSTGRES_DRIVER_PREFIX + url[len(prefix) :]
    return url


def is_sqlite_url(url: str) -> bool:
    return url.startswith("sqlite")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "SmartLearn API"
    environment: str = "development"
    debug: bool = False

    database_url: str

    secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    cors_origins: str = ""

    @field_validator("database_url")
    @classmethod
    def database_url_must_be_set(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("DATABASE_URL is empty. Set it in backend/.env")
        return normalize_database_url(value.strip())

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
