import os

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["DEBUG"] = "false"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app import models
from app.core.database import Base, get_db
from app.main import app

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(bind=test_engine, autoflush=False, expire_on_commit=False)


@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=test_engine)
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client(db_session: Session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def create_user(client):
    def _create_user(
        role: str, email: str, full_name: str = "Test User", password: str = "StrongPass123"
    ) -> dict:
        registered = client.post(
            "/auth/register",
            json={"full_name": full_name, "email": email, "password": password, "role": role},
        )
        assert registered.status_code == 201, registered.text
        token = client.post("/auth/login", json={"email": email, "password": password}).json()[
            "access_token"
        ]
        return {**registered.json(), "headers": {"Authorization": f"Bearer {token}"}}

    return _create_user
