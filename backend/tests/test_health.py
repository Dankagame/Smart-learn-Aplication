from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app import main
from app.main import app


def test_health_reports_connected_database():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "connected"}


def test_health_reports_unavailable_database(monkeypatch):
    def failing_connection():
        raise OperationalError("SELECT 1", {}, Exception("database is down"))

    monkeypatch.setattr(main, "check_db_connection", failing_connection)

    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "unavailable"}


def test_health_rejects_post_requests():
    response = TestClient(app).post("/health")

    assert response.status_code == 405
