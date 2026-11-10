import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url

from app.core.config import Settings, is_sqlite_url, normalize_database_url


@pytest.mark.parametrize(
    "raw_url",
    [
        "postgres://user:pass@db:5432/smartlearn",
        "postgresql://user:pass@db:5432/smartlearn",
        "postgresql+psycopg://user:pass@db:5432/smartlearn",
    ],
)
def test_postgres_urls_use_psycopg_driver(raw_url):
    assert normalize_database_url(raw_url) == "postgresql+psycopg://user:pass@db:5432/smartlearn"


@pytest.mark.parametrize("raw_url", ["sqlite://", "sqlite:///./smartlearn.db"])
def test_sqlite_urls_are_unchanged(raw_url):
    assert normalize_database_url(raw_url) == raw_url
    assert is_sqlite_url(raw_url)


def test_settings_normalize_postgres_url():
    settings = Settings(
        database_url="postgres://user:pass@db:5432/smartlearn",
        secret_key="test",
        _env_file=None,
    )
    url = make_url(settings.database_url)
    assert url.drivername == "postgresql+psycopg"
    assert url.host == "db"
    assert url.database == "smartlearn"
    assert not is_sqlite_url(settings.database_url)


def test_postgres_engine_loads_psycopg_dialect():
    engine = create_engine(normalize_database_url("postgresql://user:pass@localhost:5432/smartlearn"))
    assert engine.dialect.name == "postgresql"
    assert engine.dialect.driver == "psycopg"
    engine.dispose()
