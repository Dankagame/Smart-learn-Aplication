"""Database engine, session factory and declarative base (SQLAlchemy 2.0)."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

# SQLite needs this flag so FastAPI can use the connection across threads.
connect_args = (
    {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
)

engine = create_engine(settings.database_url, connect_args=connect_args)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Base class that all ORM models inherit from."""


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency: open a database session per request and close it after."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
