"""Application settings, loaded from environment variables or a .env file.

Secrets are never hard-coded: put real values in backend/.env (git-ignored)
and use backend/.env.example as the template.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # General
    app_name: str = "SmartLearn API"
    environment: str = "development"
    debug: bool = False

    # Database: SQLite locally, PostgreSQL in production
    database_url: str = "sqlite:///./smartlearn.db"

    # Authentication (JWT)
    secret_key: str = "change-me-in-env"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # CORS: comma-separated list of allowed frontend origins
    cors_origins: str = "http://localhost:5500,http://127.0.0.1:5500"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (read the environment only once)."""
    return Settings()
